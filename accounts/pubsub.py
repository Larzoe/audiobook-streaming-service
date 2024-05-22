from google.cloud import pubsub_v1
import json

publisher = pubsub_v1.PublisherClient()
activate_account_topic = publisher.topic_path("essential-tower-422709-k9", "activate-account")
deactivate_account_topic = publisher.topic_path("essential-tower-422709-k9", "deactivate-account")

def activate_account(user):
    user_json = json.dumps(user)
    data = user_json.encode("utf-8")
    future = publisher.publish(activate_account_topic, data)
    print(f"Published message on activating account: {future.result()}")
    
def deactivate_account(user):
    user_json = json.dumps(user)
    data = user_json.encode("utf-8")
    future = publisher.publish(deactivate_account_topic, data)
    print(f"Published message on deactivating account: {future.result()}")
