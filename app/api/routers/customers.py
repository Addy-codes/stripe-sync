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
stripe_endpoint_secret = settings.STRIPE_SECRET_KEY

@router.post("/customers/", status_code=201)
async def create_customer(customer_data: dict, db: AsyncSession = Depends(get_db)):
    """
    Create a new customer
    """
    try:
        new_customer = await create_customer_controller(db, customer_data)
        return new_customer
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/customers/{customer_id}")
async def read_customer(customer_id: str, db: AsyncSession = Depends(get_db)):
    """
    Get a customer by ID
    """
    try:
        customer = await read_customer_controller(db, int(customer_id))
        if customer:
            return customer
        else:
            raise HTTPException(status_code=404, detail="Customer not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/customers/{customer_id}")
async def update_customer(customer_id: str, customer_data: dict, db: AsyncSession = Depends(get_db)):
    """
    Update a customer by ID
    """
    try:
        updated_customer = await update_customer_controller(db, int(customer_id), customer_data)
        if updated_customer:
            return updated_customer
        else:
            raise HTTPException(status_code=404, detail="Customer not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/customers/{customer_id}", status_code=204)
async def delete_customer(customer_id: str, db: AsyncSession = Depends(get_db)):
    """
    Delete a customer by ID
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
    try:
        # Example function call that uses the session
        customers = await list_customers_controller(db)
        return customers
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stripe-webhook")
async def stripe_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    try:
        event = await stripe_webhook_controller(db=db, request=request)
        return event
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    