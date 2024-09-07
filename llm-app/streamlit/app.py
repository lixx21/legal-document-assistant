import streamlit as st
from src.elasticSearch import getEsClient, elasticSearch
from src.llm import query, captureUserInput, generate_document_id, captureUserFeedback
import time

def main():
    st.set_page_config(
        page_title= "Legal Assistant"
    )
    st.title("Legal Document Assistant")
    
    #TODO: Initialize session state
    if 'result' not in st.session_state:
        st.session_state.result = None
    if 'docId' not in st.session_state:
        st.session_state.docId = None
    if 'userInput' not in st.session_state:
        st.session_state.userInput = ""
    if 'feedbackSubmitted' not in st.session_state:
        st.session_state.feedbackSubmitted = False

    userInput = st.text_input("Enter your question:")

    indexName = "legal-documents"
    try:
        esClient = getEsClient()
    except Exception as e:
        print(e)
        st.write("it seems Elastic Search still running, please refresh again")

    if st.button("Ask"):
        if userInput:  
            with st.spinner("Preparing the answer..."):
                try:
                    #TODO: Get Context
                    ragOutputs = elasticSearch(esClient, userInput, indexName)
                    context = ""
                    for ragOutput in ragOutputs:
                        context += ragOutput['_source']['answer'] 
                    
                    #TODO: Use LLM Model
                    output, responseTime = query({"inputs": {"question": userInput,"context": context}})

                    result = output['answer']
                    docId = generate_document_id(userInput, result)
                  
                    #TODO: Save users' output performance
                    # captureUserInput(docId, userInput, result, output['score'], responseTime)

                    st.session_state.result = result
                    st.session_state.docId = docId
                    st.session_state.userInput = userInput
                    # Reset feedback submission flag
                    st.session_state.feedbackSubmitted = False

                except Exception as e:
                    print(e)
                    st.write("it seems Elastic Search still running, please refresh again")
        else:
            st.write("please enter a question before click ask")

   # Display result if available
    if st.session_state.result:
        st.write(st.session_state.result)
        
        # Feedback buttons
        # Show feedback buttons only if feedback hasn't been submitted
        if not st.session_state.feedbackSubmitted:
            feedback_col1, feedback_col2 = st.columns(2)
            with feedback_col1:
                if st.button('Satisfied'):
                    captureUserFeedback(st.session_state.docId, st.session_state.userInput, st.session_state.result, True)
                    st.session_state.feedbackSubmitted = True
            with feedback_col2:
                if st.button('Unsatisfied'):
                    captureUserFeedback(st.session_state.docId, st.session_state.userInput, st.session_state.result, False)
                    st.session_state.feedbackSubmitted = True


if __name__ == "__main__":
    main()