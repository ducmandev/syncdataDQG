from saler.celery_app import app
from common.services.api_client import api_client
from common.database.mssql_client import mssql_client
from common.database.mongo_client import mongo_client
from common.models.pydantic_models import SalesInvoice, SalesInvoiceDetail
import traceback

@app.task(name='sale.process_sale', bind=True)
def process_sale(self, local_invoice_id: str, shop_id: str):
    """
    Task to process a single sales invoice. It fetches, transforms, sends,
    and updates the status of the invoice.
    """
    try:
        print(f"Processing sale invoice: {local_invoice_id} for shop: {shop_id}")
        
        # 1. Fetch full data from MSSQL
        header, details_rows = mssql_client.fetch_sale_by_id(local_invoice_id)
        if not header:
            print(f"Invoice {local_invoice_id} not found.")
            return

        # 2. Transform data using Pydantic models
        detail_models = [
            SalesInvoiceDetail(
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
        
        invoice_model = SalesInvoice(
            ma_hoa_don=header.local_invoice_id,
            ma_co_so=header.pharmacy_code,
            ngay_ban=header.sale_date.strftime('%Y%m%d'),
            hoa_don_chi_tiet=detail_models,
            ma_don_thuoc_quoc_gia=header.national_prescription_id,
            ho_ten_nguoi_ban=header.seller_name,
            ho_ten_khach_hang=header.customer_name
        )

        # 3. Send data via API client
        api_response = api_client.send_sales_invoice(shop_id, invoice_model)

        # 4. On success, update status in all databases
        national_id = api_response.get('ma_hoa_don')
        mssql_client.update_sale_status(local_invoice_id, 'SYNC_SUCCESS', national_id)
        mongo_client.update_task_log_status(self.request.id, 'SUCCESS')
        print(f"Successfully synced invoice {local_invoice_id}.")

    except Exception as e:
        # 5. On final failure, update status and log detailed error
        print(f"CRITICAL: Final failure for invoice {local_invoice_id}. Error: {e}")
        mssql_client.update_sale_status(local_invoice_id, 'SYNC_FAILED')
        mongo_client.log_sync_failure(
            business_id=local_invoice_id,
            payload=invoice_model.model_dump(),
            error=traceback.format_exc(),
            queue='sale_queue'
        )
        mongo_client.update_task_log_status(self.request.id, 'FAILED')