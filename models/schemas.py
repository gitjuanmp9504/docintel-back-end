from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID


# ============================================
# DOCUMENTS
# ============================================

class DocumentMetadata(BaseModel): #response when querying a document
    id: UUID
    filename: str
    page_count: Optional[int] = None
    status: str  # "processing" | "ready" | "error"
    uploaded_at: datetime


class DocumentUploadResponse(BaseModel): #response when uploading a document
    id: UUID
    filename: str
    status: str


# ============================================
# CONVERSATIONS
# ============================================

class ConversationCreate(BaseModel): #client sends this when creating a new conversation
    document_id: UUID
    title: Optional[str] = None 


class ConversationMetadata(BaseModel): #response when querying a conversation
    id: UUID
    document_id: UUID
    title: Optional[str]
    created_at: datetime

class ConversationDetail(ConversationMetadata): #Complete view of all the mssages from a conversation.
    messages: list[MessageHistory] = []
    
# ============================================
#  QUERY
# ============================================

class QueryRequest(BaseModel): #client sends this when asking a question in a conversation
    conversation_id: UUID
    document_id: UUID
    question: str
    top_k: int = Field(default=5, ge=1, le=20)  # entre 1 y 20, default 5

class QueryResponse(BaseModel): #response from a question
    answer: str
    citations: list[Citation]

class Source(BaseModel): #where is the specific data from the pdf
    document_id: UUID
    document_name: str
    page: Optional[int] = None
    chunk_text: str
    relevance_score: float


class Citation(BaseModel):
    text: str
    source: Source


# ============================================
#  MESSAGES
# ============================================

class MessageHistory(BaseModel):
    id: UUID
    role: str  # "user" | "assistant"
    content: str
    citations: Optional[list[Citation]] = None
    created_at: datetime

