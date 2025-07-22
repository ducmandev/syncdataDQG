from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from endpoints import tai_khoan, lien_thong, hoa_don, phieu_nhap, phieu_xuat

app = FastAPI(
    title="Mock API Dược Quốc Gia",
    description="Mock API cho hệ thống liên thông dược quốc gia",
    version="1.0.0"
)

# Cấu hình CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Đăng ký các router
app.include_router(tai_khoan.router, prefix="")
app.include_router(lien_thong.router, prefix="")
app.include_router(hoa_don.router, prefix="")
app.include_router(phieu_nhap.router, prefix="")
app.include_router(phieu_xuat.router, prefix="")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
