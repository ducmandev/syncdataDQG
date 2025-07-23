# Kế hoạch Phát triển Chi tiết: Giai đoạn 1 - Nền tảng Dự án

**Mục tiêu:** Xây dựng bộ khung hoàn chỉnh cho ứng dụng. Kết quả của giai đoạn này là một bộ khung dự án có thể chạy được, được đóng gói trong container, sẵn sàng cho việc triển khai logic nghiệp vụ ở Giai đoạn 2.

---

### **Task 1.1: Tạo Cấu trúc Thư mục Dự án**

*   **Mục tiêu:** Thiết lập cấu trúc thư mục và tệp tin chuẩn hóa cho toàn bộ dự án.
*   **Người thực hiện:** 1 Lập trình viên
*   **Hướng dẫn:**
    1.  Từ thư mục gốc của dự án (`c:\Users\crayn\Project\syncdataDQG`), thực thi các lệnh sau trong terminal để tạo các thư mục và tệp tin rỗng cần thiết. Cấu trúc này là bắt buộc.
        ```bash
        mkdir -p app/core app/db app/models app/tasks app/clients
        mkdir tests
        touch app/__init__.py app/main.py
        touch app/core/__init__.py app/core/config.py
        touch app/db/__init__.py app/db/mssql.py app/db/mongodb.py
        touch app/models/__init__.py
        touch app/tasks/__init__.py
        touch app/clients/__init__.py
        touch tests/__init__.py
        touch .gitignore Dockerfile docker-compose.yml requirements.txt
        ```

---

### **Task 1.2: Triển khai Module Cấu hình (Config)**

*   **Mục tiêu:** Tạo một module tập trung để tải và xác thực tất cả các biến môi trường. Ứng dụng sẽ không khởi động nếu thiếu bất kỳ cấu hình bắt buộc nào.
*   **Người thực hiện:** 1 Lập trình viên
*   **Hướng dẫn:**
    1.  Mở tệp `app/core/config.py`.
    2.  Sao chép và dán toàn bộ khối mã dưới đây vào tệp. Mã này sử dụng `pydantic-settings` để tự động tải các biến từ tệp `.env`.
        ```python
        from pydantic_settings import BaseSettings
        from pydantic import Field
        import os

        # Đảm bảo tìm thấy tệp .env từ thư mục gốc của dự án
        env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env')

        class Settings(BaseSettings):
            # Cấu hình Redis
            REDIS_HOST: str
            REDIS_PORT: int

            # Cấu hình MongoDB
            MONGO_URI: str
            MONGO_DB_NAME: str

            # Cấu hình Microsoft SQL Server
            MSSQL_SERVER: str
            MSSQL_DATABASE: str
            MSSQL_USER: str
            MSSQL_PASSWORD: str
            MSSQL_DRIVER: str = Field(default="{ODBC Driver 17 for SQL Server}")

            # Cấu hình API Đối tác
            API_BASE_URL: str
            API_USERNAME: str
            API_PASSWORD: str

            class Config:
                env_file = env_path
                env_file_encoding = 'utf-8'
                extra = 'ignore'

        # Tạo một đối tượng settings duy nhất để các module khác import
        settings = Settings()
        ```

---

### **Task 1.3: Khởi tạo Ứng dụng Celery**

*   **Mục tiêu:** Tạo và cấu hình đối tượng ứng dụng Celery chính, kết nối nó với Redis broker.
*   **Người thực hiện:** 1 Lập trình viên
*   **Hướng dẫn:**
    1.  Mở tệp `app/main.py`.
    2.  Sao chép và dán toàn bộ khối mã dưới đây vào tệp. Mã này khởi tạo Celery và chỉ định nơi tìm các module chứa task.
        ```python
        from celery import Celery
        from app.core.config import settings

        # Xây dựng URL Redis từ settings cho broker và backend
        redis_url = f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/0"

        # Khởi tạo ứng dụng Celery
        celery_app = Celery(
            "project_hermes",
            broker=redis_url,
            backend=redis_url,
            include=[
                # Chúng ta sẽ tạo các tệp này ở các task sau
                "app.tasks.polling_service",
                "app.tasks.phieu_nhap_worker",
                "app.tasks.phieu_xuat_worker",
                "app.tasks.hoa_don_worker",
            ],
        )

        # Cấu hình Celery tùy chọn
        celery_app.conf.update(
            task_track_started=True,
        )
        ```

