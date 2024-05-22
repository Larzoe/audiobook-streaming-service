from google.cloud import pubsub_v1

subscriber = pubsub_v1.SubscriberClient()
subscription_path_change = subscriber.subscription_path("essential-tower-422709-k9", "change-audiobook-sub")
subscription_path_delete = subscriber.subscription_path("essential-tower-422709-k9", "delete-audiobook-sub")
subscription_path_add = subscriber.subscription_path("essential-tower-422709-k9", "add-audiobook-sub")

def change_book_callback(message):
    print(f"Received message on changing audiobook: {message}")
    message.ack()
    
def delete_book_callback(message):
    print(f"Received message on deleting audiobook: {message}")
    message.ack()
    
def add_book_callback(message):
    print(f"Received message on adding audiobook: {message}")
    message.ack()
    
def start_subscription(subscription_path, callback):
    future = subscriber.subscribe(subscription_path, callback=callback)
    try:
        future.result()
    except KeyboardInterrupt:
        future.cancel()
    
def initialize_pubsub():
    for subscription in [subscription_path_change, subscription_path_delete, subscription_path_add]:
        if subscription == subscription_path_change:
            start_subscription(subscription, change_book_callback)
        elif subscription == subscription_path_delete:
            start_subscription(subscription, delete_book_callback)
        elif subscription == subscription_path_add:
            start_subscription(subscription, add_book_callback)
        