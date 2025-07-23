

### **1. Model cho Hóa đơn bán thuốc (Sales Invoice)**

#### a. Bảng Header: `SalesInvoices`

Lưu thông tin chung của mỗi hóa đơn bán hàng.

| Tên cột | Kiểu dữ liệu | Bắt buộc | Ghi chú |
| :--- | :--- | :---: | :--- |
| `id` | INT, PRIMARY KEY, AUTO\_INCREMENT | ✅ | Khóa chính của bảng trong CSDL local. |
| `local_invoice_id` | NVARCHAR(50) | ✅ | Mã hóa đơn của cơ sở (tương ứng `ma_hoa_don`). |
| `national_invoice_id` | NVARCHAR(100) | | Mã hóa đơn do hệ thống Dược quốc gia trả về. |
| `pharmacy_code` | NVARCHAR(50) | ✅ | Mã cơ sở GPP (tương ứng `ma_co_so`). |
| `shop_pharmacy_code` | NVARCHAR(50) | ✅ | Mã cửa hàng của hệ thống (trường bổ sung để quản lý). |
| `national_prescription_id` | NVARCHAR(50) | | Mã đơn thuốc quốc gia (nếu có). |
| `sale_date` | DATETIME | ✅ | Ngày bán (tương ứng `ngay_ban`). |
| `seller_name` | NVARCHAR(50) | | Họ tên người bán. |
| `customer_name` | NVARCHAR(50) | | Họ tên khách hàng. |
| **`status`** | NVARCHAR(20) | ✅ | Trạng thái đồng bộ: `PENDING_SYNC`, `SYNC_SUCCESS`, `SYNC_FAILED`. |
| `sync_response_message` | TEXT | | Lưu thông báo lỗi nếu đồng bộ thất bại. |
| `created_at` | TIMESTAMP | ✅ | Thời gian tạo record. |
| `updated_at` | TIMESTAMP | ✅ | Thời gian cập nhật record lần cuối. |

#### b. Bảng Detail: `SalesInvoiceDetails`

Lưu chi tiết từng loại thuốc trong một hóa đơn.

| Tên cột | Kiểu dữ liệu | Bắt buộc | Ghi chú |
| :--- | :--- | :---: | :--- |
| `id` | INT, PRIMARY KEY, AUTO\_INCREMENT | ✅ | Khóa chính của bảng. |
| `sales_invoice_id` | INT, FOREIGN KEY | ✅ | **Khóa ngoại, liên kết tới `SalesInvoices(id)`.** |
| `drug_code` | NVARCHAR(50) | ✅ | Mã thuốc (tương ứng `ma_thuoc`). |
| `drug_name` | NVARCHAR(500) | ✅ | Tên thuốc. |
| `lot_number` | NVARCHAR(50) | ✅ | Số lô. |
| `production_date` | DATE | | Ngày sản xuất. |
| `expiry_date` | DATE | ✅ | Hạn dùng. |
| `unit` | NVARCHAR(50) | ✅ | Đơn vị tính. |
| `concentration` | NVARCHAR(500) | ✅ | Hàm lượng. |
| `dosage` | TEXT | ✅ | Liều dùng. |
| `route_of_administration`| NVARCHAR(200) | | Đường dùng. |
| `registration_number` | NVARCHAR(50) | | Số đăng ký (tương ứng `so_dang_ky`). |
| `quantity` | DECIMAL(18, 2) | ✅ | Số lượng. |
| `unit_price` | DECIMAL(18, 2) | ✅ | Đơn giá. |
| `line_total` | DECIMAL(18, 2) | ✅ | Thành tiền. |
| `conversion_ratio` | DECIMAL(18, 2) | ✅ | Tỷ lệ quy đổi. |

---

### **2. Model cho Phiếu Nhập kho (Purchase Receipt)**

#### a. Bảng Header: `PurchaseReceipts`

| Tên cột | Kiểu dữ liệu | Bắt buộc | Ghi chú |
| :--- | :--- | :---: | :--- |
| `id` | INT, PRIMARY KEY, AUTO\_INCREMENT | ✅ | Khóa chính. |
| `local_receipt_id` | NVARCHAR(50) | ✅ | Mã phiếu nhập của cơ sở (tương ứng `ma_phieu`). |
| `national_receipt_id` | NVARCHAR(100) | | Mã phiếu nhập do hệ thống Dược quốc gia trả về. |
| `pharmacy_code` | NVARCHAR(50) | ✅ | Mã cơ sở GPP. |
| `shop_pharmacy_code` | NVARCHAR(50) | ✅ | Mã cửa hàng của hệ thống (trường bổ sung để quản lý). |
| `receipt_date` | DATETIME | ✅ | Ngày nhập. |
| `receipt_type` | INT | ✅ | Loại phiếu nhập (1: NCC, 2: Khách trả, 3: Nhập tồn). |
| `supplier_name` | NVARCHAR(500) | | Tên cơ sở cung cấp. |
| `notes` | TEXT | | Ghi chú. |
| **`status`** | NVARCHAR(20) | ✅ | Trạng thái đồng bộ. |
| `sync_response_message` | TEXT | | Lưu thông báo lỗi nếu đồng bộ thất bại. |
| `created_at` | TIMESTAMP | ✅ | Thời gian tạo. |
| `updated_at` | TIMESTAMP | ✅ | Thời gian cập nhật. |

