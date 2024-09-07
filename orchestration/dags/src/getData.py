from src.connection import postgre_connection

def getData():
    # db, collection  = mongodb_connection("llm_data", "legal_document")
    conn, cur = postgre_connection()
    # legalDocuments = collection.find({},{"_id":0})

    getAll = "SELECT * FROM legal_document"
    cur.execute(getAll)
    results = cur.fetchall()
    allDocuments = []

    for result in results:
        allDocuments.append(result)

    cur.close()
    conn.close()

    return allDocuments