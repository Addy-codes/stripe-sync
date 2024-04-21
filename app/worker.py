from confluent_kafka import Consumer, KafkaError
import stripe
import json
import os

from dotenv import load_dotenv

load_dotenv()

EVENT_CUSTOMER_CREATED = 'customer_created'
EVENT_CUSTOMER_DELETED = 'customer_deleted'

stripe.api_key = os.getenv('STRIPE_SECRET_KEY')

print(stripe.api_key)

consumer = Consumer({
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'my-group',
    'auto.offset.reset': 'earliest'
})

def process_message(msg):
    event = json.loads(msg)
    customer_id = event['customer_id']
    
    if event['action'] == EVENT_CUSTOMER_CREATED:
        try:
            stripe.Customer.create(id=customer_id, name=event['customer_name'], email=event['customer_email'])
            print(f"Customer {customer_id} created on Stripe")
        except Exception as e:
            print(f"Error creating customer {customer_id} on Stripe: {str(e)}")

    elif event['action'] == EVENT_CUSTOMER_DELETED:
        try:
            stripe.Customer.delete(customer_id)
            print(f"Customer {customer_id} deleted from Stripe")
        except stripe.error.InvalidRequestError:
            print(f"Customer {customer_id} not found in Stripe")
        except Exception as e:
            print(f"Error deleting customer {customer_id} on Stripe: {str(e)}")

consumer.subscribe(['customer_events'])

while True:
    msg = consumer.poll(5.0)
    if msg is None:
        continue

    if msg.error():
        if msg.error().code() == KafkaError._PARTITION_EOF:
            print('End of partition reached')
        else:
            print('Error while consuming message: {}'.format(msg.error()))
    else:
        print('Received message: {}'.format(msg.value().decode('utf-8')))
        process_message(msg.value().decode('utf-8'))
    consumer.commit()

consumer.close()
