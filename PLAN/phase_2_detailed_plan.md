# Kế hoạch Phát triển Chi tiết: Giai đoạn 2 - Luồng End-to-End cho Phiếu Nhập

**Mục tiêu:** Xây dựng và kiểm thử thành công một luồng xử lý hoàn chỉnh cho "Phiếu Nhập", từ việc phát hiện phiếu trong DB, xử lý, gọi API đối tác, cho đến cập nhật kết quả và ghi log.

---

### **Task 2.1: Thiết lập Kết nối Cơ sở dữ liệu**

*   **Mục tiêu:** Viết các hàm để quản lý kết nối đến SQL Server và MongoDB, đảm bảo kết nối được tái sử dụng và xử lý lỗi một cách an toàn.
*   **Người thực hiện:** 1 Lập trình viên
*   **Hướng dẫn:**
    1.  **Đối với SQL Server:**
        *   Mở tệp `app/db/mssql.py`.
        *   Dán đoạn mã sau vào tệp. Mã này tạo một connection string và cung cấp một hàm để lấy con trỏ (cursor) đến DB.
            ```python
            import pyodbc
            from app.core.config import settings
            import logging

            # Xây dựng chuỗi kết nối từ settings
            CONN_STR = (
                f"DRIVER={{{settings.MSSQL_DRIVER}}};"
                f"SERVER={settings.MSSQL_SERVER};"
                f"DATABASE={settings.MSSQL_DATABASE};"
                f"UID={settings.MSSQL_USER};"
                f"PWD={settings.MSSQL_PASSWORD};"
            )

            def get_db_connection():
                """Tạo và trả về một kết nối mới đến SQL Server."""
                try:
                    conn = pyodbc.connect(CONN_STR)
                    return conn
                except pyodbc.Error as ex:
                    sqlstate = ex.args[0]
                    logging.error(f"Lỗi kết nối SQL Server: {sqlstate}")
                    raise
            ```
    2.  **Đối với MongoDB:**
        *   Mở tệp `app/db/mongodb.py`.
        *   Dán đoạn mã sau vào tệp. Mã này quản lý kết nối đến MongoDB và cung cấp một hàm để ghi log.
            ```python
            from pymongo import MongoClient
            from app.core.config import settings
            import logging
            from datetime import datetime

            client = None
            db = None

            def connect_to_mongo():
                """Khởi tạo kết nối đến MongoDB."""
                global client, db
                try:
                    client = MongoClient(settings.MONGO_URI, serverSelectionTimeoutMS=5000)
                    db = client[settings.MONGO_DB_NAME]
                    client.server_info() # Kiểm tra kết nối
                    logging.info("Kết nối MongoDB thành công.")
                except Exception as e:
                    logging.error(f"Không thể kết nối đến MongoDB: {e}")
                    client = None
                    db = None

            def get_mongo_db():
                """Trả về đối tượng database, kết nối lại nếu cần."""
                if client is None or db is None:
                    connect_to_mongo()
                return db

            def log_to_mongodb(log_data: dict):
                """Ghi một bản ghi log vào collection 'sync_logs'."""
                mongo_db = get_mongo_db()
                if mongo_db:
                    log_data['timestamp'] = datetime.utcnow()
                    mongo_db.sync_logs.insert_one(log_data)

            # Khởi tạo kết nối khi module được import
            connect_to_mongo()
            ```

---

### **Task 2.2: Định nghĩa Data Models cho Phiếu Nhập**

