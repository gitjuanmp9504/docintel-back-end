# services/conversations.py
from db.connection import get_pool
from uuid import UUID
from services.embeddings import get_embedding
from services.llm import call_claude
import json

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

async def create_message(conversation_id: UUID, question: str,  document_id: UUID,  top_k: int = 5) -> dict:
    pool = get_pool()
    query = """
        INSERT INTO messages (conversation_id, role, content, created_at)
        VALUES ($1, $2, $3, NOW())
        RETURNING id, conversation_id, role, content, created_at
    """
    row = await pool.fetchrow(query, conversation_id, "user", question)

    question_embedding = await get_embedding(question)

    chunks = await pool.fetch(
        """
        SELECT
            dc.chunk_text,
            dc.page,
            dc.document_id,
            d.filename,
            1 - (dc.embedding <=> $1::vector) AS similarity
        FROM document_chunks dc
        JOIN documents d ON d.id = dc.document_id
        WHERE dc.document_id = $2
        ORDER BY dc.embedding <=> $1::vector
        LIMIT $3
        """,
        question_embedding, document_id, top_k
    )

    context = "\n\n".join([
        f"[Fragmento de página {c['page']}]\n{c['chunk_text']}"
        for c in chunks
    ])
    answer = await call_claude(question, context)

    from models.schemas import Citation, Source
    citations = [
        Citation(
            text=c["chunk_text"][:200],
            source=Source(
                document_id=c["document_id"],
                document_name=c["filename"],
                page=c["page"],
                chunk_text=c["chunk_text"],
                relevance_score=float(c["similarity"])
            )
        )
        for c in chunks
    ]

    citations_json = json.dumps([c.dict() for c in citations])
    await pool.execute(
        """
        INSERT INTO messages (conversation_id, role, content, citations)
        VALUES ($1, $2, $3, $4)
        """,
        conversation_id, "assistant", answer, citations_json
    )

    return {
        "answer": answer,
        "citations": citations
    }


async def delete_conversation(conversation_id: UUID) -> bool:
    pool = get_pool()
    query = "DELETE FROM conversations WHERE id = $1"
    result = await pool.execute(query, conversation_id)
    # result es un string tipo "DELETE 1" o "DELETE 0"
    return result.endswith("1")