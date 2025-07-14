### **Phase 3: "Sale" Worker Service**
### **Giai đoạn 3: Dịch vụ Worker "Bán hàng"**

**Objective:** To build the first complete, end-to-end data processing pipeline: the `saler` service. This service will listen for tasks on the `sale_queue`, process sales invoice data, and send it to the national API. This phase will serve as the template for the other worker services.
**Mục tiêu:** Xây dựng luồng xử lý dữ liệu hoàn chỉnh đầu tiên từ đầu đến cuối: dịch vụ `saler`. Dịch vụ này sẽ lắng nghe các tác vụ trên `sale_queue`, xử lý dữ liệu hóa đơn bán hàng và gửi nó đến API quốc gia. Giai đoạn này sẽ đóng vai trò là khuôn mẫu cho các dịch vụ worker khác.

---

#### **Task 3.1: Implement the API Client in Common Library**

*   **Description:** Create a robust API client in the shared library that handles authentication (login, token caching) and resilient API calls with automatic retries.
*   **File to Create:** `common/services/api_client.py`
*   **Code (`common/services/api_client.py`):**
    ```python
    import httpx
    from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type
    from common.config import settings
    from common.database.redis_client import redis_client
    from common.models.pydantic_models import LoginRequest, LoginResponse, SalesInvoice

    class ApiClient:
        def __init__(self):
            self.base_url = settings.API_BASE_URL
            self.client = httpx.Client()

        @retry(stop=stop_after_attempt(5), wait=wait_fixed(2))
        def _login(self, shop_id: str) -> str:
            """Logs in to get a new token. Retries on failure."""
            # In a real app, you'd fetch shop-specific credentials
            login_data = LoginRequest(usr=settings.API_USERNAME, pwd=settings.API_PASSWORD)
            response = self.client.post(f"{self.base_url}/api/tai_khoan/dang_nhap", json=login_data.model_dump())
            response.raise_for_status()
            token_data = LoginResponse(**response.json())
            redis_client.set_token(shop_id, token_data.token)
            return token_data.token

        def _get_auth_token(self, shop_id: str) -> str:
            """Gets token from cache or triggers a new login."""
            token = redis_client.get_token(shop_id)
            if not token:
                token = self._login(shop_id)
            return token

        @retry(stop=stop_after_attempt(3), wait=wait_fixed(3), retry=retry_if_exception_type(httpx.RequestError))
        def send_sales_invoice(self, shop_id: str, invoice_data: SalesInvoice):
            """Sends sales invoice data with authorization and retry logic."""
            token = self._get_auth_token(shop_id)
            headers = {"Authorization": f"Bearer {token}"}
            
            try:
                response = self.client.post(
                    f"{self.base_url}/api/lien_thong/hoa_don",
                    json=invoice_data.model_dump(),
                    headers=headers
                )
                # If token expired, get a new one and retry once.
                if response.status_code == 401:
                    token = self._login(shop_id) # Force new login
                    headers = {"Authorization": f"Bearer {token}"}
                    response = self.client.post(f"{self.base_url}/api/lien_thong/hoa_don", json=invoice_data.model_dump(), headers=headers)
                
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                # Log failure permanently if it's not a token issue after retries
                print(f"Failed to send invoice {invoice_data.ma_hoa_don}: {e}")
                raise

    api_client = ApiClient()
    ```
*   **Output:** A powerful `api_client` that can be used by any worker.

---

#### **Task 3.2: Create the "Saler" Celery Application**

*   **Description:** Define the Celery application for the `saler` worker, ensuring it listens only to the `sale_queue`.
*   **File to Create:** `saler/celery_app.py`
*   **Code (`saler/celery_app.py`):**
    ```python
    from celery import Celery
    from common.config import settings

    app = Celery(
        "saler",
        broker=f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/0",
        backend=f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/0",
        include=["saler.tasks"]
    )

    app.conf.task_default_queue = 'sale_queue'
    ```
*   **Output:** A Celery app for the sales worker.

---

#### **Task 3.3: Implement the "Sale" Processing Task**

*   **Description:** Create the core task that processes a single sales invoice. This involves fetching data, transforming it, and calling the API client.
*   **File to Create:** `saler/tasks.py`
*   **Code (`saler/tasks.py`):**
    ```python
    from saler.celery_app import app
    from common.services.api_client import api_client
    from common.database.mssql_client import mssql_client # Requires new method
    from common.models.pydantic_models import SalesInvoice, SalesInvoiceDetail

    @app.task(name='sale.process_sale')
    def process_sale(local_invoice_id: str, shop_id: str):
        """
        Task to process a single sales invoice.
        """
        try:
            # 1. Fetch full data from MSSQL
            # Note: This requires adding a 'fetch_sale_by_id' method to mssql_client.py
            invoice_header, invoice_details = mssql_client.fetch_sale_by_id(local_invoice_id)

            # 2. Transform data using Pydantic models
            detail_models = [SalesInvoiceDetail(**detail) for detail in invoice_details]
            invoice_model = SalesInvoice(
                ma_hoa_don=invoice_header['local_invoice_id'],
                ma_co_so=invoice_header['pharmacy_code'],
                ngay_ban=invoice_header['sale_date'].strftime('%Y%m%d'),
                hoa_don_chi_tiet=detail_models,
                # ... map other fields ...
            )

            # 3. Send data via API client
            api_response = api_client.send_sales_invoice(shop_id, invoice_model)

            # 4. On success, update MSSQL status
            national_id = api_response.get('ma_hoa_don')
            mssql_client.update_sale_status(local_invoice_id, 'SYNC_SUCCESS', national_id)
            # (Also log to MongoDB 'task_logs')

        except Exception as e:
            # On final failure, update MSSQL status and log to MongoDB 'sync_failures'
            mssql_client.update_sale_status(local_invoice_id, 'SYNC_FAILED')
            # (Log detailed error to MongoDB 'sync_failures')
            print(f"Error processing sale {local_invoice_id}: {e}")

    ```
*   **Input:** `local_invoice_id`, `shop_id`.
*   **Output:** A processed invoice, with status updated in MSSQL and logs in MongoDB.