from elasticsearch import Elasticsearch

def getEsClient():

    esClient = Elasticsearch("http://elasticsearch:9200")

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
        resultDocs.append(hit['_source'])

    return resultDocs






