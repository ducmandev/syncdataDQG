import pytest
from src.workers.tasks import sync_phieu_nhap_task
from unittest.mock import patch

@patch('src.api_clients.partner_nhap.PartnerNhapAPIClient.create_phieu_nhap')
def test_sync_phieu_nhap_task_success(mock_create):
    test_data = {
        "ma_phieu": "PN_TEST",
        "ngay_ct": "2023-01-01T00:00:00",
        "ma_kho": "KHO_TEST",
        "ma_dt": "DT_TEST",
        "dien_giai": "Test task",
        "chi_tiet": [{"ma_vt": "VT_TEST", "ten_vt": "Test", "dvt": "unit", "so_luong": 1, "don_gia": 1000}]
    }
    result = sync_phieu_nhap_task(test_data)
    assert result['status'] == 'success'
    mock_create.assert_called_once()
@patch('src.api_clients.partner_xuat.PartnerXuatAPIClient.create_phieu_xuat')
def test_sync_phieu_xuat_task_success(mock_create):
    test_data = {
        "ma_phieu": "PX_TEST",
        "ngay_ct": "2023-01-01T00:00:00",
        "ma_kho": "KHO_TEST",
        "ma_dt": "DT_TEST",
        "dien_giai": "Test task xuat",
        "chi_tiet": [{"ma_vt": "VT_TEST", "ten_vt": "Test", "dvt": "unit", "so_luong": 2, "don_gia": 2000}]
    }
    from src.workers.tasks import sync_phieu_xuat_task
    result = sync_phieu_xuat_task(test_data)
    assert result['status'] == 'success'
    mock_create.assert_called_once()

from unittest.mock import patch
from src.workers.tasks import sync_hoa_don_task

@patch('src.api_clients.partner_hoadon.PartnerHoaDonAPIClient.create_hoa_don')
def test_sync_hoa_don_task_success(mock_create):
    test_data = {
        "ma_hd": "HD_TEST",
        "ngay_ct": "2023-01-01T00:00:00",
        "ma_dt": "DT_TEST",
        "dia_chi": "123 Đường Test",
        "dien_giai": "Test task hoa don",
        "chi_tiet": [
            {
                "ma_vt": "VT_TEST",
                "ten_vt": "Test",
                "dvt": "unit",
                "so_luong": 1,
                "don_gia": 1000,
                "thanh_tien": 1000
            }
        ]
    }
    result = sync_hoa_don_task(test_data)
    assert result['status'] == 'success'
    mock_create.assert_called_once()