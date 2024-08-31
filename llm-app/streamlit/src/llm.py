import requests
import os
from src.connection import mongodb_connection

def query(payload):
    API_URL = "https://api-inference.huggingface.co/models/google-bert/bert-large-uncased-whole-word-masking-finetuned-squad"
    headers = {"Authorization": f"Bearer {os.getenv('HUGGINGFACE_KEY')}"}

    response = requests.post(API_URL, headers=headers, json=payload)
	
    return response.json()

def captureUserInput(userQuery, result, llmScore):

    db, collection = mongodb_connection("llm_data", "evaluation_data")

    collection.insert_one({
        "user_input": userQuery,
        "result": result,
        "llm_score": llmScore
    })

    return "Insert Evaluation Data"
