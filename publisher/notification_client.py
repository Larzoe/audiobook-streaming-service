import requests
import os

CL_RUN_URL = os.environ["CL_URL"]


def send_notification(message):
    print("sending notification")
    url = f"{CL_RUN_URL}/send-notification"
    payload = {"message": message}
    response = requests.post(url, json=payload)
    return response.json().get("status")
