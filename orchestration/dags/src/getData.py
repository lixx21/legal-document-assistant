import orjsonl
import pandas as pd
from src.connection import mongodb_connection
import os 

def getJsonData():
    
    db, collection  = mongodb_connection("llm_data", "legal_document")

    allData = []
    legalData = orjsonl.load(f"{os.getcwd()}/dags/dataset/qa.jsonl")

    for data in legalData:
        allData.append({
            # "question": data['question'],
            "text": data['answer']
        })

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

def getCsvData():

    db, collection  = mongodb_connection("llm_data", "legal_document")

    allData = []
    legalData = pd.read_csv(f"{os.getcwd()}/dags/dataset/legal_text_classification.csv")

    for data in legalData['case_text'].values:
        allData.append({"text": data})

    #TODO: Insert all_data
    print("insert all CSV data")
    collection.insert_many(allData)

    return "SUccess Insert CSV Data"
