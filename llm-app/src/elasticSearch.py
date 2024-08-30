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
        resultDocs.append(hit)

    return resultDocs


indexName = "legal-documents"
esClient = getEsClient()
query = "In the case of Nasr v NRMA Insurance [2006] NSWSC 1018, why was the plaintiff's appeal lodged out of time?"

searchResult = elasticSearch(esClient, query, indexName)
print(f"result: {searchResult[0]}")



