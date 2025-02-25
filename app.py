import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv, find_dotenv
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.chains import RetrievalQA
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import PromptTemplate
from langchain_huggingface import HuggingFaceEndpoint

# Load environment variables
load_dotenv(find_dotenv())

# Create Flask app and set static folder to "public"
app = Flask(__name__, static_folder="public", static_url_path="")
# Enable CORS for all domains and routes (adjust if needed)
CORS(app, resources={r"/*": {"origins": "*"}})

# Use an absolute path for the FAISS vector store
DB_FAISS_PATH = os.path.join("vector_store", "db_faiss")

# Load the FAISS vector store
def get_vectorstore():
    embedding_model = HuggingFaceEmbeddings(model_name='sentence-transformers/all-MiniLM-L6-v2')
    try:
        db = FAISS.load_local(DB_FAISS_PATH, embedding_model, allow_dangerous_deserialization=True)
        return db
    except Exception as e:
        print("Error loading vector store:", e)
        return None

# Set custom prompt template
def set_custom_prompt():
    custom_prompt_template =  """
You are ShojebThings Chatbot, an AI assistant that provides information about the company strictly based on the given context.  
If the answer is not found in the context, simply respond with "I don't know." Do not add any extra information or make assumptions.  
If the question is a greeting (e.g., "Hello", "Hi"), respond with a warm greeting before addressing any follow-up question.  
When asked about the company, provide details only from the context.  
Keep responses clear, concise, and professional.  
Do not provide any information beyond the context, even if it seems relevant.  
Please answer the question as briefly as possible.  

Context: {context}  
Question: {question}  

Begin your response now.
"""
    return PromptTemplate(template=custom_prompt_template, input_variables=["context", "question"])

# Load Hugging Face LLM
def load_llm():
    HF_TOKEN = os.getenv("HF_TOKEN")
    if not HF_TOKEN:
        raise ValueError("HF_TOKEN is not set in your environment.")
    
    return HuggingFaceEndpoint(
        repo_id="mistralai/Mistral-7B-Instruct-v0.3",
        temperature=0.5,
        token=HF_TOKEN,
        max_length=512,
        do_sample=False
    )

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    print("Received data:", data)  # Debug log

    user_input = data.get("message", "")
    if not user_input:
        return jsonify({"error": "No message provided"}), 400

    try:
        vectorstore = get_vectorstore()
        if vectorstore is None:
            return jsonify({"error": "Failed to load the vector store"}), 500
        print("Vector store loaded successfully.")

        qa_chain = RetrievalQA.from_chain_type(
            llm=load_llm(),
            chain_type="stuff",
            retriever=vectorstore.as_retriever(search_kwargs={'k': 3}),
            return_source_documents=False,
            chain_type_kwargs={'prompt': set_custom_prompt()}
        )
        
        response = qa_chain.invoke({'query': user_input})
        print("QA Response:", response)
        result = response.get("result", "No result returned")

        return jsonify({"response": result})

    except Exception as e:
        print("Error during QA chain:", str(e))
        return jsonify({"error": str(e)}), 500

# Serve index.html from the public folder for the root URL
@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")

if __name__ == "__main__":
    # Run the app on port 5000 in debug mode
    app.run(debug=True, port=5000)

