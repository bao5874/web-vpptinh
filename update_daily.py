import requests
import csv
import json
import io
import os

# --- CẤU HÌNH ---
LINK_CSV = "http://datafeed.accesstrade.me/shopee.vn.csv"
FILE_JSON = "data/products.json"  
# Từ khóa lọc (Giữ nguyên)
TU_KHOA_VPP = ["bút", "giấy", "vở", "sổ", "file", "bìa", "kẹp", "ghim", "băng dính", "thước", "mực", "kéo", "hồ dán", "đế cắm", "khay", "văn phòng", "học sinh"]

def xuly_gia(gia_raw):
    """Thêm chữ đ và dấu chấm cho đẹp"""
    try:
        # Xử lý trường hợp giá là 45000.0 hoặc 45000
        gia = float(gia_raw)
        return "{:,.0f}₫".format(gia).replace(",", ".")
    except:
        return "Liên hệ"

def cap_nhat_tu_dong():
    print(f"⏳ Đang tải dữ liệu từ Accesstrade về...")
    
    try:
        # 1. Tải file
        response = requests.get(LINK_CSV, stream=True)
        response.encoding = 'utf-8' 
        
        if response.status_code != 200:
            print("❌ Lỗi: Không tải được file.")
            return

        # 2. Đọc dữ liệu
        f = io.StringIO(response.text)
        reader = csv.DictReader(f)
        
        # --- SỬA LỖI Ở ĐÂY: ÁP DỤNG ĐÚNG TÊN CỘT TỪ LOG CỦA BẠN ---
        # Dựa trên log: ['sku', 'name', 'url', 'price', 'discount', 'image', 'desc', 'category']
        col_name = 'name'
        col_price = 'price'
        col_img = 'image'
        col_link = 'url' # Đây chính là chỗ code cũ bị sai

        san_pham_list = []
        count = 0
        
        print("⚙️ Đang lọc sản phẩm văn phòng phẩm...")
        
        for row in reader:
            ten_sp = row.get(col_name, "")
            link_sp = row.get(col_link, "")
            
            # Kiểm tra xem có phải VPP không
            is_vpp = False
            for tu_khoa in TU_KHOA_VPP:
                if tu_khoa in ten_sp.lower():
                    is_vpp = True
                    break
            
            # Chỉ lấy sản phẩm có tên, có giá và là VPP
            if is_vpp and ten_sp and link_sp:
                san_pham_list.append({
                    "name": ten_sp,
                    "price": xuly_gia(row.get(col_price, "0")),
                    "image": row.get(col_img, "https://via.placeholder.com/150"),
                    "link": link_sp
                })
                count += 1
                
            if count >= 60: # Lấy 60 món thôi
                break

        # 3. Lưu file
        if not os.path.exists("data"):
            os.makedirs("data")
            
        with open(FILE_JSON, "w", encoding="utf-8") as f:
            json.dump(san_pham_list, f, ensure_ascii=False, indent=4)
        
        print(f"✅ Đã tìm thấy {len(san_pham_list)} sản phẩm VPP chuẩn xịn!")
        
        # 4. Chạy Build
        print("🔨 Đang tự động xây dựng lại web...")
        os.system("python build.py")
        
    except Exception as e:
        print(f"❌ Có lỗi xảy ra: {e}")

if __name__ == "__main__":
    cap_nhat_tu_dong()