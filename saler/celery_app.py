from celery import Celery
from common.config import settings

app = Celery(
    "saler",
    broker=f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/0",
    backend=f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/0",
    include=["saler.tasks"]
)

app.conf.task_default_queue = 'sale_queue'