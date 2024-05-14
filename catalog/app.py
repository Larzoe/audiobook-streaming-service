from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

DATABASE_URL = "postgresql://user:password@db/catalog_db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Audiobook(Base):
    __tablename__ = "audiobooks"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    author = Column(String, nullable=False)
    genre = Column(String, nullable=False)

Base.metadata.create_all(bind=engine)

app = FastAPI()

class AudiobookCreate(BaseModel):
    title: str
    author: str
    genre: str

class AudiobookUpdate(BaseModel):
    title: str = None
    author: str = None
    genre: str = None

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/audiobooks", response_model=list[AudiobookCreate])
def get_audiobooks(db: Session = Depends(get_db)):
    audiobooks = db.query(Audiobook).all()
    return audiobooks

@app.post("/audiobooks", response_model=AudiobookCreate)
def add_audiobook(audiobook: AudiobookCreate, db: Session = Depends(get_db)):
    db_audiobook = Audiobook(title=audiobook.title, author=audiobook.author, genre=audiobook.genre)
    db.add(db_audiobook)
    db.commit()
    db.refresh(db_audiobook)
    return db_audiobook

@app.put("/audiobooks/{audiobook_id}", response_model=AudiobookCreate)
def update_audiobook(audiobook_id: int, audiobook: AudiobookUpdate, db: Session = Depends(get_db)):
    db_audiobook = db.query(Audiobook).filter(Audiobook.id == audiobook_id).first()
    if not db_audiobook:
        raise HTTPException(status_code=404, detail="Audiobook not found")
    
    if audiobook.title:
        db_audiobook.title = audiobook.title
    if audiobook.author:
        db_audiobook.author = audiobook.author
    if audiobook.genre:
        db_audiobook.genre = audiobook.genre
    
    db.commit()
    db.refresh(db_audiobook)
    return db_audiobook

@app.delete("/audiobooks/{audiobook_id}", response_model=dict)
def delete_audiobook(audiobook_id: int, db: Session = Depends(get_db)):
    db_audiobook = db.query(Audiobook).filter(Audiobook.id == audiobook_id).first()
    if not db_audiobook:
        raise HTTPException(status_code=404, detail="Audiobook not found")
    
    db.delete(db_audiobook)
    db.commit()
    return {"message": "Audiobook deleted successfully"}
