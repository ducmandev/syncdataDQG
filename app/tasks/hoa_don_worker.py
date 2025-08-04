from app.clients.partner_api_client import partner_api_client
import logging
from app.main import celery_app
from app.core.config import settings
from app.db.mssql import get_db_connection
from app.db.mongodb import log_to_mongodb
from app.models.hoa_don import HoaDonDetailModel, HoaDonPayloadModel

@celery_app.task(bind=True, name="tasks.process_hoa_don_task", max_retries=3, default_retry_delay=60)
def process_hoa_don_task(self, payload: dict):
    """
    Xử lý một hóa đơn bán duy nhất: nhận payload đã chuẩn bị, gọi API, cập nhật kết quả.
    Không fetch dữ liệu từ DB.
    """
    ma_hoa_don = payload.get("ma_hoa_don")
    log_prefix = f"[Hóa Đơn Bán {ma_hoa_don}]"
    logging.info(f"{log_prefix} Bắt đầu xử lý với payload đã chuẩn bị.")

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Ghi log xử lý vào MongoDB
        log_to_mongodb({
            "ma_hoa_don": ma_hoa_don, "type": "HoaDon", "status": "PROCESSING",
            "attempt": self.request.retries + 1, "payload": payload
        })
        # Gọi API đối tác
        api_response = partner_api_client.submit_hoa_don(payload)
        # Xử lý thành công
        ma_hoa_don_qg = api_response.get("ma_hoa_don_quoc_gia")
        cursor.execute(
            "UPDATE HoaDonHeader SET status_hoa_don = 1, ma_hoa_don_quoc_gia = ?, note_log = 'Success' WHERE ma_hoa_don = ?",
            ma_hoa_don_qg, ma_hoa_don
        )
        conn.commit()
        logging.info(f"{log_prefix} Đồng bộ thành công.")
        log_to_mongodb({
            "ma_hoa_don": ma_hoa_don, "type": "HoaDon", "status": "SUCCESS",
            "response": api_response
        })
    except Exception as exc:
        error_details = f"Lỗi không xác định: {str(exc)}"
        logging.error(f"{log_prefix} {error_details}")
        cursor.execute("UPDATE HoaDonHeader SET status_hoa_don = 2, note_log = ? WHERE ma_hoa_don = ?", error_details, ma_hoa_don)
        conn.commit()
        log_to_mongodb({"ma_hoa_don": ma_hoa_don, "type": "HoaDon", "status": "FAILED_RETRYING", "error": error_details})
        raise self.retry(exc=exc)
    finally:
        if conn:
            conn.close()