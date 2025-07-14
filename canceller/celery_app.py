from celery import Celery
from common.config import settings

app = Celery(
    "canceller",
    broker=f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/0",
    backend=f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/0",
    include=["canceller.tasks"]
)

app.conf.task_default_queue = 'cancellation_queue'