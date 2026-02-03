import requests
import csv
import json
import io
import os
import re
import base64 

# --- CẤU HÌNH ---
LINK_CSV = "http://datafeed.accesstrade.me/shopee.vn.csv"
FILE_JSON = "products.json"

ACCESSTRADE_ID = "4751584435713464237"
CAMPAIGN_ID = "6906519896943843292" 
BASE_AFF_URL = f"https://go.isclix.com/deep_link/v6/{CAMPAIGN_ID}/{ACCESSTRADE_ID}?sub4=web_tu_dong&url_enc="

# 1. DUYỆT THEO DANH MỤC (Quan trọng nhất)
# Chỉ lấy những món thuộc ngành hàng này
DANH_MUC_CHUAN = [
    "văn phòng phẩm", "nhà sách", "dụng cụ học sinh", "họa cụ", 
    "bút", "giấy", "sổ", "bìa", "băng keo", "kéo", "thước", "màu vẽ"
]

# 2. DUYỆT THEO TÊN (Bộ lọc phụ)
TU_KHOA_TEN = [
    "bút", "giấy", "vở", "sổ", "file", "bìa", "kẹp", "ghim", "băng dính", 
    "thước", "mực", "kéo", "hồ dán", "đế cắm", "khay", "balo", "cặp", "tẩy"
]

# 3. DANH SÁCH CẤM (Lọc rác & Hàng hết)
TU_KHOA_CAM = [
    "vệ sinh", "ăn", "thấm dầu", "nướng", "bạc", # Rác
    "tóc", "ngực", "nách", "mặt", "dưỡng", "serum", "mỹ phẩm", # Rác
    "áo", "quần", "váy", "giày", "dép", "thời trang", # Rác
    "hết hàng", "bỏ mẫu", "ngừng kinh doanh", "liên hệ", # HÀNG ĐÃ HẾT
    "voucher", "thẻ nạp", "e-voucher" # Rác số
]

def check_hang_chuan(row):
    """Hàm kiểm tra kỹ lưỡng từng sản phẩm"""
    ten_sp = row.get('name', '').lower()
    danh_muc = row.get('category', '').lower() # Lấy cột Category
    
    # 1. LOẠI BỎ HÀNG HẾT / HÀNG RÁC NGAY LẬP TỨC
    for tu_cam in TU_KHOA_CAM:
        if tu_cam in ten_sp:
            return False
            
    # 2. KIỂM TRA GIÁ (Loại bỏ giá 0đ hoặc giá ảo)
    try:
        gia = float(row.get('price', 0))
        if gia < 1000: # Giá dưới 1k thường là lỗi hoặc rác
            return False
    except:
        return False

    # 3. ƯU TIÊN 1: KIỂM TRA DANH MỤC (Chính xác 99%)
    # Nếu danh mục có chữ "Văn phòng phẩm" hoặc "Nhà sách" -> LẤY LUÔN
    for dm in DANH_MUC_CHUAN:
        if dm in danh_muc:
            return True

    # 4. ƯU TIÊN 2: NẾU DANH MỤC KHÔNG RÕ, MỚI SOI TÊN
    # (Nhưng phải kỹ hơn: Tên phải chứa từ khóa VPP VÀ KHÔNG chứa từ cấm)
    is_vpp_name = False
    for k in TU_KHOA_TEN:
        if k in ten_sp:
            is_vpp_name = True
            break
            
    if is_vpp_name:
        # Check lại lần nữa cho chắc (ví dụ: "Kẹp" tóc -> Loại)
        if "tóc" in ten_sp or "xinh" in ten_sp or "bé gái" in ten_sp: 
            return False
        return True

    return False

def tao_link_kiem_tien(link_goc):
    if not link_goc: return "#"
    try:
        link_bytes = link_goc.strip().encode("utf-8")
        base64_str = base64.b64encode(link_bytes).decode("utf-8")
        return f"{BASE_AFF_URL}{base64_str}"
    except:
        return link_goc 

def xuly_gia(gia_raw):
    try:
        numbers = re.findall(r'\d+', str(gia_raw).replace('.', '').replace(',', ''))
        if numbers:
            gia = float(numbers[0])
            return "{:,.0f}₫".format(gia).replace(",", ".")
    except:
        pass
    return "Liên hệ"

def xuly_anh(anh_raw):
    if not anh_raw: return "https://via.placeholder.com/150"
    if "," in anh_raw: anh_raw = anh_raw.split(",")[0]
    if "|" in anh_raw: anh_raw = anh_raw.split("|")[0]
    anh_raw = anh_raw.replace('["', '').replace('"]', '').replace('"', '').strip()
    if anh_raw.startswith("http://"):
        anh_raw = anh_raw.replace("http://", "https://")
    return anh_raw

