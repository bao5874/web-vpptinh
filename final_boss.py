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

# ID CỦA BẠN
ACCESSTRADE_ID = "4751584435713464237"
CAMPAIGN_ID = "6906519896943843292" 
BASE_AFF_URL = f"https://go.isclix.com/deep_link/v6/{CAMPAIGN_ID}/{ACCESSTRADE_ID}?sub4=web_tu_dong&url_enc="

# 1. DANH SÁCH DUYỆT (Phải có từ này mới lấy)
TU_KHOA_VPP = [
    "bút", "giấy a4", "giấy in", "giấy note", "vở", "sổ", "file", "bìa", 
    "kẹp giấy", "kẹp bướm", "ghim", "băng dính", "thước", "mực bút", "mực in", 
    "kéo văn phòng", "hồ dán", "keo dán", "đế cắm", "khay đựng", "máy tính bỏ túi",
    "văn phòng", "học sinh", "balo đi học", "cặp sách", "bút chì", "tẩy", "gọt chì"
]

# 2. DANH SÁCH CẤM (Thấy từ này là vứt ngay) - CHỐNG HÀNG RÁC
TU_KHOA_CAM = [
    "vệ sinh", "ăn", "thấm dầu", "nướng", "bạc", # Chặn giấy vệ sinh, giấy ăn
    "khô", "rim", "tẩm", "nước mắm", "đông lạnh", # Chặn mực khô, đồ ăn
    "tóc", "ngực", "nách", "mặt", "dưỡng", "serum", # Chặn kẹp tóc, mỹ phẩm
    "áo", "quần", "váy", "giày", "dép", "thời trang", # Chặn quần áo
    "bếp", "nồi", "chảo", "dao", "thớt", # Chặn đồ gia dụng
    "đồ chơi", "trẻ em", "sơ sinh", "bỉm" # Chặn đồ mẹ bé không liên quan
]

def bo_loc_thong_minh(ten_sp):
    ten_sp = ten_sp.lower()
    
    # BƯỚC 1: KIỂM TRA TỪ CẤM (Blacklist)
    for tu_cam in TU_KHOA_CAM:
        if tu_cam in ten_sp:
            return False # Có từ cấm -> Loại ngay
            
    # BƯỚC 2: KIỂM TRA TỪ KHÓA VPP (Whitelist)
    for tu_khoa in TU_KHOA_VPP:
        if tu_khoa in ten_sp:
            return True # Sạch sẽ -> Lấy
            
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
            if gia > 0:
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
    print("🚀 ĐANG KHỞI ĐỘNG HỆ THỐNG VỚI BỘ LỌC THÔNG MINH...")
    
    try:
        print("⏳ Đang tải dữ liệu gốc...")
        r = requests.get(LINK_CSV)
        r.encoding = 'utf-8'
        if r.status_code != 200: return
            
        f = io.StringIO(r.text)
        reader = csv.DictReader(f)
        
        san_pham_list = []
        count = 0
        print("⚙️ Đang lọc VPP (Đã bật chế độ chặn hàng rác)...")
        
        for row in reader:
            ten = row.get('name', '')
            link_goc = row.get('url', '') 
            anh = row.get('image', '')
            gia = row.get('price', '0')
            
            # --- SỬ DỤNG BỘ LỌC THÔNG MINH ---
            if bo_loc_thong_minh(ten) and link_goc:
                aff_link = tao_link_kiem_tien(link_goc)
                san_pham_list.append({
                    "name": ten,
                    "price": xuly_gia(gia),
                    "image": xuly_anh(anh),
                    "link": aff_link 
                })
                count += 1
                
            if count >= 60: break 

        with open(FILE_JSON, "w", encoding="utf-8") as f:
            json.dump(san_pham_list, f, ensure_ascii=False, indent=4)
            
        html_content = tao_web_html(san_pham_list)
        with open("index.html", "w", encoding="utf-8") as f:
            f.write(html_content)
            
        print(f"✅ ĐÃ LỌC XONG! Lấy được {len(san_pham_list)} sản phẩm chuẩn VPP.")
        
        # Tự động đẩy lên mạng
        os.system("git add .")
        os.system('git commit -m "Update bo loc thong minh"')
        os.system("git push")
        print("🎉 Đã đẩy Web mới lên mạng!")

    except Exception as e:
        print(f"❌ Lỗi: {e}")

if __name__ == "__main__":
    chay_ngay_di()