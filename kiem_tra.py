import requests
import csv
import io

# Link CSV của bạn
LINK_CSV = "http://datafeed.accesstrade.me/shopee.vn.csv"

def soi_du_lieu():
    print("🔍 ĐANG TẢI DỮ LIỆU ĐỂ PHÂN TÍCH...")
    try:
        r = requests.get(LINK_CSV, timeout=60)
        # Lấy dòng đầu tiên (tiêu đề cột)
        lines = r.text.splitlines()
        
        if len(lines) < 2:
            print("❌ File rỗng hoặc lỗi!")
            return

        # Đọc header
        header = lines[0].split(',')
        print("\n" + "="*50)
        print("DANH SÁCH CÁC CỘT (HEADER) TÌM THẤY:")
        print("="*50)
        for i, col in enumerate(header):
            print(f"Cột {i}: {col}")
        
        print("\n" + "="*50)
        print("DỮ LIỆU MẪU (DÒNG ĐẦU TIÊN):")
        print("="*50)
        # Đọc thử dòng dữ liệu đầu tiên
        first_row = csv.reader([lines[1]])
        for row in first_row:
            print(row)
            
    except Exception as e:
        print(f"❌ Lỗi: {e}")

if __name__ == "__main__":
    soi_du_lieu()