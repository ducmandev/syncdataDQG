from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PARTNER_API_URL: str = "https://partner-api.example.com"
    PARTNER_API_KEY: str = "your-api-key"
    API_TIMEOUT: int = 30

settings = Settings()