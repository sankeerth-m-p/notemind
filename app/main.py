from fastapi import FastAPI

app = FastAPI(title="NoteMind")

@app.get("/health")
def health():
    return {"status":"ok"}
