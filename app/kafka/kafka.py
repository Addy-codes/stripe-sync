from confluent_kafka import Producer
import json

EVENT_CUSTOMER_CREATED = 'customer_created'
EVENT_CUSTOMER_DELETED = 'customer_deleted'

producer = Producer({
    'bootstrap.servers': 'localhost:9092'
})

def send_to_kafka(topic, data):
    """
    Sends a JSON serialized message to a specified Kafka topic.

    Args:
        topic (str): The Kafka topic to which the message is sent.
        data (dict): The data to be serialized and sent to the topic.

    This function serializes the 'data' dictionary to a JSON string and sends it to the specified Kafka topic.
    It ensures that the message is immediately flushed to avoid message retention in the producer buffer,
    which helps in real-time data processing needs.
    """
    # Serialize data to JSON and send to Kafka

    producer.produce(topic, key=None, value=json.dumps(data))
    producer.flush() # Flush messages to ensure they are sent immediately

def create_customer_event(action, customer_id, customer_name, customer_email):
    """
    Creates a customer-related event and sends it to the Kafka topic 'customer_events'.

    Args:
        action (str): The type of event, e.g., 'customer_created' or 'customer_deleted'.
        customer_id (str): The unique identifier of the customer.
        customer_name (str): The name of the customer.
        customer_email (str): The email of the customer.

    This function constructs a dictionary with details about a customer event based on the input parameters.
    The dictionary is then sent to the Kafka topic designated for customer events using the `send_to_kafka` function.
    """
    event_data = {
        'action': action,
        'customer_id': customer_id,
        'customer_name': customer_name,
        'customer_email': customer_email
    }
    send_to_kafka('customer_events', event_data)