from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional

class ChiTietPhieuNhap(BaseModel):
    ma_vt: str = Field(..., description="Mã vật tư")
    ten_vt: str
    dvt: str
    so_luong: float
    don_gia: float

class PhieuNhapCreate(BaseModel):
    ma_phieu: str = Field(..., max_length=20)
    ngay_ct: datetime
    ma_kho: str
    ma_dt: str
    dien_giai: str
    chi_tiet: List[ChiTietPhieuNhap]
class ChiTietPhieuXuat(BaseModel):
    ma_vt: str
    ten_vt: str
    dvt: str
    so_luong: float
    don_gia: float

class PhieuXuatCreate(BaseModel):
    ma_phieu: str = Field(..., max_length=20)
    ngay_ct: datetime
    ma_kho: str
    ma_dt: str
    dien_giai: str
    chi_tiet: List[ChiTietPhieuXuat]

class ChiTietHoaDon(BaseModel):
    ma_vt: str
    ten_vt: str
    dvt: str
    so_luong: float
    don_gia: float
    thanh_tien: float

class HoaDonCreate(BaseModel):
    ma_hd: str = Field(..., max_length=20)
    ngay_ct: datetime
    ma_dt: str
    dia_chi: str
    dien_giai: str
    chi_tiet: List[ChiTietHoaDon]