from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import random
from pubsub import payment_created, payment_failed, payment_updated, payment_passed
from google.cloud import pubsub_v1

DATABASE_URL = "postgresql://postgres:L7je8QQ29u3R6GDC@34.91.96.229/payments"  # wow this is bad practice, don't do this

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

subscriber = pubsub_v1.SubscriberClient()
subscription_path_account_activated = subscriber.subscription_path("essential-tower-422709-k9", "activate-account-sub")
subscription_path_account_deactivated = subscriber.subscription_path("essential-tower-422709-k9", "deactivate-account-sub")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def account_activated_callback(message, db: Session = Depends(get_db)):
    print(f"Received message on activating account: {message}")
    user = message.data.decode("utf-8")
    payment_id = random.randint(1000, 9999)  # Mock payment ID
    payment = Payment(id=payment_id, user_id=user, amount=10.0)
    db.add(payment)
    db.commit()
    payment_updated(payment)
    message.ack()
    
def account_deactivated_callback(message):
    print(f"Received message on deactivating account: {message}")
    message.ack()
    
def start_subscription(subscription_path, callback):
    future = subscriber.subscribe(subscription_path, callback=callback)
    try:
        future.result()
    except KeyboardInterrupt:
        future.cancel()
        
start_subscription(subscription_path_account_activated, account_activated_callback)
start_subscription(subscription_path_account_deactivated, account_deactivated_callback)

class Payment(Base):
    __tablename__ = "payments"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    amount = Column(Float, nullable=False)
    status = Column(String, default="pending")


Base.metadata.create_all(bind=engine)

app = FastAPI()


class PaymentCreate(BaseModel):
    user_id: int
    amount: float


class PaymentStatusUpdate(BaseModel):
    status: str



@app.post("/payments", response_model=PaymentCreate)
def create_payment(payment: PaymentCreate, db: Session = Depends(get_db)):
    # Simulate payment creation with Mollie
    payment_id = random.randint(1000, 9999)  # Mock payment ID
    new_payment = Payment(id=payment_id, user_id=payment.user_id, amount=payment.amount)
    db.add(new_payment)
    db.commit()
    db.refresh(new_payment)
    payment_created(new_payment)
    return new_payment


@app.post("/payments/{payment_id}/callback", response_model=dict)
def handle_callback(
    payment_id: int, update: PaymentStatusUpdate, db: Session = Depends(get_db)
):
    # Simulate handling a callback from Mollie
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if not payment:
        payment_failed(payment.user_id)
        raise HTTPException(status_code=404, detail="Payment not found")
    payment.status = update.status
    db.commit()
    payment_updated(payment)
    return {"message": "Payment status updated successfully"}


@app.get("/payments/{payment_id}", response_model=PaymentCreate)
def get_payment(payment_id: int, db: Session = Depends(get_db)):
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if not payment:
        payment_failed(payment)
        raise HTTPException(status_code=404, detail="Payment not found")
    payment_passed(payment)
    return payment
