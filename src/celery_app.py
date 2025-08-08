# src/celery_app.py
import os
from celery import Celery
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

redis_host = os.getenv("REDIS_HOST", "localhost")
redis_port = os.getenv("REDIS_PORT", "6379")
redis_db = os.getenv("REDIS_DB", "0")
broker_url = f"redis://{redis_host}:{redis_port}/{redis_db}"
result_backend = os.getenv("MONGO_URI")

celery_app = Celery(
    "worker",
    broker=broker_url,
    backend=result_backend,
    include=["src.tasks.process_records"]
)

celery_app.conf.update(
    result_extended=True,
    mongodb_backend_settings={
        "database": os.getenv("MONGO_DATABASE_NAME", "celery_logs"),
        "taskmeta_collection": "task_results",
    }
)

mongo_client = MongoClient(os.getenv("MONGO_URI"))
db = mongo_client[os.getenv("MONGO_DATABASE_NAME")]

# Beat schedule: Polling hóa đơn bán hàng mỗi phút
from celery.schedules import crontab
celery_app.conf.beat_schedule = {
    'poll-sales-invoices-every-minute': {
        'task': 'poll_new_sales_invoices',
        'schedule': crontab(),
    },
}