from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Redis Configuration
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379

    # MongoDB Configuration
    MONGO_URI: str = "mongodb://localhost:27017/"
    MONGO_DB_NAME: str = "sync_data_logs"

    # MSSQL Configuration
    MSSQL_SERVER: str
    MSSQL_DATABASE: str
    MSSQL_USER: str
    MSSQL_PASSWORD: str
    MSSQL_DRIVER: str = "{ODBC Driver 17 for SQL Server}"

    # National API Configuration
    API_BASE_URL: str
    API_USERNAME: str
    API_PASSWORD: str

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()