from fastapi import FastAPI, HTTPException
from src.core.models import PhieuNhapCreate
from src.core.models import PhieuXuatCreate
from src.core.models import HoaDonCreate
from src.core.app import process_incoming_phieu_xuat
from src.core.app import process_incoming_phieu_nhap
from src.core.app import process_incoming_hoa_don
import logging

app = FastAPI()
logger = logging.getLogger("api")

@app.post("/phieu-nhap")
async def nhap_phieu_nhap(phieu_nhap: PhieuNhapCreate):
    try:
        logger.info(f"Nhận phiếu nhập: {phieu_nhap.ma_phieu}")
        process_incoming_phieu_nhap(phieu_nhap.model_dump())
        return {"status": "success", "message": "Phiếu nhập đang được xử lý"}
    except Exception as e:
        logger.error(f"Lỗi xử lý phiếu nhập: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/phieu-xuat")
async def nhap_phieu_xuat(phieu_xuat: PhieuXuatCreate):
    try:
        logger.info(f"Nhận phiếu xuất: {phieu_xuat.ma_phieu}")
        process_incoming_phieu_xuat(phieu_xuat.model_dump())
        return {"status": "success", "message": "Phiếu xuất đang được xử lý"}
    except Exception as e:
        logger.error(f"Lỗi xử lý phiếu xuất: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/hoa-don")
async def nhap_hoa_don(hoa_don: HoaDonCreate):
    try:
        logger.info(f"Nhận hóa đơn: {hoa_don.ma_hd}")
        process_incoming_hoa_don(hoa_don.model_dump())
        return {"status": "success", "message": "Hóa đơn đang được xử lý"}
    except Exception as e:
        logger.error(f"Lỗi xử lý hóa đơn: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))