from google.cloud import pubsub_v1
import json

publisher = pubsub_v1.PublisherClient()
payment_created_topic = publisher.topic_path("essential-tower-422709-k9", "payment-created")
payment_failed_topic = publisher.topic_path("essential-tower-422709-k9", "payment-failed")
payment_updated_topic = publisher.topic_path("essential-tower-422709-k9", "payment-udated")
payment_passed_topic = publisher.topic_path("essential-tower-422709-k9", "payment-passed")

def payment_created(payment):
    payment_json = json.dumps(payment)
    data = payment_json.encode("utf-8")
    future = publisher.publish(payment_created_topic, data)
    print(f"Published message on creating payment: {future.result()}")
    
def payment_failed(user):
    user_json = json.dumps(user)
    data = user_json.encode("utf-8")
    future = publisher.publish(payment_failed_topic, data)
    print(f"Published message on failing payment: {future.result()}")
    
def payment_updated(payment):
    payment_json = json.dumps(payment)
    data = payment_json.encode("utf-8")
    future = publisher.publish(payment_updated_topic, data)
    print(f"Published message on updating payment: {future.result()}")
    
def payment_passed(payment):
    payment_json = json.dumps(payment)
    data = payment_json.encode("utf-8")
    future = publisher.publish(payment_passed_topic, data)
    print(f"Published message on passing payment: {future.result()}")
