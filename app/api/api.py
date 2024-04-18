from fastapi import APIRouter

from app.api.routers import (
    customers,
)

api_router = APIRouter()

api_router.include_router(customers.router, prefix="/api", tags=["customer"])
