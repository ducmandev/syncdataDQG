import requests
from src.core.models import HoaDonCreate
from config.settings import settings
from requests.exceptions import HTTPError

class PartnerHoaDonAPIClient:
    def __init__(self):
        self.base_url = settings.PARTNER_API_URL
        self.api_key = settings.PARTNER_API_KEY
        self.timeout = settings.API_TIMEOUT

    def create_hoa_don(self, data: HoaDonCreate) -> dict:
        headers = {"Authorization": f"Bearer {self.api_key}"}
        try:
            response = requests.post(
                f"{self.base_url}/hoa-don",
                json=data.model_dump(),
                headers=headers,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except HTTPError as e:
            if e.response.status_code == 429:
                raise Exception("Quá nhiều request") from e
            raise