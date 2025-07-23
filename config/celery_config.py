from pydantic_settings import BaseSettings

class CelerySettings(BaseSettings):
    REDIS_URL: str = "redis://redis:6379/0"
    WORKER_CONCURRENCY: int = 4

settings = CelerySettings()