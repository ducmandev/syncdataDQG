from fastapi import APIRouter, Depends, HTTPException, status
from auth import get_current_user
from models import PhieuNhapCreate, PhieuNhapResponse

router = APIRouter()

@router.post("/api/phieu_nhap", response_model=PhieuNhapResponse, status_code=status.HTTP_201_CREATED)
async def create_phieu_nhap(phieu_nhap: PhieuNhapCreate, current_user: dict = Depends(get_current_user)):
    # TODO: Implement actual receipt creation logic
    return {
        "ma_phieu_nhap": "PN001",
        "ngay_tao": "2025-07-15",
        "tong_tien": phieu_nhap.tong_tien,
        "trang_thai": "CREATED"
    }