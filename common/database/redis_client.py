import redis
from common.config import settings

class RedisClient:
    def __init__(self):
        self.client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=0,
            decode_responses=True
        )

    def get_token(self, shop_id: str) -> str | None:
        """Retrieves a token for a given shop_id."""
        return self.client.get(f"token:{shop_id}")

    def set_token(self, shop_id: str, token: str, expiry_seconds: int = 3600):
        """Caches a token for a given shop_id with an expiry."""
        self.client.set(f"token:{shop_id}", token, ex=expiry_seconds)

redis_client = RedisClient()