from sqlalchemy.future import select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from ...models.customers import Customer

async def create_customer_in_db(db: AsyncSession, customer_data: dict) -> Customer:
    """
    Create a new customer in the database.
    """
    new_customer = Customer(**customer_data)
    db.add(new_customer)
    await db.commit()
    await db.refresh(new_customer)
    return new_customer

async def get_customer_from_db(db: AsyncSession, customer_id: int) -> Customer:
    """
    Retrieve a customer by ID from the database.
    """
    async with db.begin():
        query = select(Customer).filter(Customer.id == customer_id)
        result = await db.execute(query)
        customer = result.scalars().first()
        if customer:
            return customer
        else:
            raise NoResultFound("No customer found with the given ID.")

async def update_customer_in_db(db: AsyncSession, customer_id: int, update_data: dict) -> Customer:
    """
    Update a customer in the database.
    """
    async with db.begin():
        query = select(Customer).filter(Customer.id == customer_id)
        result = await db.execute(query)
        customer = result.scalars().first()
        if customer:
            for key, value in update_data.items():
                setattr(customer, key, value)
            await db.commit()
            await db.refresh(customer)
            return customer
        else:
            raise NoResultFound("No customer found with the given ID.")

async def delete_customer_from_db(db: AsyncSession, customer_id: int) -> None:
    """
    Delete a customer from the database.
    """
    async with db.begin():
        query = select(Customer).filter(Customer.id == customer_id)
        result = await db.execute(query)
        customer = result.scalars().first()
        if customer:
            await db.delete(customer)
            await db.commit()
            return "success"
        else:
            raise NoResultFound("No customer found with the given ID.")

async def list_all_customers_from_db(db: AsyncSession) -> list:
    """
    List all customers from the database.
    """
    query = select(Customer)
    result = await db.execute(query)
    customers = result.scalars().all()
    return customers