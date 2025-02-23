from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

# Define the data path
data_path = r"C:\Users\Dell\Desktop\chatbot_llm\data"
## Uncomment the following files if you're not using pipenv as your virtual environment manager
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

# Load the documents
def load_documents(data):
    loader = DirectoryLoader(data, glob="*.pdf", loader_cls=PyPDFLoader)
    documents = loader.load()
    return documents

documents = load_documents(data_path)
print(f"Total Documents Loaded: {len(documents)}")

# Create the chunks
def create_chunks(extracted_files):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=200)
    all_chunks = text_splitter.split_documents(extracted_files)
    return all_chunks

chunks = create_chunks(documents)
print(f"Total Chunks Created: {len(chunks)}")

# Get embedding model
def get_embed_model():
    embed_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    return embed_model

embed_model = get_embed_model()

# Store embeddings in FAISS
DB_FAISS_Path = "vector_store/db_faiss"

db = FAISS.from_documents(chunks, embed_model)  # Remove DB_FAISS_Path from here
db.save_local(DB_FAISS_Path)  # Save FAISS index locally

print("FAISS DB built and saved successfully.")