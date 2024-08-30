from pymongo import MongoClient

def mongodb_connection(db_name, collection_name):
    client = MongoClient('mongodb://admin:admin@mongodb:27017/')

    db = client[db_name]
    collection = db[collection_name]

    return db, collection