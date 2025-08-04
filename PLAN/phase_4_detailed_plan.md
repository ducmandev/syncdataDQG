# Kế hoạch Phát triển Chi tiết: Giai đoạn 4 - Hoàn thiện & Bàn giao (Phiên bản cập nhật)
**Mục tiêu:** Tái cấu trúc mã nguồn để tăng tính tái sử dụng, giảm lặp lại và tạo tài liệu bàn giao rõ ràng cho đội DevOps.
---
### **Task 4.1: Tái cấu trúc logic và Hoàn thiện các Worker**
*   **Mục tiêu:** Gom logic gọi API vào một lớp `PartnerAPIClient` duy nhất. Tạo các worker còn thiếu (`phiếu xuất`, `hóa đơn`) dựa trên worker đã có và cập nhật tất cả để sử dụng client mới.
*   **Người thực hiện:** 1 Lập trình viên
*   **Hướng dẫn:**
    1.  **Tạo API Client Tập trung:**
        *   Tạo tệp mới tại `app/clients/partner_api_client.py`.
        *   Dán đoạn mã sau vào tệp. Lớp này đóng gói tất cả các tương tác với API của đối tác.
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
                        raise
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
    2.  **Cập nhật và Tạo các Worker:**
        *   **Cập nhật `phieu_nhap_worker.py`:**
            *   Import client mới: `from app.clients.partner_api_client import partner_api_client`.
            *   Thay thế khối `with httpx.Client() as client: ...` bằng dòng gọi: `api_response = partner_api_client.submit_phieu_nhap(api_payload)`.
        *   **Tạo mới `phieu_xuat_worker.py` và Model:**
            *   Tạo tệp `app/tasks/phieu_xuat_worker.py` bằng cách sao chép và điều chỉnh từ `phieu_nhap_worker.py`.
            *   Tạo tệp model tương ứng `app/models/phieu_xuat.py`.
            *   Worker này sẽ gọi `partner_api_client.submit_phieu_xuat(api_payload)`.
        *   **Tạo mới `hoa_don_worker.py` và Model:**
            *   Tạo tệp `app/tasks/hoa_don_worker.py` tương tự.
            *   Tạo tệp model tương ứng `app/models/hoa_don.py`.
            *   Worker này sẽ gọi `partner_api_client.submit_hoa_don(api_payload)`.
---
### **Task 4.2: Viết tài liệu bàn giao (README.md)**
*   **Mục tiêu:** Tạo một tài liệu `README.md` toàn diện, hướng dẫn cách thiết lập, cấu hình và chạy dự án.
*   **Người thực hiện:** 1 Lập trình viên
*   **Hướng dẫn:**
    1.  Tạo tệp `README.md` ở thư mục gốc của dự án.
    2.  Điền đầy đủ nội dung theo mẫu đã cung cấp (bao gồm kiến trúc, cấu hình, hướng dẫn chạy...).