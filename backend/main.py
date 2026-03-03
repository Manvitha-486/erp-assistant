from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from rag_pipeline import process_query
from retriever import init_custom_vector_store, list_available_documents, clear_user_data, UPLOADS_DATA_PATH
import uvicorn
import os

print("--- STARTING APP ---", flush=True)
app = FastAPI(title="ERP QA Assistant API")
print("FastAPI initialized", flush=True)

# Setup CORS for the React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    question: str
    document_id: str = "general"

@app.get("/documents")
async def get_documents():
    """Returns a list of available document modules."""
    try:
        return list_available_documents()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/clear")
async def clear_data():
    """Deletes all user uploaded documents and their specific vector indices."""
    try:
        result = clear_user_data()
        return {"message": "All user data securely deleted.", "details": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/query")
async def query_erp(request: QueryRequest):
    if not request.question:
        raise HTTPException(status_code=400, detail="Question cannot be empty.")
        
    try:
        response = process_query(request.question, request.document_id)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    if not file.filename.endswith(('.pdf', '.txt')):
        raise HTTPException(status_code=400, detail="Only PDF and TXT files are supported.")
    
    file_path = os.path.join(UPLOADS_DATA_PATH, file.filename)
    try:
        if not os.path.exists(UPLOADS_DATA_PATH):
            os.makedirs(UPLOADS_DATA_PATH, exist_ok=True)
            
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
            
        # Build the vector store index specific to this newly uploaded file
        init_custom_vector_store(file.filename)
        return {
            "message": f"Successfully uploaded and indexed {file.filename}",
            "document": {"id": file.filename, "name": file.filename}
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process file: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
