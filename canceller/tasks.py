from canceller.celery_app import app
from common.services.api_client import api_client
from common.database.mssql_client import mssql_client
from common.database.mongo_client import mongo_client
from common.models.pydantic_models import GoodsIssueSlip, GoodsIssueSlipDetail
import traceback

@app.task(name='cancellation.process_cancellation', bind=True)
def process_cancellation(self, local_slip_id: str, shop_id: str):
    """
    Task to process a single goods issue slip cancellation. It fetches, transforms, sends,
    and updates the status of the slip.
    """
    try:
        print(f"Processing cancellation slip: {local_slip_id} for shop: {shop_id}")

        # 1. Fetch full data from MSSQL
        header, details_rows = mssql_client.fetch_cancellation_by_id(local_slip_id)
        if not header:
            print(f"Goods issue slip {local_slip_id} not found.")
            return

        # 2. Transform data using Pydantic models
        detail_models = [
            GoodsIssueSlipDetail(
                ma_thuoc=row.drug_code,
                ten_thuoc=row.drug_name,
                so_lo=row.lot_number,
                han_dung=row.expiry_date.strftime('%Y%m%d'),
                don_vi_tinh=row.unit,
                ham_luong=row.concentration,
                so_luong=float(row.quantity),
                don_gia=float(row.unit_price),
                thanh_tien=float(row.line_total),
                ty_le_quy_doi=float(row.conversion_ratio),
                lieu_dung=row.dosage,
                so_dang_ky=row.registration_number,
                ngay_san_xuat=row.production_date.strftime('%Y%m%d') if row.production_date else None,
                duong_dung=row.route_of_administration
            ) for row in details_rows
        ]

        slip_model = GoodsIssueSlip(
            ma_phieu_xuat=header.local_slip_id,
            ma_co_so=header.shop_pharmacy_code,
            ngay_xuat=header.slip_date.strftime('%Y%m%d'),
            phieu_xuat_chi_tiet=detail_models,
            ma_phieu_xuat_quoc_gia=header.national_slip_id,
            ho_ten_nguoi_xuat=header.issuer_name,
            ho_ten_nguoi_nhan=header.receiver_name
        )

        # 3. Send data via API client
        national_id = api_client.send_goods_issue(shop_id, slip_model)

        # 4. On success, update status in all databases
        mssql_client.update_cancellation_status(local_slip_id, 'SYNC_SUCCESS', national_id)
        mongo_client.update_task_log_status(self.request.id, 'SUCCESS')
        print(f"Successfully synced cancellation slip {local_slip_id}.")

    except Exception as e:
        # 5. On final failure, update status and log detailed error
        print(f"CRITICAL: Final failure for cancellation slip {local_slip_id}. Error: {e}")
        mssql_client.update_cancellation_status(local_slip_id, 'SYNC_FAILED')
        mongo_client.log_sync_failure(
            business_id=local_slip_id,
            payload=slip_model.model_dump() if 'slip_model' in locals() else {},
            error=traceback.format_exc(),
            queue='cancellation_queue'
        )
        mongo_client.update_task_log_status(self.request.id, 'FAILED')