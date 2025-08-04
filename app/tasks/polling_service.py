from app.main import celery_app
from app.db.mssql import get_db_connection
from .phieu_nhap_worker import process_phieu_nhap_task
from .phieu_xuat_worker import process_phieu_xuat_task
# Import các worker khác ở đây khi chúng được tạo
import logging
from app.tasks.hoa_don_worker import process_hoa_don_task

@celery_app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # Chạy task mỗi 5 phút
    sender.add_periodic_task(300.0, find_pending_invoices.s(), name='find-all-pending-invoices')

@celery_app.task(name="tasks.find_pending_invoices")
def find_pending_invoices():
    """Quét tất cả các loại phiếu và đẩy vào hàng đợi tương ứng."""
    logging.info("Bắt đầu quét các phiếu chờ xử lý...")
    find_phieu_nhap()
    prepare_and_dispatch_phieu_xuat()
    prepare_and_dispatch_hoa_don()

def find_phieu_nhap():
    """Tìm và đưa các phiếu nhập vào hàng đợi, kèm header và details."""
    from app.models.phieu_nhap import PhieuNhapHeader, PhieuNhapDetail
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # 1. Fetch all pending headers
        query_headers = """
            SELECT ma_phieu, ngay_nhap, ten_co_so_cung_cap, dia_chi_co_so_cung_cap, so_hoa_don, ngay_hoa_don, tong_tien, ghi_chu
            FROM PhieuNhapHeader
            WHERE status_phieu IN (0, 2)
            ORDER BY ngay_nhap ASC
        """
        cursor.execute(query_headers)
        header_rows = cursor.fetchall()
        if not header_rows:
            logging.info("Không có phiếu nhập chờ xử lý.")
            return

        # Build a map of ma_phieu to header
        headers = {}
        ma_phieu_list = []
        for row in header_rows:
            header = PhieuNhapHeader(
                ma_phieu=row[0],
                ngay_nhap=row[1],
                ten_co_so_cung_cap=row[2],
                dia_chi_co_so_cung_cap=row[3],
                so_hoa_don=row[4],
                ngay_hoa_don=row[5],
                tong_tien=row[6],
                ghi_chu=row[7]
            )
            headers[row[0]] = header
            ma_phieu_list.append(row[0])

        # 2. Fetch all details in batch
        format_strings = ','.join(['?'] * len(ma_phieu_list))
        query_details = f"""
            SELECT ma_phieu, ma_thuoc, ten_thuoc, so_lo, ngay_san_xuat, han_dung, so_dklh, so_luong, don_gia, thanh_tien, don_vi_tinh
            FROM PhieuNhapDetail
            WHERE ma_phieu IN ({format_strings})
        """
        cursor.execute(query_details, ma_phieu_list)
        detail_rows = cursor.fetchall()

        # Group details by ma_phieu
        details_map = {ma_phieu: [] for ma_phieu in ma_phieu_list}
        for row in detail_rows:
            detail = PhieuNhapDetail(
                ma_phieu=row[0],
                ma_thuoc=row[1],
                ten_thuoc=row[2],
                so_lo=row[3],
                ngay_san_xuat=row[4],
                han_dung=row[5],
                so_dklh=row[6],
                so_luong=row[7],
                don_gia=row[8],
                thanh_tien=row[9],
                don_vi_tinh=row[10]
            )
            details_map[row[0]].append(detail)

        # 3. Build payloads and enqueue
        for ma_phieu in ma_phieu_list:
            payload = {
                "header": headers[ma_phieu].dict(by_alias=True),
                "details": [d.dict(by_alias=True) for d in details_map.get(ma_phieu, [])]
            }
            logging.info(f"Đưa phiếu nhập '{ma_phieu}' (payload) vào hàng đợi 'phieu_nhap_queue'.")
            process_phieu_nhap_task.apply_async(args=[payload], queue='phieu_nhap_queue')

    except Exception as e:
        logging.error(f"Lỗi khi quét phiếu nhập: {e}")
    finally:
        if conn:
            conn.close()

