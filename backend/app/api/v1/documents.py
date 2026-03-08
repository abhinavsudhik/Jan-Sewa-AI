from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from app.models.schemas import DocumentSummary
from datetime import datetime
from typing import List
import uuid

router = APIRouter()

# Mock document storage
MOCK_DOCUMENTS = []

@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    document_type: str = Form(...),
    category: str = Form(...)
):
    """Upload a document"""
    document_id = str(uuid.uuid4())
    
    # Read file size
    content = await file.read()
    file_size = len(content)
    
    document = DocumentSummary(
        document_id=document_id,
        document_name=file.filename,
        document_type=document_type,
        category=category,
        upload_date=datetime.now(),
        file_size=file_size
    )
    
    MOCK_DOCUMENTS.append(document)
    
    return {"document_id": document_id, "message": "Document uploaded successfully"}

@router.get("/", response_model=List[DocumentSummary])
async def list_documents():
    """List all user documents"""
    return MOCK_DOCUMENTS

@router.get("/{doc_id}", response_model=DocumentSummary)
async def get_document(doc_id: str):
    """Get document details"""
    for doc in MOCK_DOCUMENTS:
        if doc.document_id == doc_id:
            return doc
    raise HTTPException(status_code=404, detail="Document not found")

@router.delete("/{doc_id}")
async def delete_document(doc_id: str):
    """Delete a document"""
    global MOCK_DOCUMENTS
    MOCK_DOCUMENTS = [doc for doc in MOCK_DOCUMENTS if doc.document_id != doc_id]
    return {"message": "Document deleted successfully"}
