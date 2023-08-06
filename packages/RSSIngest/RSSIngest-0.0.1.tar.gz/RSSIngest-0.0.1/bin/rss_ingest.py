import os
import yaml
import feedparser
import pymongo.errors
import logging
from time import mktime
from xml.sax.saxutils import unescape
from datetime import datetime
from bin.article_interpreter import ArticleInterpreter

from definitions import ROOT_DIR, HTML_ESCAPE_TABLE, SENTDB

config_dir = os.path.join(ROOT_DIR, "config")
try:
    config_file = os.path.join(config_dir, "config.yaml")
except FileNotFoundError:
    print("No config file found.")


class RSSIngestor:
    def __init__(self):
        self.logger = logging.getLogger("RSSINGESTOR")
        self.logfile_name = self.configure_logger()
        self.config_yaml = yaml.load(open(config_file, 'r'))
        self.unproc = SENTDB['unproc']
        self.article_buffer = []

    def __str__(self):
        for rss_config in self.config_yaml.items():
            yield rss_config[0]

    def configure_logger(self):
        """
        Configures the logger for RSSIngest object
        :return: Name of the log file
        """
        logger_settings = self.logger
        logfile_name = "logs{0}{1}-LOGS.log".format(
            os.sep, str(datetime.now().replace(microsecond=0)).replace(' ', '-'))
        log_file = open(os.path.join(ROOT_DIR, logfile_name), 'w+')
        logger_settings.setLevel(logging.DEBUG)
        handler = logging.FileHandler(os.path.abspath(log_file.name))
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        handler.setFormatter(formatter)
        logger_settings.addHandler(handler)

        self.logger.debug("LOGGER OUTPUT INITIALISED")
        return logfile_name

    def get_latest_articles(self):
        """
        Retrieve latest articles from outlets found in config.yaml
        """
        for outlet, rss_url in self.config_yaml.items():
            rss = feedparser.parse(rss_url)

            for rss_item in rss['entries']:
                article_url = rss_item['id']
                if self.check_document_exists(article_url):
                    continue

                article_title = unescape(rss_item['title'], HTML_ESCAPE_TABLE)
                article_published = datetime.fromtimestamp(mktime(rss_item['published_parsed']))
                article_recorded = datetime.now().replace(microsecond=0)

                interpreter = ArticleInterpreter(self.logfile_name)
                article_attrs = interpreter.preprocess_article(article_url)

                self.add_document_to_buffer(article_url, outlet, article_title,
                                            article_attrs, article_published, article_recorded)

            buffer_size = len(self.article_buffer)
            if buffer_size > 0:
                self.logger.info("Ingesting {0} articles.".format(buffer_size))
                self.bulk_insert_articles()
            else:
                self.logger.info("No new articles to ingest.")

    def check_document_exists(self, url):
        """
        Check database to see if document already exists
        :param url: URL used as document ID
        :return: True or False
        """
        if self.unproc.find({'_id': url}).count() > 0:
            return True
        else:
            return False

    def add_document_to_buffer(self, url, outlet, title, attrs, published, ingested):
        """
        Adds dictionary object representing document to document buffer for batch insertion
        :param url: Article URL
        :param outlet: Article outlet
        :param title: Article title
        :param attrs: Dictionary of article attributes including topic(s)
        :param published: Date article was published
        :param ingested: Date article was ingested
        """
        article = {
            "_id": url,
            "outlet": outlet,
            "title": title,
            "attributes": attrs,
            "published": published,
            "ingested": ingested
        }

        self.article_buffer.append(article)

    def bulk_insert_articles(self):
        """
        Batch insert articles into mongo
        """
        while True:
            try:
                self.unproc.insert_many(self.article_buffer)
                self.logger.info("Inserted articles:")
                for article in self.article_buffer:
                    self.logger.info(article["title"])
            except pymongo.errors.BulkWriteError as bwe:
                for error in bwe.details['writeErrors']:
                    if error['code'] == 11000:
                        bad_article = error['op']
                        self.article_buffer.remove(bad_article)
                        self.logger.error("Could not insert {0} article titled '{1}' -- Already inserted.".format(
                            bad_article['outlet'].title(), bad_article['title']))
                continue
            except TypeError:
                self.logger.info("No new articles to ingest.")
                self.logger.critical(self.unproc.find())
            break


if __name__ == '__main__':
    ingestor = RSSIngestor()
    ingestor.logger.info(' '.join(ingestor.__str__()))
    ingestor.get_latest_articles()
