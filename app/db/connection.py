import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from ..core.config import settings
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = f"postgresql+asyncpg://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}/{settings.DB_NAME}"
engine = create_async_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

def create_database():
    """Create PostgreSQL database if it does not exist."""
    conn = psycopg2.connect(dbname='postgres', user=settings.DB_USER, password=settings.DB_PASSWORD,
                            host=settings.DB_HOST)
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = %s", (settings.DB_NAME,))
    exists = cursor.fetchone()
    if not exists:
        cursor.execute(f"CREATE DATABASE {settings.DB_NAME}")
        print(f"Database {settings.DB_NAME} created.")
    else:
        print(f"Database {settings.DB_NAME} already exists.")
    
    cursor.close()
    conn.close()

async def get_db():
    """
    Dependency function for FastAPI to provide a database session.

    This function generates an asynchronous session to the database, which can be used in FastAPI route handlers.
    It's designed to yield a session that is used throughout the context of a single request, and ensures that
    the session is closed after the request is handled, regardless of whether the request was successful or
    raised an exception. This pattern helps prevent database connection leaks.

    Yields:
        AsyncSession: A session object that can be used to execute database operations.

    Note:
        This is a generator function, which is a special type of iterator that yields one item at a time
        to the context of the FastAPI endpoint using it. After the endpoint is done, execution continues
        in this generator to close the session, ensuring cleanup is performed.
    """
    db: AsyncSession = SessionLocal()
    try:
        yield db
    finally:
        await db.close()