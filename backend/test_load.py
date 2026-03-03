import os
from langchain_community.document_loaders import PyPDFLoader, TextLoader

BASE_DATA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../data")
CORE_DATA_PATH = os.path.join(BASE_DATA_PATH, "core")

print(f"Checking path: {CORE_DATA_PATH}")
if not os.path.exists(CORE_DATA_PATH):
    print("Core path doesn't exist.")
else:
    files = os.listdir(CORE_DATA_PATH)
    print(f"Found files: {files}")
    
    docs = []
    for f in files:
        full_path = os.path.join(CORE_DATA_PATH, f)
        if f.endswith('.pdf'):
            try:
                loader = PyPDFLoader(full_path)
                docs.extend(loader.load())
                print(f"Loaded PDF: {f}")
            except Exception as e:
                print(f"Error loading {f}: {e}")
        elif f.endswith('.txt'):
            try:
                loader = TextLoader(full_path, autodetect_encoding=True)
                docs.extend(loader.load())
                print(f"Loaded TXT: {f}")
            except Exception as e:
                print(f"Error loading {f}: {e}")
                
    print(f"Total documents loaded: {len(docs)}")
