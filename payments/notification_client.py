import requests

def send_notification(message):
    url = 'https://your-notification-service-url/send-notification'
    payload = {'message': message}
    response = requests.post(url, json=payload)
    return response.json().get('status')