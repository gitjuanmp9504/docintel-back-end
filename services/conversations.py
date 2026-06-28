# services/conversations.py
from db.connection import get_pool
from uuid import UUID


async def create_conversation(document_id: UUID, title: str | None) -> dict:
    pool = get_pool()
    query = """
        INSERT INTO conversations (document_id, title)
        VALUES ($1, $2)
        RETURNING id, document_id, title, created_at
    """
    row = await pool.fetchrow(query, document_id, title)
    return dict(row)


async def list_conversations() -> list[dict]:
    pool = get_pool()
    query = """
        SELECT id, document_id, title, created_at
        FROM conversations
        ORDER BY created_at DESC
    """
    rows = await pool.fetch(query)
    return [dict(row) for row in rows]


async def get_conversation_by_id(conversation_id: UUID) -> dict | None:
    pool = get_pool()
    query = """
        SELECT id, document_id, title, created_at
        FROM conversations
        WHERE id = $1
    """
    row = await pool.fetchrow(query, conversation_id)
    return dict(row) if row else None


async def get_messages_for_conversation(conversation_id: UUID) -> list[dict]:
    pool = get_pool()
    query = """
        SELECT id, role, content, citations, created_at
        FROM messages
        WHERE conversation_id = $1
        ORDER BY created_at ASC
    """
    rows = await pool.fetch(query, conversation_id)
    return [dict(row) for row in rows]


async def delete_conversation(conversation_id: UUID) -> bool:
    pool = get_pool()
    query = "DELETE FROM conversations WHERE id = $1"
    result = await pool.execute(query, conversation_id)
    # result es un string tipo "DELETE 1" o "DELETE 0"
    return result.endswith("1")