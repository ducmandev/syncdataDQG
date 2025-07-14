### **Phase 2: Scheduler Service**
### **Giai đoạn 2: Dịch vụ Lập lịch**

**Objective:** To build the standalone `scheduler` service. This service's sole responsibility is to run Celery Beat, periodically scan the MSSQL database for new records, and dispatch processing tasks to the correct worker queues.
**Mục tiêu:** Xây dựng dịch vụ `scheduler` độc lập. Trách nhiệm duy nhất của dịch vụ này là chạy Celery Beat, quét định kỳ cơ sở dữ liệu MSSQL để tìm các bản ghi mới và gửi các tác vụ xử lý đến đúng hàng đợi của worker.

---

#### **Task 2.1: Implement MSSQL and MongoDB Clients in Common Library**

*   **Description:** Before the scheduler can query data, we must first implement the database clients in the shared library.
*   **Files to Create:** `common/database/mssql_client.py`, `common/database/mongo_client.py`
*   **Code (`common/database/mssql_client.py`):**
    ```python
    import pyodbc
    from common.config import settings

    class MSSQLClient:
        def __init__(self):
            self.conn_str = (
                f"DRIVER={settings.MSSQL_DRIVER};"
                f"SERVER={settings.MSSQL_SERVER};"
                f"DATABASE={settings.MSSQL_DATABASE};"
                f"UID={settings.MSSQL_USER};"
                f"PWD={settings.MSSQL_PASSWORD};"
            )
            self.connection = pyodbc.connect(self.conn_str)

        def fetch_pending_sales(self):
            cursor = self.connection.cursor()
            cursor.execute("SELECT local_invoice_id, shop_pharmacy_code FROM SalesInvoices WHERE status = 'PENDING_SYNC'")
            return cursor.fetchall()

        # ... (Similar methods for fetch_pending_imports and fetch_pending_cancellations) ...

    mssql_client = MSSQLClient()
    ```
*   **Code (`common/database/mongo_client.py`):**
    ```python
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

    mongo_client = MongoClient()
    ```
*   **Output:** Functional database clients ready for use by the scheduler.

---

#### **Task 2.2: Create the Scheduler's Celery Application**

*   **Description:** Define the Celery application for the `scheduler`. This app needs to know the names of the worker queues for routing and must be configured to run Celery Beat.
*   **File to Create:** `scheduler/celery_app.py`
*   **Code (`scheduler/celery_app.py`):**
    ```python
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
    ```
*   **Output:** A configured Celery app ready to run the orchestration task on a schedule.

---

#### **Task 2.3: Implement the Orchestration Task**

*   **Description:** Create the core task that queries the database and dispatches jobs to the worker queues.
*   **File to Create:** `scheduler/tasks.py`
*   **Code (`scheduler/tasks.py`):**
    ```python
    from scheduler.celery_app import app, TaskQueues
    from common.database.mssql_client import mssql_client
    from common.database.mongo_client import mongo_client

    @app.task
    def scan_and_dispatch():
        # 1. Process Sales
        pending_sales = mssql_client.fetch_pending_sales()
        for sale in pending_sales:
            local_invoice_id, shop_id = sale
            task = app.send_task(
                'sale.process_sale', # Name of the task in the 'saler' worker
                args=[local_invoice_id, shop_id],
                queue=TaskQueues.SALE
            )
            mongo_client.log_task_dispatch(task.id, local_invoice_id, TaskQueues.SALE)

        # 2. Process Imports (similar logic)
        # ...

        # 3. Process Cancellations (similar logic)
        # ...
    ```
*   **Input:** Database clients from the `common` library.
*   **Output:** A Celery task that populates the worker queues.