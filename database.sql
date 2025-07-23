-- =================================================================
-- 1. TẠO DATABASE NẾU CHƯA TỒN TẠI
-- =================================================================
IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = N'DQG')
BEGIN
    CREATE DATABASE DQG;
END
GO

USE DQG;
GO

-- =================================================================
-- 2. TẠO CẤU TRÚC CÁC BẢNG
-- =================================================================

-- Bảng chứa thông tin chung của phiếu xuất kho
CREATE TABLE PhieuXuatHeader (
    ma_phieu NVARCHAR(50) PRIMARY KEY,
    ma_phieu_xuat_quoc_gia NVARCHAR(250) NULL,
    ma_co_so NVARCHAR(50),
    shop_code INT,
    ngay_xuat DATE,
    loai_phieu_xuat INT,
    ghi_chu NVARCHAR(MAX),
    ten_co_so_nhan NVARCHAR(255),
    dateinsert DATETIME DEFAULT GETDATE(),
    status_phieu INT,
    note_log NVARCHAR(MAX) NULL
);
GO

-- Bảng chứa thông tin chi tiết sản phẩm của phiếu xuất kho
CREATE TABLE PhieuXuatDetail (
    id INT IDENTITY(1,1) PRIMARY KEY,
    ma_phieu NVARCHAR(50),
    ma_thuoc NVARCHAR(50),
    ten_thuoc NVARCHAR(255),
    so_lo NVARCHAR(50),
    ngay_san_xuat DATE NULL,
    han_dung DATE,
    so_dklh NVARCHAR(50),
    so_luong INT,
    don_gia DECIMAL(18, 2),
    don_vi_tinh NVARCHAR(50),
    FOREIGN KEY (ma_phieu) REFERENCES PhieuXuatHeader(ma_phieu)
);
GO

-- Bảng chứa thông tin chung của hóa đơn bán hàng
CREATE TABLE HoaDonHeader (
    ma_hoa_don NVARCHAR(50) PRIMARY KEY,
    ma_co_so NVARCHAR(50),
    ma_don_thuoc_quoc_gia NVARCHAR(50) NULL,
    ngay_ban DATE,
    ho_ten_khach_hang NVARCHAR(255),
    ho_ten_nguoi_ban NVARCHAR(255),
    status_phieu INT,
    note_log NVARCHAR(MAX) NULL
);
GO

-- Bảng chứa thông tin chi tiết sản phẩm của hóa đơn bán hàng
CREATE TABLE HoaDonDetail (
    id INT IDENTITY(1,1) PRIMARY KEY,
    ma_hoa_don NVARCHAR(50),
    ma_thuoc NVARCHAR(50),
    ten_thuoc NVARCHAR(500),
    so_lo NVARCHAR(50),
    ngay_san_xuat DATE,
    han_dung DATE,
    don_vi_tinh NVARCHAR(50),
    ham_luong NVARCHAR(100),
    duong_dung NVARCHAR(100),
    lieu_dung NVARCHAR(255),
    so_dang_ky NVARCHAR(50),
    so_luong INT,
    don_gia DECIMAL(18, 2),
    thanh_tien DECIMAL(18, 2),
    ty_le_quy_doi DECIMAL(18, 4),
    FOREIGN KEY (ma_hoa_don) REFERENCES HoaDonHeader(ma_hoa_don)
);
GO

-- =================================================================
-- 3. TẠO CẤU TRÚC BẢNG PHIẾU NHẬP KHO
-- =================================================================

-- Bảng chứa thông tin chung của phiếu nhập kho
CREATE TABLE PhieuNhapHeader (
    ma_phieu NVARCHAR(50) PRIMARY KEY,
    ma_phieu_nhap_quoc_gia NVARCHAR(250) NULL,
    ma_co_so NVARCHAR(50),
    ngay_nhap DATETIME,
    loai_phieu_nhap INT,
    ghi_chu NVARCHAR(MAX),
    ten_co_so_cung_cap NVARCHAR(255),
    dateinsert DATETIME DEFAULT GETDATE(),
    status_phieu INT,
    note_log NVARCHAR(MAX) NULL
);
GO

-- Bảng chứa thông tin chi tiết sản phẩm của phiếu nhập kho
CREATE TABLE PhieuNhapDetail (
    id INT IDENTITY(1,1) PRIMARY KEY,
    ma_phieu NVARCHAR(50),
    ma_thuoc NVARCHAR(50),
    ten_thuoc NVARCHAR(255),
    so_lo NVARCHAR(50),
    ngay_san_xuat DATE NULL,
    han_dung DATE,
    so_dklh NVARCHAR(50),
    so_luong INT,
    don_gia DECIMAL(18, 2),
    thanh_tien DECIMAL(18, 2),
    don_vi_tinh NVARCHAR(50),
    FOREIGN KEY (ma_phieu) REFERENCES PhieuNhapHeader(ma_phieu)
);
GO
