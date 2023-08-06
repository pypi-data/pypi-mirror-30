from RSSIngest.definitions import ROOT_DIR
import urllib.request
import os
import logging
from bs4 import BeautifulSoup
from nltk import word_tokenize, pos_tag
from nltk.corpus import stopwords
from collections import Counter


class ArticleInterpreter:
    def __init__(self, logfile_name):
        self.logger = logging.getLogger("ARTICLEINTERPRETER")
        self.configure_logger(logfile_name)
        self.attributes = {'doc_summary': []}

    def configure_logger(self, logfile):
        """
        Configure logger for ArticleInterpreter object
        :param logfile: path of log file
        """
        logger_settings = self.logger
        log_file = open(os.path.join("/tmp", logfile), 'a')
        logger_settings.setLevel(logging.DEBUG)
        handler = logging.FileHandler(os.path.abspath(log_file.name))
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        handler.setFormatter(formatter)
        logger_settings.addHandler(handler)

    def preprocess_article(self, url):
        """
        Controller for article interpreter
        :param url: Article URL
        :return: Extracted topic attributes
        """
        del self.attributes['doc_summary'][:]
        article_text = self.get_article_text(url)

        self.get_topics(article_text)
        return self.attributes

    def get_article_text(self, url):
        """
        Extracts text from article for processing
        :param url:
        :return:
        """
        html = urllib.request.urlopen(url).read()
        soup = BeautifulSoup(html, 'html.parser')
        article_text = []

        article_text.extend([h.get_text() for h in soup.find_all('h1')])
        para_list = [p.get_text() for p in soup.findAll('p')]

        para_set = set(para_list)
        distinct_paras = list(para_set)

        for para in distinct_paras:
            if len(para.split()) < 5:
                distinct_paras.remove(para)

        article_text.extend(distinct_paras)
        return article_text

    def get_topics(self, article):
        stop = set(stopwords.words('english'))
        title = article[0]

        self.attributes['title_keywords'] = Counter(list(set([noun[0] for noun in pos_tag(word_tokenize(title))
                                                    if noun[1].startswith('NN')])))
        self.attributes['title_topics'] = [p_noun for p_noun in self.attributes['title_keywords']
                                           if p_noun[0][0].isupper()]

        for para in article[1:]:
            clean_para = ' '.join([word for word in para.split() if word not in stop])
            token_para = word_tokenize(clean_para)
            len_para = len(token_para)
            matches = 0

            for keyword in self.attributes['title_keywords']:
                if keyword in token_para:
                    matches += 1
                    self.attributes['title_keywords'][keyword] += 1

            sentence_score = (matches / len_para)
            if sentence_score > 0:
                self.attributes['doc_summary'].extend([clean_para])
