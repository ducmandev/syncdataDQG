# Kế hoạch Chi tiết - Phase 1: Thiết lập Nền tảng
**Mục tiêu:** Xây dựng và xác minh "bộ xương" của ứng dụng, đảm bảo các thành phần cốt lõi (Celery, Redis, MongoDB) có thể kết nối và giao tiếp với nhau. Toàn bộ giai đoạn này chỉ tập trung vào việc thiết lập và cấu hình, không chứa logic nghiệp vụ.
**Kết quả đầu ra (Deliverables):**
1.  Một cấu trúc thư mục hoàn chỉnh cho ứng dụng.
2.  File `.env` được định nghĩa với các biến môi trường cần thiết.
3.  Các file Python được thiết kế (chưa code) để khởi tạo và cấu hình Celery.
4.  Một kịch bản vận hành chi tiết để xác minh toàn bộ hệ thống hoạt động.
---
### **Bước 1: Thiết kế Cấu trúc Thư mục**
Cấu trúc thư mục được đề xuất sẽ tích hợp gọn gàng vào dự án hiện tại của bạn. Thư mục `app` sẽ chứa logic chính của ứng dụng Celery.
```
syncdataDQG/
├── .dockerignore
├── .env                  <-- Sẽ được định nghĩa chi tiết
├── .gitignore
├── app/                  <-- THƯ MỤC MỚI: Chứa logic ứng dụng
│   ├── __init__.py       <-- File trống để biến `app` thành một Python package
│   ├── celery_app.py     <-- File khởi tạo và cấu hình Celery
│   └── tasks.py          <-- Nơi định nghĩa các Celery tasks
├── database.sql
├── docker-compose.app.yml
├── docker-compose.data.yml
├── docker-compose.yml
├── Dockerfile
├── InfoTable.md
├── ListAPI.md
├── mock_api/
├── PLAN.md
├── README.md
├── RELEASE.md
├── requirements.txt
└── run_verification.py   <-- FILE MỚI: Script để kiểm tra hoạt động của Phase 1
```
---
### **Bước 2: Chi tiết Kế hoạch cho từng File**
#### **2.1. File `.env`**
*   **Mục đích:** Lưu trữ các thông tin cấu hình và chuỗi kết nối nhạy cảm, tách biệt khỏi mã nguồn.
*   **Kế hoạch:** File này sẽ chứa các biến sau, sử dụng cho kết nối tới Redis và MongoDB đang chạy trong Docker.
    ```ini
    # URL kết nối tới Redis, server:port/database_number
    REDIS_URL=redis://localhost:6379/0
    # URL kết nối tới MongoDB, nơi lưu trữ kết quả của các task
    MONGO_URL=mongodb://localhost:27017/celery_results
    ```
#### **2.2. File `app/celery_app.py`**
*   **Mục đích:** Là trái tim của ứng dụng Celery. File này chịu trách nhiệm khởi tạo, đọc cấu hình và liên kết các thành phần lại với nhau.
*   **Giải pháp & Kế hoạch Logic:**
    1.  **Imports:** Import thư viện `Celery` từ `celery` và `os` để đọc biến môi trường.
    2.  **Load Environment:** Sử dụng thư viện `dotenv` để tự động tải các biến từ file `.env`.
    3.  **Khởi tạo Celery:** Tạo một đối tượng Celery: `app = Celery('syncdataDQG')`.
    4.  **Cấu hình:**
        *   Sử dụng `app.conf.broker_url` để gán giá trị từ `os.environ.get('REDIS_URL')`.
        *   Sử dụng `app.conf.result_backend` để gán giá trị từ `os.environ.get('MONGO_URL')`.
    5.  **Tự động phát hiện Tasks:** Sử dụng `app.autodiscover_tasks(['app'])` để Celery tự động tìm các file `tasks.py` trong các module được chỉ định (ở đây là module `app`).
#### **2.3. File `app/tasks.py`**
*   **Mục đích:** Nơi định nghĩa tất cả các "công việc" (tasks) mà Celery worker sẽ thực thi.
*   **Giải pháp & Kế hoạch Logic:**
    1.  **Import:** Import đối tượng `app` từ `app.celery_app`.
    2.  **Định nghĩa Verification Task:**
        *   Tạo một hàm Python đơn giản `add(x, y)`.
        *   Sử dụng decorator `@app.task` ngay trên hàm `add` để biến nó thành một Celery task.
        *   Hàm này sẽ chỉ chứa một dòng lệnh: `return x + y`.
#### **2.4. File `run_verification.py`**
*   **Mục đích:** Một kịch bản độc lập dùng để kích hoạt một task và kiểm tra xem kết quả có được trả về đúng hay không. Đây là công cụ xác minh cho Phase 1.
*   **Giải pháp & Kế hoạch Logic:**
    1.  **Import:** Import task `add` từ `app.tasks`. Import `time` để có thể chờ kết quả.
    2.  **Gửi Task:**
        *   Gọi `result = add.delay(5, 5)`. Lệnh `.delay()` sẽ gửi task vào hàng đợi Redis mà không làm block chương trình.
    3.  **Nhận và In kết quả:**
        *   In ra màn hình ID của task: `print(f"Task sent with ID: {result.id}")`.
        *   Chờ đợi kết quả bằng cách gọi `final_result = result.get(timeout=10)`. Lệnh `.get()` sẽ block chương trình cho đến khi có kết quả (hoặc hết thời gian chờ).
        *   In kết quả cuối cùng: `print(f"Result received: {final_result}")`.
---
### **Bước 3: Kế hoạch Vận hành và Xác minh**
Đây là các bước sẽ được thực hiện (trong các phase sau) để kiểm tra toàn bộ hệ thống đã được thiết lập đúng.
1.  **Khởi động Infrastructure:** Chạy lệnh `docker-compose -f docker-compose.data.yml up -d` để khởi động Redis và MongoDB.
2.  **Khởi động Celery Worker:** Mở một terminal, kích hoạt môi trường ảo và chạy lệnh: `celery -A app.celery_app worker --loglevel=info`.
3.  **Chạy Script Xác minh:** Mở một terminal khác, kích hoạt môi trường ảo và chạy lệnh: `python run_verification.py`.
4.  **Kết quả mong đợi:**
    *   Terminal của worker sẽ hiển thị log nhận và hoàn thành task `app.tasks.add`.
    *   Terminal của script xác minh sẽ in ra:
        ```
        Task sent with ID: [một chuỗi ID ngẫu nhiên]
        Result received: 10
        ```
    *   Nếu kết quả là `10`, Phase 1 được xem là thành công 100%.