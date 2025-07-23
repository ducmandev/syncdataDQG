from src.api_clients.partner_nhap import PartnerNhapAPIClient
from src.core.models import PhieuNhapCreate
from .celery_app import celery_app
import logging

logger = logging.getLogger(__name__)

@celery_app.task(bind=True, max_retries=3)
def sync_phieu_nhap_task(self, phieu_nhap_data: dict):
    try:
        client = PartnerNhapAPIClient()
        phieu_nhap = PhieuNhapCreate(**phieu_nhap_data)
        result = client.create_phieu_nhap(phieu_nhap)
        return {"status": "success", "result": result}
    except Exception as e:
        logger.error(f"Lỗi đồng bộ phiếu nhập: {str(e)}")
        raise self.retry(exc=e)
@celery_app.task(bind=True, max_retries=3)
def sync_phieu_xuat_task(self, phieu_xuat_data: dict):
    try:
        from src.api_clients.partner_xuat import PartnerXuatAPIClient
        from src.core.models import PhieuXuatCreate
        client = PartnerXuatAPIClient()
        phieu_xuat = PhieuXuatCreate(**phieu_xuat_data)
        result = client.create_phieu_xuat(phieu_xuat)
        return {"status": "success", "result": result}
    except Exception as e:
        logger.error(f"Lỗi đồng bộ phiếu xuất: {str(e)}")
        raise self.retry(exc=e)

@celery_app.task(bind=True, max_retries=3)
def sync_hoa_don_task(self, hoa_don_data: dict):
    try:
        from src.api_clients.partner_hoadon import PartnerHoaDonAPIClient
        from src.core.models import HoaDonCreate
        client = PartnerHoaDonAPIClient()
        hoa_don = HoaDonCreate(**hoa_don_data)
        result = client.create_hoa_don(hoa_don)
        return {"status": "success", "result": result}
    except Exception as e:
        logger.error(f"Lỗi đồng bộ hóa đơn: {str(e)}")
        raise self.retry(exc=e)