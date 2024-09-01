from connection import mongodb_connection
import json

# script to extract all dataset and store to json
# for creating a ground truth
def getData():
    db, collection  = mongodb_connection("llm_data", "legal_document")

    legalDocuments = collection.find({},{"_id":0})
    allDocuments = []

    for document in legalDocuments:
        allDocuments.append(document)

    return allDocuments

allDocuments = getData()
finalData = []
for data in allDocuments:
    finalData.append(data)

with open("allDocument.json", "a") as file:
    json.dump(finalData, file)