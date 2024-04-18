from fastapi import HTTPException
from app.api.utils.customer_utils import (
    create_customer_in_db,
    get_customer_from_db,
    update_customer_in_db,
    delete_customer_from_db,
    list_all_customers_from_db,
)


async def create_customer(customer_data: dict):
    """
    Create a new customer
    """
    try:
        new_customer = await create_customer_in_db(customer_data)
        return new_customer
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


async def read_customer(customer_id: str):
    """
    Get a customer by ID
    """
    try:
        customer = await get_customer_from_db(customer_id)
        if customer:
            return customer
        else:
            raise HTTPException(status_code=404, detail="Customer not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def update_customer(customer_id: str, customer_data: dict):
    """
    Update a customer by ID
    """
    try:
        updated_customer = await update_customer_in_db(customer_id, customer_data)
        if updated_customer:
            return updated_customer
        else:
            raise HTTPException(status_code=404, detail="Customer not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def delete_customer(customer_id: str):
    """
    Delete a customer by ID
    """
    try:
        deletion_success = await delete_customer_from_db(customer_id)
        if deletion_success:
            return {"message": "Customer deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="Customer not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def list_customers():
    """
    List all customers
    """
    try:
        customers = await list_all_customers_from_db()
        return customers
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
