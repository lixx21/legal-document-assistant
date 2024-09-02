import orjsonl
import pandas as pd
from src.connection import mongodb_connection
import os 
from shutil import ExecError
from elasticsearch import Elasticsearch
from src.getData import getData
import hashlib

def generate_document_id(doc):
    # combined = f"{doc['course']}-{doc['question']}"
    combined = f"{doc['text'][:10]}-{doc['question']}"
    hash_object = hashlib.md5(combined.encode())
    hash_hex = hash_object.hexdigest()
    document_id = hash_hex[:8]
    return document_id

def insertJsonData():
    
    db, collection  = mongodb_connection("llm_data", "legal_document")

    allData = []
    legalData = orjsonl.load(f"{os.getcwd()}/dags/dataset/qa.jsonl")

    for data in legalData[0:500]:

        data = {
            "question": str(data['question']),
            "text": str(data['answer'])
        }

        docId = generate_document_id(data)
        data["doc_id"] = str(docId)

        allData.append(data)

    try:
        if collection.count_documents({})>0:
            collection.delete_many({})
            print("Truncate all data")
    except Exception as e:
        print(f"error: {e}")
        
    #TODO:insert all data
    print("insert all JSON data")
        
    collection.insert_many(allData)
    
    return "Success Insert JSON data"

def insertCsvData():

    db, collection  = mongodb_connection("llm_data", "legal_document")

    allData = []
    legalData = pd.read_csv(f"{os.getcwd()}/dags/dataset/legal_text_classification.csv")

    for index, row in legalData.head(500).iterrows():
        
        data = {
            "question": str(row['case_title']),
            "text": str(row['case_text'])
        }

        docId = generate_document_id(data)
        data["doc_id"] = str(docId)

        allData.append(data)

    #TODO: Insert all_data
    print("insert all CSV data")
    collection.insert_many(allData)

    return "SUccess Insert CSV Data"

def createIndex():

    esClient = Elasticsearch("http://elasticsearch:9200")
    indexSettings= {
        "settings": {
            "number_of_shards": 1,
            "number_of_replicas": 0
        },
        "mappings":{
            "properties":{
                "question": {"type": "text"},
                "text": {"type": "text"},
                
            }
        }
    }
    try:
        esClient.indices.create(index=indexName, body=indexSettings)
    except:
        pass

    #TODO: Ingest data
    data = getData()
    indexName = "legal-documents"
    print("create index...")

    # Check if the index exists
    if esClient.indices.exists(index=indexName):
        # Delete the index
        print("delete old index")
        esClient.indices.delete(index=indexName)

    for doc in data:
        try:
            esClient.index(index=indexName, document=doc)
        except Exception as e:
            print(f"error message {e}")
            print(f"error doc: {doc}")

    return "Success Ingest Data"