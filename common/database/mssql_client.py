import pyodbc
from common.config import settings

class MSSQLClient:
    def __init__(self):
        self.conn_str = (
            f"DRIVER={settings.MSSQL_DRIVER};"
            f"SERVER={settings.MSSQL_SERVER};"
            f"DATABASE={settings.MSSQL_DATABASE};"
            f"UID={settings.MSSQL_USER};"
            f"PWD={settings.MSSQL_PASSWORD};"
        )
        self.connection = pyodbc.connect(self.conn_str)

    def fetch_pending_sales(self):
        cursor = self.connection.cursor()
        cursor.execute("SELECT local_invoice_id, shop_pharmacy_code FROM SalesInvoices WHERE status = 'PENDING_SYNC'")
        return cursor.fetchall()

    def fetch_pending_imports(self):
        cursor = self.connection.cursor()
        cursor.execute("SELECT local_receipt_id, shop_pharmacy_code FROM PurchaseReceipts WHERE status = 'PENDING_SYNC'")
        return cursor.fetchall()

    def fetch_import_by_id(self, local_receipt_id: str):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM PurchaseReceipts WHERE local_receipt_id = ?", local_receipt_id)
        header = cursor.fetchone()
        cursor.execute("SELECT * FROM PurchaseReceiptDetails WHERE purchase_receipt_id = ?", header.id)
        details = cursor.fetchall()
        return header, details

    def update_import_status(self, local_receipt_id: str, status: str, national_id: str = None):
        cursor = self.connection.cursor()
        if national_id:
            cursor.execute("UPDATE PurchaseReceipts SET status = ?, national_receipt_id = ? WHERE local_receipt_id = ?", status, national_id, local_receipt_id)
        else:
            cursor.execute("UPDATE PurchaseReceipts SET status = ? WHERE local_receipt_id = ?", status, local_receipt_id)
        self.connection.commit()

    def fetch_pending_cancellations(self):
        cursor = self.connection.cursor()
        cursor.execute("SELECT local_slip_id, shop_pharmacy_code FROM GoodsIssueSlips WHERE status = 'PENDING_SYNC'")
        return cursor.fetchall()

    def fetch_cancellation_by_id(self, local_slip_id: str):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM GoodsIssueSlips WHERE local_slip_id = ?", local_slip_id)
        header = cursor.fetchone()
        cursor.execute("SELECT * FROM GoodsIssueSlipDetails WHERE goods_issue_slip_id = ?", header.id)
        details = cursor.fetchall()
        return header, details

    def update_cancellation_status(self, local_slip_id: str, status: str, national_id: str = None):
        cursor = self.connection.cursor()
        if national_id:
            cursor.execute("UPDATE GoodsIssueSlips SET status = ?, national_slip_id = ? WHERE local_slip_id = ?", status, national_id, local_slip_id)
        else:
            cursor.execute("UPDATE GoodsIssueSlips SET status = ? WHERE local_slip_id = ?", status, local_slip_id)
        self.connection.commit()

    def fetch_sale_by_id(self, local_invoice_id: str):
        """Fetches the header and details for a single sales invoice."""
        cursor = self.connection.cursor()
        # Fetch header
        cursor.execute("SELECT * FROM SalesInvoices WHERE local_invoice_id = ?", local_invoice_id)
        header = cursor.fetchone()
        # Fetch details
        cursor.execute("SELECT * FROM SalesInvoiceDetails WHERE sales_invoice_id = ?", header.id)
        details = cursor.fetchall()
        return header, details

    def update_sale_status(self, local_invoice_id: str, status: str, national_id: str = None):
        """Updates the status and national_id of a sales invoice."""
        cursor = self.connection.cursor()
        if national_id:
            cursor.execute("UPDATE SalesInvoices SET status = ?, national_invoice_id = ? WHERE local_invoice_id = ?", status, national_id, local_invoice_id)
        else:
            cursor.execute("UPDATE SalesInvoices SET status = ? WHERE local_invoice_id = ?", status, local_invoice_id)
        self.connection.commit()

mssql_client = MSSQLClient()