def prepare_and_dispatch_phieu_xuat():
    """Tìm và đưa các phiếu xuất vào hàng đợi, kèm header và details."""
    from app.models.phieu_xuat import PhieuXuatHeader, PhieuXuatDetail
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # 1. Fetch all pending headers
        query_headers = """
            SELECT ma_phieu, ngay_xuat, ten_nguoi_nhan, dia_chi_nguoi_nhan, ly_do_xuat, tong_tien, ghi_chu
            FROM PhieuXuatHeader
            WHERE status_phieu IN (0, 2)
            ORDER BY ngay_xuat ASC
        """
        cursor.execute(query_headers)
        header_rows = cursor.fetchall()
        if not header_rows:
            logging.info("Không có phiếu xuất chờ xử lý.")
            return

        headers = {}
        ma_phieu_list = []
        for row in header_rows:
            header = PhieuXuatHeader(
                ma_phieu=row[0],
                ngay_xuat=row[1],
                ten_nguoi_nhan=row[2],
                dia_chi_nguoi_nhan=row[3],
                ly_do_xuat=row[4],
                tong_tien=row[5],
                ghi_chu=row[6]
            )
            headers[row[0]] = header
            ma_phieu_list.append(row[0])

        # 2. Fetch all details in batch
        format_strings = ','.join(['?'] * len(ma_phieu_list))
        query_details = f"""
            SELECT ma_phieu, ma_thuoc, ten_thuoc, so_lo, han_dung, so_luong, don_gia, thanh_tien, don_vi_tinh
            FROM PhieuXuatDetail
            WHERE ma_phieu IN ({format_strings})
        """
        cursor.execute(query_details, ma_phieu_list)
        detail_rows = cursor.fetchall()

        # Group details by ma_phieu
        details_map = {ma_phieu: [] for ma_phieu in ma_phieu_list}
        for row in detail_rows:
            detail = PhieuXuatDetail(
                ma_phieu=row[0],
                ma_thuoc=row[1],
                ten_thuoc=row[2],
                so_lo=row[3],
                han_dung=row[4],
                so_luong=row[5],
                don_gia=row[6],
                thanh_tien=row[7],
                don_vi_tinh=row[8]
            )
            details_map[row[0]].append(detail)

        # 3. Build payloads and enqueue
        for ma_phieu in ma_phieu_list:
            payload = {
                "header": headers[ma_phieu].dict(by_alias=True),
                "details": [d.dict(by_alias=True) for d in details_map.get(ma_phieu, [])]
            }
            logging.info(f"Đưa phiếu xuất '{ma_phieu}' (payload) vào hàng đợi 'phieu_xuat_queue'.")
            process_phieu_xuat_task.apply_async(args=[payload], queue='phieu_xuat_queue')

    except Exception as e:
        logging.error(f"Lỗi khi quét phiếu xuất: {e}")
    finally:
        if conn:
            conn.close()

def prepare_and_dispatch_hoa_don():
    """Tìm và đưa các hóa đơn bán vào hàng đợi, kèm header và details."""
    from app.models.hoa_don import HoaDonHeader, HoaDonDetail, HoaDonDetailModel, HoaDonPayloadModel
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # 1. Fetch all pending headers
        query_headers = """
            SELECT ma_hoa_don, ngay_hoa_don, ten_khach_hang, tong_tien
            FROM HoaDonHeader
            WHERE status_hoa_don IN (0, 2)
            ORDER BY ngay_hoa_don ASC
        """
        cursor.execute(query_headers)
        header_rows = cursor.fetchall()
        if not header_rows:
            logging.info("Không có hóa đơn bán chờ xử lý.")
            return

        headers = {}
        ma_hoa_don_list = []
        for row in header_rows:
            header = HoaDonHeader(
                ma_hoa_don=row[0],
                ngay_hoa_don=row[1],
                ten_khach_hang=row[2],
                tong_tien=row[3]
            )
            headers[row[0]] = header
            ma_hoa_don_list.append(row[0])

        # 2. Fetch all details in batch
        format_strings = ','.join(['?'] * len(ma_hoa_don_list))
        query_details = f"""
            SELECT ma_hoa_don, ma_san_pham, so_luong, don_gia, thanh_tien
            FROM HoaDonDetail
            WHERE ma_hoa_don IN ({format_strings})
        """
        cursor.execute(query_details, ma_hoa_don_list)
        detail_rows = cursor.fetchall()

        # Group details by ma_hoa_don
        details_map = {ma_hoa_don: [] for ma_hoa_don in ma_hoa_don_list}
        for row in detail_rows:
            detail = HoaDonDetailModel(
                ma_san_pham=row[1],
                so_luong=row[2],
                don_gia=row[3]
            )
            details_map[row[0]].append(detail)

        # 3. Build payloads and enqueue
        for ma_hoa_don in ma_hoa_don_list:
            payload = HoaDonPayloadModel(
                ma_hoa_don=ma_hoa_don,
                ngay_hoa_don=headers[ma_hoa_don].ngay_hoa_don,
                ten_khach_hang=headers[ma_hoa_don].ten_khach_hang,
                details=details_map.get(ma_hoa_don, [])
            )
            logging.info(f"Đưa hóa đơn bán '{ma_hoa_don}' (payload) vào hàng đợi 'hoa_don_queue'.")
            process_hoa_don_task.apply_async(args=[payload.dict(by_alias=True)], queue='hoa_don_queue')

    except Exception as e:
        logging.error(f"Lỗi khi quét hóa đơn bán: {e}")
    finally:
        if conn:
            conn.close()
