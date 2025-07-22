IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = N'test_db')
BEGIN
    CREATE DATABASE test_db;
END
GO
USE test_db;
GO

-- Tạo bảng SalesInvoices
CREATE TABLE SalesInvoices (
    id INT PRIMARY KEY IDENTITY(1,1),
    local_invoice_id VARCHAR(50) NOT NULL,
    national_invoice_id VARCHAR(100),
    pharmacy_code VARCHAR(50) NOT NULL,
    shop_pharmacy_code VARCHAR(50) NOT NULL,
    national_prescription_id VARCHAR(50),
    sale_date DATETIME NOT NULL,
    seller_name VARCHAR(50),
    customer_name VARCHAR(50),
    status VARCHAR(20) NOT NULL,
    sync_response_message NVARCHAR(MAX),
    created_at DATETIME NOT NULL DEFAULT GETDATE(),
    updated_at DATETIME NOT NULL DEFAULT GETDATE()
);
GO

-- Tạo bảng SalesInvoiceDetails
CREATE TABLE SalesInvoiceDetails (
    id INT PRIMARY KEY IDENTITY(1,1),
    sales_invoice_id INT NOT NULL,
    drug_code VARCHAR(50) NOT NULL,
    drug_name VARCHAR(500) NOT NULL,
    lot_number VARCHAR(50) NOT NULL,
    production_date DATE,
    expiry_date DATE NOT NULL,
    unit VARCHAR(50) NOT NULL,
    concentration VARCHAR(500) NOT NULL,
    dosage NVARCHAR(MAX) NOT NULL,
    route_of_administration VARCHAR(200),
    registration_number VARCHAR(50),
    quantity DECIMAL(18,2) NOT NULL,
    unit_price DECIMAL(18,2) NOT NULL,
    line_total DECIMAL(18,2) NOT NULL,
    conversion_ratio DECIMAL(18,2) NOT NULL,
    FOREIGN KEY (sales_invoice_id) REFERENCES SalesInvoices(id)
);
GO

-- Tạo bảng PurchaseReceipts
CREATE TABLE PurchaseReceipts (
    id INT PRIMARY KEY IDENTITY(1,1),
    local_receipt_id VARCHAR(50) NOT NULL,
    national_receipt_id VARCHAR(100),
    pharmacy_code VARCHAR(50) NOT NULL,
    shop_pharmacy_code VARCHAR(50) NOT NULL,
    receipt_date DATETIME NOT NULL,
    receipt_type INT NOT NULL,
    supplier_name VARCHAR(500),
    notes NVARCHAR(MAX),
    status VARCHAR(20) NOT NULL,
    sync_response_message NVARCHAR(MAX),
    created_at DATETIME NOT NULL DEFAULT GETDATE(),
    updated_at DATETIME NOT NULL DEFAULT GETDATE()
);
GO

-- Tạo bảng PurchaseReceiptDetails
CREATE TABLE PurchaseReceiptDetails (
    id INT PRIMARY KEY IDENTITY(1,1),
    purchase_receipt_id INT NOT NULL,
    drug_code VARCHAR(50) NOT NULL,
    drug_name VARCHAR(500) NOT NULL,
    lot_number VARCHAR(50) NOT NULL,
    production_date DATE,
    expiry_date DATE NOT NULL,
    registration_number VARCHAR(50) NOT NULL,
    quantity DECIMAL(18,2) NOT NULL,
    unit_price DECIMAL(18,2),
    unit VARCHAR(200) NOT NULL,
    FOREIGN KEY (purchase_receipt_id) REFERENCES PurchaseReceipts(id)
);
GO

