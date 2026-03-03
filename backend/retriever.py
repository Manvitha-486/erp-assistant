import os
import shutil
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from embeddings import get_embeddings

BASE_DATA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
CORE_DATA_PATH = os.path.join(BASE_DATA_PATH, "core")
UPLOADS_DATA_PATH = os.path.join(BASE_DATA_PATH, "uploads")
VECTOR_STORE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "vector_store")

print(f"DEBUG: BASE_DATA_PATH={BASE_DATA_PATH}", flush=True)
print(f"DEBUG: VECTOR_STORE_PATH={VECTOR_STORE_PATH}", flush=True)

# Simple memory cache so we don't read from disk every time
_vector_stores = {}

def get_db_path(index_name):
    return os.path.join(VECTOR_STORE_PATH, f"faiss_index_{index_name}")

def load_or_build_index(folder_path, index_name):
    """Loads a FAISS index from disk, or builds it from scratch if it doesn't exist."""
    global _vector_stores
    
    # 1. Check if it's already loaded in memory
    if index_name in _vector_stores:
        return _vector_stores[index_name]
        
    db_path = get_db_path(index_name)
    embeddings = get_embeddings()
    
    # 2. Check if it's saved on the hard drive
    if os.path.exists(db_path):
        print(f"Loading index from disk: {index_name}")
        store = FAISS.load_local(db_path, embeddings, allow_dangerous_deserialization=True)
        _vector_stores[index_name] = store
        return store
        
    # 3. Otherwise, we must read the raw PDFs/TXTs and build it
    print(f"Building new index '{index_name}' from {folder_path}...")
    documents = []
    
    if os.path.exists(folder_path):
        for file in os.listdir(folder_path):
            file_path = os.path.join(folder_path, file)
            if file.endswith('.pdf'):
                documents.extend(PyPDFLoader(file_path).load())
            elif file.endswith('.txt'):
                documents.extend(TextLoader(file_path, autodetect_encoding=True).load())

    if not documents:
        return None

    # Split text and embed
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=400, chunk_overlap=50)
    chunks = text_splitter.split_documents(documents)
    
    # Save the new index to memory and disk
    store = FAISS.from_documents(chunks, embeddings)
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    store.save_local(db_path)
    
    _vector_stores[index_name] = store
    return store

def init_custom_vector_store(filename):
    """Handles building an index for a freshly uploaded file."""
    # Create a temporary folder to process just this single file
    temp_folder = os.path.join(UPLOADS_DATA_PATH, f"temp_{filename}")
    os.makedirs(temp_folder, exist_ok=True)
    
    source_file = os.path.join(UPLOADS_DATA_PATH, filename)
    dest_file = os.path.join(temp_folder, filename)
    
    if os.path.exists(source_file):
        shutil.copy2(source_file, dest_file)
        
        # Delete old disk index if it exists to force rebuild
        db_path = get_db_path(filename)
        if os.path.exists(db_path):
            shutil.rmtree(db_path)
            if filename in _vector_stores:
                del _vector_stores[filename]
                
        # Build new index
        store = load_or_build_index(temp_folder, filename)
        shutil.rmtree(temp_folder) # cleanup temp
        return store
    return None

def get_retriever(document_id="general"):
    """Returns the text search engine for the given document module."""
    if document_id == "general":
        vector_store = load_or_build_index(CORE_DATA_PATH, "general")
    else:
        vector_store = load_or_build_index(UPLOADS_DATA_PATH, document_id)
        # Fallback if not indexed yet
        if not vector_store:
             vector_store = init_custom_vector_store(document_id)
        
    if vector_store:
        return vector_store.as_retriever(search_kwargs={"k": 3})
    return None

def list_available_documents():
    """Returns a list of available document modules."""
    docs = [{"id": "general", "name": "General ERP Database"}]
    
    if os.path.exists(UPLOADS_DATA_PATH):
        for file in os.listdir(UPLOADS_DATA_PATH):
            if file.endswith(('.pdf', '.txt')):
                docs.append({"id": file, "name": file})
    return docs

def clear_user_data():
    """Deletes all user uploaded files and their specific embeddings."""
    global _vector_stores
    
    # Delete uploaded files
    if os.path.exists(UPLOADS_DATA_PATH):
        for file in os.listdir(UPLOADS_DATA_PATH):
            file_path = os.path.join(UPLOADS_DATA_PATH, file)
            if os.path.isfile(file_path):
                os.remove(file_path)
                
    # Delete vector indices EXCEPT 'general'
    if os.path.exists(VECTOR_STORE_PATH):
        for item in os.listdir(VECTOR_STORE_PATH):
            if item.startswith("faiss_index_") and item != "faiss_index_general":
                shutil.rmtree(os.path.join(VECTOR_STORE_PATH, item))
                    
    # Clear memory cache for everything except 'general'
    _vector_stores = {k: v for k, v in _vector_stores.items() if k == "general"}
    
    return {"status": "success"}
