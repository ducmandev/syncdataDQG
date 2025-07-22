from fastapi import APIRouter, Depends, HTTPException, Header
from typing import Optional

router = APIRouter(prefix="/api/lien_thong", tags=["Liên thông"])

# Hàm kiểm tra token (tạm thời)
def verify_token(authorization: str = Header(...)):
    # Accept any Bearer token for mock purposes
    if not authorization.startswith("Bearer ") or len(authorization.split(" ")[1]) < 10:
        raise HTTPException(status_code=401, detail="Token không hợp lệ")
    return True

@router.post("/hoa_don", summary="Gửi hóa đơn liên thông")
async def hoa_don(
    payload: dict,
    token_valid: bool = Depends(verify_token)
):
    # Xử lý hóa đơn ở đây (tạm thời trả về response mẫu)
    return {
        "status": "success",
        "message": "Hóa đơn đã được tiếp nhận",
        "ma_hoa_don": "HD_123456"
    }

@router.post("/phieu_nhap", summary="Gửi phiếu nhập liên thông")
async def phieu_nhap(
    payload: dict,
    token_valid: bool = Depends(verify_token)
):
    # Xử lý phiếu nhập ở đây
    return {
        "status": "success",
        "message": "Phiếu nhập đã được tiếp nhận",
        "ma_phieu_nhap": "PN_789012"
    }

@router.post("/phieu_xuat", summary="Gửi phiếu xuất liên thông")
async def phieu_xuat(
    payload: dict,
    token_valid: bool = Depends(verify_token)
):
    # Xử lý phiếu xuất ở đây
    return {
        "status": "success",
        "message": "Phiếu xuất đã được tiếp nhận",
        "ma_phieu_xuat": "PX_345678"
    }
