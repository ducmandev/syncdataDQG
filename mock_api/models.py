from pydantic import BaseModel
from typing import Optional, List

class UserCreate(BaseModel):
    shop_id: str
    ma_co_so: str
    tai_khoan: str
    mat_khau: str

class UserLogin(BaseModel):
    tai_khoan: str
    mat_khau: str

class HoaDon(BaseModel):
    ma_hoa_don: str
    ma_co_so: str
    ma_don_thuoc_quoc_gia: Optional[str] = None
    ngay_ban: str
    ho_ten_nguoi_ban: Optional[str] = None
    ho_ten_khach_hang: Optional[str] = None
    hoa_don_chi_tiet: List[dict]

class PhieuNhap(BaseModel):
    ma_phieu: str
    ma_co_so: str
    ngay_nhap: str
    loai_phieu_nhap: int
    ghi_chu: Optional[str] = None
    ten_co_so_cung_cap: Optional[str] = None
    chi_tiet: List[dict]

class PhieuXuat(BaseModel):
    ma_phieu: str
    ma_co_so: str
    ngay_xuat: str
    loai_phieu_xuat: int
    ghi_chu: str
    ten_co_so_nhan: Optional[str] = None

class HoaDonCreate(BaseModel):
    tong_tien: float

class HoaDonResponse(BaseModel):
    pass

class PhieuNhapCreate(BaseModel):
    tong_tien: float

class PhieuNhapResponse(BaseModel):
    pass

class PhieuXuatCreate(BaseModel):
    pass

class PhieuXuatResponse(BaseModel):
    pass
