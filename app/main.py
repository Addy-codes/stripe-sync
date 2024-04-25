import uvicorn
from fastapi import FastAPI
from app.api.api import api_router
from .db.connection import create_database

app = FastAPI(title="Zenskar", description="Two-Way Integrations")


app.include_router(api_router)

@app.on_event("startup")
async def startup_event():
    # Ensure the database is created at startup
    create_database()
    # Include other startup tasks like running Alembic migrations
    # os.system("alembic upgrade head")



@app.get("/")
async def read_root():
    return {"Hello": "W0rld"}


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
