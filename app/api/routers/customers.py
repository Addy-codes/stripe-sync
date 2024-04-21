from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from ...db.connection import get_db
from fastapi import HTTPException
from app.api.controllers.customers import (
    create_customer as create_customer_controller,
    read_customer as read_customer_controller,
    update_customer as update_customer_controller,
    delete_customer as delete_customer_controller,
    list_customers as list_customers_controller,
    stripe_webhook as stripe_webhook_controller
)
from ...core.config import settings
import stripe
import json

router = APIRouter()

# Set your Stripe secret key and endpoint secret
stripe.api_key = settings.STRIPE_API_KEY
stripe_endpoint_secret = settings.STRIPE_WEBHOOK_KEY

@router.post("/stripe-webhook")
async def stripe_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    """
    Process webhook events sent by Stripe.

    Args:
        request (Request): The request object containing the webhook data from Stripe.
        db (AsyncSession): The database session dependency injected by FastAPI.

    Returns:
        The response from the webhook controller which processes the event.

    Raises:
        HTTPException: An error status and message if an exception occurs during processing.
    """
    try:
        event = await stripe_webhook_controller(db=db, request=request)
        return event
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/customers/", status_code=201)
async def create_customer(customer_data: dict, db: AsyncSession = Depends(get_db)):
    """
    Create a new customer in the database from provided data.

    Args:
        customer_data (dict): A dictionary containing customer data, typically including 'name' and 'email'.
        db (AsyncSession): The database session dependency injected by FastAPI, used for transaction management.

    Returns:
        The newly created customer object, serialized for response.

    Raises:
        HTTPException: An error status and message if there's a problem during customer creation.
    """
    try:
        new_customer = await create_customer_controller(db, customer_data)
        return new_customer
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    
@router.delete("/customers/{customer_id}", status_code=204)
async def delete_customer(customer_id: str, db: AsyncSession = Depends(get_db)):
    """
    Delete a customer by their unique ID.

    Args:
        customer_id (str): The unique identifier of the customer to delete.
        db (AsyncSession): The database session dependency injected by FastAPI.

    Returns:
        A success message if the deletion is successful.

    Raises:
        HTTPException: An error status and message if the customer cannot be found or if an error occurs during deletion.
    """
    try:
        deletion_success = await delete_customer_controller(db, customer_id)
        if deletion_success:
            return {"message": "Customer deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="Customer not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/customers/")
async def list_customers(db: AsyncSession = Depends(get_db)):
    """
    List all customers in the database.

    Args:
        db (AsyncSession): The database session dependency injected by FastAPI, used for querying the database.

    Returns:
        A list of all customer objects, serialized for response.

    Raises:
        HTTPException: An error status and message if an internal error occurs during the fetching of customers.
    """
    try:
        customers = await list_customers_controller(db)
        return customers
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/customers/{customer_id}")
async def read_customer(customer_id: str, db: AsyncSession = Depends(get_db)):
    """
    Retrieve a customer by their unique ID.

    Args:
        customer_id (str): The unique identifier of the customer to retrieve.
        db (AsyncSession): The database session dependency injected by FastAPI, used for querying the database.

    Returns:
        The customer object if found, serialized for response.

    Raises:
        HTTPException: An error status and message if no customer is found with the given ID or if an internal error occurs.
    """
    try:
        customer = await read_customer_controller(db, customer_id)
        if customer:
            return customer
        else:
            raise HTTPException(status_code=404, detail="Customer not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@router.put("/customers/{customer_id}")
async def update_customer(customer_id: str, customer_data: dict, db: AsyncSession = Depends(get_db)):
    """
    Update an existing customer by their unique ID with provided data.

    Args:
        customer_id (str): The unique identifier of the customer to update.
        customer_data (dict): A dictionary containing the data to update the customer with.
        db (AsyncSession): The database session dependency injected by FastAPI.

    Returns:
        The updated customer object, serialized for response.

    Raises:
        HTTPException: An error status and message if no customer is found with the given ID or if an internal error occurs during update.
    """
    try:
        updated_customer = await update_customer_controller(db, customer_id, customer_data)
        if updated_customer:
            return updated_customer
        else:
            raise HTTPException(status_code=404, detail="Customer not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
