from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import random
from pubsub import payment_created, payment_failed, payment_updated, payment_passed
from google.cloud import pubsub_v1
import json
import os
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import random
import os
from notification_client import send_notification


DB_PASS = os.environ["DB_PASSWORD"]
DB_URL = os.environ["DB_URL"]
CL_RUN_URL = os.environ["CL_URL"]
DATABASE_URL = f"postgresql://postgres:{DB_PASS}@{DB_URL}/storystream-db"  # wow this is bad practice, don't do this

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

subscriber = pubsub_v1.SubscriberClient()
subscription_path_account_activated = subscriber.subscription_path(
    "essential-tower-422709-k9", "activate-account-sub"
)
subscription_path_account_deactivated = subscriber.subscription_path(
    "essential-tower-422709-k9", "deactivate-account-sub"
)


class Payment(Base):
    __tablename__ = "payments"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    amount = Column(Float, nullable=False)
    status = Column(String, default="pending")

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def account_activated_callback(message):
    print(f"Received message on activating account: {message}")
    db = SessionLocal()
    user = json.loads(message.data.decode("utf-8"))
    print(user)
    payment_id = random.randint(1000, 9999)  # Mock payment ID
    if user["id"] == None:
        user_id = random.randint(1000, 9999)
    else:
        user_id = user["id"]

    payment = Payment(id=payment_id, user_id=user_id, amount=20.0)
    payment_dict = {
        "id": payment_id,
        "user_id": user_id,
        "amount": 20.0,
        "status": "pending",
    }
    db.add(payment)
    db.commit()
    db.refresh(payment)

    payment_created(payment_dict)
    message.ack()


def account_deactivated_callback(message):
    db = SessionLocal()
    print(f"Received message on deactivating account: {message}")
    user = json.loads(message.data.decode("utf-8"))
    user_id = user.id
    payment = db.query(Payment).filter(Payment.user_id == user_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    payment.status = "cancelled"
    db.commit()
    message.ack()


future = subscriber.subscribe(
    subscription_path_account_activated, callback=account_activated_callback
)
future1 = subscriber.subscribe(
    subscription_path_account_deactivated, callback=account_deactivated_callback
)


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
    payment_created(new_payment.as_dict())
    send_notification(f"New payment created: {new_payment.id}")

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
    send_notification(f"Payment {payment_id} status updated to: {update.status}")

    return {"message": "Payment status updated successfully"}


@app.get("/payments/{payment_id}", response_model=PaymentCreate)
def get_payment(payment_id: int, db: Session = Depends(get_db)):
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    return payment


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
    send_notification(f"New payment created: {new_payment.id}")

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
    send_notification(f"Payment {payment_id} status updated to: {update.status}")

    return {"message": "Payment status updated successfully"}


@app.get("/payments/{payment_id}", response_model=PaymentCreate)
def get_payment(payment_id: int, db: Session = Depends(get_db)):
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if not payment:
        payment_failed(payment)
        raise HTTPException(status_code=404, detail="Payment not found")
    payment_passed(payment)
    return payment


@app.delete("/payments/{payment_id}", response_model=dict)
def cancel_payment(payment_id: int, db: Session = Depends(get_db)):
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    payment.status = "cancelled"
    db.commit()
    return {"message": "Payment cancelled successfully"}
