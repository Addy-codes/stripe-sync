from fastapi import HTTPException, Response, Request
from app.api.utils.customer_utils import (
    create_customer_in_db,
    get_customer_from_db,
    update_customer_in_db,
    delete_customer_from_db,
    list_all_customers_from_db,
)
from ...core.config import settings
import stripe
import json
from ...db.connection import get_db
from ...kafka.kafka import(
    create_customer_event,
    EVENT_CUSTOMER_CREATED,
    EVENT_CUSTOMER_DELETED
)


stripe.api_key = settings.STRIPE_API_KEY
stripe_endpoint_secret = settings.STRIPE_SECRET_KEY

async def create_customer(db, customer_data: dict):
    """
    Create a new customer
    """
    try:
        customer = await create_customer_in_db(db, customer_data)
        create_customer_event(EVENT_CUSTOMER_CREATED, customer.id, customer.name, customer.email)
        return customer
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


async def read_customer(db, customer_id):
    """
    Get a customer by ID
    """
    try:
        customer = await get_customer_from_db(db, customer_id)
        if customer:
            return customer
        else:
            raise HTTPException(status_code=404, detail="Customer not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def update_customer(db, customer_id, customer_data: dict):
    """
    Update a customer by ID
    """
    try:
        updated_customer = await update_customer_in_db(db, customer_id, customer_data)
        if updated_customer:
            return updated_customer
        else:
            raise HTTPException(status_code=404, detail="Customer not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def delete_customer(db, customer_id):
    """
    Delete a customer by ID
    """
    try:
        deletion_success = await delete_customer_from_db(db, customer_id)
        if deletion_success:
            create_customer_event(EVENT_CUSTOMER_DELETED, customer_id, "", "")
            return {"message": "Customer deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="Customer not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def list_customers(db):
    """
    List all customers
    """
    try:
        customers = await list_all_customers_from_db(db=db)
        return customers
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def stripe_webhook(db, request: Request):
    payload = await request.body()
    sig_header = request.headers.get('stripe-signature')
    if not sig_header:
        raise HTTPException(status_code=400, detail="Missing Stripe signature header")
    
    print("payload: ", payload)
    print("stripe-signature: ", sig_header)

    try:
        event = stripe.Event.construct_from(
      json.loads(payload), stripe.api_key
    )

    except ValueError as e:
        print("1")
        raise HTTPException(status_code=400, detail=str(e))
    except stripe.error.SignatureVerificationError as e:
        print("2")
        raise HTTPException(status_code=400, detail=str(e))

    # Handling events
    if event['type'] == 'customer.created':
        customer_info = event['data']['object']
        new_customer = {
            'id': customer_info['id'],
            'name': customer_info['name'],
            'email': customer_info['email']
        }
        await create_customer(db, new_customer)
    elif event['type'] == 'customer.deleted':
        await delete_customer(db, event['data']['object']["id"])
    else:
        return Response(content="Unhandled event type", status_code=400)

    return {"status": "success"}

# Define the event handlers
def handle_customer_created(customer):
    print("Customer created:", customer)

def handle_customer_deleted(customer):
    print("Customer deleted:", customer)