### **Phase 4: "Import" & "Cancellation" Worker Services**
### **Giai đoạn 4: Dịch vụ Worker "Nhập" & "Hủy"**

**Objective:** To build the remaining two worker services (`importer` and `canceller`) by replicating the pattern established in Phase 3. This involves creating their respective Celery applications and processing tasks, and extending the shared `common` library to support their specific data types.
**Mục tiêu:** Xây dựng hai dịch vụ worker còn lại (`importer` và `canceller`) bằng cách sao chép mẫu đã được thiết lập trong Giai đoạn 3. Điều này bao gồm việc tạo các ứng dụng Celery và tác vụ xử lý tương ứng, đồng thời mở rộng thư viện `common` được chia sẻ để hỗ trợ các loại dữ liệu cụ thể của chúng.

---

#### **Task 4.1: Extend Common Library for New Data Types**

*   **Description:** Add new methods to the shared database and API clients to handle "import" and "cancellation" data.
*   **Files to Modify:**
    *   `common/database/mssql_client.py`
    *   `common/services/api_client.py`
    *   `common/models/pydantic_models.py`
*   **Code Changes:**
    *   **In `mssql_client.py`:** Add `fetch_import_by_id()`, `update_import_status()`, `fetch_cancellation_by_id()`, and `update_cancellation_status()` methods.
    *   **In `api_client.py`:** Add `send_purchase_receipt()` and `send_goods_issue()` methods, following the pattern of `send_sales_invoice()`.
    *   **In `pydantic_models.py`:** Add Pydantic models for `PurchaseReceipt` and `GoodsIssueSlip` based on `ListAPI.md`.
*   **Output:** The `common` library is now feature-complete for all data pipelines.

---

#### **Task 4.2: Implement the "Importer" Worker Service**

*   **Description:** Create the full application for processing purchase receipts.
*   **Files to Create:** `importer/celery_app.py`, `importer/tasks.py`
*   **Code (`importer/celery_app.py`):**
    ```python
    from celery import Celery
    from common.config import settings

    app = Celery(
        "importer",
        broker=f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/0",
        backend=f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/0",
        include=["importer.tasks"]
    )

    app.conf.task_default_queue = 'import_queue'
    ```
*   **Code (`importer/tasks.py`):**
    ```python
    from importer.celery_app import app
    from common.services.api_client import api_client
    from common.database.mssql_client import mssql_client
    from common.models.pydantic_models import PurchaseReceipt # Assumes this is created

    @app.task(name='import.process_import')
    def process_import(local_receipt_id: str, shop_id: str):
        """
        Task to process a single purchase receipt.
        """
        try:
            # 1. Fetch data from MSSQL
            header, details = mssql_client.fetch_import_by_id(local_receipt_id)
            
            # 2. Transform data to Pydantic model
            # ... (transformation logic similar to Phase 3) ...
            import_model = PurchaseReceipt(...)

            # 3. Send data via API client
            api_response = api_client.send_purchase_receipt(shop_id, import_model)

            # 4. Update status in MSSQL
            national_id = api_response # API returns string directly
            mssql_client.update_import_status(local_receipt_id, 'SYNC_SUCCESS', national_id)
        except Exception as e:
            mssql_client.update_import_status(local_receipt_id, 'SYNC_FAILED')
            # Log to MongoDB 'sync_failures'
            print(f"Error processing import {local_receipt_id}: {e}")
    ```
*   **Output:** A fully functional `importer` service.

---

#### **Task 4.3: Implement the "Canceller" Worker Service**

*   **Description:** Create the application for processing goods issue slips (cancellations).
*   **Files to Create:** `canceller/celery_app.py`, `canceller/tasks.py`
*   **Code (`canceller/celery_app.py`):**
    ```python
    from celery import Celery
    from common.config import settings

    app = Celery(
        "canceller",
        broker=f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/0",
        backend=f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/0",
        include=["canceller.tasks"]
    )

    app.conf.task_default_queue = 'cancellation_queue'
    ```
*   **Code (`canceller/tasks.py`):**
    ```python
    from canceller.celery_app import app
    from common.services.api_client import api_client
    from common.database.mssql_client import mssql_client
    from common.models.pydantic_models import GoodsIssueSlip # Assumes this is created

    @app.task(name='cancellation.process_cancellation')
    def process_cancellation(local_slip_id: str, shop_id: str):
        """
        Task to process a single goods issue slip.
        """
        try:
            # 1. Fetch data from MSSQL
            header, details = mssql_client.fetch_cancellation_by_id(local_slip_id)
            
            # 2. Transform data to Pydantic model
            # ... (transformation logic similar to Phase 3) ...
            cancellation_model = GoodsIssueSlip(...)

            # 3. Send data via API client
            api_response = api_client.send_goods_issue(shop_id, cancellation_model)

            # 4. Update status in MSSQL
            national_id = api_response # API returns string directly
            mssql_client.update_cancellation_status(local_slip_id, 'SYNC_SUCCESS', national_id)
        except Exception as e:
            mssql_client.update_cancellation_status(local_slip_id, 'SYNC_FAILED')
            # Log to MongoDB 'sync_failures'
            print(f"Error processing cancellation {local_slip_id}: {e}")
    ```
*   **Output:** A fully functional `canceller` service.