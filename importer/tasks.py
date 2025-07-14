from importer.celery_app import app
from common.services.api_client import api_client
from common.database.mssql_client import mssql_client
from common.database.mongo_client import mongo_client
from common.models.pydantic_models import PurchaseReceipt, PurchaseReceiptDetail
import traceback

@app.task(name='import.process_import', bind=True)
def process_import(self, local_receipt_id: str, shop_id: str):
    """
    Task to process a single purchase receipt. It fetches, transforms, sends,
    and updates the status of the receipt.
    """
    try:
        print(f"Processing import receipt: {local_receipt_id} for shop: {shop_id}")

        # 1. Fetch full data from MSSQL
        header, details_rows = mssql_client.fetch_import_by_id(local_receipt_id)
        if not header:
            print(f"Receipt {local_receipt_id} not found.")
            return

        # 2. Transform data using Pydantic models
        detail_models = [
            PurchaseReceiptDetail(
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

        receipt_model = PurchaseReceipt(
            ma_phieu_nhap=header.local_receipt_id,
            ma_co_so=header.shop_pharmacy_code,
            ngay_nhap=header.receipt_date.strftime('%Y%m%d'),
            phieu_nhap_chi_tiet=detail_models,
            ma_phieu_nhap_quoc_gia=header.national_receipt_id,
            ho_ten_nguoi_nhap=header.importer_name,
            ho_ten_nha_cung_cap=header.supplier_name
        )

        # 3. Send data via API client
        national_id = api_client.send_purchase_receipt(shop_id, receipt_model)

        # 4. On success, update status in all databases
        mssql_client.update_import_status(local_receipt_id, 'SYNC_SUCCESS', national_id)
        mongo_client.update_task_log_status(self.request.id, 'SUCCESS')
        print(f"Successfully synced import receipt {local_receipt_id}.")

    except Exception as e:
        # 5. On final failure, update status and log detailed error
        print(f"CRITICAL: Final failure for import receipt {local_receipt_id}. Error: {e}")
        mssql_client.update_import_status(local_receipt_id, 'SYNC_FAILED')
        mongo_client.log_sync_failure(
            business_id=local_receipt_id,
            payload=receipt_model.model_dump() if 'receipt_model' in locals() else {},
            error=traceback.format_exc(),
            queue='import_queue'
        )
        mongo_client.update_task_log_status(self.request.id, 'FAILED')