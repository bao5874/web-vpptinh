import requests
import csv
from io import StringIO

LINK_CSV = "http://datafeed.accesstrade.me/shopee.vn.csv"

def check_header():
    print("dang tai 1 phan du lieu de kiem tra...")
    try:
        # Tải 1 chút dữ liệu thôi (stream)
        with requests.get(LINK_CSV, stream=True) as r:
            lines = (line.decode('utf-8') for line in r.iter_lines())
            
            # Lấy dòng đầu tiên (Header)
            header = next(lines)
            print("-" * 20)
            print("CÁC CỘT CÓ TRONG FILE CSV:")
            print(header)
            print("-" * 20)
            
            # Lấy thử dòng dữ liệu đầu tiên để xem mẫu
            first_row = next(lines)
            print("MẪU DỮ LIỆU:")
            print(first_row)
            
    except Exception as e:
        print(f"Lỗi: {e}")

if __name__ == "__main__":
    check_header()