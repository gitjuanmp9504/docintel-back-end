# routers/conversations.py
from fastapi import APIRouter, HTTPException
from uuid import UUID

from models.schemas import (
    ConversationCreate,
    ConversationMetadata,
    ConversationDetail,
    MessageHistory,
    QueryRequest,
    QueryResponse
)
from services import conversations as conversation_service

router = APIRouter(prefix="/conversations", tags=["conversations"])


@router.post("/", response_model=ConversationMetadata)
async def create_conversation(payload: ConversationCreate):
    conversation = await conversation_service.create_conversation(
        document_id=payload.document_id,
        title=payload.title,
    )
    return ConversationMetadata(**conversation)

@router.post("/{conversation_id}/messages", response_model=QueryResponse)
async def create_message(conversation_id: UUID, payload: QueryRequest):
    message = await conversation_service.create_message(
        conversation_id=conversation_id,
        document_id=payload.document_id,
        question= payload.content,
    )
    return QueryResponse(**message)

@router.get("/", response_model=list[ConversationMetadata])
async def list_conversations():
    conversations = await conversation_service.list_conversations()
    return [ConversationMetadata(**c) for c in conversations]


@router.get("/{conversation_id}", response_model=ConversationDetail)
async def get_conversation(conversation_id: UUID):
    conversation = await conversation_service.get_conversation_by_id(conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversación no encontrada")

    messages = await conversation_service.get_messages_for_conversation(conversation_id)

    return ConversationDetail(
        **conversation,
        messages=[MessageHistory(**m) for m in messages],
    )


@router.delete("/{conversation_id}")
async def delete_conversation(conversation_id: UUID):
    deleted = await conversation_service.delete_conversation(conversation_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Conversación no encontrada")
    return {"message": "Conversación eliminada"}