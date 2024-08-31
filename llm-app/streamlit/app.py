import streamlit as st
from src.elasticSearch import getEsClient, elasticSearch

def main():
    st.set_page_config(
        page_title= "Legal Assistant"
    )
    st.title("Legal Document Assistant")
    user_input = st.text_input("Enter your question:")

    indexName = "legal-documents"
    try:
        esClient = getEsClient()
    except Exception as e:
        print(e)
        st.write("it seems Elastic Search still running, please refresh again")

    if st.button("Ask"):
        if user_input:  
            with st.spinner("Preparing the answer..."):
                try:
                    ragOutput = elasticSearch(esClient, user_input, indexName)
                except Exception as e:
                    print(e)
                    st.write("it seems Elastic Search still running, please refresh again")
                st.write(ragOutput)

        else:
            st.write("please enter a question before click ask")

if __name__ == "__main__":
    main()