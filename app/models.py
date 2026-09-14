from sqlalchemy import Column,Integer,String,Text,ForeignKey,DateTime,func
from sqlalchemy.dialects.postgresql import ARRAY
from pgvector.sqlalchemy import Vector
from app.db import Base

class USer(Base):
    __tablename__="users"
    id =Column(Integer,primary_key=True)
    email = Column(String,unique=True,nullable=False,index=True)
    hashed_password=Column(String,nullable=False)
    created_At=Column(DateTime,server_default=func.now())

class Note(Base):
    __tablename__ = "notes"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String, nullable=False)
    body = Column(Text, nullable=False)
    s3_key = Column(String, nullable=True)       # optional attachment
    created_at = Column(DateTime, server_default=func.now())

class NoteChuck(Base):
    __tablename__="note_chunks"
    id=Column(Integer,primary_key=True)
    note_id=Column(Integer,ForeignKey("notes.id"),nullable=False,index=True)
    chunk_text=Column(Text,nullable=False)
    embedding=Column(Vector(384)) #384 =all-MiniLM-L6-v2 output size


