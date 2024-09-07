import requests
import os
from src.connection import mongodb_connection
import hashlib
from datetime import datetime
import time

def generate_document_id(userQuery, answer):
    # combined = f"{doc['course']}-{doc['question']}"
    combined = f"{userQuery[:10]}-{answer[:10]}"
    hash_object = hashlib.md5(combined.encode())
    hash_hex = hash_object.hexdigest()
    document_id = hash_hex[:8]
    return document_id

def query(payload):
    API_URL = "https://api-inference.huggingface.co/models/google-bert/bert-large-uncased-whole-word-masking-finetuned-squad"
    headers = {"Authorization": f"Bearer {os.getenv('HUGGINGFACE_KEY')}"}

    start_time = time.time()
    response = requests.post(API_URL, headers=headers, json=payload)
    end_time = time.time()

    responseTime = round(end_time -start_time, 2)
    return response.json(), responseTime

def captureUserInput(docId,userQuery, result, llmScore, responseTime):

    db, collection = mongodb_connection("llm_data", "evaluation_data")

    collection.insert_one({
        "doc_id": docId,
        "user_input": userQuery,
        "result": result,
        "llm_score": llmScore,
        "response_time": responseTime,
        "created_at": datetime.now().isoformat()
    })

    return "Insert Evaluation Data"

def captureUserFeedback(docId, userQuery, result, feedback):

    db, collection = mongodb_connection("llm_data", "user_feedback")

    collection.insert_one({
        "doc_id": docId,
        "user_input": userQuery,
        "result": result,
        "is_satisfied": feedback,
        "created_at": datetime.now().isoformat()
    })

    return "Insert Feedback Data"