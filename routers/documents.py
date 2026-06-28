# routers/documents.py
from fastapi import APIRouter, UploadFile, File, HTTPException
from uuid import UUID

from models.schemas import (
    DocumentUploadResponse,
    DocumentMetadata
)
from services import documents as document_service

router = APIRouter(prefix="/documents", tags=["documents"])

@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(file: UploadFile = File(...)):
    if file.content_type != "application/pdf":
            raise HTTPException(status_code=400, detail="Solo se aceptan PDFs por ahora")

    contents = await file.read()

    document = await document_service.create_document(
        filename=file.filename,
        file_bytes=contents,
    )
    return DocumentUploadResponse(**document)

@router.get("/", response_model=list[DocumentMetadata])
async def list_documents():
    documents = await document_service.list_documents()
    return [DocumentMetadata(**c) for c in documents]