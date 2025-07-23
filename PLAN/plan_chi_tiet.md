### **LỘ TRÌNH PHÁT TRIỂN CHI TIẾT - PROJECT HERMES (Phiên bản tinh chỉnh)**

**Giả định:**
*   Hệ thống đã có sẵn Redis và MongoDB đang chạy và có thể truy cập được từ môi trường phát triển.
*   Thông tin kết nối (host, port, credentials) được cung cấp qua file `.env`.

---

### **GIAI ĐOẠN 1: THIẾT LẬP NỀN TẢNG DỰ ÁN (Foundation Setup)**

*Mục tiêu: Tạo bộ khung vững chắc cho dự án, đảm bảo các dev có thể bắt đầu code ngay lập tức.*

**Task 1.1: Dựng Cấu trúc Thư mục và File Dự án (Không đổi)**
*   **Mô tả:** Tạo cấu trúc thư mục và các file cơ bản cho dự án.
*   **Các bước thực hiện:**
    1.  Tạo cây thư mục như sau:
        ```
        project-hermes/
        ├── app/
        │   ├── __init__.py
        │   ├── main.py             # Khai báo Celery app
        │   ├── core/
        │   │   └── config.py       # Module đọc cấu hình
        │   ├── db/
        │   │   ├── mssql.py        # Module kết nối SQL Server
        │   │   └── mongodb.py      # Module kết nối MongoDB
        │   ├── models/             # Chứa các Pydantic model
        │   ├── tasks/              # Chứa các Celery task
        │   └── clients/            # Chứa các API client
        ├── tests/
        ├── .env
        ├── .gitignore
        ├── Dockerfile
        ├── docker-compose.yml
        └── requirements.txt
        ```

**Task 1.2: Thiết lập Module Cấu hình (Config) (Không đổi)**
*   **Mô tả:** Tạo module để đọc và xác thực tất cả các biến môi trường từ file `.env`.
*   **Các bước thực hiện:**
    1.  Trong `app/core/config.py`, sử dụng `pydantic-settings` để định nghĩa class `Settings`.
    2.  **Ví dụ code:**
        ```python
        from pydantic_settings import BaseSettings

        class Settings(BaseSettings):
            # Redis
            REDIS_HOST: str
            REDIS_PORT: int

            # MongoDB
            MONGO_URI: str
            MONGO_DB_NAME: str

            # SQL Server
            MSSQL_SERVER: str
            # ... các biến còn lại

            class Config:
                env_file = ".env"

        settings = Settings()
        ```

**Task 1.3: Container hóa Ứng dụng với Docker (Đã điều chỉnh)**
*   **Mô tả:** Tạo `Dockerfile` để đóng gói ứng dụng Python và `docker-compose.yml` để chạy các service worker của chúng ta. `docker-compose.yml` sẽ không chứa Redis hay MongoDB.
*   **Các bước thực hiện:**
    1.  **Viết `Dockerfile` (Không đổi):**
        ```dockerfile
        FROM python:3.9-slim
        WORKDIR /app
        COPY requirements.txt .
        RUN pip install --no-cache-dir -r requirements.txt
        COPY ./app /app
        ```
    2.  **Viết `docker-compose.yml` (Đã đơn giản hóa):**
        ```yaml
        version: '3.8'
        services:
          # Worker cho Phiếu Nhập
          phieu_nhap_worker:
            build: .
            command: ["celery", "-A", "app.main.celery_app", "worker", "-Q", "phieu_nhap_queue", "--loglevel=info"]
            env_file:
              - .env
            depends_on:
              - scheduler # Đảm bảo scheduler chạy trước

          # Worker cho Phiếu Xuất (sẽ thêm sau)
          # phieu_xuat_worker: ...

          # Worker cho Hóa Đơn Bán (sẽ thêm sau)
          # hoa_don_worker: ...

          # Service lập lịch
          scheduler:
            build: .
            command: ["celery", "-A", "app.main.celery_app", "beat", "--loglevel=info"]
            env_file:
              - .env
        ```
        *   **Lưu ý:** Chúng ta đã định nghĩa các worker riêng biệt và sử dụng hàng đợi (queue) khác nhau (`-Q phieu_nhap_queue`) để có thể mở rộng từng loại worker một cách độc lập.

**Task 1.4: Thiết lập Pipeline CI Cơ bản (Không đổi)**
*   **Mô tả:** Tạo workflow trên GitHub Actions để tự động kiểm tra code style và chạy unit test.
*   **Các bước thực hiện:**
    1.  Tạo file `.github/workflows/ci.yml` với các bước linting và testing.

---

### **GIAI ĐOẠN 2: XÂY DỰNG LUỒNG END-TO-END ĐẦU TIÊN (PHIẾU NHẬP)**

*Mục tiêu: Hoàn thành một luồng xử lý đầy đủ cho `Phiếu Nhập` làm khuôn mẫu.*

**Task 2.1: Định nghĩa Data Models cho Phiếu Nhập (Không đổi)**
*   **Mô tả:** Tạo các Pydantic model trong `app/models/phieu_nhap.py` để biểu diễn cấu trúc dữ liệu của `PhieuNhapHeader` và `PhieuNhapDetail`.

