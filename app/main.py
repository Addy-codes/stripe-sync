import uvicorn
from fastapi import FastAPI
from app.api.api import api_router

app = FastAPI(title="Zenskar", description="Two-Way Integrations")


app.include_router(api_router)


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
