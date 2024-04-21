from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DB_HOST: str
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str
    STRIPE_API_KEY: str
    STRIPE_WEBHOOK_KEY: str
    STRIPE_SECRET_KEY: str

    class Config:
        env_file = ".env"

settings = Settings()
