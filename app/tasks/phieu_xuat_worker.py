from app.clients.partner_api_client import partner_api_client
import logging
from app.main import celery_app
from app.core.config import settings
from app.db.mssql import get_db_connection
from app.db.mongodb import log_to_mongodb
from app.models.phieu_xuat import PhieuXuatDetailModel, PhieuXuatPayloadModel

@celery_app.task(bind=True, name="tasks.process_phieu_xuat", max_retries=3, default_retry_delay=60)
def process_phieu_xuat_task(self, payload: dict):
    """
    Xử lý một phiếu xuất duy nhất: nhận payload đã chuẩn bị, gọi API, cập nhật kết quả.
    Không fetch dữ liệu từ DB.
    """
    ma_phieu = payload.get("ma_phieu")
    log_prefix = f"[Phiếu Xuất {ma_phieu}]"
    logging.info(f"{log_prefix} Bắt đầu xử lý với payload đã chuẩn bị.")

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Ghi log xử lý vào MongoDB
        log_to_mongodb({
            "ma_phieu": ma_phieu, "type": "PhieuXuat", "status": "PROCESSING",
            "attempt": self.request.retries + 1, "payload": payload
        })
        # Gọi API đối tác
        api_response = partner_api_client.submit_phieu_xuat(payload)
        # Xử lý thành công
        ma_phieu_qg = api_response.get("ma_phieu_xuat_quoc_gia")
        cursor.execute(
            "UPDATE PhieuXuatHeader SET status_phieu = 1, ma_phieu_xuat_quoc_gia = ?, note_log = 'Success' WHERE ma_phieu = ?",
            ma_phieu_qg, ma_phieu
        )
        conn.commit()
        logging.info(f"{log_prefix} Đồng bộ thành công.")
        log_to_mongodb({
            "ma_phieu": ma_phieu, "type": "PhieuXuat", "status": "SUCCESS",
            "response": api_response
        })
    except Exception as exc:
        error_details = f"Lỗi không xác định: {str(exc)}"
        logging.error(f"{log_prefix} {error_details}")
        cursor.execute("UPDATE PhieuXuatHeader SET status_phieu = 2, note_log = ? WHERE ma_phieu = ?", error_details, ma_phieu)
        conn.commit()
        log_to_mongodb({"ma_phieu": ma_phieu, "type": "PhieuXuat", "status": "FAILED_RETRYING", "error": error_details})
        raise self.retry(exc=exc)
    finally:
        if conn:
            conn.close()