**Task 2.2: Tạo Polling Service để tìm Phiếu Nhập cần đồng bộ (Đã điều chỉnh)**
*   **Mô tả:** Tạo một Celery task chạy định kỳ để quét DB, tìm các phiếu nhập có `status_phieu` là `0` hoặc `2`, và đẩy `ma_phieu` của chúng vào hàng đợi `phieu_nhap_queue`.
*   **Các bước thực hiện:**
    1.  Trong `app/main.py`, cấu hình Celery Beat.
    2.  Tạo file `app/tasks/polling_service.py`.
    3.  **Ví dụ code:**
        ```python
        from app.main import celery_app
        from app.db.mssql import get_db_cursor
        from .phieu_nhap_worker import process_phieu_nhap_task

        @celery_app.on_after_configure.connect
        def setup_periodic_tasks(sender, **kwargs):
            # Chạy task mỗi 5 phút
            sender.add_periodic_task(300.0, find_pending_phieu_nhap.s(), name='find-pending-phieu-nhap')

        @celery_app.task
        def find_pending_phieu_nhap():
            """Quét và đẩy các phiếu nhập cần xử lý vào hàng đợi."""
            # ... (logic query DB như cũ) ...
            for row in rows:
                ma_phieu = row[0]
                # Gửi task đến hàng đợi cụ thể
                process_phieu_nhap_task.apply_async(args=[ma_phieu], queue='phieu_nhap_queue')
        ```

**Task 2.3: Xây dựng Worker xử lý Phiếu Nhập (Đã điều chỉnh)**
*   **Mô tả:** Tạo Celery worker để xử lý một phiếu nhập cụ thể.
*   **Các bước thực hiện:**
    1.  Tạo file `app/tasks/phieu_nhap_worker.py`.
    2.  **Viết code cho task `process_phieu_nhap_task`:**
        ```python
        # ... (import các thư viện cần thiết) ...

        @celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
        def process_phieu_nhap_task(self, ma_phieu: str):
            # Logic xử lý không đổi:
            # 1. Lấy dữ liệu từ DB.
            # 2. Validate bằng Pydantic model.
            # 3. Chuyển đổi thành payload cho API.
            # 4. Ghi log "PROCESSING" vào MongoDB.
            # 5. Gọi API đối tác.
            # 6. Xử lý kết quả (thành công, lỗi 4xx, lỗi 5xx).
            # 7. Cập nhật status vào SQL Server.
            # 8. Ghi log kết quả cuối cùng vào MongoDB.
        ```

---

### **GIAI ĐOẠN 3: MỞ RỘNG CHO CÁC LOẠI PHIẾU KHÁC**

*Mục tiêu: Tái sử dụng tối đa code để xử lý các loại phiếu còn lại.*

**Task 3.1: Xây dựng luồng xử lý cho Phiếu Xuất**
*   **Mô tả:** Sao chép và điều chỉnh luồng xử lý của Phiếu Nhập để áp dụng cho Phiếu Xuất.
*   **Các bước thực hiện:**
    1.  **Tạo Model:** Tạo `app/models/phieu_xuat.py`.
    2.  **Tạo Worker:** Tạo `app/tasks/phieu_xuat_worker.py`.
    3.  **Cập nhật Polling Service:** Thêm task định kỳ `find_pending_phieu_xuat` để đẩy task vào hàng đợi `phieu_xuat_queue`.
    4.  **Cập nhật `docker-compose.yml`:** Thêm service `phieu_xuat_worker` và chỉ định nó lắng nghe trên `phieu_xuat_queue`.

**Task 3.2: Xây dựng luồng xử lý cho Hóa Đơn Bán**
*   **Mô tả:** Sao chép và điều chỉnh luồng xử lý để áp dụng cho Hóa Đơn Bán.
*   **Các bước thực hiện:**
    1.  **Tạo Model:** Tạo `app/models/hoa_don.py`.
    2.  **Tạo Worker:** Tạo `app/tasks/hoa_don_worker.py`.
    3.  **Cập nhật Polling Service:** Thêm task định kỳ `find_pending_hoa_don` để đẩy task vào hàng đợi `hoa_don_queue`.
    4.  **Cập nhật `docker-compose.yml`:** Thêm service `hoa_don_worker` và chỉ định nó lắng nghe trên `hoa_don_queue`.

---

### **GIAI ĐOẠN 4: HOÀN THIỆN VÀ BÀN GIAO**

*Mục tiêu: Tối ưu code và chuẩn bị tài liệu cần thiết để bàn giao.*

**Task 4.1: Tái cấu trúc API Client (Không đổi)**
*   **Mô tả:** Gom logic gọi API vào một lớp `PartnerAPIClient` trong `app/clients/partner_api_client.py` để dễ quản lý.

**Task 4.2: Viết tài liệu bàn giao (README.md) (Không đổi)**
*   **Mô tả:** Tạo file `README.md` đầy đủ, giải thích cách chạy dự án và các cấu hình cần thiết.
*   **Nội dung cần có:**
    *   Mô tả ngắn về dự án.
    *   Danh sách tất cả các biến môi trường cần thiết.
    *   Hướng dẫn chạy dự án trên môi trường local: `docker-compose up --build`.
    *   Mô tả các service worker và các hàng đợi Celery tương ứng (`phieu_nhap_queue`, `phieu_xuat_queue`, `hoa_don_queue`).

---

Kế hoạch này giờ đây đã được tối ưu hóa, loại bỏ các phần không thuộc phạm vi của team và tập trung vào việc phát triển các thành phần cốt lõi. Các task được chia nhỏ và đủ chi tiết để các thành viên có thể làm việc song song và hiệu quả.