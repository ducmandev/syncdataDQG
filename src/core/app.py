import logging
from src.workers.celery_app import celery_app
from src.workers import tasks

class CoreService:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
    
    def run(self):
        self.logger.info("Core service started")
        # Giữ service chạy
        while True:
            pass

def process_incoming_phieu_nhap(data: dict):
    tasks.sync_phieu_nhap_task.delay(data)
def process_incoming_phieu_xuat(data: dict):
    tasks.sync_phieu_xuat_task.delay(data)

def process_incoming_hoa_don(data: dict):
    tasks.sync_hoa_don_task.delay(data)