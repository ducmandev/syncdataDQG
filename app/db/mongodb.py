from pymongo import MongoClient
from app.core.config import settings
import logging
from datetime import datetime

client = None
db = None

def connect_to_mongo():
    """Khởi tạo kết nối đến MongoDB."""
    global client, db
    try:
        client = MongoClient(settings.MONGO_URI, serverSelectionTimeoutMS=5000)
        db = client[settings.MONGO_DB_NAME]
        client.server_info() # Kiểm tra kết nối
        logging.info("Kết nối MongoDB thành công.")
    except Exception as e:
        logging.error(f"Không thể kết nối đến MongoDB: {e}")
        client = None
        db = None

def get_mongo_db():
    """Trả về đối tượng database, kết nối lại nếu cần."""
    if client is None or db is None:
        connect_to_mongo()
    return db

def log_to_mongodb(log_data: dict):
    """Ghi một bản ghi log vào collection 'sync_logs'."""
    mongo_db = get_mongo_db()
    if mongo_db:
        try:
            log_data['timestamp'] = datetime.utcnow()
            mongo_db.sync_logs.insert_one(log_data)
        except Exception as e:
            logging.error(f"Lỗi khi ghi log vào MongoDB: {e}")

# Khởi tạo kết nối khi module được import
connect_to_mongo()
