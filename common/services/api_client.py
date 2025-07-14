import httpx
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type
from common.config import settings
from common.database.redis_client import redis_client
from common.models.pydantic_models import LoginRequest, LoginResponse, SalesInvoice

class ApiClient:
    def __init__(self):
        self.base_url = settings.API_BASE_URL
        self.client = httpx.Client()

    @retry(stop=stop_after_attempt(5), wait=wait_fixed(2), retry=retry_if_exception_type(httpx.RequestError))
    def _login(self, shop_id: str) -> str:
        """Logs in to get a new token. Retries on failure."""
        # In a real app, you'd fetch shop-specific credentials from a secure source
        # For this implementation, we use the global credentials from settings
        login_data = LoginRequest(usr=settings.API_USERNAME, pwd=settings.API_PASSWORD)
        
        print(f"Attempting login for shop_id: {shop_id}...")
        response = self.client.post(f"{self.base_url}/api/tai_khoan/dang_nhap", json=login_data.model_dump())
        
        response.raise_for_status() # Will raise an exception for 4xx/5xx statuses
        
        token_data = LoginResponse(**response.json())
        redis_client.set_token(shop_id, token_data.token)
        print(f"Login successful for shop_id: {shop_id}. Token cached.")
        return token_data.token

    def _get_auth_token(self, shop_id: str) -> str:
        """Gets token from cache or triggers a new login."""
        token = redis_client.get_token(shop_id)
        if not token:
            print(f"No token found in cache for shop_id: {shop_id}. Initiating new login.")
            token = self._login(shop_id)
        return token

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(3), retry=retry_if_exception_type(httpx.RequestError))
    def send_sales_invoice(self, shop_id: str, invoice_data: SalesInvoice):
        """Sends sales invoice data with authorization and retry logic."""
        token = self._get_auth_token(shop_id)
        headers = {"Authorization": f"Bearer {token}"}
        
        try:
            print(f"Sending sales invoice {invoice_data.ma_hoa_don} for shop {shop_id}...")
            response = self.client.post(
                f"{self.base_url}/api/lien_thong/hoa_don",
                json=invoice_data.model_dump(),
                headers=headers
            )
            
            # If token expired (401), force a new login and retry the request once immediately.
            if response.status_code == 401:
                print(f"Token expired for shop {shop_id}. Forcing new login and retrying.")
                token = self._login(shop_id) # Force new login
                headers = {"Authorization": f"Bearer {token}"}
                response = self.client.post(f"{self.base_url}/api/lien_thong/hoa_don", json=invoice_data.model_dump(), headers=headers)
            
            response.raise_for_status()
            print(f"Successfully sent sales invoice {invoice_data.ma_hoa_don}.")
            return response.json()
        except httpx.HTTPStatusError as e:
            print(f"Failed to send invoice {invoice_data.ma_hoa_don} after retries: {e}")
            # The exception will be caught by the Celery task for final failure logging.
            raise

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(3), retry=retry_if_exception_type(httpx.RequestError))
    def send_purchase_receipt(self, shop_id: str, receipt_data):
        """Sends purchase receipt data."""
        token = self._get_auth_token(shop_id)
        headers = {"Authorization": f"Bearer {token}"}
        try:
            response = self.client.post(f"{self.base_url}/api/lien_thong/phieu_nhap", json=receipt_data.model_dump(), headers=headers)
            if response.status_code == 401:
                token = self._login(shop_id)
                headers = {"Authorization": f"Bearer {token}"}
                response = self.client.post(f"{self.base_url}/api/lien_thong/phieu_nhap", json=receipt_data.model_dump(), headers=headers)
            response.raise_for_status()
            return response.text.strip('"')
        except httpx.HTTPStatusError as e:
            raise

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(3), retry=retry_if_exception_type(httpx.RequestError))
    def send_goods_issue(self, shop_id: str, slip_data):
        """Sends goods issue slip data."""
        token = self._get_auth_token(shop_id)
        headers = {"Authorization": f"Bearer {token}"}
        try:
            response = self.client.post(f"{self.base_url}/api/lien_thong/phieu_xuat", json=slip_data.model_dump(), headers=headers)
            if response.status_code == 401:
                token = self._login(shop_id)
                headers = {"Authorization": f"Bearer {token}"}
                response = self.client.post(f"{self.base_url}/api/lien_thong/phieu_xuat", json=slip_data.model_dump(), headers=headers)
            response.raise_for_status()
            return response.text.strip('"')
        except httpx.HTTPStatusError as e:
            raise

api_client = ApiClient()