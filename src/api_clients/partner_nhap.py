import requests
from src.core.models import PhieuNhapCreate
from config.settings import settings
from requests.exceptions import HTTPError

class PartnerNhapAPIClient:
    def __init__(self):
        self.base_url = settings.PARTNER_API_URL
        self.api_key = settings.PARTNER_API_KEY
        self.timeout = settings.API_TIMEOUT

    def create_phieu_nhap(self, data: PhieuNhapCreate) -> dict:
        headers = {"Authorization": f"Bearer {self.api_key}"}
        try:
            response = requests.post(
                f"{self.base_url}/phieu-nhap",
                json=data.model_dump(),
                headers=headers,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except HTTPError as e:
            # Xử lý lỗi API
            if e.response.status_code == 429:
                raise Exception("Quá nhiều request") from e
            raise