*   **Mục tiêu:** Tạo các lớp Pydantic để xác thực cấu trúc dữ liệu của `PhieuNhapHeader` và `PhieuNhapDetail` sau khi đọc từ DB.
*   **Người thực hiện:** 1 Lập trình viên
*   **Hướng dẫn:**
    1.  Tạo tệp mới tại `app/models/phieu_nhap.py`.
    2.  Dán đoạn mã sau vào tệp. Các model này ánh xạ chính xác với các cột trong bảng DB.
        ```python
        from pydantic import BaseModel, Field
        from typing import List, Optional
        from datetime import date, datetime

        class PhieuNhapDetailModel(BaseModel):
            ma_thuoc: str
            ten_thuoc: str
            so_lo: str
            ngay_san_xuat: Optional[date] = None
            han_dung: date
            so_dklh: Optional[str] = None
            so_luong: int
            don_gia: float
            thanh_tien: float
            don_vi_tinh: str

            class Config:
                orm_mode = True

        class PhieuNhapPayloadModel(BaseModel):
            ma_phieu: str = Field(alias="invoiceCode")
            ngay_nhap: datetime = Field(alias="importDate")
            ten_co_so_cung_cap: str = Field(alias="supplierName")
            details: List[PhieuNhapDetailModel] = Field(alias="items")
            # Thêm các trường khác nếu API đối tác yêu cầu

            class Config:
                allow_population_by_field_name = True
                json_encoders = {
                    datetime: lambda v: v.strftime('%Y-%m-%dT%H:%M:%S'),
                    date: lambda v: v.strftime('%Y-%m-%d')
                }
        ```
        *   **Lưu ý:** `PhieuNhapPayloadModel` được thiết kế để chuyển đổi tên trường từ Python-style (`ma_phieu`) sang camelCase (`invoiceCode`) khi tạo JSON để gửi đi.

---

### **Task 2.3: Tạo Polling Service**

*   **Mục tiêu:** Tạo một Celery task chạy định kỳ để quét DB, tìm các phiếu cần đồng bộ và đưa chúng vào hàng đợi xử lý.
*   **Người thực hiện:** 1 Lập trình viên
*   **Hướng dẫn:**
    1.  Tạo tệp mới tại `app/tasks/polling_service.py`.
    2.  Dán đoạn mã sau vào tệp.
        ```python
        from app.main import celery_app
        from app.db.mssql import get_db_connection
        from .phieu_nhap_worker import process_phieu_nhap_task
        # Import các worker khác ở đây khi chúng được tạo
        import logging

        @celery_app.on_after_configure.connect
        def setup_periodic_tasks(sender, **kwargs):
            # Chạy task mỗi 5 phút
            sender.add_periodic_task(300.0, find_pending_invoices.s(), name='find-all-pending-invoices')

        @celery_app.task(name="tasks.find_pending_invoices")
        def find_pending_invoices():
            """Quét tất cả các loại phiếu và đẩy vào hàng đợi tương ứng."""
            logging.info("Bắt đầu quét các phiếu chờ xử lý...")
            find_phieu_nhap()
            # Gọi các hàm find_phieu_xuat(), find_hoa_don() ở đây trong tương lai

        def find_phieu_nhap():
            """Tìm và đưa các phiếu nhập vào hàng đợi."""
            conn = None
            try:
                conn = get_db_connection()
                cursor = conn.cursor()
                query = "SELECT ma_phieu FROM PhieuNhapHeader WHERE status_phieu IN (0, 2) ORDER BY ngay_nhap ASC"
                cursor.execute(query)
                rows = cursor.fetchall()
                for row in rows:
                    ma_phieu = row[0]
                    logging.info(f"Đưa phiếu nhập '{ma_phieu}' vào hàng đợi 'phieu_nhap_queue'.")
                    process_phieu_nhap_task.apply_async(args=[ma_phieu], queue='phieu_nhap_queue')
            except Exception as e:
                logging.error(f"Lỗi khi quét phiếu nhập: {e}")
            finally:
                if conn:
                    conn.close()
        ```

---

### **Task 2.4: Xây dựng Worker xử lý Phiếu Nhập**

