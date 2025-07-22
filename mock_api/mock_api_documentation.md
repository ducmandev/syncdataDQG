# Mock API Documentation

This document describes all endpoints in the mock_api service and provides sample data for testing.

---

## 1. Đăng nhập (Login)

**POST** `/api/tai_khoan/dang_nhap`

**Request:**
```json
{
  "usr": "user1",
  "pwd": "password1"
}
```

**Response:**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyMSIsImV4cCI6MTc1MzAzMTc0MX0.4vE7403AAB6HkS719Fx5abnssdjADSY3PEQj5QN5o4A",
  "token_type": "bearer"
}
```

---

## 2. Tạo mới tài khoản (Create User)

**POST** `/api/tai_khoan/tao_moi`

**Request:**
```json
{
  "shop_id": "SHOP001",
  "ma_co_so": "CS001",
  "tai_khoan": "user1",
  "mat_khau": "password1"
}
```

---

## 3. Lấy thông tin tài khoản (Get User Info)

**GET** `/api/tai_khoan/thong_tin`

**Header:**
```
Authorization: Bearer {token}
```

---

## 4. Liên thông Hóa Đơn

**POST** `/api/lien_thong/hoa_don`

**Header:**
```
Authorization: Bearer {token}
Content-Type: application/json
```

**Request:**
```json
{
  "ma_hoa_don": "HD001",
  "ma_co_so": "CS001",
  "ma_don_thuoc_quoc_gia": "DTQG001",
  "ngay_ban": "20250720",
  "ho_ten_nguoi_ban": "Nguyen Van A",
  "ho_ten_khach_hang": "Le Thi B",
  "hoa_don_chi_tiet": [
    {
      "ma_thuoc": "T001",
      "ten_thuoc": "Thuoc B",
      "so_lo": "L001",
      "ngay_san_xuat": "20250101",
      "han_dung": "20260101",
      "don_vi_tinh": "hop",
      "ham_luong": "500mg",
      "duong_dung": "Uong",
      "lieu_dung": "2 vien/ngay",
      "so_dang_ky": "SDK001",
      "so_luong": 5,
      "don_gia": 10000,
      "thanh_tien": 50000,
      "ty_le_quy_doi": 1
    }
  ]
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Hóa đơn đã được tiếp nhận",
  "ma_hoa_don": "HD_123456"
}
```

---

## 5. Liên thông Phiếu Nhập

**POST** `/api/lien_thong/phieu_nhap`

**Header:**
```
Authorization: Bearer {token}
Content-Type: application/json
```

**Request:**
```json
{
  "ma_phieu": "PN001",
  "ma_co_so": "CS001",
  "ngay_nhap": "20250720",
  "loai_phieu_nhap": 1,
  "ghi_chu": "Test nhập",
  "ten_co_so_cung_cap": "Supplier A",
  "chi_tiet": [
    {
      "ma_thuoc": "T001",
      "ten_thuoc": "Thuoc A",
      "so_lo": "L001",
      "ngay_san_xuat": "20250101",
      "han_dung": "20260101",
      "so_dklh": "DKLH001",
      "so_luong": 10,
      "don_gia": 5000,
      "don_vi_tinh": "hop"
    }
  ]
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Phiếu nhập đã được tiếp nhận",
  "ma_phieu_nhap": "PN_789012"
}
```

---

## 6. Liên thông Phiếu Xuất

**POST** `/api/lien_thong/phieu_xuat`

**Header:**
```
Authorization: Bearer {token}
Content-Type: application/json
```

**Request (Xuất trả nhà cung cấp):**
```json
{
  "ma_phieu": "PX001",
  "ma_co_so": "CS001",
  "ngay_xuat": "20250720",
  "loai_phieu_xuat": 2,
  "ghi_chu": "Test xuất",
  "ten_co_so_nhan": "Receiver A",
  "chi_tiet": [
    {
      "ma_thuoc": "T002",
      "ten_thuoc": "Thuoc C",
      "so_lo": "L002",
      "han_dung": "20260101",
      "so_dklh": "DKLH002",
      "so_luong": 3,
      "don_gia": 7000,
      "don_vi_tinh": "hop"
    }
  ]
}
```

**Request (Xuất hủy):**
```json
{
  "ma_phieu": "PX002",
  "ma_co_so": "CS001",
  "ngay_xuat": "20250720",
  "loai_phieu_xuat": 3,
  "ghi_chu": "Xuất hủy thuốc hết hạn",
  "ten_co_so_nhan": "",
  "chi_tiet": [
    {
      "ma_thuoc": "T003",
      "ten_thuoc": "Thuoc D",
      "so_lo": "L003",
      "han_dung": "20250101",
      "so_dklh": "DKLH003",
      "so_luong": 2,
      "don_gia": 0,
      "don_vi_tinh": "hop"
    }
  ]
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Phiếu xuất đã được tiếp nhận",
  "ma_phieu_xuat": "PX_345678"
}
```

---

## Sample Token

```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyMSIsImV4cCI6MTc1MzAzMTc0MX0.4vE7403AAB6HkS719Fx5abnssdjADSY3PEQj5QN5o4A
```

Use this token for Authorization header in all liên thông requests.
