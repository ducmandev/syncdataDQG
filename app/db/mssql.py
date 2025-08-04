import pyodbc
from app.core.config import settings
import logging

# Xây dựng chuỗi kết nối từ settings
CONN_STR = (
    f"DRIVER={{{settings.MSSQL_DRIVER}}};"
    f"SERVER={settings.MSSQL_SERVER};"
    f"DATABASE={settings.MSSQL_DATABASE};"
    f"UID={settings.MSSQL_USER};"
    f"PWD={settings.MSSQL_PASSWORD};"
)

def get_db_connection():
    """Tạo và trả về một kết nối mới đến SQL Server."""
    try:
        conn = pyodbc.connect(CONN_STR)
        return conn
    except pyodbc.Error as ex:
        sqlstate = ex.args[0]
        logging.error(f"Lỗi kết nối SQL Server: {sqlstate}")
        raise

def get_db_cursor():
    """Tạo và trả về một cursor mới đến SQL Server, xử lý lỗi kết nối."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        return cursor
    except pyodbc.Error as ex:
        logging.error(f"Lỗi khi lấy cursor SQL Server: {ex}")
        raise
