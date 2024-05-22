from google.cloud import pubsub_v1

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
        
def initialize_pubsub():
    for subscription in [subscription_path_created, subscription_path_updated, subscription_path_failed, subscription_path_passed]:
        if subscription == subscription_path_created:
            start_subscription(subscription, payment_created_callback)
        elif subscription == subscription_path_updated:
            start_subscription(subscription, payment_updated_callback)
        elif subscription == subscription_path_failed:
            start_subscription(subscription, payment_failed_callback)
        elif subscription == subscription_path_passed:
            start_subscription(subscription, payment_passed_callback)