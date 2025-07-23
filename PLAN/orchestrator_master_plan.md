# Kế hoạch Tổng thể - Project Hermes

## 1. Mục tiêu Dự án

Xây dựng một hệ thống đồng bộ dữ liệu tự động, hiệu suất cao và có khả năng chịu lỗi. Hệ thống sẽ đọc dữ liệu từ SQL Server, xử lý và đẩy lên API của đối tác một cách an toàn và có kiểm soát.

## 2. Các Giai đoạn Phát triển

Dự án được chia thành 4 giai đoạn chính. Mỗi giai đoạn có một kế hoạch chi tiết riêng.

*   **[Giai đoạn 1: Thiết lập Nền tảng Dự án](./phase_1_detailed_plan.md)**
    *   **Mục tiêu:** Xây dựng bộ khung hoàn chỉnh cho ứng dụng, bao gồm cấu trúc thư mục, cấu hình, dependencies, và thiết lập Docker.
    *   **Kết quả:** Một bộ khung dự án có thể chạy được, sẵn sàng cho việc triển khai logic nghiệp vụ.

*   **[Giai đoạn 2: Luồng End-to-End cho Phiếu Nhập](./phase_2_detailed_plan.md)**
    *   **Mục tiêu:** Xây dựng và kiểm thử thành công một luồng xử lý hoàn chỉnh cho "Phiếu Nhập", làm khuôn mẫu cho các luồng khác.
    *   **Kết quả:** Luồng xử lý phiếu nhập hoạt động đầy đủ, từ DB -> API -> Cập nhật DB -> Ghi Log.

*   **[Giai đoạn 3: Mở rộng cho các loại phiếu khác](./phase_3_detailed_plan.md)**
    *   **Mục tiêu:** Triển khai các luồng xử lý cho `Phiếu Xuất` và `Hóa Đơn Bán` bằng cách tái sử dụng tối đa code đã có.
    *   **Kết quả:** Hệ thống có khả năng xử lý tất cả các loại phiếu được yêu cầu.

*   **[Giai đoạn 4: Hoàn thiện & Bàn giao](./phase_4_detailed_plan.md)**
    *   **Mục tiêu:** Tái cấu trúc mã nguồn để tăng tính tái sử dụng và tạo tài liệu bàn giao `README.md` rõ ràng.
    *   **Kết quả:** Mã nguồn được tối ưu và có tài liệu đầy đủ, sẵn sàng để team DevOps triển khai.

## 3. Hướng dẫn cho Orchestrator

-   Bắt đầu bằng cách thực hiện các task trong **Giai đoạn 1**.
-   Sau khi Giai đoạn 1 hoàn tất, chuyển sang **Giai đoạn 2**.
-   Tiếp tục tuần tự qua các giai đoạn cho đến khi hoàn thành Giai đoạn 4.
-   Mỗi tệp kế hoạch chi tiết chứa các task cụ thể có thể giao cho các mode khác (như "Code") để thực hiện.