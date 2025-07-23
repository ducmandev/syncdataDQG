from celery import Celery
from config.celery_config import settings

celery_app = Celery(
    'hermes_worker',
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=['src.workers.tasks']
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='Asia/Saigon',
    enable_utc=True,
)

if __name__ == '__main__':
    celery_app.start()