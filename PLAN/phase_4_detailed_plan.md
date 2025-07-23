# Kế hoạch Phát triển Chi tiết: Giai đoạn 4 - Hoàn thiện & Bàn giao

**Mục tiêu:** Tái cấu trúc mã nguồn để tăng tính tái sử dụng, giảm lặp lại và tạo tài liệu bàn giao rõ ràng cho đội DevOps.

---

### **Task 4.1: Tái cấu trúc logic gọi API vào một Client riêng**

*   **Mục tiêu:** Hiện tại, logic gọi API bằng `httpx` đang bị lặp lại trong mỗi worker. Task này sẽ gom toàn bộ logic đó vào một lớp `PartnerAPIClient` duy nhất để dễ dàng quản lý, bảo trì và thay đổi khi cần.
*   **Người thực hiện:** 1 Lập trình viên
*   **Hướng dẫn:**
    1.  Tạo tệp mới tại `app/clients/partner_api_client.py`.
    2.  Dán đoạn mã sau vào tệp. Lớp này sẽ đóng gói tất cả các tương tác với API của đối tác.
        ```python
        import httpx
        from app.core.config import settings
        import logging

        class PartnerAPIClient:
            def __init__(self):
                self.base_url = settings.API_BASE_URL
                self.auth = (settings.API_USERNAME, settings.API_PASSWORD)
                self.timeout = 30.0

            def _make_request(self, method: str, endpoint: str, payload: dict) -> dict:
                """Hàm chung để thực hiện các request đến API đối tác."""
                url = f"{self.base_url}{endpoint}"
                try:
                    with httpx.Client() as client:
                        response = client.request(
                            method,
                            url,
                            json=payload,
                            auth=self.auth,
                            timeout=self.timeout
                        )
                        response.raise_for_status()
                        return response.json()
                except httpx.HTTPStatusError as exc:
                    logging.error(f"Lỗi API khi gọi {method} {url}: {exc.response.status_code} - {exc.response.text}")
                    raise # Ném lại lỗi để worker có thể xử lý
                except Exception as exc:
                    logging.error(f"Lỗi không xác định khi gọi {method} {url}: {exc}")
                    raise

            def submit_phieu_nhap(self, payload: dict) -> dict:
                """Gửi dữ liệu phiếu nhập."""
                logging.info(f"Gửi phiếu nhập {payload.get('invoiceCode')} đến API.")
                return self._make_request("POST", "/phieunhap", payload)

            def submit_phieu_xuat(self, payload: dict) -> dict:
                """Gửi dữ liệu phiếu xuất."""
                logging.info(f"Gửi phiếu xuất {payload.get('invoiceCode')} đến API.")
                return self._make_request("POST", "/phieuxuat", payload)

            def submit_hoa_don(self, payload: dict) -> dict:
                """Gửi dữ liệu hóa đơn bán."""
                logging.info(f"Gửi hóa đơn {payload.get('billCode')} đến API.")
                return self._make_request("POST", "/hoadon", payload)

        # Tạo một instance duy nhất để các worker sử dụng
        partner_api_client = PartnerAPIClient()
        ```
    3.  **Cập nhật các Worker:**
        *   Mở từng tệp worker (`phieu_nhap_worker.py`, `phieu_xuat_worker.py`, `hoa_don_worker.py`).
        *   Import client mới: `from app.clients.partner_api_client import partner_api_client`.
        *   Thay thế khối `with httpx.Client() as client: ...` bằng một dòng gọi duy nhất. Ví dụ trong `phieu_nhap_worker.py`:
            ```python
            # Thay thế khối code gọi API cũ bằng dòng này:
            api_response = partner_api_client.submit_phieu_nhap(api_payload)
            ```

---

### **Task 4.2: Viết tài liệu bàn giao (README.md)**

*   **Mục tiêu:** Tạo một tài liệu `README.md` toàn diện, hướng dẫn cách thiết lập, cấu hình và chạy dự án. Đây là tài liệu quan trọng nhất để bàn giao cho team DevOps hoặc cho một lập trình viên mới.
*   **Người thực hiện:** 1 Lập trình viên
*   **Hướng dẫn:**
    1.  Tạo hoặc mở tệp `README.md` ở thư mục gốc của dự án.
    2.  Dán và điền đầy đủ nội dung theo mẫu sau:
        ```markdown
        # Project Hermes: Data Synchronization Gateway

        Hệ thống này chịu trách nhiệm đồng bộ dữ liệu phiếu nhập, phiếu xuất và hóa đơn bán hàng từ cơ sở dữ liệu nội bộ (SQL Server) lên hệ thống API của đối tác.

        ## Kiến trúc

        Hệ thống sử dụng kiến trúc hướng tác vụ (Task-Driven) với Celery và Redis.
        - **Celery Beat (Scheduler):** Quét cơ sở dữ liệu định kỳ để tìm các phiếu cần đồng bộ.
        - **Celery Workers:** Các tiến trình nền thực thi việc xử lý và gửi dữ liệu cho từng loại phiếu.
        - **Redis:** Đóng vai trò là Message Broker, điều phối tác vụ giữa Scheduler và Workers.
        - **MongoDB:** Lưu trữ log chi tiết của mỗi lần đồng bộ.

        ## Yêu cầu hệ thống

        - Docker & Docker Compose
        - Python 3.9+

        ## Cấu hình Môi trường

        Tạo một tệp `.env` ở thư mục gốc của dự án và điền các giá trị sau. Đây là các thông tin nhạy cảm và không được commit vào Git.

        ```ini
        # Cấu hình Redis
        REDIS_HOST=your_redis_host
        REDIS_PORT=6379

        # Cấu hình MongoDB
        MONGO_URI=mongodb://user:password@your_mongo_host:27017
        MONGO_DB_NAME=sync_data_logs

        # Cấu hình SQL Server
        MSSQL_SERVER=your_sql_server_host
        MSSQL_DATABASE=DQG
        MSSQL_USER=your_user
        MSSQL_PASSWORD=your_password
        # MSSQL_DRIVER (tùy chọn, mặc định là {ODBC Driver 17 for SQL Server})

        # Cấu hình API Đối tác
        API_BASE_URL=http://partner_api_url
        API_USERNAME=api_user
        API_PASSWORD=api_password
        ```

        ## Hướng dẫn Chạy trên Local

        1.  **Cài đặt các thư viện (nếu chạy không dùng Docker):**
            ```bash
            pip install -r requirements.txt
            ```

        2.  **Chạy bằng Docker Compose (Khuyến khích):**
            Lệnh này sẽ build các image cần thiết và khởi chạy tất cả các service (scheduler và các workers) được định nghĩa trong `docker-compose.yml`.
            ```bash
            docker-compose up --build -d
            ```

        3.  **Xem logs của một service cụ thể:**
            ```bash
            docker-compose logs -f <tên_service>
            # Ví dụ:
            # docker-compose logs -f phieu_nhap_worker
            ```

        4.  **Dừng hệ thống:**
            ```bash
            docker-compose down
            ```

        ## Cấu trúc các hàng đợi (Queues)

        Hệ thống sử dụng các hàng đợi riêng biệt cho từng loại phiếu để tối ưu hóa việc xử lý:
        - `phieu_nhap_queue`: Dành cho các tác vụ xử lý phiếu nhập.
        - `phieu_xuat_queue`: Dành cho các tác vụ xử lý phiếu xuất.
        - `hoa_don_queue`: Dành cho các tác vụ xử lý hóa đơn bán.