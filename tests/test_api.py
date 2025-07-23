import pytest
from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)
from unittest.mock import patch

@patch('src.workers.tasks.sync_phieu_nhap_task.delay')
def test_api_calls_celery_task(mock_task):
    payload = {
        "ma_phieu": "PN001",
        "ngay_ct": "2023-10-10T00:00:00",
        "ma_kho": "KHO01",
        "ma_dt": "DT001",
        "dien_giai": "Nhập hàng tháng 10",
        "chi_tiet": [
            {"ma_vt": "VT01", "ten_vt": "Vật tư 1", "dvt": "cái", "so_luong": 10, "don_gia": 10000}
        ]
    }
    response = client.post("/phieu-nhap", json=payload)
    assert response.status_code == 200
    mock_task.assert_called_once()

def test_nhap_phieu_nhap():
    payload = {
        "ma_phieu": "PN001",
        "ngay_ct": "2023-10-10T00:00:00",
        "ma_kho": "KHO01",
        "ma_dt": "DT001",
        "dien_giai": "Nhập hàng tháng 10",
        "chi_tiet": [
            {"ma_vt": "VT01", "ten_vt": "Vật tư 1", "dvt": "cái", "so_luong": 10, "don_gia": 10000}
        ]
    }
    response = client.post("/phieu-nhap", json=payload)
    assert response.status_code == 200
    assert response.json()["status"] == "success"
from unittest.mock import patch

@patch('src.workers.tasks.sync_phieu_xuat_task.delay')
def test_api_calls_celery_task_xuat(mock_task):
    payload = {
        "ma_phieu": "PX001",
        "ngay_ct": "2023-10-10T00:00:00",
        "ma_kho": "KHO01",
        "ma_dt": "DT001",
        "dien_giai": "Xuất hàng tháng 10",
        "chi_tiet": [
            {"ma_vt": "VT01", "ten_vt": "Vật tư 1", "dvt": "cái", "so_luong": 5, "don_gia": 20000}
        ]
    }
    response = client.post("/phieu-xuat", json=payload)
    assert response.status_code == 200
    mock_task.assert_called_once()

def test_nhap_phieu_xuat():
    payload = {
        "ma_phieu": "PX001",
        "ngay_ct": "2023-10-10T00:00:00",
        "ma_kho": "KHO01",
        "ma_dt": "DT001",
        "dien_giai": "Xuất hàng tháng 10",
        "chi_tiet": [
            {"ma_vt": "VT01", "ten_vt": "Vật tư 1", "dvt": "cái", "so_luong": 5, "don_gia": 20000}
        ]
    }
    response = client.post("/phieu-xuat", json=payload)
    assert response.status_code == 200
    assert response.json()["status"] == "success"

from unittest.mock import patch

@patch('src.workers.tasks.sync_hoa_don_task.delay')
def test_api_calls_celery_task_hoa_don(mock_task):
    payload = {
        "ma_hd": "HD001",
        "ngay_ct": "2023-10-10T00:00:00",
        "ma_dt": "DT001",
        "dia_chi": "123 Đường ABC",
        "dien_giai": "Hóa đơn tháng 10",
        "chi_tiet": [
            {
                "ma_vt": "VT01",
                "ten_vt": "Vật tư 1",
                "dvt": "cái",
                "so_luong": 2,
                "don_gia": 50000,
                "thanh_tien": 100000
            }
        ]
    }
    response = client.post("/hoa-don", json=payload)
    assert response.status_code == 200
    mock_task.assert_called_once()

def test_nhap_hoa_don():
    payload = {
        "ma_hd": "HD001",
        "ngay_ct": "2023-10-10T00:00:00",
        "ma_dt": "DT001",
        "dia_chi": "123 Đường ABC",
        "dien_giai": "Hóa đơn tháng 10",
        "chi_tiet": [
            {
                "ma_vt": "VT01",
                "ten_vt": "Vật tư 1",
                "dvt": "cái",
                "so_luong": 2,
                "don_gia": 50000,
                "thanh_tien": 100000
            }
        ]
    }
    response = client.post("/hoa-don", json=payload)
    assert response.status_code == 200
    assert response.json()["status"] == "success"