-- Tạo bảng GoodsIssueSlips
CREATE TABLE GoodsIssueSlips (
    id INT PRIMARY KEY IDENTITY(1,1),
    local_slip_id VARCHAR(50) NOT NULL,
    national_slip_id VARCHAR(100),
    pharmacy_code VARCHAR(50) NOT NULL,
    shop_pharmacy_code VARCHAR(50) NOT NULL,
    issue_date DATETIME NOT NULL,
    issue_type INT NOT NULL,
    recipient_name VARCHAR(500),
    notes NVARCHAR(MAX) NOT NULL,
    status VARCHAR(20) NOT NULL,
    sync_response_message NVARCHAR(MAX),
    created_at DATETIME NOT NULL DEFAULT GETDATE(),
    updated_at DATETIME NOT NULL DEFAULT GETDATE()
);
GO

-- Tạo bảng GoodsIssueSlipDetails
CREATE TABLE GoodsIssueSlipDetails (
    id INT PRIMARY KEY IDENTITY(1,1),
    goods_issue_slip_id INT NOT NULL,
    drug_code VARCHAR(50) NOT NULL,
    drug_name VARCHAR(500) NOT NULL,
    lot_number VARCHAR(50) NOT NULL,
    production_date DATE,
    expiry_date DATE NOT NULL,
    registration_number VARCHAR(50) NOT NULL,
    quantity DECIMAL(18,2) NOT NULL,
    unit_price DECIMAL(18,2) NOT NULL,
    unit VARCHAR(200) NOT NULL,
    FOREIGN KEY (goods_issue_slip_id) REFERENCES GoodsIssueSlips(id)
);
GO

-- Tạo bảng AccountShop
CREATE TABLE AccountShop (
    shop_pharmacy_code NVARCHAR(50) NOT NULL,
    pharmacy_code NVARCHAR(50) NOT NULL,
    account NVARCHAR(50) NOT NULL,
    password NVARCHAR(50) NOT NULL,
    shop_name NVARCHAR(100) NOT NULL,
    address NVARCHAR(200) NOT NULL,
    phone_number NVARCHAR(20) NOT NULL,
    email NVARCHAR(100),
    status INT NOT NULL,
    created_at DATETIME NOT NULL,
    updated_at DATETIME,
    PRIMARY KEY (shop_pharmacy_code, pharmacy_code, account)
);
GO

-- Dữ liệu mẫu cho SalesInvoices
INSERT INTO SalesInvoices (local_invoice_id, national_invoice_id, pharmacy_code, shop_pharmacy_code, national_prescription_id, sale_date, seller_name, customer_name, status, sync_response_message, created_at, updated_at)
VALUES
('HD001', 'QGHD001', 'PHARM001', 'SHOP01', 'QGDT001', '2025-07-10 08:00:00', 'Nguyen Van A', 'Tran Thi B', 'PENDING_SYNC', NULL, GETDATE(), GETDATE()),
('HD002', 'QGHD002', 'PHARM001', 'SHOP01', NULL, '2025-07-09 09:30:00', 'Nguyen Van B', 'Le Van C', 'SYNC_SUCCESS', NULL, GETDATE(), GETDATE());
GO

-- Dữ liệu mẫu cho SalesInvoiceDetails
INSERT INTO SalesInvoiceDetails (sales_invoice_id, drug_code, drug_name, lot_number, production_date, expiry_date, unit, concentration, dosage, route_of_administration, registration_number, quantity, unit_price, line_total, conversion_ratio)
VALUES
(1, 'TH001', 'Paracetamol 500mg', 'L001', '2025-01-01', '2026-01-01', 'Hộp', '500mg', N'2 viên/lần', 'Uống', 'SDK001', 2, 15000, 30000, 1),
(1, 'TH002', 'Amoxicillin 500mg', 'L002', '2025-02-01', '2026-02-01', 'Vỉ', '500mg', N'1 viên/lần', 'Uống', 'SDK002', 1, 20000, 20000, 1),
(2, 'TH003', 'Vitamin C', 'L003', '2025-03-01', '2026-03-01', 'Lọ', '100mg', N'1 viên/ngày', 'Uống', 'SDK003', 1, 10000, 10000, 1);
GO

