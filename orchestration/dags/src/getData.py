from src.connection import mongodb_connection

def getData():
    db, collection  = mongodb_connection("llm_data", "legal_document")

    legalDocuments = collection.find({},{"_id":0})
    allDocuments = []

    for document in legalDocuments:
        allDocuments.append(document)

    return allDocuments