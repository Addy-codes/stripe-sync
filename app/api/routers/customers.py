from fastapi import APIRouter


from fastapi import HTTPException
from app.api.controllers.customers import (
    create_customer as create_customer_controller,
    read_customer as read_customer_controller,
    update_customer as update_customer_controller,
    delete_customer as delete_customer_controller,
    list_customers as list_customers_controller,
)

router = APIRouter()


@router.post("/customers/", status_code=201)
async def create_customer(customer_data: dict):
    """
    Create a new customer
    """
    try:
        new_customer = await create_customer_controller(customer_data)
        return new_customer
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/customers/{customer_id}", response_model=dict)
async def read_customer(customer_id: str):
    """
    Get a customer by ID
    """
    try:
        customer = await read_customer_controller(customer_id)
        if customer:
            return customer
        else:
            raise HTTPException(status_code=404, detail="Customer not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/customers/{customer_id}", response_model=dict)
async def update_customer(customer_id: str, customer_data: dict):
    """
    Update a customer by ID
    """
    try:
        updated_customer = await update_customer_controller(customer_id, customer_data)
        if updated_customer:
            return updated_customer
        else:
            raise HTTPException(status_code=404, detail="Customer not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/customers/{customer_id}", status_code=204)
async def delete_customer(customer_id: str):
    """
    Delete a customer by ID
    """
    try:
        deletion_success = await delete_customer_controller(customer_id)
        if deletion_success:
            return {"message": "Customer deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="Customer not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/customers/", response_model=list)
async def list_customers():
    """
    List all customers
    """
    try:
        customers = await list_customers_controller()
        return customers
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
