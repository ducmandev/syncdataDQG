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