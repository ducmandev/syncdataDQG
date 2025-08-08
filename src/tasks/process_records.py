# src/tasks/process_records.py
from src.celery_app import celery_app, db
from src.database import get_new_records
import json
from datetime import datetime

@celery_app.task(name="process_record_task", bind=True, autoretry_for=(Exception,), retry_backoff=True, max_retries=3)
def process_record_task(self, record_data: dict, record_type: str):
    """
    Task xử lý logic cho một bản ghi.
    - Cập nhật trạng thái log trong MongoDB.
    - Gọi API đối tác (giả lập).
    - Xử lý lỗi và tự động retry.
    - Lưu trạng thái SUCCESS/FAILED vào MongoDB.
    """
    from datetime import datetime
    import requests

    task_id = self.request.id
    record_id = record_data.get("id")
    db.processing_logs.update_one(
        {"record_id": record_id, "record_type": record_type},
        {"$set": {"status": "PROCESSING", "task_id": str(task_id), "started_at": datetime.utcnow()}}
    )
    print(f"[{task_id}] Started processing {record_type} record: {record_id}")

    try:
        # Giả lập gọi API đối tác (thay bằng endpoint thực tế)
        api_url = "https://mockapi.example.com/partner/process"
        api_key = os.getenv("PARTNER_API_KEY", "demo-key")
        response = requests.post(
            api_url,
            json={"record": record_data, "type": record_type},
            headers={"Authorization": f"Bearer {api_key}"}
        )
        response.raise_for_status()
        result = response.json()
        db.processing_logs.update_one(
            {"record_id": record_id, "record_type": record_type},
            {"$set": {
                "status": "SUCCESS",
                "result": result,
                "finished_at": datetime.utcnow()
            }}
        )
        print(f"[{task_id}] SUCCESS for {record_type} record: {record_id}")
        return f"SUCCESS: {record_id}"
    except Exception as e:
        db.processing_logs.update_one(
            {"record_id": record_id, "record_type": record_type},
            {"$set": {
                "status": "FAILED",
                "error": str(e),
                "finished_at": datetime.utcnow()
            }}
        )
        print(f"[{task_id}] FAILED for {record_type} record: {record_id} - {e}")
        raise

@celery_app.task(name="poll_new_hoadonheader")
def poll_new_hoadonheader():
    """
    Polls HoaDonHeader for new invoices (status_phieu=0, ngay_ban=today).
    Deduplicates using MongoDB and queues process_record_task.
    """
    from datetime import date
    today = date.today().isoformat()
    candidate_records = get_new_records(
        table_name="HoaDonHeader",
        date_column="ngay_ban"
    )
    tasks_created_count = 0
    for record in candidate_records:
        if record.get("status_phieu") != 0 or str(record.get("ngay_ban")) != today:
            continue
        record_id = record.get("id")
        record_type = "HoaDonHeader"
        log_entry = db.processing_logs.find_one_and_update(
            {"record_id": record_id, "record_type": record_type},
            {"$setOnInsert": {
                "status": "QUEUED",
                "created_at": datetime.utcnow(),
                "data": record
            }},
            upsert=True,
            return_document=True
        )
        if log_entry and log_entry.get("status") == "QUEUED":
            process_record_task.delay(record, record_type)
            tasks_created_count += 1
    return f"Queued {tasks_created_count} new HoaDonHeader records."

@celery_app.task(name="poll_new_hoadondetail")
def poll_new_hoadondetail():
    """
    Polls HoaDonDetail for new invoice details (status_phieu=0, ngay_ban=today).
    Deduplicates using MongoDB and queues process_record_task.
    """
    from datetime import date
    today = date.today().isoformat()
    candidate_records = get_new_records(
        table_name="HoaDonDetail",
        date_column="ngay_ban"
    )
    tasks_created_count = 0
    for record in candidate_records:
        if record.get("status_phieu") != 0 or str(record.get("ngay_ban")) != today:
            continue
        record_id = record.get("id")
        record_type = "HoaDonDetail"
        log_entry = db.processing_logs.find_one_and_update(
            {"record_id": record_id, "record_type": record_type},
            {"$setOnInsert": {
                "status": "QUEUED",
                "created_at": datetime.utcnow(),
                "data": record
            }},
            upsert=True,
            return_document=True
        )
        if log_entry and log_entry.get("status") == "QUEUED":
            process_record_task.delay(record, record_type)
            tasks_created_count += 1
    return f"Queued {tasks_created_count} new HoaDonDetail records."
@celery_app.task(name="collect_successful_tasks")
def collect_successful_tasks():
    """
    Tổng hợp các bản ghi SUCCESS và lưu báo cáo vào MongoDB (collection: reports).
    """
    from datetime import datetime
    today = datetime.utcnow().date().isoformat()
    successful_logs = list(db.processing_logs.find({"status": "SUCCESS", "finished_at": {"$gte": today}}))
    report = {
        "date": today,
        "total_success": len(successful_logs),
        "records": successful_logs,
        "created_at": datetime.utcnow()
    }
    db.reports.insert_one(report)
    print(f"Report for {today} saved with {len(successful_logs)} successful records.")
    return f"Report saved for {today}."

@celery_app.task(name="cleanup_old_logs")
def cleanup_old_logs(days: int = 7):
    """
    Xóa các bản ghi SUCCESS đã cũ hơn số ngày chỉ định (mặc định 7 ngày).
    """
    from datetime import datetime, timedelta
    threshold = datetime.utcnow() - timedelta(days=days)
    result = db.processing_logs.delete_many({
        "status": "SUCCESS",
        "finished_at": {"$lt": threshold}
    })
    print(f"Deleted {result.deleted_count} old SUCCESS logs.")
    return f"Deleted {result.deleted_count} old SUCCESS logs."