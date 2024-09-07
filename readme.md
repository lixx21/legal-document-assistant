# Background

In today's legal industry, the sheer volume of legal documents, case laws, and statutes available can be overwhelming for lawyers and legal professionals. Efficiently managing and retrieving relevant legal information is crucial to building a strong case or providing timely advice to clients. However, the manual process of sifting through extensive documents can be time-consuming and prone to human error. The evolution of technology, particularly in artificial intelligence (AI) and natural language processing (NLP), has opened new avenues for enhancing legal research processes. By utilizing advanced AI models such as large language models (LLMs) and techniques like Retrieval-Augmented Generation (RAG), it is now possible to automate the retrieval of legal information with high accuracy and relevance.

# Problem Statement

Law firms and legal professionals face significant challenges in managing large collections of legal documents, case laws, and statutes. The manual process of searching for relevant information is not only time-consuming but also inefficient, as it may lead to missing critical information or wasting valuable resources on non-essential documents. Existing legal research tools often fail to provide contextually relevant suggestions or insights, limiting their usefulness in complex cases. The need for a system that can quickly, accurately, and contextually retrieve relevant legal documents is more pressing than ever.

# Solution

The Legal Document Assistant aims to solve these challenges by implementing a Retrieval-Augmented Generation (RAG) approach, combined with a powerful large language model (LLM). This system allows law firms to efficiently query vast collections of legal documents and receive contextually accurate answer. By integrating LLM with a knowledge base, the application provides lawyers with instant access to relevant case laws, legal precedents, statutes, and other legal documents. The assistant can streamline legal research, reduce the time spent on manual searches, and ensure that critical information is not overlooked, ultimately improving the legal research process and enhancing decision-making capabilities.

## Dataset

- https://www.kaggle.com/datasets/umarbutler/open-australian-legal-qa/data?select=qa.jsonl
- https://www.kaggle.com/datasets/amohankumar/legal-text-classification-dataset
- https://www.kaggle.com/datasets/kageneko/legal-case-document-summarization

## Project Flow

### Retrieval

### RAG 

- [google-bert/bert-large-uncased-whole-word-masking-finetuned-squad](https://huggingface.co/google-bert/bert-large-uncased-whole-word-masking-finetuned-squad?context=In+Nasr+v+NRMA+Insurance+%5B2006%5D+NSWSC+1018%2C+the+plaintiff%27s+appeal+was+lodged+out+of+time+because+the+summons+was+filed+on+8+June+2006%2C+seven+months+after+the+decision+of+the+Local+Court+was+made+on+4+October+2005.+No+explanation+was+provided+for+this+delay.&text=In+the+case+of+Nasr+v+NRMA+Insurance+%5B2006%5D+NSWSC+1018%2C+why+was+the+plaintiff%27s+appeal+lodged+out+of+time%3F)

### Evaluation

### Dashboard

## How to run

