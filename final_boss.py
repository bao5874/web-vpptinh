import requests
import csv
import json
import io
import os
import re
import urllib.parse 

# --- CẤU HÌNH ---
LINK_CSV = "http://datafeed.accesstrade.me/shopee.vn.csv"
FILE_JSON = "products.json"

# ID CỦA BẠN (ĐÃ KIỂM TRA: CHUẨN)
ACCESSTRADE_ID = "4751584435713464237"
CAMPAIGN_ID = "6906519896943843292" 

# Link nền tạo Deep Link
BASE_AFF_URL = f"https://go.isclix.com/deep_link/v6/{CAMPAIGN_ID}/{ACCESSTRADE_ID}?url="

TU_KHOA_VPP = ["bút", "giấy", "vở", "sổ", "file", "bìa", "kẹp", "ghim", "băng dính", "thước", "mực", "kéo", "hồ dán", "đế cắm", "khay", "văn phòng", "học sinh"]

def tao_link_kiem_tien(link_goc):
    """Biến link thường thành link Affiliate (Phiên bản Fix Lỗi 404)"""
    if not link_goc: return "#"
    
    # BƯỚC SỬA LỖI QUAN TRỌNG:
    # safe="" nghĩa là ép nó mã hóa cả dấu / thành %2F để Accesstrade không bị nhầm
    link_encoded = urllib.parse.quote(link_goc.strip(), safe="")
    
    return f"{BASE_AFF_URL}{link_encoded}"

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
    print("🚀 ĐANG KHỞI ĐỘNG HỆ THỐNG FIX LỖI 404...")
    
    try:
        print("⏳ Đang tải dữ liệu gốc từ Accesstrade...")
        r = requests.get(LINK_CSV)
        r.encoding = 'utf-8'
        if r.status_code != 200:
            print("❌ Lỗi mạng! Không tải được file.")
            return
            
        f = io.StringIO(r.text)
        reader = csv.DictReader(f)
        
        san_pham_list = []
        count = 0
        print("⚙️ Đang lọc VPP và gắn mã Affiliate (Chuẩn hóa URL)...")
        
        for row in reader:
            ten = row.get('name', '')
            link_goc = row.get('url', '') 
            anh = row.get('image', '')
            gia = row.get('price', '0')
            
            is_vpp = False
            for k in TU_KHOA_VPP:
                if k in ten.lower():
                    is_vpp = True
                    break
            
            if is_vpp and ten and link_goc:
                # Tạo link chuẩn không bị lỗi 404
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
            
        print(f"✅ ĐÃ SỬA XONG! {len(san_pham_list)} link đã được mã hóa lại.")
        print("👉 Giờ bạn hãy đẩy lên mạng và thử bấm lại xem!")

    except Exception as e:
        print(f"❌ Lỗi: {e}")

if __name__ == "__main__":
    chay_ngay_di()