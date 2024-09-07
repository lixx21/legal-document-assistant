import orjsonl
import pandas as pd
from src.connection import mongodb_connection, postgre_connection
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

def createTable():
    conn, cur = postgre_connection()
    print(conn.status)
    # try:
    #     checkRow = "SELECT COUNT(*) Total_Row FROM public.legal_document"
    #     cur.execute(checkRow)
    #     results = cur.fetchone()
    #     for result in results:
    #         if result['Total_Row'] >0:
    #             deleteRow = "DELETE FROM public.legal_document"
    #             cur.execute(deleteRow)
    #             conn.commit()

    #             print("Truncate all data")
    # except Exception as e:
    #     print(f"error: {e}")
    try:
        create = """
            CREATE TABLE legal_document (

            id SERIAL PRIMARY KEY,
            doc_id VARCHAR(10),
            question TEXT NOT NULL,
            answer TEXT NOT NULL
        );
        """
        cur.execute(create)

    except Exception as e:
        print(e)

        try:
            print("try truncate table")
            create = """
                TRUNCATE TABLE legal_document;
            """
            cur.execute(create)

        except Exception as e:
            print(e)
    conn.commit()
    cur.close()
    conn.close()

def insertJsonData():
    
    # db, collection  = mongodb_connection("llm_data", "legal_document")

    allData = []
    legalData = orjsonl.load(f"{os.getcwd()}/dags/dataset/qa.jsonl")
    # SQL query to insert multiple rows
    conn, cur = postgre_connection()

    insert_query = """
    INSERT INTO legal_document (doc_id, question, answer) VALUES (%s, %s, %s)
    """
    for data in legalData[0:25]:

        data = {
            "question": str(data['question']),
            "text": str(data['answer'])
        }

        docId = generate_document_id(data)
        # data["doc_id"] = str(docId)


        allData.append((str(docId), str(data['question']), str(data['text'])))
    
    #TODO:insert all data
    print("insert all JSON data")
        
    try:
        # Insert data into the table
        args = ','.join(cur.mogrify("(%s,%s,%s)", i).decode('utf-8')
                        for i in allData)
        insert_query = "INSERT INTO legal_document (doc_id, question, answer) VALUES" + (args)
        print(insert_query)
        cur.execute(insert_query)

        # Commit the transaction
        conn.commit()
        print("Data inserted successfully")
    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()
    finally:
        # Close the cursor and connection
        cur.close()
        conn.close()
    
    return "SUccess Insert JSON Data"

def insertCsvData():

    # db, collection  = mongodb_connection("llm_data", "legal_document")
    conn, cur = postgre_connection()


    allData = []
    legalData = pd.read_csv(f"{os.getcwd()}/dags/dataset/legal_text_classification.csv")

    for index, row in legalData.head(25).iterrows():
        
        data = {
            "question": str(row['case_title']),
            "text": str(row['case_text'])
        }

        docId = generate_document_id(data)
        # data["doc_id"] = str(docId)

        allData.append((str(docId), data['question'], data['text']))

    #TODO: Insert all_data
    print("insert all CSV data")
    try:
        # Insert data into the tablse
        # cursor.mogrify() to insert multiple values
        args = ','.join(cur.mogrify("(%s,%s,%s)", i).decode('utf-8')
                        for i in allData)
        insert_query = "INSERT INTO legal_document (doc_id, question, answer) VALUES" + (args)
        print(insert_query)
        cur.execute(insert_query)

        # Commit the transaction
        conn.commit()
        print("Data inserted successfully")
    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()
    finally:
        # Close the cursor and connection
        cur.close()
        conn.close()

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
    print(data)
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