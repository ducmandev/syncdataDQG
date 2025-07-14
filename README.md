# Python-Celery Data Synchronization System
## Hệ thống Đồng bộ Dữ liệu Python-Celery

This project is a robust, multi-service application designed to synchronize data from an MSSQL database to a set of REST APIs. It is built with a scalable architecture using Python, Celery, Redis, and MongoDB.
*Dự án này là một ứng dụng đa dịch vụ mạnh mẽ được thiết kế để đồng bộ hóa dữ liệu từ cơ sở dữ liệu MSSQL đến một bộ các REST API. Nó được xây dựng với kiến trúc có khả năng mở rộng bằng Python, Celery, Redis và MongoDB.*

---

## System Architecture / Kiến trúc Hệ thống

The application is designed as a microservices-style monorepo with four main services and a shared common library:
*Ứng dụng được thiết kế theo kiểu monorepo đa dịch vụ với bốn dịch vụ chính và một thư viện chung được chia sẻ:*

-   **`common`**: A shared Python library containing all core logic, including database clients, the API client, Pydantic data models, and configuration management. / *Một thư viện Python dùng chung chứa tất cả logic cốt lõi, bao gồm các trình kết nối cơ sở dữ liệu, trình kết nối API, mô hình dữ liệu Pydantic và quản lý cấu hình.*
-   **`scheduler`**: A standalone Celery Beat service that periodically queries the MSSQL database for new records and dispatches processing tasks. / *Một dịch vụ Celery Beat độc lập, định kỳ truy vấn cơ sở dữ liệu MSSQL để tìm các bản ghi mới và gửi đi các tác vụ xử lý.*
-   **`saler`**: A Celery worker service that listens to the `sale_queue` to process and sync sales invoice data. / *Một dịch vụ worker Celery lắng nghe `sale_queue` để xử lý và đồng bộ dữ liệu hóa đơn bán hàng.*
-   **`importer`**: A Celery worker service that listens to the `import_queue` to process and sync purchase receipt data. / *Một dịch vụ worker Celery lắng nghe `import_queue` để xử lý và đồng bộ dữ liệu phiếu nhập kho.*
-   **`canceller`**: A Celery worker service that listens to the `cancellation_queue` to process and sync goods issue/cancellation data. / *Một dịch vụ worker Celery lắng nghe `cancellation_queue` để xử lý và đồng bộ dữ liệu phiếu xuất/hủy.*

This separation allows for independent scaling and deployment of each component.
*Sự tách biệt này cho phép mở rộng quy mô và triển khai độc lập cho từng thành phần.*

---

## Prerequisites / Yêu cầu Cần có

-   Docker and Docker Compose / *Docker và Docker Compose*
-   Python 3.10+
-   Access to an MSSQL database, a MongoDB instance, and a Redis instance. / *Quyền truy cập vào cơ sở dữ liệu MSSQL, một instance MongoDB và một instance Redis.*

---

## Getting Started / Bắt đầu

### 1. Clone the Repository / Tải Repository về

```bash
git clone <your-repository-url>
cd <repository-name>
```

### 2. Create the Environment File / Tạo Tệp Môi trường

Create a file named `.env` in the root of the project. Use the structure below and fill in the credentials for your databases and the target API.
*Tạo một tệp có tên `.env` ở thư mục gốc của dự án. Sử dụng cấu trúc bên dưới và điền thông tin xác thực cho cơ sở dữ liệu của bạn và API đích.*

```env
# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379

# MongoDB Configuration
MONGO_URI=mongodb://localhost:27017/
MONGO_DB_NAME=sync_data_logs

# MSSQL Configuration
MSSQL_SERVER=your_mssql_server_address
MSSQL_DATABASE=your_database_name
MSSQL_USER=your_mssql_username
MSSQL_PASSWORD=your_mssql_password
MSSQL_DRIVER='{ODBC Driver 17 for SQL Server}' # Ensure this driver is installed / Đảm bảo driver này đã được cài đặt

# National API Configuration
API_BASE_URL=http://api.example.com
API_USERNAME=your_api_username
API_PASSWORD=your_api_password
```

### 3. Install Dependencies / Cài đặt Thư viện

Install all the required Python packages from the central `requirements.txt` file.
*Cài đặt tất cả các gói Python cần thiết từ tệp `requirements.txt`.*

```bash
pip install -r requirements.txt
```

---

## Running the Application / Chạy Ứng dụng

### Using Docker Compose (Recommended) / Sử dụng Docker Compose (Khuyến nghị)

The easiest way to run the entire system is with Docker Compose.
*Cách dễ nhất để chạy toàn bộ hệ thống là sử dụng Docker Compose.*

```bash
docker-compose up --build
```

This command will: / *Lệnh này sẽ:*
1.  Build the Docker images for all services. / *Xây dựng Docker image cho tất cả các dịch vụ.*
2.  Start containers for Redis, MongoDB, and all four Python services. / *Khởi động các container cho Redis, MongoDB và cả bốn dịch vụ Python.*
3.  Automatically apply the environment variables from your `.env` file. / *Tự động áp dụng các biến môi trường từ tệp `.env` của bạn.*

To stop the services, press `Ctrl+C` and then run: / *Để dừng các dịch vụ, nhấn `Ctrl+C` và sau đó chạy:*
```bash
docker-compose down
```

### Running Services Manually / Chạy Thủ công Từng Dịch vụ

You can also run each service individually in separate terminal windows.
*Bạn cũng có thể chạy từng dịch vụ riêng lẻ trong các cửa sổ terminal khác nhau.*

**Terminal 1: Start the Scheduler / *Khởi động Scheduler***
```bash
celery -A scheduler.celery_app beat -l info
```

**Terminal 2: Start the Sale Worker / *Khởi động Worker Bán hàng***
```bash
celery -A saler.celery_app worker -l info -Q sale_queue
```

**Terminal 3: Start the Import Worker / *Khởi động Worker Nhập hàng***
```bash
celery -A importer.celery_app worker -l info -Q import_queue
```

**Terminal 4: Start the Cancellation Worker / *Khởi động Worker Hủy hàng***
```bash
celery -A canceller.celery_app worker -l info -Q cancellation_queue
```

---

## Project Structure / Cấu trúc Dự án

```
syncdataDQG/
├── common/             # Shared library / Thư viện dùng chung
├── importer/           # Import worker service / Dịch vụ worker Nhập
├── saler/              # Sale worker service / Dịch vụ worker Bán
├── canceller/          # Cancellation worker service / Dịch vụ worker Hủy
├── scheduler/          # Scheduler (Celery Beat) service / Dịch vụ Lập lịch
├── tests/              # Unit and integration tests / Kiểm thử
├── project_plan/       # Detailed multi-phase project plans / Kế hoạch dự án chi tiết
├── .env                # Local environment variables (MUST BE CREATED) / Biến môi trường (CẦN TẠO)
├── docker-compose.yml  # Docker Compose orchestration file / Tệp điều phối Docker Compose
└── requirements.txt    # All Python dependencies / Tất cả các thư viện Python