from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
from pydantic import BaseModel, Field

Base = declarative_base()

class Customer(Base):
    __tablename__ = 'customers'

    id = Column(String, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)

    # Relationship to link to IDMap
    services = relationship("IDMap", back_populates="customer")


class IDMap(Base):
    __tablename__ = 'id_map'

    local_id = Column(String, ForeignKey('customers.id', ondelete='CASCADE'), primary_key=True)
    # Create a separate service ID in case there are services that do not allow manual creation of ids
    # service_id = Column(String, primary_key=True)
    service_name = Column(String, primary_key=True)

    customer = relationship("Customer", back_populates="services")


# Pydantic model for customer creation input
class CustomerCreate(BaseModel):
    id: str = Field(..., example="cust123", description="The unique identifier of the customer")
    name: str = Field(..., example="John Doe", description="The full name of the customer")
    email: str = Field(..., example="john.doe@example.com", description="The email address of the customer")

# Pydantic model for output serialization
class CustomerDisplay(BaseModel):
    id: str
    name: str
    email: str

    class Config:
        orm_mode = True