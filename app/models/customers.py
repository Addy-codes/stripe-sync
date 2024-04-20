from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class Customer(Base):
    __tablename__ = 'customers'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)

    # Relationship to link to IDMap
    services = relationship("IDMap", back_populates="customer")

class IDMap(Base):
    __tablename__ = 'id_map'

    local_id = Column(Integer, ForeignKey('customers.id'), primary_key=True)
    service_id = Column(String, primary_key=True)
    service_name = Column(String, primary_key=True)

    # Establish relationship to the Customer model
    customer = relationship("Customer", back_populates="services")
