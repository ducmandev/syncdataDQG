from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date, datetime

# Pydantic models mapping exactly to DB columns for Phiếu Nhập

class PhieuNhapHeader(BaseModel):
    ma_phieu: str = Field(alias="invoiceCode")
    ngay_nhap: datetime = Field(alias="importDate")
    ten_co_so_cung_cap: str = Field(alias="supplierName")
    dia_chi_co_so_cung_cap: Optional[str] = Field(default=None, alias="supplierAddress")
    so_hoa_don: Optional[str] = Field(default=None, alias="invoiceNumber")
    ngay_hoa_don: Optional[date] = Field(default=None, alias="invoiceDate")
    tong_tien: float = Field(alias="totalAmount")
    ghi_chu: Optional[str] = Field(default=None, alias="note")

    class Config:
        allow_population_by_field_name = True
        orm_mode = True

class PhieuNhapDetail(BaseModel):
    ma_phieu: str = Field(alias="invoiceCode")
    ma_thuoc: str = Field(alias="medicineCode")
    ten_thuoc: str = Field(alias="medicineName")
    so_lo: str = Field(alias="batchNumber")
    ngay_san_xuat: Optional[date] = Field(default=None, alias="manufactureDate")
    han_dung: date = Field(alias="expiryDate")
    so_dklh: Optional[str] = Field(default=None, alias="registrationNumber")
    so_luong: int = Field(alias="quantity")
    don_gia: float = Field(alias="unitPrice")
    thanh_tien: float = Field(alias="amount")
    don_vi_tinh: str = Field(alias="unit")

    class Config:
        allow_population_by_field_name = True
        orm_mode = True
