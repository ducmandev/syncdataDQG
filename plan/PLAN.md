# KẾ HOẠCH TRIỂN KHAI TOÀN DIỆN
Tài liệu này vạch ra lộ trình đầy đủ để xây dựng hệ thống xử lý dữ liệu bất đồng bộ.
## I. Kế hoạch Tổng quan (Overall Plan)
Dự án sẽ được chia thành 4 phase chính, mỗi phase xây dựng dựa trên kết quả của phase trước đó:
-   **Phase 1: Thiết lập Nền tảng & Cấu hình.**
    -   **Mục tiêu:** Xây dựng và xác minh "bộ xương" của ứng dụng, đảm bảo các thành phần cốt lõi (Celery, Redis, MongoDB) có thể kết nối với nhau.
    -   **Kết quả:** Một cấu trúc dự án sẵn sàng, các file cấu hình hoàn chỉnh, và khả năng chạy một task đơn giản để chứng minh kết nối thành công.
-   **Phase 2: Polling Dữ liệu & Tạo Task.**
    -   **Mục tiêu:** Tự động phát hiện dữ liệu mới từ MSSQL và tạo ra các task xử lý tương ứng một cách đáng tin cậy.
    -   **Kết quả:** Một Celery Beat task có khả năng truy vấn MSSQL theo lịch trình, tạo log trong MongoDB, và đẩy task vào hàng đợi Redis.
-   **Phase 3: Hoàn thiện Logic Xử lý của Worker.**
    -   **Mục tiêu:** Xây dựng logic nghiệp vụ cốt lõi, bao gồm gọi API đối tác và xử lý các kịch bản thành công/thất bại.
    -   **Kết quả:** Một Celery worker có khả năng nhận task, gọi API bên ngoài, xử lý lỗi, thử lại, và cập nhật kết quả cuối cùng vào MongoDB.
-   **Phase 4: Thu thập, Báo cáo & Dọn dẹp Tự động.**
    -   **Mục tiêu:** Hoàn thiện vòng đời của dữ liệu bằng cách tự động hóa việc thu thập kết quả và bảo trì hệ thống.
    -   **Kết quả:** Các Celery Beat tasks được lên lịch để tự động tổng hợp báo cáo và dọn dẹp các bản ghi đã cũ, giúp hệ thống tự vận hành bền vững.
---
## II. Kế hoạch Chi tiết - Phase 1: Thiết lập Nền tảng & Cấu hình
**Mục tiêu:** Hoàn thành việc chuẩn bị và cấu hình nền tảng kỹ thuật mà không cần viết logic nghiệp vụ.
-   **Bước 1.1: Thiết kế Cấu trúc Thư mục & File**
    -   **Công việc:** Dựa trên cấu trúc hiện có, thiết kế và vẽ ra sơ đồ cây thư mục cho ứng dụng Celery.
    -   **Kết quả:** Một sơ đồ cây thư mục rõ ràng, xác định vị trí của các file quan trọng như `celery_app.py`, `tasks.py`, `config.py`, `.env`, và thư mục `app`.
-   **Bước 1.2: Định nghĩa Biến Môi trường**
    -   **Công việc:** Liệt kê tất cả các biến môi trường cần thiết để ứng dụng có thể kết nối tới các dịch vụ bên ngoài (Redis, MongoDB).
    -   **Kết quả:** Một danh sách các cặp `KEY=VALUE` mẫu để đưa vào file `.env`, ví dụ: `REDIS_URL=redis://localhost:6379/0`, `MONGO_URL=mongodb://localhost:27017/celery_logs`.
-   **Bước 1.3: Lên Kế hoạch cho Module Cấu hình Celery (`celery_app.py`)**
    -   **Công việc:** Vạch ra các khối logic chính cần có trong file này.
    -   **Kết quả:** Một bản thiết kế (dưới dạng pseudocode hoặc gạch đầu dòng) mô tả việc:
        1.  Tải các biến môi trường từ file `.env`.
        2.  Khởi tạo đối tượng Celery app.
        3.  Cấu hình `broker_url` và `result_backend`.
        4.  Tự động phát hiện các tasks từ file `tasks.py`.
-   **Bước 1.4: Lên Kế hoạch cho Task Xác minh (`tasks.py`)**
    -   **Công việc:** Thiết kế một task đơn giản nhất có thể để kiểm tra kết nối.
    -   **Kết quả:** Mô tả về task `add(x, y)`: nhận hai số, trả về tổng của chúng. Task này được dùng để xác minh rằng một công việc có thể đi từ điểm bắt đầu, qua hàng đợi, được worker xử lý, và trả về kết quả.