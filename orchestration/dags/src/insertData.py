import orjsonl
import pandas as pd
from src.connection import mongodb_connection
import os 

def insertJsonData():
    
    db, collection  = mongodb_connection("llm_data", "legal_document")

    allData = []
    legalData = orjsonl.load(f"{os.getcwd()}/dags/dataset/qa.jsonl")

    for data in legalData:
        allData.append({
            "question": str(data['question']),
            "text": str(data['answer'])
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

def insertCsvData():

    db, collection  = mongodb_connection("llm_data", "legal_document")

    allData = []
    legalData = pd.read_csv(f"{os.getcwd()}/dags/dataset/legal_text_classification.csv")

    for index, row in legalData.iterrows():
        allData.append({
            "question": str(row['case_title']),
            "text": str(row['case_text'])
        })

    print(allData[0])

    #TODO: Insert all_data
    print("insert all CSV data")
    collection.insert_many(allData)

    return "SUccess Insert CSV Data"
