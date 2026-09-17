from fastapi import FastAPI

app = FastAPI(title="NoteMind")

@app.get("/health")
def health():
    return {"status":"ok"}


from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from app.db import get_db
from app.models import Note, USer
from app import auth

class SignupIn(BaseModel):
    email: EmailStr
    password: str

@app.post("/auth/signup", status_code=201)
def signup(body: SignupIn, db: Session = Depends(get_db)):
    if db.query(USer).filter(USer.email == body.email).first():
        raise HTTPException(400, "Email already registered")
    user = USer(email=body.email, hashed_password=auth.hash_password(body.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"id": user.id, "email": user.email}

@app.post("/auth/login")
def login(body: SignupIn, db: Session = Depends(get_db)):
    user = db.query(USer).filter(USer.email == body.email).first()
    if not user or not auth.verify_password(body.password, user.hashed_password):
        raise HTTPException(401, "Invalid credentials")
    return {
        "access_token": auth.create_access_token(user.id),
        "refresh_token": auth.create_refresh_token(user.id),
        "token_type": "bearer",
    }

@app.get("/me")
def me(user_id: int = Depends(auth.get_current_user_id), db: Session = Depends(get_db)):
    user = db.query(USer).get(user_id)
    return {"id": user.id, "email": user.email}


from fastapi import UploadFile, File
from app import s3 as s3_module
@app.post("/notes/{note_id}/attachment")
async def upload_attachment(note_id: int, file: UploadFile = File(...),
                             user_id: int = Depends(auth.get_current_user_id),
                             db: Session = Depends(get_db)):
    note = db.query(Note).filter(Note.id == note_id, Note.user_id == user_id).first()
    if not note:
        raise HTTPException(404, "Note not found")
    key = f"users/{user_id}/notes/{note_id}/{file.filename}"
    content = await file.read()
    s3_module.upload_file(key, content, file.content_type)
    note.s3_key = key
    db.commit()
    return {"key": key, "url": s3_module.presigned_url(key)}


from pydantic import BaseModel

class NoteIn(BaseModel):
    title: str
    body: str

@app.post("/notes")
def create_note(body: NoteIn, user_id: int = Depends(auth.get_current_user_id), db: Session = Depends(get_db)):
    note = Note(user_id=user_id, title=body.title, body=body.body)
    db.add(note)
    db.commit()
    db.refresh(note)
    return {"id": note.id}