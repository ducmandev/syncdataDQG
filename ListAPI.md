Chắc chắn rồi! Dưới đây là tài liệu API được trình bày dưới dạng file Markdown, giúp bạn dễ dàng đọc, chia sẻ và tích hợp vào các công cụ quản lý tài liệu như GitHub, GitLab, hoặc Notion.

Bạn có thể sao chép toàn bộ nội dung bên dưới và lưu vào một file có đuôi `.md` (ví dụ: `api_duoc_quoc_gia.md`).

```markdown
# Tài liệu API Liên thông Hệ thống Dược Quốc gia

Tài liệu này mô tả các API để phần mềm quản lý của cơ sở GPP (Nhà thuốc, Quầy thuốc) kết nối và đồng bộ dữ liệu với Hệ thống Dược Quốc gia.

**Luồng làm việc chung:**
1.  Gọi API **Đăng nhập** để lấy `token` xác thực.
2.  Sử dụng `token` này trong Header `Authorization` cho tất cả các API nghiệp vụ khác (liên thông hóa đơn, phiếu nhập, phiếu xuất).

---

## 1. Đăng nhập và Lấy Token

Xác thực tài khoản của cơ sở và lấy `token` (mã phiên làm việc) để sử dụng cho các API khác.

-   **Method:** `POST`
-   **URL:** `/api/tai_khoan/dang_nhap`
-   **Header:**
    -   `Content-Type: application/json`

#### Dữ liệu gửi lên (Request Body)
```json
{
  "usr": "{username}",
  "pwd": "{password}"
}
```

#### Chi tiết Dữ liệu đầu vào
| Tên Field | Kiểu dữ liệu | Kích thước tối đa | Bắt buộc | Ghi chú |
| :--- | :--- | :--- | :---: | :--- |
| `usr` | Chuỗi ký tự | 50 | ✅ | Tên đăng nhập do hệ thống Dược quốc gia cung cấp. |
| `pwd` | Chuỗi ký tự | 30 | ✅ | Mật khẩu tài khoản. |

#### Dữ liệu trả về (Response)

-   **Trường hợp thành công (Status `200 OK`)**
    ```json
    {
      "token": "xxxxxxxxxxxxx.xxxxxxxx.xxxxxx",
      "token_type": "bearer"
    }
    ```
-   **Trường hợp lỗi (Status `400 Bad Request`)**
    -   Tên đăng nhập hoặc mật khẩu không đúng.

---

## 2. Liên thông Hóa đơn Bán thuốc

Gửi thông tin hóa đơn bán thuốc của cơ sở lên hệ thống Dược quốc gia.

-   **Method:** `POST`
-   **URL:** `/api/lien_thong/hoa_don`
-   **Header:**
    -   `Content-Type: application/json`
    -   `Authorization: bearer {token}` (Token lấy từ API Đăng nhập)

#### Dữ liệu gửi lên (Request Body)
```json
{
  "ma_hoa_don": "string",
  "ma_co_so": "string",
  "ma_don_thuoc_quoc_gia": "string",
  "ngay_ban": "string",
  "ho_ten_nguoi_ban": "string",
  "ho_ten_khach_hang": "string",
  "hoa_don_chi_tiet": [
    {
      "ma_thuoc": "string",
      "ten_thuoc": "string",
      "so_lo": "string",
      "ngay_san_xuat": "string",
      "han_dung": "string",
      "don_vi_tinh": "string",
      "ham_luong": "string",
      "duong_dung": "string",
      "lieu_dung": "string",
      "so_dang_ky": "string",
      "so_luong": 0,
      "don_gia": 0,
      "thanh_tien": 0,
      "ty_le_quy_doi": 0
    }
  ]
}
```

#### Chi tiết Dữ liệu đầu vào
| Tên Field | Kiểu dữ liệu | Kích thước tối đa | Bắt buộc | Ghi chú |
| :--- | :--- | :--- | :---: | :--- |
| `ma_hoa_don` | Chuỗi ký tự | 50 | ✅ | Mã hóa đơn của cơ sở. |
| `ma_co_so` | Chuỗi ký tự | 50 | ✅ | Mã cơ sở GPP do hệ thống Dược quốc gia cấp. |
| `ma_don_thuoc_quoc_gia` | Chuỗi ký tự | 50 | | Mã đơn thuốc bán theo hóa đơn mua thuốc. |
| `ngay_ban` | Chuỗi ký tự | 12 | ✅ | Định dạng: `yyyyMMdd`. |
| `ho_ten_nguoi_ban` | Chuỗi ký tự | 50 | | Họ tên người bán. |
| `ho_ten_khach_hang` | Chuỗi ký tự | 50 | | Họ tên khách mua thuốc. |
| `hoa_don_chi_tiet[].ma_thuoc` | Chuỗi ký tự | 50 | ✅ | Mã thuốc do hệ thống Dược quốc gia cung cấp. |
| `hoa_don_chi_tiet[].ten_thuoc` | Chuỗi ký tự | 500 | ✅ | Tên thuốc. |
| `hoa_don_chi_tiet[].so_lo` | Chuỗi ký tự | 50 | ✅ | Số lô của thuốc. |
| `hoa_don_chi_tiet[].ngay_san_xuat` | Chuỗi ký tự | 12 | | Ngày sản xuất. Định dạng: `yyyyMMdd`. |
| `hoa_don_chi_tiet[].han_dung` | Chuỗi ký tự | 12 | ✅ | Hạn dùng. Định dạng: `yyyyMMdd`. |
| `hoa_don_chi_tiet[].don_vi_tinh` | Chuỗi ký tự | 50 | ✅ | Tên đơn vị tính của thuốc. |
| `hoa_don_chi_tiet[].ham_luong` | Chuỗi ký tự | 500 | ✅ | Hàm lượng hoạt chất chính. |
| `hoa_don_chi_tiet[].so_luong` | Số | | ✅ | Số lượng thuốc theo đơn vị tính. |
| `hoa_don_chi_tiet[].don_gia` | Số | | ✅ | Đơn giá thuốc. |
| `hoa_don_chi_tiet[].thanh_tien` | Số | | ✅ | Thành tiền. |
| `hoa_don_chi_tiet[].ty_le_quy_doi` | Số | | ✅ | Tỷ lệ quy đổi so với đơn vị cơ bản. |
| `hoa_don_chi_tiet[].lieu_dung` | Chuỗi ký tự | n | ✅ | Liều dùng. |
| `hoa_don_chi_tiet[].duong_dung` | Chuỗi ký tự | 200 | | Đường dùng. |


#### Dữ liệu trả về (Response)

-   **Trường hợp thành công (Status `200 OK`)**
    ```json
    {
      "ma_hoa_don": "HD_QG_xxxxxxx",
      "code": 200,
      "mess": "Thành công"
    }
    ```
-   **Trường hợp lỗi**
    -   **Status `401 Unauthorized`**: Tài khoản chưa xác thực (token không hợp lệ hoặc hết hạn).
    -   **Status `400 Bad Request`**: Dữ liệu đầu vào chưa hợp lệ (Mã cơ sở không chính xác, Ngày bán không đúng định dạng...).

---

## 3. Liên thông Phiếu Nhập kho

Gửi thông tin phiếu nhập kho thuốc (từ nhà cung cấp, khách trả, nhập tồn) lên hệ thống Dược quốc gia.

-   **Method:** `POST`
-   **URL:** `/api/lien_thong/phieu_nhap`
-   **Header:**
    -   `Content-Type: application/json`
    -   `Authorization: bearer {token}`

#### Dữ liệu gửi lên (Request Body)
```json
{
  "ma_phieu": "string",
  "ma_co_so": "string",
  "ngay_nhap": "string",
  "loai_phieu_nhap": 0,
  "ghi_chu": "string",
  "ten_co_so_cung_cap": "string",
  "chi_tiet": [
    {
      "ma_thuoc": "string",
      "ten_thuoc": "string",
      "so_lo": "string",
      "ngay_san_xuat": "string",
      "han_dung": "string",
      "so_dklh": "string",
      "so_luong": 0,
      "don_gia": 0,
      "don_vi_tinh": "string"
    }
  ]
}
```

#### Chi tiết Dữ liệu đầu vào
| Tên Field | Kiểu dữ liệu | Kích thước tối đa | Bắt buộc | Ghi chú |
| :--- | :--- | :--- | :---: | :--- |
| `ma_phieu` | Chuỗi ký tự | 50 | ✅ | Mã phiếu nhập của cơ sở GPP. |
| `ma_co_so` | Chuỗi ký tự | 50 | ✅ | Mã cơ sở GPP do hệ thống Dược quốc gia cấp. |
| `ngay_nhap` | Chuỗi ký tự | 12 | ✅ | Ngày nhập. Định dạng: `yyyyMMdd`. |
| `loai_phieu_nhap` | Số | | ✅ | 1: Nhập từ nhà cung cấp, 2: Khách trả, 3: Nhập tồn. |
| `ghi_chu` | Chuỗi ký tự | 500 | | Ghi chú. |
| `ten_co_so_cung_cap` | Chuỗi ký tự | 500 | | Tên cơ sở cung cấp (nếu `loai_phieu_nhap` là 1). |
| `chi_tiet[].ma_thuoc` | Chuỗi ký tự | 50 | ✅ | Mã thuốc do hệ thống Dược quốc gia cung cấp. |
| `chi_tiet[].ten_thuoc` | Chuỗi ký tự | 500 | ✅ | Tên thuốc. |
| `chi_tiet[].so_lo` | Chuỗi ký tự | 50 | ✅ | Số lô thuốc. |
| `chi_tiet[].han_dung` | Chuỗi ký tự | 12 | ✅ | Hạn dùng. Định dạng: `yyyyMMdd`. |
| `chi_tiet[].so_dklh` | Chuỗi ký tự | 50 | ✅ | Số đăng ký lưu hành của thuốc. |
| `chi_tiet[].so_luong` | Số | | ✅ | Số lượng thuốc (đơn vị tính nhỏ nhất). |
| `chi_tiet[].don_gia` | Số | | | Đơn giá thuốc. |
| `chi_tiet[].don_vi_tinh` | Chuỗi ký tự | 200 | ✅ | Tên đơn vị tính nhỏ nhất của thuốc. |

#### Dữ liệu trả về (Response)

-   **Trường hợp thành công (Status `200 OK`)**
    -   Body trả về là một chuỗi (string) chứa mã phiếu nhập trên hệ thống quốc gia.
    -   *Ví dụ:* `"PN_QG_12345678"`
-   **Trường hợp lỗi**
    -   **Status `401 Unauthorized`**: Tài khoản chưa xác thực.
    -   **Status `400 Bad Request`**: Dữ liệu đầu vào không hợp lệ (Ngày nhập sai định dạng, Mã cơ sở không chính xác, Mã phiếu trống...).

---

## 4. Liên thông Phiếu Xuất kho

Gửi thông tin phiếu xuất kho thuốc (trả nhà cung cấp, xuất hủy) lên hệ thống Dược quốc gia.

-   **Method:** `POST`
-   **URL:** `/api/lien_thong/phieu_xuat`
-   **Header:**
    -   `Content-Type: application/json`
    -   `Authorization: bearer {token}`

#### Dữ liệu gửi lên (Request Body)
```json
{
  "ma_phieu": "string",
  "ma_co_so": "string",
  "ngay_xuat": "string",
  "loai_phieu_xuat": 0,
  "ghi_chu": "string",
  "ten_co_so_nhan": "string",
  "chi_tiet": [
    {
      "ma_thuoc": "string",
      "ten_thuoc": "string",
      "so_lo": "string",
      "han_dung": "string",
      "so_dklh": "string",
      "so_luong": 0,
      "don_gia": 0,
      "don_vi_tinh": "string"
    }
  ]
}
```

#### Chi tiết Dữ liệu đầu vào
| Tên Field | Kiểu dữ liệu | Kích thước tối đa | Bắt buộc | Ghi chú |
| :--- | :--- | :--- | :---: | :--- |
| `ma_phieu` | Chuỗi ký tự | 50 | ✅ | Mã phiếu xuất của cơ sở GPP. |
| `ma_co_so` | Chuỗi ký tự | 50 | ✅ | Mã cơ sở GPP do hệ thống Dược quốc gia cấp. |
| `ngay_xuat` | Chuỗi ký tự | 12 | ✅ | Ngày xuất. Định dạng: `yyyyMMdd`. |
| `loai_phieu_xuat` | Số | | ✅ | 2: Xuất trả nhà cung cấp, 3: Xuất hủy. |
| `ghi_chu` | Chuỗi ký tự | 500 | ✅ | Ghi chú. |
| `ten_co_so_nhan` | Chuỗi ký tự | 500 | | Tên cơ sở nhận. |
| `chi_tiet[].ma_thuoc` | Chuỗi ký tự | 50 | ✅ | Mã thuốc do hệ thống Dược quốc gia cung cấp. |
| `chi_tiet[].ten_thuoc` | Chuỗi ký tự | 500 | ✅ | Tên thuốc. |
| `chi_tiet[].so_lo` | Chuỗi ký tự | 50 | ✅ | Số lô thuốc. |
| `chi_tiet[].han_dung` | Chuỗi ký tự | 12 | ✅ | Hạn dùng. Định dạng: `yyyyMMdd`. |
| `chi_tiet[].so_dklh` | Chuỗi ký tự | 50 | ✅ | Số đăng ký lưu hành của thuốc. |
| `chi_tiet[].so_luong` | Số | | ✅ | Số lượng thuốc (đơn vị tính nhỏ nhất). |
| `chi_tiet[].don_gia` | Số | | ✅ | Đơn giá thuốc. |
| `chi_tiet[].don_vi_tinh` | Chuỗi ký tự | 200 | ✅ | Tên đơn vị tính nhỏ nhất của thuốc. |

#### Dữ liệu trả về (Response)

-   **Trường hợp thành công (Status `200 OK`)**
    -   Body trả về là một chuỗi (string) chứa mã phiếu xuất trên hệ thống quốc gia.
    -   *Ví dụ:* `"PX_QG_12345678"`
-   **Trường hợp lỗi**
    -   **Status `401 Unauthorized`**: Tài khoản chưa xác thực.
    -   **Status `400 Bad Request`**: Dữ liệu đầu vào không hợp lệ (Ngày xuất sai định dạng, Mã cơ sở không chính xác, Mã phiếu trống...).

```