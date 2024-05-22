from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from passlib.context import CryptContext
from google.cloud import pubsub_v1
from pubsub import activate_account, deactivate_account

DATABASE_URL = "postgresql://user:password@db/accounts_db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

subscriber = pubsub_v1.SubscriberClient()
subscription_path_created = subscriber.subscription_path("essential-tower-422709-k9", "payment-created-sub")
subscription_path_updated = subscriber.subscription_path("essential-tower-422709-k9", "payment-updated-sub")
subscription_path_failed = subscriber.subscription_path("essential-tower-422709-k9", "payment-failed-sub")
subscription_path_passed = subscriber.subscription_path("essential-tower-422709-k9", "payment-passed-sub")

def payment_created_callback(message):
    print(f"Received message on creating payment: {message}")
    message.ack()
    
def payment_updated_callback(message):
    print(f"Received message on updating payment: {message}")
    message.ack()
    
def payment_failed_callback(message):
    print(f"Received message on failing payment: {message}")
    user = message.data.decode("utf-8")
    deactivate_account(user)
    message.ack()
    
def payment_passed_callback(message):
    print(f"Received message on passing payment: {message}")
    message.ack()
    
def start_subscription(subscription_path, callback):
    future = subscriber.subscribe(subscription_path, callback=callback)
    try:
        future.result()
    except KeyboardInterrupt:
        future.cancel()
        
start_subscription(subscription_path_created, payment_created_callback)
start_subscription(subscription_path_updated, payment_updated_callback)
start_subscription(subscription_path_failed, payment_failed_callback)
start_subscription(subscription_path_passed, payment_passed_callback)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)

Base.metadata.create_all(bind=engine)

app = FastAPI()

class UserCreate(BaseModel):
    username: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

@app.post("/register", response_model=dict)
def register(user: UserCreate, db: Session = Depends(get_db)):
    db_user = get_user_by_username(db, user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    hashed_password = get_password_hash(user.password)
    new_user = User(username=user.username, hashed_password=hashed_password)
    activate_account(new_user)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User registered successfully"}

@app.post("/login", response_model=dict)
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = get_user_by_username(db, user.username)
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"message": "Login successful"}
