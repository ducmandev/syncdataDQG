# src/database.py
import os
import pyodbc
from dotenv import load_dotenv
load_dotenv()

class MSSQL:
    def __init__(self):
        self.server = os.getenv("MSSQL_SERVER")
        self.database = os.getenv("MSSQL_DATABASE")
        self.user = os.getenv("MSSQL_USER")
        self.password = os.getenv("MSSQL_PASSWORD")
        self.driver = os.getenv("MSSQL_DRIVER")
        self.conn_str = (
            f"DRIVER={self.driver};SERVER={self.server};DATABASE={self.database};"
            f"UID={self.user};PWD={self.password}"
        )
        self.conn = None

    def __enter__(self):
        self.conn = pyodbc.connect(self.conn_str)
        return self.conn

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.conn:
            self.conn.close()

def get_new_records(table_name: str, date_column: str, batch_size: int = 100):
    """
    Truy vấn (SELECT) các bản ghi mới trong ngày từ MSSQL.
    Chỉ lấy các bản ghi có status = 'PENDING_SYNC'.
    """
    records = []
    query = f"""
    SELECT TOP {batch_size} *
    FROM {table_name}
    WHERE status = 'PENDING_SYNC'
      AND {date_column} >= CAST(GETDATE() AS DATE)
    ORDER BY {date_column} ASC;
    """
    try:
        with MSSQL() as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            rows = cursor.fetchall()
            columns = [column[0] for column in cursor.description]
            for row in rows:
                records.append(dict(zip(columns, row)))
    except pyodbc.Error as e:
        print(f"Database error fetching new records from {table_name}: {e}")
    return records