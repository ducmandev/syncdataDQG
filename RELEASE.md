# Release Notes – Giai đoạn 4

## Tổng hợp các tính năng đã hoàn thành
- Tích hợp các API đối tác: hóa đơn, nhập, xuất.
- Hoàn thiện mô hình dữ liệu và các endpoint chính.
- Xây dựng worker xử lý nền với Celery.
- Thiết lập hệ thống kiểm thử tự động.
- Hoàn thiện tài liệu hướng dẫn sử dụng ([docs/user_guide.md](docs/user_guide.md:1)).

## Hướng dẫn đóng gói source code
1. Đảm bảo source code đã được clean, không chứa file tạm, log, hoặc thông tin nhạy cảm.
2. Đóng gói toàn bộ thư mục dự án, bao gồm:
   - Mã nguồn trong `src/`, `mock_api/`, `config/`, `scripts/`
   - Tài liệu hướng dẫn sử dụng: [`docs/user_guide.md`](docs/user_guide.md:1)
   - File cấu hình: `.env`, `requirements.txt`, các file trong `config/`
   - File kiểm thử: các file trong `tests/`
   - File CI/CD: `.gitignore`, `Dockerfile`, các file docker-compose

## Yêu cầu môi trường triển khai
- Python >= 3.10
- Docker & Docker Compose
- Hệ điều hành: Linux hoặc Windows 10+
- Cài đặt các package trong `requirements.txt`

## Checklist kiểm thử trước bàn giao
- [x] Đã chạy toàn bộ test tự động trong `tests/`
- [x] Đã kiểm tra các endpoint API hoạt động đúng
- [x] Đã kiểm tra worker Celery hoạt động ổn định
- [x] Đã kiểm tra đóng gói và triển khai bằng Docker Compose
- [x] Đã kiểm tra tài liệu hướng dẫn sử dụng đầy đủ
