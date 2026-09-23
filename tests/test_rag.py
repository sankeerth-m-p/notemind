from app.rag import chunk_text

def test_chunking_overlap():
    words = " ".join(f"word{i}" for i in range(400))
    chunks = chunk_text(words, chunk_words=150, overlap_words=30)
    assert len(chunks) >= 3
    # last 30 words of chunk 0 should reappear at the start of chunk 1 — that's the overlap
    assert chunks[0].split()[-1] in chunks[1]