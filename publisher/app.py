from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import random
import os

DB_PASS = os.environ["DB_PASSWORD"]
DB_URL = os.environ["DB_URL"]
DATABASE_URL = f"postgresql://postgres:{DB_PASS}@{DB_URL}/catalog_db"  # wow this is bad practice, don't do this

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Audiobook(Base):
    __tablename__ = "audiobooks"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    author = Column(String, nullable=False)
    genre = Column(String, nullable=False)
    price = Column(Float, nullable=False)


Base.metadata.create_all(bind=engine)

app = FastAPI()


class AudiobookCreate(BaseModel):
    title: str
    author: str
    genre: str
    price: float


class AudiobookUpdate(BaseModel):
    title: str = None
    author: str = None
    genre: str = None
    price: float = None


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/audiobooks", response_model=AudiobookCreate)
def add_audiobook(audiobook: AudiobookCreate, db: Session = Depends(get_db)):
    # Simulate adding an audiobook
    audiobook_id = random.randint(1000, 9999)  # Mock audiobook ID
    new_audiobook = Audiobook(
        id=audiobook_id,
        title=audiobook.title,
        author=audiobook.author,
        genre=audiobook.genre,
        price=audiobook.price,
    )
    db.add(new_audiobook)
    db.commit()
    db.refresh(new_audiobook)
    return new_audiobook


@app.put("/audiobooks/{audiobook_id}", response_model=AudiobookCreate)
def update_audiobook(
    audiobook_id: int, audiobook: AudiobookUpdate, db: Session = Depends(get_db)
):
    db_audiobook = db.query(Audiobook).filter(Audiobook.id == audiobook_id).first()
    if not db_audiobook:
        raise HTTPException(status_code=404, detail="Audiobook not found")

    if audiobook.title:
        db_audiobook.title = audiobook.title
    if audiobook.author:
        db_audiobook.author = audiobook.author
    if audiobook.genre:
        db_audiobook.genre = audiobook.genre
    if audiobook.price:
        db_audiobook.price = audiobook.price

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
