import os

from sentence_transformers import SentenceTransformer

_model =None
def get_model():
    global _model
    if _model is None:
        _model=SentenceTransformer("all-MiniLM-L6-v2")
    return _model

def chunk_text(text_:str,chunk_words:int=150,overlap_words:int=30)-> list[str]:
    words=text_.split()
    chunks, i=[],0
    while i<len(words):
        chunks.append(" ".join(words[i:i+chunk_words]))
        i+=chunk_words-overlap_words
    return chunks

def embed(texts: list[str]) -> list[list[float]]:
    return get_model().encode(texts).tolist()

from sqlalchemy import text
from sqlalchemy.orm import Session

def index_note(db: Session, note_id: int, body: str):
    chunks = chunk_text(body)
    vectors = embed(chunks)
    for chunk, vector in zip(chunks, vectors):
        db.execute(
            text("INSERT INTO note_chunks (note_id, chunk_text, embedding) VALUES (:nid, :ct, :emb)"),
            {"nid": note_id, "ct": chunk, "emb": str(vector)}
        )
    db.commit()

    
def search(db: Session, query: str, user_id: int, k: int = 5) -> list[dict]:
    query_vector = embed([query])[0]
    # <=> is pgvector's cosine-distance operator: smaller = more similar
    rows = db.execute(
        text("""
            SELECT nc.chunk_text, nc.note_id, n.title
            FROM note_chunks nc
            JOIN notes n ON n.id = nc.note_id
            WHERE n.user_id = :uid
            ORDER BY nc.embedding <=> :qv
            LIMIT :k
        """),
        {"uid": user_id, "qv": str(query_vector), "k": k}
    ).fetchall()
    return [{"chunk": r[0], "note_id": r[1], "title": r[2]} for r in rows]

from google import genai

_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def ask(db: Session, question: str, user_id: int) -> dict:
    chunks = search(db, question, user_id)
    context = "\n\n".join(f"[Note: {c['title']}]\n{c['chunk']}" for c in chunks)
    prompt = f"""Answer the question using ONLY the context below. If the answer isn't in the context, say so.

Context:
{context}

Question: {question}"""
    response = _client.models.generate_content(model="gemini-3.5-flash-lite", contents=prompt)
    return {"answer": response.text, "sources": [c["note_id"] for c in chunks]}