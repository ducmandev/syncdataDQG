# Kế hoạch chi tiết - Giai đoạn 2: Polling và Tạo Task (Cập nhật theo database.sql)
**Mục tiêu:** Xây dựng một cơ chế tự động để đọc các hóa đơn mới trong ngày từ bảng `HoaDonHeader` và tạo task xử lý tương ứng. Hệ thống sẽ không cập nhật cơ sở dữ liệu nguồn và sẽ sử dụng MongoDB để quản lý trạng thái, ngăn chặn xử lý trùng lặp.
**Thông tin cốt lõi (từ `database.sql`):**
- **Bảng mục tiêu:** `HoaDonHeader`
- **Cột trạng thái:** `status_phieu` (Giá trị cần tìm: `0` - Giả định)
- **Cột ngày để lọc:** `ngay_ban`
- **Khóa chính:** `ma_hoa_don`
---
### 1. **Hoàn thiện Module `database.py` (Cập nhật)**
**Mục tiêu:** Cung cấp các hàm để truy vấn (chỉ đọc) dữ liệu từ `HoaDonHeader` và `HoaDonDetail`.
**Hành động:** Cập nhật thiết kế cho file `src/database.py`.
**Nội dung đề xuất:**
```python
# src/database.py
import os
import pyodbc
from dotenv import load_dotenv
load_dotenv()

# Lớp MSSQL giữ nguyên
class MSSQL:
    # ... (code giữ nguyên) ...

def get_new_hoa_don_headers(batch_size: int = 100):
    """
    **Đã cập nhật:** Truy vấn các bản ghi header mới từ bảng `HoaDonHeader`.
    """
    records = []
    # **Câu lệnh SQL đã được cập nhật theo schema mới**
    query = f"""
    SELECT TOP {batch_size} *
    FROM HoaDonHeader
    WHERE status_phieu = 0  -- Giả định 0 là trạng thái mới
      AND ngay_ban >= CAST(GETDATE() AS DATE)
    ORDER BY ngay_ban ASC;
    """
    try:
        with MSSQL() as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            rows = cursor.fetchall()
            columns = [column[0] for column in cursor.description]
            for row in rows:
                records.append(dict(zip(columns, row)))
    except pyodbc.Error as e:
        print(f"Database error fetching new records from HoaDonHeader: {e}")
    return records

def get_hoa_don_details(ma_hoa_don: str):
    """
    **Hàm mới:** Lấy tất cả các dòng chi tiết cho một hóa đơn cụ thể.
    Hàm này sẽ được sử dụng trong Giai đoạn 3.
    """
    details = []
    query = "SELECT * FROM HoaDonDetail WHERE ma_hoa_don = ?"
    try:
        with MSSQL() as conn:
            cursor = conn.cursor()
            cursor.execute(query, ma_hoa_don)
            rows = cursor.fetchall()
            columns = [column[0] for column in cursor.description]
            for row in rows:
                details.append(dict(zip(columns, row)))
    except pyodbc.Error as e:
        print(f"Database error fetching details for ma_hoa_don {ma_hoa_don}: {e}")
    return details
```
---
### 2. **Xây dựng Logic Chống Trùng lặp và Tạo Task (Cập nhật)**
**Mục tiêu:** Tạo task polling có khả năng chống race condition bằng MongoDB, sử dụng `ma_hoa_don` làm khóa định danh.
**Hành động:** Cập nhật thiết kế cho `src/tasks/process_records.py`.
**Nội dung đề xuất:**
```python
# src/tasks/process_records.py
from src.celery_app import celery_app, db
from src.database import get_new_hoa_don_headers
import json
from datetime import datetime

@celery_app.task(name="process_hoa_don_task", bind=True)
def process_hoa_don_task(self, header_data: dict):
    """
    **Đã cập nhật:** Task này sẽ xử lý logic cho một hóa đơn.
    Nó nhận toàn bộ dữ liệu của header.
    """
    task_id = self.request.id
    record_id = header_data.get("ma_hoa_don")
    db.processing_logs.update_one(
        {"record_id": record_id, "record_type": "hoa_don"},
        {"$set": {"status": "PROCESSING", "task_id": str(task_id)}}
    )
    print(f"[{task_id}] Started processing hoa_don: {record_id}")
    # Logic xử lý chi tiết (gồm cả việc gọi `get_hoa_don_details`) sẽ nằm ở Giai đoạn 3.
    return f"Processing started for hoa_don {record_id}."

@celery_app.task(name="poll_new_hoa_don")
def poll_new_hoa_don():
    """
    **Đã cập nhật:** Task định kỳ để tìm và tạo task cho các hóa đơn mới.
    """
    print("Polling for new HoaDon...")
    candidate_headers = get_new_hoa_don_headers()
    if not candidate_headers:
        return "No new HoaDon found."
    
    tasks_created_count = 0
    for header in candidate_headers:
        record_id = header.get("ma_hoa_don")
        record_type = "hoa_don"
        
        # Logic chống race condition với MongoDB giữ nguyên, chỉ thay đổi key
        log_entry = db.processing_logs.find_one_and_update(
            {"record_id": record_id, "record_type": record_type},
            {"$setOnInsert": {
                "status": "QUEUED",
                "created_at": datetime.utcnow()
            }},
            upsert=True
        )
        
        if log_entry is None:
            process_hoa_don_task.delay(header_data=header)
            tasks_created_count += 1
            print(f"Claimed and queued task for hoa_don: {record_id}")
        else:
            print(f"Hoa_don {record_id} was already queued. Skipping.")
            
    message = f"Polling complete. Created {tasks_created_count} new tasks."
    print(message)
    return message
```
---
### 3. **Cấu hình Lịch chạy (Beat Schedule) (Cập nhật)**
**Mục tiêu:** Cập nhật lịch chạy để gọi đúng task polling mới.
**Hành động:** Cập nhật thiết kế cho `src/celery_app.py`.
**Nội dung cần thêm/thay đổi trong `src/celery_app.py`:**
```python
# src/celery_app.py (cuối file)
from celery.schedules import crontab

celery_app.conf.beat_schedule = {
    'poll-hoa-don-every-minute': {
        'task': 'poll_new_hoa_don', # **Tên task đã được cập nhật**
        'schedule': crontab(),
    },
}
```
---
**Kết quả cần đạt được của Giai đoạn 2 (đã cập nhật):**
- [ ] Module `database.py` có thể đọc dữ liệu từ `HoaDonHeader` và `HoaDonDetail`.
- [ ] Task `poll_new_hoa_don` chạy định kỳ, lấy các header có `status_phieu=0` trong ngày.
- [ ] Task polling sử dụng `ma_hoa_don` để "claim" bản ghi trong MongoDB, đảm bảo không tạo task trùng lặp.
- [ ] Một task `process_hoa_don_task` được tạo cho mỗi hóa đơn mới.
- [ ] Log trong MongoDB được tạo và cập nhật chính xác.