---

### **Task 1.4: Hoàn thiện các Thư viện Phụ thuộc (Dependencies)**

*   **Mục tiêu:** Liệt kê tất cả các thư viện Python cần thiết vào tệp `requirements.txt`.
*   **Người thực hiện:** 1 Lập trình viên
*   **Hướng dẫn:**
    1.  Mở tệp `requirements.txt`.
    2.  Đảm bảo tệp chứa các thư viện sau, mỗi thư viện trên một dòng riêng.
        ```
        celery
        redis
        pydantic
        pydantic-settings
        pyodbc
        pymongo
        httpx
        ```

---

### **Task 1.5: Tạo Dockerfile cho Ứng dụng**

*   **Mục tiêu:** Tạo một `Dockerfile` để xây dựng một image di động cho ứng dụng, bao gồm tất cả các thư viện hệ thống cần thiết để kết nối cơ sở dữ liệu.
*   **Người thực hiện:** 1 Lập trình viên
*   **Hướng dẫn:**
    1.  Mở tệp `Dockerfile`.
    2.  Sao chép và dán toàn bộ nội dung dưới đây vào tệp. `Dockerfile` này cài đặt driver Microsoft ODBC mà `pyodbc` yêu cầu để kết nối đến SQL Server.
        ```dockerfile
        # Sử dụng image Python chính thức, phiên bản nhẹ.
        FROM python:3.9-slim

        # Thiết lập thư mục làm việc trong container.
        WORKDIR /app

        # Cài đặt các thư viện hệ thống cần thiết cho pyodbc (MSSQL)
        RUN apt-get update && apt-get install -y --no-install-recommends \
            curl \
            gnupg \
            unixodbc-dev \
            && apt-get clean && rm -rf /var/lib/apt/lists/*

        # Thêm kho chứa chính thức của Microsoft cho ODBC driver
        RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
        RUN curl https://packages.microsoft.com/config/debian/11/prod.list > /etc/apt/sources.list.d/mssql-release.list

        # Cài đặt ODBC driver cho SQL Server
        RUN apt-get update && ACCEPT_EULA=Y apt-get install -y msodbcsql17

        # Sao chép tệp requirements và cài đặt các thư viện Python.
        COPY requirements.txt .
        RUN pip install --no-cache-dir -r requirements.txt

        # Sao chép mã nguồn ứng dụng vào container.
        COPY ./app /app
        ```

---

### **Task 1.6: Tạo Cấu hình Docker Compose**

*   **Mục tiêu:** Định nghĩa tất cả các dịch vụ của ứng dụng (`scheduler`, `workers`) trong một tệp `docker-compose.yml` để dễ dàng phát triển và điều phối cục bộ.
*   **Người thực hiện:** 1 Lập trình viên
*   **Hướng dẫn:**
    1.  Mở tệp `docker-compose.yml`.
    2.  Sao chép và dán toàn bộ nội dung dưới đây vào tệp.
        ```yaml
        version: '3.8'

        services:
          scheduler:
            build: .
            container_name: hermes_scheduler
            command: ["celery", "-A", "app.main.celery_app", "beat", "--loglevel=info", "-s", "/tmp/celerybeat-schedule"]
            volumes:
              - ./app:/app
            env_file:
              - .env

          phieu_nhap_worker:
            build: .
            container_name: hermes_phieu_nhap_worker
            command: ["celery", "-A", "app.main.celery_app", "worker", "-Q", "phieu_nhap_queue", "--loglevel=info", "-c", "2"]
            volumes:
              - ./app:/app
            env_file:
              - .env
            depends_on:
              - scheduler

          phieu_xuat_worker:
            build: .
            container_name: hermes_phieu_xuat_worker
            command: ["celery", "-A", "app.main.celery_app", "worker", "-Q", "phieu_xuat_queue", "--loglevel=info", "-c", "2"]
            volumes:
              - ./app:/app
            env_file:
              - .env
            depends_on:
              - scheduler

          hoa_don_worker:
            build: .
            container_name: hermes_hoa_don_worker
            command: ["celery", "-A", "app.main.celery_app", "worker", "-Q", "hoa_don_queue", "--loglevel=info", "-c", "2"]
            volumes:
              - ./app:/app
            env_file:
              - .env
            depends_on:
              - scheduler