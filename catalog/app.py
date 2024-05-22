from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import List

# DATABASE_URL = "postgresql://postgres:L7je8QQ29u3R6GDC@34.91.96.229/catalog_db"  # wow this is bad practice, don't do this
DATABASE_URL = "sqlite:///./catalog.sqlite"


engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


from google.cloud import pubsub_v1

subscriber = pubsub_v1.SubscriberClient()
subscription_path_change = subscriber.subscription_path(
    "essential-tower-422709-k9", "change-audiobook-sub"
)
subscription_path_delete = subscriber.subscription_path(
    "essential-tower-422709-k9", "delete-audiobook-sub"
)
subscription_path_add = subscriber.subscription_path(
    "essential-tower-422709-k9", "add-audiobook-sub"
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


def start_subscription(subscription_path, callback):
    future = subscriber.subscribe(subscription_path, callback=callback)
    try:
        future.result()
    except KeyboardInterrupt:
        future.cancel()


def initialize_pubsub():
    for subscription in [
        subscription_path_change,
        subscription_path_delete,
        subscription_path_add,
    ]:
        if subscription == subscription_path_change:
            start_subscription(subscription, change_book_callback)
        elif subscription == subscription_path_delete:
            start_subscription(subscription, delete_book_callback)
        elif subscription == subscription_path_add:
            start_subscription(subscription_path_add, add_book_callback)


class Audiobook(Base):
    __tablename__ = "audiobooks"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    author = Column(String, nullable=False)
    genre = Column(String, nullable=False)
    url = Column(String, nullable=False)


Base.metadata.create_all(bind=engine)

app = FastAPI()

start_subscription(subscription_path_add, add_book_callback)


class AudiobookCreate(BaseModel):
    title: str
    author: str
    genre: str
    url: str


class AudiobookUpdate(BaseModel):
    title: str = None
    author: str = None
    genre: str = None
    url: str


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/audiobooks", response_model=List[AudiobookCreate])
def get_audiobooks(db: Session = Depends(get_db)):
    audiobooks = db.query(Audiobook).all()
    return audiobooks


@app.get("/audiobooks/{audiobook_id}", response_model=AudiobookCreate)
def get_audiobook(audiobook_id: int, db: Session = Depends(get_db)):
    audiobook = db.query(Audiobook).filter(Audiobook.id == audiobook_id).first()
    if not audiobook:
        raise HTTPException(status_code=404, detail="Audiobook not found")
    return audiobook


@app.post("/audiobooks", response_model=AudiobookCreate)
def create_audiobook(audiobook: AudiobookCreate, db: Session = Depends(get_db)):
    db_audiobook = Audiobook(
        title=audiobook.title,
        author=audiobook.author,
        genre=audiobook.genre,
        url=audiobook.url,
    )
    db.add(db_audiobook)
    db.commit()
    db.refresh(db_audiobook)
    return db_audiobook


@app.put("/audiobooks/{audiobook_id}", response_model=AudiobookCreate)
def update_audiobook(
    audiobook_id: int, audiobook: AudiobookUpdate, db: Session = Depends(get_db)
):
    db_audiobook = db.query(Audiobook).filter(Audiobook.id == audiobook_id).first()
    if not db_audiobook:
        raise HTTPException(status_code=404, detail="Audiobook not found")
    update_data = audiobook.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_audiobook, key, value)
    db.commit()
    db.refresh(db_audiobook)
    return db_audiobook


@app.delete("/audiobooks/{audiobook_id}", response_model=AudiobookCreate)
def delete_audiobook(audiobook_id: int, db: Session = Depends(get_db)):
    db_audiobook = db.query(Audiobook).filter(Audiobook.id == audiobook_id).first()
    if not db_audiobook:
        raise HTTPException(status_code=404, detail="Audiobook not found")
    db.delete(db_audiobook)
    db.commit()
    return db_audiobook
