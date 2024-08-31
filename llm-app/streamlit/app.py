import streamlit as st
from src.elasticSearch import getEsClient, elasticSearch
from src.llm import query

def main():
    st.set_page_config(
        page_title= "Legal Assistant"
    )
    st.title("Legal Document Assistant")
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
                        context += ragOutput['_source']['text'] 
                    
                    #TODO: Use LLM Model
                    output = query({
                        "inputs": {
                        "question": userInput,
                        "context": context
                        },
                    })

                    #TODO: Save users' output performance

                    st.write(output['answer'])

                except Exception as e:
                    print(e)
                    st.write("it seems Elastic Search still running, please refresh again")

                

        else:
            st.write("please enter a question before click ask")

if __name__ == "__main__":
    main()