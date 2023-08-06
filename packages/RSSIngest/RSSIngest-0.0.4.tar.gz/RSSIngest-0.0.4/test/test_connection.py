import pymongo


if __name__ == '__main__':
    client = pymongo.MongoClient("mongodb://ingestor:i7629228@18.220.195.22/sentdb")

    db = client.sentdb
