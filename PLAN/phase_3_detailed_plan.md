# Phase 3 Detailed Development Plan: Extending to Other Document Types

**Objective:**  
Implement end-to-end processing flows for `Phiếu Xuất` (Goods Issue) and `Hóa Đơn Bán` (Sales Invoice) by reusing the structure and logic from the `Phiếu Nhập` (Goods Receipt) flow.

---

## Task 3.1: Implement Processing Flow for "Phiếu Xuất"

- **Goal:**  
  Complete the synchronization flow for `Phiếu Xuất`.

- **Subtasks:**

  - **Task 3.1.1: Define Data Models for "Phiếu Xuất"**
    - **Assignee:** 1 Developer
    - **Instructions:**
      - Create [`app/models/phieu_xuat.py`](app/models/phieu_xuat.py).
      - Define models matching the structure of `PhieuXuatHeader` and `PhieuXuatDetail` tables, supporting field aliasing for API payloads.

  - **Task 3.1.2: Create "Phiếu Xuất" Processing Worker**
    - **Assignee:** 1 Developer
    - **Instructions:**
      - Create [`app/tasks/phieu_xuat_worker.py`](app/tasks/phieu_xuat_worker.py).
      - Copy the logic from [`app/tasks/phieu_nhap_worker.py`](app/tasks/phieu_nhap_worker.py) and adjust:
        - Task and function names for "Phiếu Xuất".
        - Use the correct API endpoint and database updates for "Phiếu Xuất".
        - Update logging and error handling to reflect "Phiếu Xuất".

  - **Task 3.1.3: Update Polling Service for "Phiếu Xuất"**
    - **Assignee:** 1 Developer
    - **Instructions:**
      - Edit [`app/tasks/polling_service.py`](app/tasks/polling_service.py).
      - Add a `prepare_and_dispatch_phieu_xuat()` function, and call it in the main polling task.
      - Ensure it fetches data from `PhieuXuatHeader` and `PhieuXuatDetail`, builds payloads, and enqueues them for processing.

---

## Task 3.2: Implement Processing Flow for "Hóa Đơn Bán"

- **Goal:**  
  Complete the synchronization flow for `Hóa Đơn Bán`.

- **Subtasks:**

  - **Task 3.2.1: Define Data Models for "Hóa Đơn Bán"**
    - **Assignee:** 1 Developer
    - **Instructions:**
      - Create [`app/models/hoa_don.py`](app/models/hoa_don.py).
      - Define models matching the structure of `HoaDonHeader` and `HoaDonDetail` tables, supporting field aliasing for API payloads.

  - **Task 3.2.2: Create "Hóa Đơn Bán" Processing Worker**
    - **Assignee:** 1 Developer
    - **Instructions:**
            2.  Thêm hàm `prepare_and_dispatch_phieu_xuat()` và gọi nó bên trong task `find_pending_invoices`.
                ```python
                # Thêm import ở đầu file
                from .phieu_xuat_worker import process_phieu_xuat_task
                from app.models.phieu_xuat import PhieuXuatPayloadModel, PhieuXuatDetailModel
                # Sửa task find_pending_invoices
                @celery_app.task(name="tasks.find_pending_invoices")
                def find_pending_invoices():
                    # ...
                    prepare_and_dispatch_phieu_nhap()
                    prepare_and_dispatch_phieu_xuat() // Thêm dòng này
                    # ...
                # Thêm hàm mới này vào cuối file
                def prepare_and_dispatch_phieu_xuat():
                    """Lấy dữ liệu, xây dựng payload và gửi task cho các phiếu xuất."""
                    # Logic tương tự prepare_and_dispatch_phieu_nhap, nhưng:
                    # - Query từ PhieuXuatHeader và PhieuXuatDetail.
                    # - Sử dụng PhieuXuatPayloadModel và PhieuXuatDetailModel.
                    # - Gửi task đến hàng đợi 'phieu_xuat_queue' với payload tương ứng.
                    #   process_phieu_xuat_task.apply_async(args=[api_payload], queue='phieu_xuat_queue')
                    pass # Lập trình viên sẽ triển khai chi tiết
                ```
