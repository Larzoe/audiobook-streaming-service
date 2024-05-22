from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import random
from pubsub import change_book_update, delete_book_update, add_book_update
from google.cloud import pubsub_v1

# DATABASE_URL = "postgresql://postgres:L7je8QQ29u3R6GDC@34.91.96.229/publisher"  # wow this is bad practice, don't do this
import os
from notification_client import send_notification


DB_PASS = os.environ["DB_PASSWORD"]
DB_URL = os.environ["DB_URL"]
CL_RUN_URL = os.environ["CL_URL"]

DATABASE_URL = f"postgresql://postgres:{DB_PASS}@{DB_URL}/catalog_db"  # wow this is bad practice, don't do this

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

subscriber = pubsub_v1.SubscriberClient()
subscription_path_change = subscriber.subscription_path(
    "essential-tower-422709-k9", "update-audiobook-catalog-sub"
)
subscription_path_delete = subscriber.subscription_path(
    "essential-tower-422709-k9", "delete-audiobook-catalog-sub"
)
subscription_path_add = subscriber.subscription_path(
    "essential-tower-422709-k9", "create-audiobook-catalog-sub"
)


def change_book_callback(message):
    print(f"Received message on changing audiobook: {message}")
    message.ack()


def delete_book_callback(message):
    print(f"Received message on deleting audiobook: {message}")
    message.ack()


def add_book_callback(message):
    print(f"Received message on adding audiobook: {message}")
    message.ack()


class Audiobook(Base):
    __tablename__ = "audiobooks"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    author = Column(String, nullable=False)
    genre = Column(String, nullable=False)
    price = Column(Float, nullable=False)


Base.metadata.create_all(bind=engine)

app = FastAPI()

future = subscriber.subscribe(subscription_path_add, callback=add_book_callback)
future1 = subscriber.subscribe(subscription_path_change, callback=change_book_callback)
future2 = subscriber.subscribe(subscription_path_delete, callback=delete_book_callback)


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
    new_audiobook = Audiobook(
        title=audiobook.title,
        author=audiobook.author,
        genre=audiobook.genre,
        price=audiobook.price,
    )
    db.add(new_audiobook)
    db.commit()
    db.refresh(new_audiobook)
    add_book_update(new_audiobook)
    send_notification(f"New audiobook added: {new_audiobook.title}")

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
    change_book_update(db_audiobook)

    send_notification(f"Audiobook updated: {db_audiobook.title}")

    return db_audiobook


@app.delete("/audiobooks/{audiobook_id}", response_model=dict)
def delete_audiobook(audiobook_id: int, db: Session = Depends(get_db)):
    db_audiobook = db.query(Audiobook).filter(Audiobook.id == audiobook_id).first()
    if not db_audiobook:
        raise HTTPException(status_code=404, detail="Audiobook not found")

    db.delete(db_audiobook)
    db.commit()
    delete_book_update(db_audiobook)
    send_notification(f"Audiobook deleted: {db_audiobook.title}")

    return {"message": "Audiobook deleted successfully"}
