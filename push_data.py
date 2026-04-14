import os
import sys
import json
import pymongo
import pandas as pd
from dotenv import load_dotenv

from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging

import certifi
ca = certifi.where()

load_dotenv()
MONGO_DB_URL = os.getenv('MONGO_DB_URL')

class NetworkDataExtract():
    def __init__(self):
        try:
            pass
        except Exception as e:
            raise NetworkSecurityException(e,sys)

    def cv_to_json_convertor(self, file_path):
        try:
            data = pd.read_csv(file_path)
            data.reset_index(drop=True, inplace=True)
            records = list(json.loads(data.T.to_json()).values())
            return records
        except Exception as e:
            raise NetworkSecurityException(e, sys)
        
    def insert_data_mongodb(self, records, database, collection):
        try:
            self.records = records
            self.database = database
            self.collection = collection

            self.mongo_client = pymongo.MongoClient(MONGO_DB_URL)
            self.database = self.mongo_client[self.database]

            self.collection = self.database[self.collection]
            self.collection.insert_many(self.records)
            return len(self.records)
        except Exception as e:
            raise NetworkSecurityException(e,sys)
        
if __name__ == "__main__":
    FILEPATH = "network_data/phisingData.csv"
    DATABASE = "Bootcamp"
    COLLECTION = "NetworkData"

    network_obj = NetworkDataExtract()
    records = network_obj.cv_to_json_convertor(FILEPATH)
    print(records)
    no_of_records = network_obj.insert_data_mongodb(records=records, database=DATABASE, collection=COLLECTION)
    print(no_of_records)