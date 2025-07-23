# Hướng dẫn sử dụng Project Hermes

## 1. Giới thiệu
Project Hermes là hệ thống đồng bộ hóa dữ liệu phiếu nhập, phiếu xuất, hóa đơn giữa hệ thống nội bộ và đối tác qua API, sử dụng kiến trúc microservices với Celery, FastAPI, Docker.

## 2. Khởi động hệ thống
- Cài đặt Docker & Docker Compose.
- Chạy lệnh:
  ```
  docker compose up -d
  ```
- Các service sẽ tự động khởi động: core (API), worker (Celery), redis (broker).

## 3. Gửi dữ liệu Phiếu Nhập
- Gửi HTTP POST tới endpoint:
  ```
  POST /phieu-nhap
  Content-Type: application/json
  ```
- Payload mẫu:
  ```json
  {
    "ma_phieu": "PN001",
    "ngay_ct": "2023-10-10T00:00:00",
    "ma_kho": "KHO01",
    "ma_dt": "DT001",
    "dien_giai": "Nhập hàng tháng 10",
    "chi_tiet": [
      {"ma_vt": "VT01", "ten_vt": "Vật tư 1", "dvt": "cái", "so_luong": 10, "don_gia": 10000}
    ]
  }
  ```

## 4. Gửi dữ liệu Phiếu Xuất
- Gửi HTTP POST tới endpoint:
  ```
  POST /phieu-xuat
  Content-Type: application/json
  ```
- Payload mẫu:
  ```json
  {
    "ma_phieu": "PX001",
    "ngay_ct": "2023-10-10T00:00:00",
    "ma_kho": "KHO01",
    "ma_dt": "DT001",
    "dien_giai": "Xuất hàng tháng 10",
    "chi_tiet": [
      {"ma_vt": "VT01", "ten_vt": "Vật tư 1", "dvt": "cái", "so_luong": 5, "don_gia": 12000}
    ]
  }
  ```

## 5. Gửi dữ liệu Hóa đơn
- Gửi HTTP POST tới endpoint:
  ```
  POST /hoa-don
  Content-Type: application/json
  ```
- Payload mẫu:
  ```json
  {
    "ma_hd": "HD001",
    "ngay_ct": "2023-10-10T00:00:00",
    "ma_dt": "DT001",
    "dia_chi": "123 Đường ABC",
    "dien_giai": "Thanh toán hóa đơn tháng 10",
    "chi_tiet": [
      {"ma_vt": "VT01", "ten_vt": "Vật tư 1", "dvt": "cái", "so_luong": 2, "don_gia": 15000, "thanh_tien": 30000}
    ]
  }
  ```

## 6. Kiểm tra trạng thái xử lý
- Xem log bằng lệnh:
  ```
  docker compose logs worker
  ```
- Kết quả trả về qua API là trạng thái tiếp nhận, xử lý bất đồng bộ.

## 7. Kiểm thử tự động
- Chạy test:
  ```
  docker compose run test
  ```
- Các test mẫu nằm trong thư mục [`tests/`](tests/).

## 8. Cấu hình hệ thống
- Sửa các biến cấu hình trong file [`config/settings.py`](config/settings.py:1) và `.env` theo môi trường thực tế.

## 9. Bàn giao & mở rộng
- Để bàn giao, đóng gói source code và tài liệu.
- Có thể mở rộng thêm các loại phiếu hoặc tích hợp đối tác mới bằng cách bổ sung models, API client, Celery task tương ứng.
