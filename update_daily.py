import requests
import csv
import json
import io
import os
import re # Thư viện xử lý chữ

# --- CẤU HÌNH ---
LINK_CSV = "http://datafeed.accesstrade.me/shopee.vn.csv"
FILE_JSON = "data/products.json"  
# Từ khóa lọc
TU_KHOA_VPP = ["bút", "giấy", "vở", "sổ", "file", "bìa", "kẹp", "ghim", "băng dính", "thước", "mực", "kéo", "hồ dán", "đế cắm", "khay", "văn phòng", "học sinh"]

def xuly_gia(gia_raw):
    """Lọc lấy số từ giá tiền (kể cả khi nó là 10.000 - 20.000)"""
    try:
        # Tìm tất cả các con số trong chuỗi giá
        numbers = re.findall(r'\d+', str(gia_raw).replace('.', '').replace(',', ''))
        if numbers:
            # Lấy số đầu tiên (thường là giá thấp nhất)
            gia = float(numbers[0])
            if gia > 0:
                return "{:,.0f}₫".format(gia).replace(",", ".")
    except:
        pass
    return "Liên hệ" # Nếu lỗi thì trả về Liên hệ

def xuly_anh(anh_raw):
    """Cắt lấy 1 link ảnh sạch sẽ"""
    if not anh_raw:
        return "https://via.placeholder.com/150"
    
    # 1. Nếu ảnh bị dính chùm bằng dấu phẩy (link1, link2) -> Lấy cái đầu
    if "," in anh_raw:
        anh_raw = anh_raw.split(",")[0]
        
    # 2. Nếu ảnh bị dính chùm bằng dấu gạch đứng (link1|link2)
    if "|" in anh_raw:
        anh_raw = anh_raw.split("|")[0]
        
    # 3. Nếu ảnh bị bọc trong ngoặc ["link"] (Format JSON)
    anh_raw = anh_raw.replace('["', '').replace('"]', '').replace('"', '').strip()
    
    return anh_raw

def cap_nhat_tu_dong():
    print(f"⏳ Đang tải dữ liệu từ Accesstrade về...")
    
    try:
        response = requests.get(LINK_CSV, stream=True)
        response.encoding = 'utf-8' 
        
        if response.status_code != 200:
            print("❌ Lỗi: Không tải được file.")
            return

        f = io.StringIO(response.text)
        reader = csv.DictReader(f)
        
        # CẤU HÌNH CỘT (Theo đúng file của bạn)
        col_name = 'name'
        col_price = 'price'
        col_img = 'image'
        col_link = 'url' 

        san_pham_list = []
        count = 0
        
        print("⚙️ Đang lọc và làm sạch dữ liệu...")
        
        for row in reader:
            ten_sp = row.get(col_name, "")
            link_sp = row.get(col_link, "")
            raw_img = row.get(col_img, "")
            raw_price = row.get(col_price, "0")

            # Kiểm tra VPP
            is_vpp = False
            for tu_khoa in TU_KHOA_VPP:
                if tu_khoa in ten_sp.lower():
                    is_vpp = True
                    break
            
            if is_vpp and ten_sp and link_sp:
                # --- SỬA LỖI Ở ĐÂY ---
                final_img = xuly_anh(raw_img)
                final_price = xuly_gia(raw_price)
                
                san_pham_list.append({
                    "name": ten_sp,
                    "price": final_price,
                    "image": final_img,
                    "link": link_sp
                })
                count += 1
                
            if count >= 60: 
                break

        # Lưu file
        if not os.path.exists("data"):
            os.makedirs("data")
            
        with open(FILE_JSON, "w", encoding="utf-8") as f:
            json.dump(san_pham_list, f, ensure_ascii=False, indent=4)
        
        print(f"✅ Đã xử lý xong {len(san_pham_list)} sản phẩm (Ảnh & Giá đã sạch)!")
        
        print("🔨 Đang xây dựng lại web...")
        os.system("python build.py")
        
    except Exception as e:
        print(f"❌ Có lỗi xảy ra: {e}")

if __name__ == "__main__":
    cap_nhat_tu_dong()