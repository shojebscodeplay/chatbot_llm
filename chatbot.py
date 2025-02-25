import os
import streamlit as st

from langchain.embeddings import HuggingFaceEmbeddings
from langchain.chains import RetrievalQA
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import PromptTemplate
from langchain_huggingface import HuggingFaceEndpoint
from dotenv import load_dotenv, find_dotenv

# Load environment variables
load_dotenv(find_dotenv())

# Path to the FAISS vector store (using a relative path)
DB_FAISS_PATH = os.path.join("vector_store", "db_faiss")

@st.cache_resource
def get_vectorstore():
    embedding_model = HuggingFaceEmbeddings(model_name='sentence-transformers/all-MiniLM-L6-v2')
    db = FAISS.load_local(DB_FAISS_PATH, embedding_model, allow_dangerous_deserialization=True)
    return db

def set_custom_prompt(custom_prompt_template):
    return PromptTemplate(template=custom_prompt_template, input_variables=["context", "question"])

def load_llm(huggingface_repo_id, HF_TOKEN):
    llm = HuggingFaceEndpoint(
        repo_id=huggingface_repo_id,
        temperature=0.5,
        token=HF_TOKEN,
        max_length=512,
        do_sample=False
    )
    return llm

def main():
    st.title("Hello, hope you are doing well!")

    # Initialize chat history with a welcome message if not already set
    if 'messages' not in st.session_state:
        st.session_state.messages = []
        welcome_message = (
            "Hi, I am ShojebThings Chatbot. I will give you info about this company, ask your queries about the company."
        )
        st.session_state.messages.append({'role': 'assistant', 'content': welcome_message})

    # Display chat history
    for message in st.session_state.messages:
        st.chat_message(message['role']).markdown(message['content'])

    # Get new user prompt
    prompt = st.chat_input("Pass your prompt here")

    if prompt:
        st.chat_message('user').markdown(prompt)
        st.session_state.messages.append({'role': 'user', 'content': prompt})

        CUSTOM_PROMPT_TEMPLATE = """
            You are ShojebThings Chatbot, an AI assistant providing information about the company strictly based on the given context.  
If the answer is not found in the context, simply respond with "I don't know." Do not add any extra information or make assumptions.  

- If a user greets you, respond warmly before addressing their question.  
- If asked about the company, provide details only from the context.  
- Keep responses clear, concise, and professional.  
- Do not provide any information beyond the context, even if it seems relevant.  

Context: {context}  
Question: {question}  

Begin your response now.
"""

        HUGGINGFACE_REPO_ID = "mistralai/Mistral-7B-Instruct-v0.3"
        HF_TOKEN = os.environ.get("HF_TOKEN")
        if not HF_TOKEN:
            st.error("HF_TOKEN is not set in your environment.")
            return

        try:
            vectorstore = get_vectorstore()
            if vectorstore is None:
                st.error("Failed to load the vector store")
                return

            qa_chain = RetrievalQA.from_chain_type(
                llm=load_llm(huggingface_repo_id=HUGGINGFACE_REPO_ID, HF_TOKEN=HF_TOKEN),
                chain_type="stuff",
                retriever=vectorstore.as_retriever(search_kwargs={'k': 3}),
                return_source_documents=False,
                chain_type_kwargs={'prompt': set_custom_prompt(CUSTOM_PROMPT_TEMPLATE)}
            )

            response = qa_chain.invoke({'query': prompt})
            result = response["result"]

            st.chat_message('assistant').markdown(result)
            st.session_state.messages.append({'role': 'assistant', 'content': result})

        except Exception as e:
            st.error(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
