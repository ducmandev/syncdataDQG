# Kế hoạch Phát triển Chi tiết: Giai đoạn 3 - Mở rộng cho các loại phiếu khác

**Mục tiêu:** Triển khai các luồng xử lý end-to-end cho `Phiếu Xuất` và `Hóa Đơn Bán` bằng cách tái sử dụng cấu trúc và logic từ luồng `Phiếu Nhập`.

---

### **Task 3.1: Xây dựng luồng xử lý cho Phiếu Xuất**

*   **Mục tiêu:** Hoàn thiện luồng đồng bộ cho `Phiếu Xuất`.
*   **Phân rã thành các sub-task nhỏ:**

    *   **Task 3.1.1: Định nghĩa Data Models cho Phiếu Xuất**
        *   **Người thực hiện:** 1 Lập trình viên
        *   **Hướng dẫn:**
            1.  Tạo tệp mới tại `app/models/phieu_xuat.py`.
            2.  Dán đoạn mã sau vào tệp. Model này phải khớp với cấu trúc bảng `PhieuXuatHeader` và `PhieuXuatDetail`.
                ```python
                from pydantic import BaseModel, Field
                from typing import List, Optional
                from datetime import date

                class PhieuXuatDetailModel(BaseModel):
                    ma_thuoc: str
                    ten_thuoc: str
                    so_lo: str
                    han_dung: date
                    so_luong: int
                    don_gia: float
                    don_vi_tinh: str
                    # ... các trường khác từ bảng PhieuXuatDetail

                    class Config:
                        orm_mode = True

                class PhieuXuatPayloadModel(BaseModel):
                    ma_phieu: str = Field(alias="invoiceCode")
                    ngay_xuat: date = Field(alias="exportDate")
                    # ... các trường khác từ PhieuXuatHeader mà API yêu cầu
                    details: List[PhieuXuatDetailModel] = Field(alias="items")

                    class Config:
                        allow_population_by_field_name = True
                        json_encoders = {
                            date: lambda v: v.strftime('%Y-%m-%d')
                        }
                ```

    *   **Task 3.1.2: Tạo Worker xử lý Phiếu Xuất**
        *   **Người thực hiện:** 1 Lập trình viên
        *   **Hướng dẫn:**
            1.  Tạo tệp mới tại `app/tasks/phieu_xuat_worker.py`.
            2.  **Sao chép toàn bộ nội dung** từ tệp `app/tasks/phieu_nhap_worker.py`.
            3.  **Chỉnh sửa các điểm sau:**
                *   Đổi tên task: `@celery_app.task(..., name="tasks.process_phieu_xuat", ...)`
                *   Đổi tên hàm: `def process_phieu_xuat_task(self, ma_phieu: str):`
                *   Import model mới: `from app.models.phieu_xuat import ...`
                *   Câu lệnh SQL: Thay `PhieuNhapHeader` bằng `PhieuXuatHeader` và `PhieuNhapDetail` bằng `PhieuXuatDetail`.
                *   Tạo Payload: Sử dụng `PhieuXuatPayloadModel` thay vì `PhieuNhapPayloadModel`.
                *   Endpoint API: Gọi đến endpoint của phiếu xuất (ví dụ: `/phieuxuat`).
                *   Cập nhật DB khi thành công: `UPDATE PhieuXuatHeader SET status_phieu = 1, ma_phieu_xuat_quoc_gia = ? ...`
                *   Cập nhật DB khi lỗi: `UPDATE PhieuXuatHeader SET status_phieu = 2 (hoặc 3) ...`
                *   Ghi log: Thay đổi `type` thành `"PhieuXuat"`.

    *   **Task 3.1.3: Cập nhật Polling Service cho Phiếu Xuất**
        *   **Người thực hiện:** 1 Lập trình viên
        *   **Hướng dẫn:**
            1.  Mở tệp `app/tasks/polling_service.py`.
            2.  Thêm hàm `find_phieu_xuat()` và gọi nó bên trong task `find_pending_invoices`.
                ```python
                # Thêm import ở đầu file
                from .phieu_xuat_worker import process_phieu_xuat_task

                # Sửa task find_pending_invoices
                @celery_app.task(name="tasks.find_pending_invoices")
                def find_pending_invoices():
                    """Quét tất cả các loại phiếu và đẩy vào hàng đợi tương ứng."""
                    logging.info("Bắt đầu quét các phiếu chờ xử lý...")
                    find_phieu_nhap()
                    find_phieu_xuat() // Thêm dòng này
                    # ...

                # Thêm hàm mới này vào cuối file
                def find_phieu_xuat():
                    """Tìm và đưa các phiếu xuất vào hàng đợi."""
                    conn = None
                    try:
                        conn = get_db_connection()
                        cursor = conn.cursor()
                        # Thay đổi tên bảng và cột ngày cho phù hợp
                        query = "SELECT ma_phieu FROM PhieuXuatHeader WHERE status_phieu IN (0, 2) ORDER BY ngay_xuat ASC"
                        cursor.execute(query)
                        rows = cursor.fetchall()
                        for row in rows:
                            ma_phieu = row[0]
                            logging.info(f"Đưa phiếu xuất '{ma_phieu}' vào hàng đợi 'phieu_xuat_queue'.")
                            # Gửi task đến đúng hàng đợi
                            process_phieu_xuat_task.apply_async(args=[ma_phieu], queue='phieu_xuat_queue')
                    except Exception as e:
                        logging.error(f"Lỗi khi quét phiếu xuất: {e}")
                    finally:
                        if conn:
                            conn.close()
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

    *   **Task 3.2.2: Tạo Worker xử lý Hóa Đơn Bán**
        *   **Người thực hiện:** 1 Lập trình viên
        *   **Hướng dẫn:**
            1.  Tạo tệp mới tại `app/tasks/hoa_don_worker.py`.
            2.  **Sao chép toàn bộ nội dung** từ tệp `app/tasks/phieu_nhap_worker.py`.
            3.  **Chỉnh sửa các điểm sau:**
                *   Đổi tên task: `@celery_app.task(..., name="tasks.process_hoa_don", ...)`
                *   Đổi tên hàm: `def process_hoa_don_task(self, ma_hoa_don: str):`
                *   Import model mới: `from app.models.hoa_don import ...`
                *   Câu lệnh SQL: Thay `PhieuNhap...` bằng `HoaDonHeader` và `HoaDonDetail`.
                *   Tạo Payload: Sử dụng `HoaDonPayloadModel`.
                *   Endpoint API: Gọi đến endpoint của hóa đơn (ví dụ: `/hoadon`).
                *   Cập nhật DB khi thành công: `UPDATE HoaDonHeader SET status_phieu = 1, ma_don_thuoc_quoc_gia = ? ...`
                *   Cập nhật DB khi lỗi: `UPDATE HoaDonHeader SET status_phieu = 2 (hoặc 3) ...`
                *   Ghi log: Thay đổi `type` thành `"HoaDon"`.

    *   **Task 3.2.3: Cập nhật Polling Service cho Hóa Đơn Bán**
        *   **Người thực hiện:** 1 Lập trình viên
        *   **Hướng dẫn:**
            1.  Mở tệp `app/tasks/polling_service.py`.
            2.  Thêm hàm `find_hoa_don()` và gọi nó bên trong task `find_pending_invoices`.
                ```python
                # Thêm import ở đầu file
                from .hoa_don_worker import process_hoa_don_task

                # Sửa task find_pending_invoices
                @celery_app.task(name="tasks.find_pending_invoices")
                def find_pending_invoices():
                    # ...
                    find_phieu_xuat()
                    find_hoa_don() // Thêm dòng này

                # Thêm hàm mới này vào cuối file
                def find_hoa_don():
                    """Tìm và đưa các hóa đơn bán vào hàng đợi."""
                    # Logic tương tự find_phieu_nhap, nhưng query bảng HoaDonHeader
                    # và gửi task đến hàng đợi 'hoa_don_queue'
                    # process_hoa_don_task.apply_async(args=[ma_hoa_don], queue='hoa_don_queue')