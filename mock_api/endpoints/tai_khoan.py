from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import JSONResponse
from auth import create_access_token, get_current_user
from database import create_user, find_user_by_username
from models import UserCreate, UserLogin

router = APIRouter()

@router.post("/api/tai_khoan/tao_moi", status_code=status.HTTP_201_CREATED)
async def create_new_user(user: UserCreate):
    # Check if username already exists
    if find_user_by_username(user.tai_khoan):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tài khoản đã tồn tại"
        )
    
    # Create new user
    new_user = {
        "tai_khoan": user.tai_khoan,
        "mat_khau": user.mat_khau,
    }
    create_user(new_user)
    return {"message": "Tài khoản được tạo thành công"}

@router.post("/api/tai_khoan/dang_nhap")
async def login_user(user: UserLogin):
    # Find user by username
    db_user = find_user_by_username(user.tai_khoan)
    if not db_user or db_user["mat_khau"] != user.mat_khau:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Tài khoản hoặc mật khẩu không đúng",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create token
    token = create_access_token(data={"sub": user.tai_khoan})
    return {"access_token": token, "token_type": "bearer"}

@router.get("/api/tai_khoan/thong_tin")
async def get_user_info(current_user: dict = Depends(get_current_user)):
    return {
        "tai_khoan": current_user["tai_khoan"],
    }
