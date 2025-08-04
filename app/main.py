from celery import Celery
from app.core.config import settings

# Xây dựng URL Redis từ settings cho broker và backend
redis_url = f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/0"

# Khởi tạo ứng dụng Celery
celery_app = Celery(
    "project_hermes",
    broker=redis_url,
    backend=redis_url,
    include=[
        # Chúng ta sẽ tạo các tệp này ở các task sau
        "app.tasks.polling_service",
        "app.tasks.phieu_nhap_worker",
        "app.tasks.phieu_xuat_worker",
        "app.tasks.hoa_don_worker",
    ],
)

# Cấu hình Celery tùy chọn
celery_app.conf.update(
    task_track_started=True,
)
