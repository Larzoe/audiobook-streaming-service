from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class NotificationRequest(BaseModel):
    message: str


@app.post("/send-notification")
async def send_notification(request: NotificationRequest):
    print(f"Received message: {request.message}")
    return {"status": "Message received"}
