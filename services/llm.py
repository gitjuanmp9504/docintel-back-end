# services/llm.py
import os
import anthropic

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


async def call_claude(question: str, context: str) -> str:
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        messages=[
            {
                "role": "user",
                "content": f"""You are a document analysis assistant. 
Answer the question based ONLY on the provided context fragments.
If the answer is not in the context, say so clearly.

Context:
{context}

Question: {question}"""
            }
        ]
    )
    return message.content[0].text