*   **Mục tiêu:** Đây là task cốt lõi. Tạo Celery worker để thực hiện toàn bộ logic xử lý cho một phiếu nhập.
*   **Người thực hiện:** 1 Lập trình viên
*   **Hướng dẫn:**
    1.  Tạo tệp mới tại `app/tasks/phieu_nhap_worker.py`.
    2.  Dán đoạn mã sau vào tệp. Đây là bộ khung hoàn chỉnh cho worker.
        ```python
        import httpx
        import logging
        from app.main import celery_app
        from app.core.config import settings
        from app.db.mssql import get_db_connection
        from app.db.mongodb import log_to_mongodb
        from app.models.phieu_nhap import PhieuNhapDetailModel, PhieuNhapPayloadModel

        @celery_app.task(bind=True, name="tasks.process_phieu_nhap", max_retries=3, default_retry_delay=60)
        def process_phieu_nhap_task(self, ma_phieu: str):
            """Xử lý một phiếu nhập duy nhất: lấy dữ liệu, gọi API, cập nhật kết quả."""
            log_prefix = f"[Phiếu Nhập {ma_phieu}]"
            logging.info(f"{log_prefix} Bắt đầu xử lý.")
            
            conn = get_db_connection()
            cursor = conn.cursor()

            try:
                # Bước 1: Lấy dữ liệu Header và Details từ SQL Server
                cursor.execute("SELECT * FROM PhieuNhapHeader WHERE ma_phieu=?", ma_phieu)
                header_row = cursor.fetchone()
                if not header_row:
                    raise ValueError("Không tìm thấy phiếu nhập.")

                cursor.execute("SELECT * FROM PhieuNhapDetail WHERE ma_phieu=?", ma_phieu)
                details_rows = cursor.fetchall()

                # Bước 2: Validate và chuyển đổi dữ liệu bằng Pydantic
                # Lưu ý: Cần bật orm_mode=True trong Pydantic model để from_orm hoạt động
                details_data = [PhieuNhapDetailModel.from_orm(row) for row in details_rows]
                payload_data = PhieuNhapPayloadModel(
                    ma_phieu=header_row.ma_phieu,
                    ngay_nhap=header_row.ngay_nhap,
                    ten_co_so_cung_cap=header_row.ten_co_so_cung_cap,
                    details=details_data
                )
                api_payload = payload_data.dict(by_alias=True)

                # Bước 3: Ghi log xử lý vào MongoDB
                log_to_mongodb({
                    "ma_phieu": ma_phieu, "type": "PhieuNhap", "status": "PROCESSING",
                    "attempt": self.request.retries + 1, "payload": api_payload
                })

                # Bước 4: Gọi API đối tác
                with httpx.Client() as client:
                    response = client.post(
                        f"{settings.API_BASE_URL}/phieunhap",
                        json=api_payload,
                        auth=(settings.API_USERNAME, settings.API_PASSWORD),
                        timeout=30.0
                    )
                    response.raise_for_status() # Ném lỗi nếu status là 4xx hoặc 5xx

                # Bước 5: Xử lý thành công
                api_response = response.json()
                ma_phieu_qg = api_response.get("ma_phieu_nhap_quoc_gia")
                
                cursor.execute(
                    "UPDATE PhieuNhapHeader SET status_phieu = 1, ma_phieu_nhap_quoc_gia = ?, note_log = 'Success' WHERE ma_phieu = ?",
                    ma_phieu_qg, ma_phieu
                )
                conn.commit()
                logging.info(f"{log_prefix} Đồng bộ thành công.")
                log_to_mongodb({
                    "ma_phieu": ma_phieu, "type": "PhieuNhap", "status": "SUCCESS",
                    "response": api_response
                })

            except httpx.HTTPStatusError as exc:
                error_details = f"Lỗi API: {exc.response.status_code}, Body: {exc.response.text}"
                logging.error(f"{log_prefix} {error_details}")
                
                if 400 <= exc.response.status_code < 500:
                    # Lỗi 4xx: Lỗi dữ liệu, không thử lại
                    cursor.execute("UPDATE PhieuNhapHeader SET status_phieu = 3, note_log = ? WHERE ma_phieu = ?", error_details, ma_phieu)
                    log_to_mongodb({"ma_phieu": ma_phieu, "type": "PhieuNhap", "status": "FAILED_PERMANENT", "error": error_details})
                else:
                    # Lỗi 5xx: Lỗi server, thử lại
                    cursor.execute("UPDATE PhieuNhapHeader SET status_phieu = 2, note_log = ? WHERE ma_phieu = ?", error_details, ma_phieu)
                    log_to_mongodb({"ma_phieu": ma_phieu, "type": "PhieuNhap", "status": "FAILED_RETRYING", "error": error_details})
                    raise self.retry(exc=exc)
                conn.commit()

            except Exception as exc:
                error_details = f"Lỗi không xác định: {str(exc)}"
                logging.error(f"{log_prefix} {error_details}")
                cursor.execute("UPDATE PhieuNhapHeader SET status_phieu = 2, note_log = ? WHERE ma_phieu = ?", error_details, ma_phieu)
                conn.commit()
                log_to_mongodb({"ma_phieu": ma_phieu, "type": "PhieuNhap", "status": "FAILED_RETRYING", "error": error_details})
                raise self.retry(exc=exc)
            
            finally:
                if conn:
                    conn.close()