from shutil import ExecError
from elasticsearch import Elasticsearch
from getData import getData
from tqdm import tqdm 

def createIndex(indexName):

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

    return esClient 

def elasticSearch(esClient, query, indexName):

    searchQuery = {
        "size":5,
        "query": {
            "bool":{
                "must": {
                    "multi_match":{
                        "query": query,
                        "fields": ["question^2", "text"],
                        "type": "best_fields"
                    }
                }
            }
        }
    }

    response = esClient.search(index=indexName, body=searchQuery)
    resultDocs = []

    for hit in response['hits']['hits']:
        resultDocs.append(hit)

    return resultDocs

# data = getData()
# # print(data[0])
# indexName = "legal-documents"
# esClient = createIndex(indexName)
# query = "In the case of Nasr v NRMA Insurance [2006] NSWSC 1018, why was the plaintiff's appeal lodged out of time?"
# print("create index...")
# for doc in data:
#     try:
#         esClient.index(index=indexName, document=doc)
#     except Exception as e:
#         print(f"error message {e}")
#         print(f"error doc: {doc}")

# searchResult = elasticSearch(esClient, query, indexName)
# print(f"result: {searchResult[0]}")



