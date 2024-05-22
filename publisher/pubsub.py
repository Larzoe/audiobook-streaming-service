from google.cloud import pubsub_v1
import json

publisher = pubsub_v1.PublisherClient()
topic_path_change = publisher.topic_path(
    "essential-tower-422709-k9", "change-audiobook"
)
topic_path_delete = publisher.topic_path(
    "essential-tower-422709-k9", "delete-audiobook"
)
topic_path_add = publisher.topic_path("essential-tower-422709-k9", "add-audiobook")


def change_book_update(audiobook):
    audiobook_json = json.dumps(audiobook)
    data = audiobook_json.encode("utf-8")
    future = publisher.publish(topic_path_change, data)
    print(f"Published message on changing audiobook: {future.result()}")


def delete_book_update(audiobook):
    audiobook_json = json.dumps(audiobook)
    data = audiobook_json.encode("utf-8")
    future = publisher.publish(topic_path_delete, data)
    print(f"Published message on deleting audiobook: {future.result()}")


def add_book_update(audiobook):
    audiobook_json = json.dumps(audiobook)
    data = audiobook_json.encode("utf-8")
    future = publisher.publish(topic_path_add, data)
    print(f"Published message on adding audiobook: {future.result()}")
