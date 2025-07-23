import pyodbc
from common.config import settings

print("=== Test 1: Hardcoded connection ===")
conn_str1 = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=localhost;"
    "DATABASE=test_db;"
    "UID=sa;"
    "PWD=YourStrong!Passw0rd"
)
try:
    conn1 = pyodbc.connect(conn_str1, timeout=5)
    print("Test 1: Kết nối MSSQL thành công!")
    conn1.close()
except Exception as e:
    print("Test 1: Kết nối MSSQL thất bại:", e)

print("\n=== Test 2: Config from common.config ===")
print("MSSQL_SERVER:", settings.MSSQL_SERVER)
print("MSSQL_USER:", settings.MSSQL_USER)
print("MSSQL_PASSWORD:", settings.MSSQL_PASSWORD)
print("MSSQL_DATABASE:", settings.MSSQL_DATABASE)
print("MSSQL_DRIVER:", settings.MSSQL_DRIVER)
conn_str2 = (
    f"DRIVER={settings.MSSQL_DRIVER};"
    f"SERVER={settings.MSSQL_SERVER};"
    f"DATABASE={settings.MSSQL_DATABASE};"
    f"UID={settings.MSSQL_USER};"
    f"PWD={settings.MSSQL_PASSWORD}"
)
try:
    conn2 = pyodbc.connect(conn_str2, timeout=5)
    print("Test 2: Kết nối MSSQL thành công!")
    conn2.close()
except Exception as e:
    print("Test 2: Kết nối MSSQL thất bại:", e)
