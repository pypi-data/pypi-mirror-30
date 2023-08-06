import os
import pymongo

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

HTML_ESCAPE_TABLE = {
    "&amp;": "&",
    "&quot;": '"',
    "&apos;": "'",
    "&gt;": ">",
    "&lt;": "<",
}

user = "ingestor"
pwd = "i7629228"
ssh_address = "18.220.195.22"
mongo_client = pymongo.MongoClient("mongodb://{0}:{1}@{2}:27017/sentdb".format(user, pwd, ssh_address))
SENTDB = mongo_client['sentdb']
