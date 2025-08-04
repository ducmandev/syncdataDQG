from pydantic_settings import BaseSettings
from pydantic import Field
import os

# Đảm bảo tìm thấy tệp .env từ thư mục gốc của dự án
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env')

class Settings(BaseSettings):
    # Cấu hình Redis
    REDIS_HOST: str
    REDIS_PORT: int

    # Cấu hình MongoDB
    MONGO_URI: str
    MONGO_DB_NAME: str

    # Cấu hình Microsoft SQL Server
    MSSQL_SERVER: str
    MSSQL_DATABASE: str
    MSSQL_USER: str
    MSSQL_PASSWORD: str
    MSSQL_DRIVER: str = Field(default="{ODBC Driver 17 for SQL Server}")

    # Cấu hình API Đối tác
    API_BASE_URL: str
    API_USERNAME: str
    API_PASSWORD: str

    class Config:
        env_file = env_path
        env_file_encoding = 'utf-8'
        extra = 'ignore'

# Tạo một đối tượng settings duy nhất để các module khác import
settings = Settings()