def tao_web_html(products):
    html = """
    <!DOCTYPE html>
    <html lang="vi">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <meta name="referrer" content="no-referrer"> 
        <title>VPP Tịnh - Bình An Trao Tay</title>
        <style>
            :root { --primary-color: #d4a373; --bg-color: #fefae0; }
            body { font-family: 'Segoe UI', sans-serif; background-color: var(--bg-color); margin: 0; padding: 20px; }
            header { text-align: center; margin-bottom: 40px; background: #fff; padding: 20px; border-radius: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }
            h1 { color: #8B4513; margin: 0; text-transform: uppercase; }
            .product-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 20px; max-width: 1200px; margin: 0 auto; }
            .product-card { background: #fff; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.1); transition: transform 0.2s; display: flex; flex-direction: column; }
            .product-card:hover { transform: translateY(-5px); }
            .product-image { width: 100%; height: 180px; object-fit: contain; padding: 10px; box-sizing: border-box; }
            .product-info { padding: 15px; flex-grow: 1; display: flex; flex-direction: column; justify-content: space-between; }
            .product-title { font-size: 0.95em; color: #333; margin: 0 0 10px 0; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; height: 2.8em; }
            .product-price { font-size: 1.2em; color: #e63946; font-weight: bold; margin-bottom: 10px; }
            .btn-buy { display: block; width: 100%; padding: 10px 0; background-color: #ee4d2d; color: white; text-align: center; text-decoration: none; border-radius: 4px; font-weight: bold; }
            .btn-buy:hover { background-color: #d73211; }
        </style>
    </head>
    <body>
        <header>
            <h1>VPP Tịnh</h1>
            <p>🌿 Chuyên Văn Phòng Phẩm Chất Lượng 🌿</p>
        </header>
        <div class="product-grid">
    """
    for p in products:
        html += f"""
            <div class="product-card">
                <img src="{p['image']}" alt="{p['name']}" class="product-image" loading="lazy">
                <div class="product-info">
                    <h3 class="product-title">{p['name']}</h3>
                    <div class="product-price">{p['price']}</div>
                    <a href="{p['link']}" class="btn-buy" target="_blank" rel="nofollow">Mua Ngay</a>
                </div>
            </div>
        """
    html += "</div></body></html>"
    return html

def chay_ngay_di():
    print("🚀 ĐANG CHẠY BỘ LỌC 'SOI CHỨNG MINH THƯ'...")
    
    try:
        print("⏳ Đang tải dữ liệu...")
        r = requests.get(LINK_CSV)
        r.encoding = 'utf-8'
        if r.status_code != 200: return
            
        f = io.StringIO(r.text)
        reader = csv.DictReader(f)
        
        san_pham_list = []
        count = 0
        
        # Thống kê cho bạn xem
        tong_so = 0
        bi_loai = 0
        
        print("⚙️ Đang lọc kỹ từng món hàng...")
        
        for row in reader:
            tong_so += 1
            
            # --- KIỂM TRA KỸ ---
            if check_hang_chuan(row):
                # Chỉ lấy nếu còn hàng (thông qua việc có link và giá hợp lệ)
                link_goc = row.get('url', '')
                if link_goc:
                    san_pham_list.append({
                        "name": row.get('name', ''),
                        "price": xuly_gia(row.get('price', '0')),
                        "image": xuly_anh(row.get('image', '')),
                        "link": tao_link_kiem_tien(link_goc)
                    })
                    count += 1
            else:
                bi_loai += 1
                
            if count >= 60: break 

        print(f"📊 Đã quét {tong_so} món. Loại bỏ {bi_loai} món rác/hết hàng.")
        print(f"✅ Lấy được {len(san_pham_list)} món VPP chuẩn.")

        with open(FILE_JSON, "w", encoding="utf-8") as f:
            json.dump(san_pham_list, f, ensure_ascii=False, indent=4)
            
        html_content = tao_web_html(san_pham_list)
        with open("index.html", "w", encoding="utf-8") as f:
            f.write(html_content)
            
        # Tự động đẩy lên mạng
        os.system("git add .")
        os.system('git commit -m "Update bo loc category chuan"')
        os.system("git push")
        print("🎉 Đã đẩy Web mới lên mạng!")

    except Exception as e:
        print(f"❌ Lỗi: {e}")

if __name__ == "__main__":
    chay_ngay_di()