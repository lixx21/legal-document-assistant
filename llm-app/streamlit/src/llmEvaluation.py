from streamlit.src.connection import mongodb_connection

def captureUserInput(userQuery, result, llmScore):

    db, collection = mongodb_connection("llm_data", "evaluation_data")

    collection.insert_one({
        "user_input": userQuery,
        "result": result,
        "llm_score": llmScore
    })

    return "Insert Evaluation Data"