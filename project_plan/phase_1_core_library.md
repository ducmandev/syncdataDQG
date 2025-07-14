### **Phase 1: Core Library & Project Setup**
### **Giai đoạn 1: Thư viện Lõi & Cài đặt Dự án**

**Objective:** To create the foundational `common` library that will be shared by all other services. This phase ensures all core components for database interaction, API communication, and configuration are built first.
**Mục tiêu:** Tạo thư viện `common` nền tảng sẽ được chia sẻ bởi tất cả các dịch vụ khác. Giai đoạn này đảm bảo tất cả các thành phần cốt lõi để tương tác cơ sở dữ liệu, giao tiếp API và cấu hình được xây dựng trước tiên.

---

#### **Task 1.1: Create Project Structure and `requirements.txt`**

*   **Description:** Create the main directories and the central `requirements.txt` file.
*   **Action:**
    1.  Create directories: `common/`, `importer/`, `saler/`, `canceller/`, `scheduler/`.
    2.  Create a file named `requirements.txt` in the root directory.
*   **Code (`requirements.txt`):**
    ```
    # Celery and Broker
    celery==5.3.6
    redis==5.0.4

    # Database Clients
    pymongo==4.7.2
    pyodbc==5.1.0  # For MSSQL

    # API Communication
    httpx==0.27.0
    tenacity==8.3.0 # For retries

    # Configuration
    pydantic==2.7.4
    pydantic-settings==2.3.3

    # Utilities
    python-dotenv==1.0.1
    ```
*   **Output:** A structured directory tree and a `requirements.txt` file.

---

#### **Task 1.2: Implement Configuration Management**

*   **Description:** Create a centralized configuration system using Pydantic to manage all settings from environment variables.
*   **File to Create:** `common/config.py`
*   **Code (`common/config.py`):**
    ```python
    from pydantic_settings import BaseSettings, SettingsConfigDict

    class Settings(BaseSettings):
        # Redis Configuration
        REDIS_HOST: str = "localhost"
        REDIS_PORT: int = 6379

        # MongoDB Configuration
        MONGO_URI: str = "mongodb://localhost:27017/"
        MONGO_DB_NAME: str = "sync_data_logs"

        # MSSQL Configuration
        MSSQL_SERVER: str
        MSSQL_DATABASE: str
        MSSQL_USER: str
        MSSQL_PASSWORD: str
        MSSQL_DRIVER: str = "{ODBC Driver 17 for SQL Server}"

        # National API Configuration
        API_BASE_URL: str
        API_USERNAME: str
        API_PASSWORD: str

        model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    settings = Settings()
    ```
*   **Input:** Requires a `.env` file in the root directory with the specified variables.
*   **Output:** A `settings` object that can be imported across the project.

---

#### **Task 1.3: Implement Redis Client for Caching**

*   **Description:** Create a client to manage caching of authentication tokens in Redis.
*   **File to Create:** `common/database/redis_client.py`
*   **Code (`common/database/redis_client.py`):**
    ```python
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
    ```
*   **Input:** `settings` object from `common.config`.
*   **Output:** A `redis_client` instance for token management.

---

#### **Task 1.4: Implement Pydantic Models for API Payloads**

*   **Description:** Define Pydantic models for all API request and response bodies based on `ListAPI.md`. This ensures data validation and type safety.
*   **File to Create:** `common/models/pydantic_models.py`
*   **Code (`common/models/pydantic_models.py`):**
    ```python
    from pydantic import BaseModel, Field
    from typing import List

    # 1. Login Models
    class LoginRequest(BaseModel):
        usr: str
        pwd: str

    class LoginResponse(BaseModel):
        token: str
        token_type: str

    # 2. Sales Invoice Models
    class SalesInvoiceDetail(BaseModel):
        ma_thuoc: str
        ten_thuoc: str
        so_lo: str
        han_dung: str # Format: yyyyMMdd
        don_vi_tinh: str
        ham_luong: str
        so_luong: float
        don_gia: float
        thanh_tien: float
        ty_le_quy_doi: float
        lieu_dung: str
        so_dang_ky: str
        ngay_san_xuat: str | None = None
        duong_dung: str | None = None

    class SalesInvoice(BaseModel):
        ma_hoa_don: str
        ma_co_so: str
        ngay_ban: str # Format: yyyyMMdd
        hoa_don_chi_tiet: List[SalesInvoiceDetail]
        ma_don_thuoc_quoc_gia: str | None = None
        ho_ten_nguoi_ban: str | None = None
        ho_ten_khach_hang: str | None = None

    # (Models for PurchaseReceipt and GoodsIssueSlip would follow the same pattern)
    ```
*   **Input:** The schemas defined in `ListAPI.md`.
*   **Output:** Pydantic classes for API data structures.