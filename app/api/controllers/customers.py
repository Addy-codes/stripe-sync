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
stripe_endpoint_secret = settings.STRIPE_WEBHOOK_KEY

async def create_customer(db, customer_data: dict):
    """
    Create a new customer.

    Args:
    - db: Database session for operations.
    - customer_data: Dictionary containing the customer's 'name' and 'email'.

    Returns:
    - The created Customer object.
    
    Raises:
    - HTTPException: An error occurred that prevents the customer from being created.
    """

    # The service data is hardcoded for stripe for now, open to changes for future integrations
    service_data = {
        "local_id": customer_data['id'],
        "service_name": "stripe"
    }

    try:
        # Create the customer in the database
        customer = await create_customer_in_db(db, customer_data, service_data)
        
        # Send an event to Kafka indicating that a new customer has been created
        create_customer_event(
            EVENT_CUSTOMER_CREATED,
            customer.id,
            customer.name,
            customer.email
        )
        
        return customer
    except Exception as e:
        # Raising an HTTPException with a specific status code and detail
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
    """
    Process incoming Stripe webhook events.

    This function handles different Stripe events like customer creation and deletion by parsing the event data,
    verifying the signature, and taking appropriate actions based on the event type.

    Args:
        db: The database session for any database operations required.
        request (Request): The request object containing the webhook data from Stripe.

    Raises:
        HTTPException: Raises an HTTP 400 error for missing signature, JSON parsing errors,
                       signature verification failures, or unhandled event types.
    """
    payload = await request.body()
    sig_header = request.headers.get('stripe-signature')

    if not sig_header:
        raise HTTPException(status_code=400, detail="Missing Stripe signature header")

    try:
        event = stripe.Event.construct_from(
      json.loads(payload), stripe.api_key
    )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except stripe.error.SignatureVerificationError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Handling events
    if event['type'] == 'customer.created':

        customer_info = event['data']['object']
        customer = await get_customer_from_db(db, customer_info['id'])
        if customer:
            return {"status": "Already exists, ignore"}
        new_customer = {
            'id': customer_info['id'],
            'name': customer_info['name'],
            'email': customer_info['email']
        }
        await handle_customer_creation(db, new_customer)

    elif event['type'] == 'customer.deleted':

        customer_info = event['data']['object']
        customer = await get_customer_from_db(db, customer_info['id'])
        if customer:
            await handle_customer_deletion(db, event['data']['object']["id"])
        else:
            return {"status": "Does not exist, ignore"}
        
    else:
        return Response(content="Unhandled event type", status_code=400)

    return {"status": "success"}


async def handle_customer_creation(db, customer_data):
    """
    Handles the creation of a new customer in the database.

    This function is typically called by the webhook handler when a customer.created event is received.
    It adds a new customer to the database using the provided data.

    Args:
        db: The database session for performing the database operation.
        customer_data (dict): A dictionary containing the customer's details like id, name, and email.

    Returns:
        A new customer object as created in the database.

    Raises:
        HTTPException: Raises HTTP 400 if there is an issue creating the customer in the database.
    """

     # The service data is hardcoded for stripe for now, open to changes for future integrations
    service_data = {
        "local_id": customer_data['id'],
        "service_name": "stripe"
    }
    try:
        customer = await create_customer_in_db(db, customer_data, service_data)
        return customer
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


async def handle_customer_deletion(db, customer_id):
    """
    Handles the deletion of a customer from the database.

    This function is typically called by the webhook handler when a customer.deleted event is received.
    It removes the customer from the database using the provided customer ID.

    Args:
        db: The database session for performing the database operation.
        customer_id (str): The unique identifier of the customer to be deleted.

    Returns:
        A success message if the deletion was successful.

    Raises:
        HTTPException: Raises HTTP 404 if the customer is not found, or HTTP 500 for other errors during deletion.
    """
    try:
        deletion_success = await delete_customer_from_db(db, customer_id)
        if deletion_success:
            return {"message": "Customer deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="Customer not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))