#### b. Bảng Detail: `PurchaseReceiptDetails`

| Tên cột | Kiểu dữ liệu | Bắt buộc | Ghi chú |
| :--- | :--- | :---: | :--- |
| `id` | INT, PRIMARY KEY, AUTO\_INCREMENT | ✅ | Khóa chính. |
| `purchase_receipt_id` | INT, FOREIGN KEY | ✅ | **Khóa ngoại, liên kết tới `PurchaseReceipts(id)`.** |
| `drug_code` | NVARCHAR(50) | ✅ | Mã thuốc. |
| `drug_name` | NVARCHAR(500) | ✅ | Tên thuốc. |
| `lot_number` | NVARCHAR(50) | ✅ | Số lô. |
| `production_date` | DATE | | Ngày sản xuất. |
| `expiry_date` | DATE | ✅ | Hạn dùng. |
| `registration_number` | NVARCHAR(50) | ✅ | Số đăng ký lưu hành (tương ứng `so_dklh`). |
| `quantity` | DECIMAL(18, 2) | ✅ | Số lượng. |
| `unit_price` | DECIMAL(18, 2) | | Đơn giá. |
| `unit` | NVARCHAR(200) | ✅ | Đơn vị tính. |

---

### **3. Model cho Phiếu Xuất kho (Goods Issue Slip)**

#### a. Bảng Header: `GoodsIssueSlips`

| Tên cột | Kiểu dữ liệu | Bắt buộc | Ghi chú |
| :--- | :--- | :---: | :--- |
| `id` | INT, PRIMARY KEY, AUTO\_INCREMENT | ✅ | Khóa chính. |
| `local_slip_id` | NVARCHAR(50) | ✅ | Mã phiếu xuất của cơ sở (tương ứng `ma_phieu`). |
| `national_slip_id` | NVARCHAR(100) | | Mã phiếu xuất do hệ thống Dược quốc gia trả về. |
| `pharmacy_code` | NVARCHAR(50) | ✅ | Mã cơ sở GPP. |
| `shop_pharmacy_code` | NVARCHAR(50) | ✅ | Mã cửa hàng của hệ thống (trường bổ sung để quản lý). |
| `issue_date` | DATETIME | ✅ | Ngày xuất. |
| `issue_type` | INT | ✅ | Loại phiếu xuất (2: Trả NCC, 3: Xuất hủy). |
| `recipient_name` | NVARCHAR(500) | | Tên cơ sở nhận. |
| `notes` | TEXT | ✅ | Ghi chú. |
| **`status`** | NVARCHAR(20) | ✅ | Trạng thái đồng bộ. |
| `sync_response_message` | TEXT | | Lưu thông báo lỗi nếu đồng bộ thất bại. |
| `created_at` | TIMESTAMP | ✅ | Thời gian tạo. |
| `updated_at` | TIMESTAMP | ✅ | Thời gian cập nhật. |

#### b. Bảng Detail: `GoodsIssueSlipDetails`

*Bảng này có cấu trúc tương tự `PurchaseReceiptDetails`.*

| Tên cột | Kiểu dữ liệu | Bắt buộc | Ghi chú |
| :--- | :--- | :---: | :--- |
| `id` | INT, PRIMARY KEY, AUTO\_INCREMENT | ✅ | Khóa chính. |
| `goods_issue_slip_id` | INT, FOREIGN KEY | ✅ | **Khóa ngoại, liên kết tới `GoodsIssueSlips(id)`.** |
| `drug_code` | NVARCHAR(50) | ✅ | Mã thuốc. |
| `drug_name` | NVARCHAR(500) | ✅ | Tên thuốc. |
| `lot_number` | NVARCHAR(50) | ✅ | Số lô. |
| `production_date` | DATE | | Ngày sản xuất. |
| `expiry_date` | DATE | ✅ | Hạn dùng. |
| `registration_number` | NVARCHAR(50) | ✅ | Số đăng ký lưu hành (tương ứng `so_dklh`). |
| `quantity` | DECIMAL(18, 2) | ✅ | Số lượng. |
| `unit_price` | DECIMAL(18, 2) | ✅ | Đơn giá. |
| `unit` | NVARCHAR(200) | ✅ | Đơn vị tính. |


### **4. Model cho bảng thông tin login tài khoản

#### a. Bảng AccountShop
| Tên cột | Kiểu dữ liệu | Bắt buộc | Ghi chú |
| :--- | :--- | :---: | :--- |
| `shop_pharmacy_code` | NVARCHAR(50) | ✅ | Mã shop ở cơ sở |
| `pharmacy_code` | NVARCHAR(50) | ✅ | Mã cơ sở GPP. |
| `account` | NVARCHAR(50) | ✅ | **Khóa ngoại, liên kết tới `GoodsIssueSlips(id)`.** |
| `password` | NVARCHAR(50) | ✅ | (Ẩn thông tin nhạy cảm) |