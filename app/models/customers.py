from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

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

