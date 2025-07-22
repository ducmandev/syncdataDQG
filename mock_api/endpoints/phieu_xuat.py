from fastapi import APIRouter, Depends, HTTPException, status
from auth import get_current_user
from models import PhieuXuatCreate, PhieuXuatResponse

router = APIRouter()

@router.post("/api/phieu_xuat", response_model=PhieuXuatResponse, status_code=status.HTTP_201_CREATED)
async def create_phieu_xuat(phieu_xuat: PhieuXuatCreate, current_user: dict = Depends(get_current_user)):
    # TODO: Implement actual export creation logic
    return {
        "ma_phieu_xuat": "PX001",
        "ngay_tao": "2025-07-15",
        "tong_tien": phieu_xuat.tong_tien,
        "trang_thai": "CREATED"
    }