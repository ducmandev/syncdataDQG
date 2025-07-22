from pydantic import BaseModel, Field
from typing import List, Optional

class BaseModelIgnoreExtra(BaseModel):
    class Config:
        extra = "ignore"

# 1. Login Models
class LoginRequest(BaseModelIgnoreExtra):
    usr: str
    pwd: str

class LoginResponse(BaseModelIgnoreExtra):
    token: str
    token_type: str

# 2. Sales Invoice Models
class SalesInvoiceDetail(BaseModelIgnoreExtra):
    ma_thuoc: str
    ten_thuoc: str
    so_lo: str
    han_dung: str  # Format: yyyyMMdd
    don_vi_tinh: str
    ham_luong: str
    so_luong: float
    don_gia: float
    thanh_tien: float
    ty_le_quy_doi: float
    lieu_dung: str
    so_dang_ky: str
    ngay_san_xuat: Optional[str] = None
    duong_dung: Optional[str] = None

class SalesInvoice(BaseModelIgnoreExtra):
    ma_hoa_don: str
    ma_co_so: str
    ngay_ban: str  # Format: yyyyMMdd
    hoa_don_chi_tiet: List[SalesInvoiceDetail]
    ma_don_thuoc_quoc_gia: Optional[str] = None
    ho_ten_nguoi_ban: Optional[str] = None
    ho_ten_khach_hang: Optional[str] = None

# 3. Purchase Receipt Models
class PurchaseReceiptDetail(BaseModelIgnoreExtra):
    ma_thuoc: str
    ten_thuoc: str
    so_lo: str
    han_dung: str  # Format: yyyyMMdd
    so_dklh: str
    so_luong: float
    don_vi_tinh: str
    ngay_san_xuat: Optional[str] = None
    don_gia: Optional[float] = None

class PurchaseReceipt(BaseModelIgnoreExtra):
    ma_phieu: str
    ma_co_so: str
    ngay_nhap: str  # Format: yyyyMMdd
    loai_phieu_nhap: int
    chi_tiet: List[PurchaseReceiptDetail]
    ghi_chu: Optional[str] = None
    ten_co_so_cung_cap: Optional[str] = None

# 4. Goods Issue (Cancellation) Models
class GoodsIssueDetail(BaseModelIgnoreExtra):
    ma_thuoc: str
    ten_thuoc: str
    so_lo: str
    han_dung: str  # Format: yyyyMMdd
    so_dklh: str
    so_luong: float
    don_gia: float
    don_vi_tinh: str

class GoodsIssueSlip(BaseModelIgnoreExtra):
    ma_phieu: str
    ma_co_so: str
    ngay_xuat: str  # Format: yyyyMMdd
    loai_phieu_xuat: int
    ghi_chu: str
    chi_tiet: List[GoodsIssueDetail]
    ten_co_so_nhan: Optional[str] = None
