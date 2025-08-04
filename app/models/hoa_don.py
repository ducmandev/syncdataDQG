from pydantic import BaseModel, Field
from typing import List
from datetime import datetime
class HoaDonHeader(BaseModel):
    ma_hoa_don: str = Field(..., alias="billCode")
    ngay_hoa_don: datetime = Field(..., alias="billDate")
    ten_khach_hang: str = Field(..., alias="customerName")
    tong_tien: float = Field(..., alias="totalAmount")
    class Config:
        orm_mode = True
        allow_population_by_field_name = True

class HoaDonDetail(BaseModel):
    ma_hoa_don: str = Field(..., alias="billCode")
    ma_san_pham: str = Field(..., alias="productCode")
    so_luong: int = Field(..., alias="quantity")
    don_gia: float = Field(..., alias="unitPrice")
    thanh_tien: float = Field(..., alias="amount")
    class Config:
        orm_mode = True
        allow_population_by_field_name = True

class HoaDonDetailModel(BaseModel):
    ma_san_pham: str = Field(..., alias="productCode")
    so_luong: int = Field(..., alias="quantity")
    don_gia: float = Field(..., alias="unitPrice")
    class Config:
        orm_mode = True
        allow_population_by_field_name = True
class HoaDonPayloadModel(BaseModel):
    ma_hoa_don: str = Field(..., alias="billCode")
    ngay_hoa_don: datetime = Field(..., alias="billDate")
    ten_khach_hang: str = Field(..., alias="customerName")
    details: List[HoaDonDetailModel]
    class Config:
        orm_mode = True
        allow_population_by_field_name = True