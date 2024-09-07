from connection import postgre_connection
import json

# script to extract all dataset and store to json
# for creating a ground truth
def getData():
    # db, collection  = mongodb_connection("llm_data", "legal_document")
    conn, cur = postgre_connection()
    # legalDocuments = collection.find({},{"_id":0})

    getAll = "SELECT * FROM legal_document"
    cur.execute(getAll)
    results = cur.fetchall()
    allDocuments = []

    cur.close()
    conn.close()

    for result in results:
        allDocuments.append(result)

    return allDocuments

allDocuments = getData()
finalData = []
for data in allDocuments:
    finalData.append(data)

with open("allDocument.json", "a") as file:
    json.dump(finalData, file)