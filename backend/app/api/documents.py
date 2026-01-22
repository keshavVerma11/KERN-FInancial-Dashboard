"""
Documents API routes
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.auth import get_current_user
from app.models.models import Document, DocumentStatus
from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID
from datetime import datetime

router = APIRouter()


class DocumentResponse(BaseModel):
    id: UUID
    filename: str
    file_type: Optional[str]
    file_size: Optional[int]
    status: DocumentStatus
    uploaded_at: datetime
    processed_at: Optional[datetime]
    error_message: Optional[str]
    
    class Config:
        from_attributes = True


@router.post("/upload", response_model=DocumentResponse, status_code=201)
async def upload_document(
    file: UploadFile = File(...),
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload a financial document (CSV, PDF, Excel, etc.)
    """
    # Validate file type
    allowed_types = [
        "text/csv",
        "application/pdf",
        "application/vnd.ms-excel",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    ]
    
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"File type {file.content_type} not supported. Allowed: CSV, PDF, Excel"
        )
    
    # Read file content
    content = await file.read()
    file_size = len(content)
    
    # TODO: Upload to S3 or Supabase Storage
    # For now, we'll just store metadata
    storage_path = f"uploads/{user['user_id']}/{file.filename}"
    
    # Create document record
    db_document = Document(
        organization_id=user["user_id"],
        filename=file.filename,
        file_type=file.content_type,
        file_size=file_size,
        storage_path=storage_path,
        status=DocumentStatus.PENDING
    )
    
    db.add(db_document)
    db.commit()
    db.refresh(db_document)
    
    return db_document


@router.get("/", response_model=List[DocumentResponse])
async def list_documents(
    skip: int = 0,
    limit: int = 100,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List all uploaded documents
    """
    documents = db.query(Document).filter(
        Document.organization_id == user["user_id"]
    ).order_by(Document.uploaded_at.desc()).offset(skip).limit(limit).all()
    
    return documents


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: UUID,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a single document by ID
    """
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.organization_id == user["user_id"]
    ).first()
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return document


@router.post("/{document_id}/process")
async def process_document(
    document_id: UUID,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Process a document to extract transactions
    """
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.organization_id == user["user_id"]
    ).first()
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    if document.status != DocumentStatus.PENDING:
        raise HTTPException(
            status_code=400,
            detail=f"Document already processed (status: {document.status})"
        )
    
    # Update status to processing
    document.status = DocumentStatus.PROCESSING
    db.commit()
    
    # TODO: Implement actual document processing
    # This will be in a background task/service
    # For now, return a message
    
    return {
        "message": "Document processing started",
        "document_id": document_id,
        "status": "processing"
    }


@router.delete("/{document_id}")
async def delete_document(
    document_id: UUID,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a document
    """
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.organization_id == user["user_id"]
    ).first()
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # TODO: Delete from S3/Supabase Storage
    
    db.delete(document)
    db.commit()
    
    return {"message": "Document deleted successfully"}
