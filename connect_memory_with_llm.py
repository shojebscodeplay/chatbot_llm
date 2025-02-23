from langchain_huggingface import HuggingFaceEndpoint, HuggingFaceEmbeddings
from langchain_core.prompts import PromptTemplate  # If this causes issues, try: from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from langchain_community.vectorstores import FAISS
from dotenv import load_dotenv, find_dotenv
import os

# Load environment variables from .env file
dotenv_path = find_dotenv()
print("Found .env file at:", dotenv_path)
load_dotenv(dotenv_path)
HF_Token = os.environ.get('HF_Token')
print('HF_Token:', HF_Token)

# Repository for the LLM model
huggingface_repo_id = "mistralai/Mistral-7B-Instruct-v0.3"

# Function to load the LLM using HuggingFaceEndpoint
def load_llm(huggingface_repo_id):
    llm = HuggingFaceEndpoint(
        repo_id=huggingface_repo_id,
        temperature=0.5,
        model_kwargs={
            "token": HF_Token,
            "max_length": "512"
        }
    )
    return llm

# Define a custom prompt template
CUSTOM_PROMPT_TEMPLATE = """
Use the pieces of information provided in the context to answer the user's question.
If you don't know the answer, just say that you don't know; don't try to make up an answer. 
Don't provide anything outside of the given context.

Context: {context}
Question: {question}

Start the answer directly. No small talk, please.
"""

def set_custom_prompt(custom_prompt_template):
    prompt = PromptTemplate(
        template=custom_prompt_template, 
        input_variables=["context", "question"]
    )
    return prompt

# Load FAISS vector store
DB_FAISS_PATH = r"C:\Users\Dell\Desktop\chatbot_llm\vector_store\db_faiss"
embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
db = FAISS.load_local(DB_FAISS_PATH, embedding_model, allow_dangerous_deserialization=True)

# Create QA chain
qa_chain = RetrievalQA.from_chain_type(
    llm=load_llm(huggingface_repo_id),
    chain_type="stuff",
    retriever=db.as_retriever(search_kwargs={'k': 3}),
    return_source_documents=False,
    chain_type_kwargs={'prompt': set_custom_prompt(CUSTOM_PROMPT_TEMPLATE)}
)

# Get user query and run the chain
user_query = input("Write Query Here: ")
response = qa_chain.invoke({'query': user_query})
print("RESULT:", response["result"])
#print("SOURCE DOCUMENTS:", response["source_documents"])