---
### **Task 3.2: Xây dựng luồng xử lý cho Hóa Đơn Bán**
*   **Mục tiêu:** Hoàn thiện luồng đồng bộ cho `Hóa Đơn Bán`.
*   **Phân rã thành các sub-task nhỏ:**
    *   **Task 3.2.1: Định nghĩa Data Models cho Hóa Đơn Bán**
        *   **Người thực hiện:** 1 Lập trình viên
        *   **Hướng dẫn:**
            1.  Tạo tệp mới tại `app/models/hoa_don.py`.
            2.  Dán đoạn mã sau vào tệp, đảm bảo khớp với cấu trúc bảng `HoaDonHeader` và `HoaDonDetail`.
                ```python
                from pydantic import BaseModel, Field
                from typing import List, Optional
                from datetime import date
                class HoaDonDetailModel(BaseModel):
                    ma_thuoc: str
                    ten_thuoc: str
                    # ... tất cả các trường cần thiết từ bảng HoaDonDetail
                    class Config:
                        orm_mode = True
                class HoaDonPayloadModel(BaseModel):
                    ma_hoa_don: str = Field(alias="billCode")
                    ngay_ban: date = Field(alias="saleDate")
                    # ... các trường khác từ HoaDonHeader mà API yêu cầu
                    details: List[HoaDonDetailModel] = Field(alias="items")
                    class Config:
                        allow_population_by_field_name = True
                        json_encoders = {
                            date: lambda v: v.strftime('%Y-%m-%d')
                        }
                ```
    *   **Task 3.2.2: Tạo Worker xử lý Hóa Đơn Bán (Đã điều chỉnh)**
        *   **Người thực hiện:** 1 Lập trình viên
        *   **Hướng dẫn:**
            1.  Tạo tệp mới tại `app/tasks/hoa_don_worker.py`.
            2.  **Sao chép toàn bộ nội dung** từ tệp `app/tasks/phieu_nhap_worker.py` (phiên bản đã điều chỉnh).
            3.  **Chỉnh sửa các điểm sau:**
                *   Đổi tên task: `@celery_app.task(..., name="tasks.process_hoa_don", ...)`
                *   Đổi tên hàm: `def process_hoa_don_task(self, api_payload: dict):`
                *   Lấy `ma_hoa_don` từ payload: `ma_hoa_don = api_payload.get("billCode")`
                *   Endpoint API: Gọi đến endpoint của hóa đơn (ví dụ: `/hoadon`).
                *   Cập nhật DB khi thành công: `UPDATE HoaDonHeader SET status_phieu = 1, ma_don_thuoc_quoc_gia = ? ...`
                *   Cập nhật DB khi lỗi: `UPDATE HoaDonHeader SET status_phieu = 2 (hoặc 3) ...`
                *   Ghi log: Thay đổi `type` thành `"HoaDon"`.
    *   **Task 3.2.3: Cập nhật Polling Service cho Hóa Đơn Bán (Đã điều chỉnh)**
        *   **Người thực hiện:** 1 Lập trình viên
        *   **Hướng dẫn:**
            1.  Mở tệp `app/tasks/polling_service.py`.
            2.  Thêm hàm `prepare_and_dispatch_hoa_don()` và gọi nó bên trong task `find_pending_invoices`.
                ```python
                # Thêm import ở đầu file
                from .hoa_don_worker import process_hoa_don_task
                from app.models.hoa_don import HoaDonPayloadModel, HoaDonDetailModel
                # Sửa task find_pending_invoices
                @celery_app.task(name="tasks.find_pending_invoices")
                def find_pending_invoices():
                    # ...
                    prepare_and_dispatch_phieu_xuat()
                    prepare_and_dispatch_hoa_don() // Thêm dòng này
                # Thêm hàm mới này vào cuối file
                def prepare_and_dispatch_hoa_don():
                    """Lấy dữ liệu, xây dựng payload và gửi task cho các hóa đơn."""
                    # Logic tương tự prepare_and_dispatch_phieu_nhap, nhưng:
                    # - Query từ HoaDonHeader và HoaDonDetail.
                    # - Sử dụng HoaDonPayloadModel và HoaDonDetailModel.
                    # - Gửi task đến hàng đợi 'hoa_don_queue' với payload tương ứng.
                    #   process_hoa_don_task.apply_async(args=[api_payload], queue='hoa_don_queue')
                    pass # Lập trình viên sẽ triển khai chi tiết