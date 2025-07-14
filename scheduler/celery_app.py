from celery import Celery
from celery.schedules import crontab
from common.config import settings

# Define the queues
class TaskQueues:
    IMPORT = "import_queue"
    SALE = "sale_queue"
    CANCELLATION = "cancellation_queue"

app = Celery(
    "scheduler",
    broker=f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/0",
    backend=f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/0",
    include=["scheduler.tasks"]
)

app.conf.beat_schedule = {
    'scan-for-new-data-every-minute': {
        'task': 'scheduler.tasks.scan_and_dispatch',
        'schedule': crontab(),  # Runs every minute
    },
}
app.conf.timezone = 'UTC'