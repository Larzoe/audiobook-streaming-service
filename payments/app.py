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


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/payments", response_model=PaymentCreate)
def create_payment(payment: PaymentCreate, db: Session = Depends(get_db)):
    # Simulate payment creation with Mollie
    payment_id = random.randint(1000, 9999)  # Mock payment ID
    new_payment = Payment(id=payment_id, user_id=payment.user_id, amount=payment.amount)
    db.add(new_payment)
    db.commit()
    db.refresh(new_payment)
    return new_payment


@app.post("/payments/{payment_id}/callback", response_model=dict)
def handle_callback(
    payment_id: int, update: PaymentStatusUpdate, db: Session = Depends(get_db)
):
    # Simulate handling a callback from Mollie
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    payment.status = update.status
    db.commit()
    return {"message": "Payment status updated successfully"}


@app.get("/payments/{payment_id}", response_model=PaymentCreate)
def get_payment(payment_id: int, db: Session = Depends(get_db)):
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    return payment
