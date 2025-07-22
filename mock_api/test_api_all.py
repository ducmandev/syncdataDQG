import requests
import json

BASE_URL = "http://localhost:8000/api/tai_khoan"

def load_users():
    with open("users.json", "r", encoding="utf-8") as f:
        return json.load(f)

def test_create_user(user):
    url = f"{BASE_URL}/tao_moi"
    resp = requests.post(url, json=user)
    print(f"Create user {user['tai_khoan']}: {resp.status_code} {resp.text}")

def test_login(user):
    url = f"{BASE_URL}/dang_nhap"
    payload = {
        "tai_khoan": user["tai_khoan"],
        "mat_khau": user["mat_khau"]
    }
    resp = requests.post(url, json=payload)
    print(f"Login {user['tai_khoan']}: {resp.status_code} {resp.text}")
    if resp.status_code == 200:
        return resp.json().get("access_token")
    return None

def test_get_info(token):
    url = f"{BASE_URL}/thong_tin"
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(url, headers=headers)
    print(f"Get info: {resp.status_code} {resp.text}")

def test_phieu_nhap(token):
    url = "http://localhost:8000/api/phieu_nhap"
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "ma_phieu": "PN001",
        "ma_co_so": "CS001",
        "ngay_nhap": "2025-07-20",
        "loai_phieu_nhap": 1,
        "ghi_chu": "Test nhập",
        "ten_co_so_cung_cap": "Supplier A",
        "chi_tiet": [{"item": "Thuoc A", "so_luong": 10}]
    }
    resp = requests.post(url, json=payload, headers=headers)
    print(f"PhieuNhap: {resp.status_code} {resp.text}")

def test_hoa_don(token):
    url = "http://localhost:8000/api/hoa_don"
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "ma_hoa_don": "HD001",
        "ma_co_so": "CS001",
        "ngay_ban": "2025-07-20",
        "ho_ten_nguoi_ban": "Nguyen Van A",
        "ho_ten_khach_hang": "Le Thi B",
        "hoa_don_chi_tiet": [{"item": "Thuoc B", "so_luong": 5}]
    }
    resp = requests.post(url, json=payload, headers=headers)
    print(f"HoaDon: {resp.status_code} {resp.text}")

def test_phieu_xuat(token):
    url = "http://localhost:8000/api/phieu_xuat"
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "ma_phieu": "PX001",
        "ma_co_so": "CS001",
        "ngay_xuat": "2025-07-20",
        "loai_phieu_xuat": 2,
        "ghi_chu": "Test xuất",
        "ten_co_so_nhan": "Receiver A"
    }
    resp = requests.post(url, json=payload, headers=headers)
    print(f"PhieuXuat: {resp.status_code} {resp.text}")

if __name__ == "__main__":
    users = load_users()
    for user in users:
        test_create_user(user)
        token = test_login(user)
        if token:
            test_get_info(token)
            test_phieu_nhap(token)
            test_hoa_don(token)
            test_phieu_xuat(token)
