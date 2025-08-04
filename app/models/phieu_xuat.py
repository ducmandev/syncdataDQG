from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, datetime

# Pydantic models mapping exactly to DB columns for Phiếu Xuất

class PhieuXuatHeader(BaseModel):
    ma_phieu: str = Field(alias="invoiceCode")
    ngay_xuat: datetime = Field(alias="exportDate")
    ten_nguoi_nhan: str = Field(alias="recipientName")
    dia_chi_nguoi_nhan: Optional[str] = Field(default=None, alias="recipientAddress")
    ly_do_xuat: Optional[str] = Field(default=None, alias="reason")
    tong_tien: float = Field(alias="totalAmount")
    ghi_chu: Optional[str] = Field(default=None, alias="note")

    class Config:
        allow_population_by_field_name = True
        orm_mode = True

class PhieuXuatDetail(BaseModel):
    ma_phieu: str = Field(alias="invoiceCode")
    ma_thuoc: str = Field(alias="medicineCode")
    ten_thuoc: str = Field(alias="medicineName")
    so_lo: str = Field(alias="batchNumber")
    han_dung: date = Field(alias="expiryDate")
    so_luong: int = Field(alias="quantity")
    don_gia: float = Field(alias="unitPrice")
    thanh_tien: float = Field(alias="amount")
    don_vi_tinh: str = Field(alias="unit")

    class Config:
        allow_population_by_field_name = True
        orm_mode = True