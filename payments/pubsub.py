from google.cloud import pubsub_v1

publisher = pubsub_v1.PublisherClient()
payment_created_topic = publisher.topic_path("essential-tower-422709-k9", "payment-created")
payment_failed_topic = publisher.topic_path("essential-tower-422709-k9", "payment-failed")
payment_updated_topic = publisher.topic_path("essential-tower-422709-k9", "payment-udated")
payment_passed_topic = publisher.topic_path("essential-tower-422709-k9", "payment-passed")

def payment_created(payment):
    data = str(payment).encode("utf-8")
    future = publisher.publish(payment_created_topic, data)
    print(f"Published message on creating payment: {future.result()}")
    
def payment_failed(user):
    data = str(user).encode("utf-8")
    future = publisher.publish(payment_failed_topic, data)
    print(f"Published message on failing payment: {future.result()}")
    
def payment_updated(payment):
    data = str(payment).encode("utf-8")
    future = publisher.publish(payment_updated_topic, data)
    print(f"Published message on updating payment: {future.result()}")
    
def payment_passed(payment):
    data = str(payment).encode("utf-8")
    future = publisher.publish(payment_passed_topic, data)
    print(f"Published message on passing payment: {future.result()}")
    