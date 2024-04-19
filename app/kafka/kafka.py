from confluent_kafka import Producer
import json

EVENT_CUSTOMER_CREATED = 'customer_created'
EVENT_CUSTOMER_DELETED = 'customer_deleted'

producer = Producer({
    'bootstrap.servers': 'localhost:9092'
})

def send_to_kafka(topic, data):
    # Ensure data is a serialized string for Kafka
    producer.produce(topic, key=None, value=json.dumps(data))
    producer.flush()

def create_customer_event(action, customer_id, customer_name, customer_email):
    event_data = {
        'action': action,
        'customer_id': customer_id,
        'customer_name': customer_name,
        'customer_email': customer_email
    }
    send_to_kafka('customer_events', event_data)