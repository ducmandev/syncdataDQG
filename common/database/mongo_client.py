from pymongo import MongoClient
from common.config import settings
import datetime

class MongoClient:
    def __init__(self):
        self.client = MongoClient(settings.MONGO_URI)
        self.db = self.client[settings.MONGO_DB_NAME]

    def log_task_dispatch(self, celery_task_id: str, business_id: str, queue: str):
        """Logs when a task is first dispatched."""
        self.db.task_logs.insert_one({
            "celery_task_id": celery_task_id,
            "business_id": business_id, # e.g., local_invoice_id
            "queue": queue,
            "status": "PENDING",
            "created_at": datetime.datetime.utcnow()
        })

    def log_sync_failure(self, business_id: str, payload: dict, error: str, queue: str):
        """Logs a task that failed permanently."""
        self.db.sync_failures.insert_one({
            "business_id": business_id,
            "queue": queue,
            "payload": payload,
            "error_message": error,
            "failed_at": datetime.datetime.utcnow()
        })

    def update_task_log_status(self, celery_task_id: str, status: str):
        """Updates the final status of a task in the log."""
        self.db.task_logs.update_one(
            {"celery_task_id": celery_task_id},
            {"$set": {"status": status, "completed_at": datetime.datetime.utcnow()}}
        )

mongo_client = MongoClient()