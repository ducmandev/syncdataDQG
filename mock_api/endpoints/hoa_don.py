from fastapi import APIRouter, Depends, HTTPException, status
from auth import get_current_user
from models import HoaDonCreate, HoaDonResponse

router = APIRouter()

@router.post("/api/hoa_don", response_model=HoaDonResponse, status_code=status.HTTP_201_CREATED)
async def create_hoa_don(hoa_don: HoaDonCreate, current_user: dict = Depends(get_current_user)):
    # TODO: Implement actual invoice creation logic
    return {
        "ma_hoa_don": "HD001",
        "ngay_tao": "2025-07-15",
        "tong_tien": hoa_don.tong_tien,
        "trang_thai": "CREATED"
    }