-- Dữ liệu mẫu cho PurchaseReceipts
INSERT INTO PurchaseReceipts (local_receipt_id, national_receipt_id, pharmacy_code, shop_pharmacy_code, receipt_date, receipt_type, supplier_name, notes, status, sync_response_message, created_at, updated_at)
VALUES
('PN001', 'QGPN001', 'PHARM001', 'SHOP01', '2025-07-08 10:00:00', 1, N'Công ty Dược ABC', NULL, 'PENDING_SYNC', NULL, GETDATE(), GETDATE()),
('PN002', NULL, 'PHARM001', 'SHOP01', '2025-07-07 11:00:00', 2, N'Khách hàng trả', N'Trả hàng', 'SYNC_SUCCESS', NULL, GETDATE(), GETDATE());
GO

-- Dữ liệu mẫu cho PurchaseReceiptDetails
INSERT INTO PurchaseReceiptDetails (purchase_receipt_id, drug_code, drug_name, lot_number, production_date, expiry_date, registration_number, quantity, unit_price, unit)
VALUES
(1, 'TH001', 'Paracetamol 500mg', 'L001', '2025-01-01', '2026-01-01', 'SDK001', 100, 12000, 'Hộp'),
(2, 'TH002', 'Amoxicillin 500mg', 'L002', '2025-02-01', '2026-02-01', 'SDK002', 50, 18000, 'Vỉ');
GO

-- Dữ liệu mẫu cho GoodsIssueSlips
INSERT INTO GoodsIssueSlips (local_slip_id, national_slip_id, pharmacy_code, shop_pharmacy_code, issue_date, issue_type, recipient_name, notes, status, sync_response_message, created_at, updated_at)
VALUES
('PX001', 'QGPX001', 'PHARM001', 'SHOP01', '2025-07-06 14:00:00', 2, N'Công ty Dược XYZ', N'Trả NCC', 'PENDING_SYNC', NULL, GETDATE(), GETDATE()),
('PX002', NULL, 'PHARM001', 'SHOP01', '2025-07-05 15:00:00', 3, N'Hủy hàng', N'Xuất hủy', 'SYNC_SUCCESS', NULL, GETDATE(), GETDATE());
GO

-- Dữ liệu mẫu cho GoodsIssueSlipDetails
INSERT INTO GoodsIssueSlipDetails (goods_issue_slip_id, drug_code, drug_name, lot_number, production_date, expiry_date, registration_number, quantity, unit_price, unit)
VALUES
(1, 'TH001', 'Paracetamol 500mg', 'L001', '2025-01-01', '2026-01-01', 'SDK001', 10, 12000, 'Hộp'),
(2, 'TH003', 'Vitamin C', 'L003', '2025-03-01', '2026-03-01', 'SDK003', 5, 9000, 'Lọ');
GO

-- Dữ liệu mẫu cho AccountShop
INSERT INTO AccountShop (shop_pharmacy_code, pharmacy_code, account, password, shop_name, address, phone_number, email, status, created_at, updated_at)
VALUES
('SHOP01', 'PHARM001', 'shopuser1', 'pass123', N'Nhà thuốc Trung Tâm', N'123 Đường Lớn, Quận 1, TP.HCM', '0909123456', 'shop1@example.com', 1, '2025-07-01 08:00:00', '2025-07-10 10:00:00'),
('SHOP02', 'PHARM002', 'shopuser2', 'pass456', N'Nhà thuốc Bình Minh', N'456 Đường Nhỏ, Quận 3, TP.HCM', '0912345678', 'shop2@example.com', 1, '2025-07-02 09:00:00', '2025-07-10 11:00:00'),
('SHOP03', 'PHARM003', 'shopuser3', 'pass789', N'Nhà thuốc An Khang', N'789 Đường Mới, Quận 5, TP.HCM', '0923456789', 'shop3@example.com', 0, '2025-07-03 10:00:00', '2025-07-10 12:00:00');
GO
