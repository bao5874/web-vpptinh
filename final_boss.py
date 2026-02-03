import requests
import csv
import json
import io
import os
import re
import base64 

# --- 1. CẤU HÌNH ---
LINK_CSV = "http://datafeed.accesstrade.me/shopee.vn.csv"
FILE_JSON = "products.json"

# Thông tin Affiliate của bạn
ACCESSTRADE_ID = "4751584435713464237"
CAMPAIGN_ID = "6906519896943843292" 
# Link gốc đã tích hợp UTM để Shopee biết là khách VPP
BASE_AFF_URL = f"https://go.isclix.com/deep_link/v6/{CAMPAIGN_ID}/{ACCESSTRADE_ID}?sub4=web_tu_dong&utm_source=shopee&utm_campaign=vpp_tinh&url_enc="

# DANH SÁCH TỪ KHÓA CHUẨN (VPP)
VPP_KEYWORDS = [
    "bút", "vở", "sổ", "giấy a4", "giấy in", "kẹp giấy", "thước", "file", 
    "bìa", "băng dính", "ghim", "hộp bút", "balo", "cặp sách", "máy tính bỏ túi",
    "dập ghim", "hồ dán", "keo dán", "bảng", "phấn", "mực"
]

# DANH SÁCH TỪ KHÓA CẤM (CHẶN RÁC & MỸ PHẨM)
CANT_TAKE = [
    "mắt", "mày", "môi", "mi", "son", "kem", "phấn", "makeup", "trang điểm", "da", "nám", "mụn", "serum", "dưỡng", # Mỹ phẩm
    "bánh", "kẹo", "đồ ăn", "thực phẩm", "mắm", "muối", "gia vị", "bếp", "nồi", # Đồ ăn
    "xe", "honda", "yamaha", "phụ tùng", "lốp", "nhớt", # Xe cộ
    "áo", "quần", "váy", "giày", "dép", "thời trang", "túi xách" # Thời trang
]

# --- 2. CÁC HÀM XỬ LÝ ---

def tao_link_aff(url_goc):
    """Mã hóa link sản phẩm thành Base64 để không bị lỗi"""
    if not url_goc: return "#"
    try:
        encoded = base64.b64encode(url_goc.strip().encode("utf-8")).decode("utf-8")
        return f"{BASE_AFF_URL}{encoded}"
    except:
        return url_goc

def xuly_gia(gia_raw):
    """Làm đẹp giá tiền (ví dụ: 10000 -> 10.000₫)"""
    try:
        numbers = re.findall(r'\d+', str(gia_raw).replace('.', '').replace(',', ''))
        if numbers:
            gia = float(numbers[0])
            if gia > 0:
                return "{:,.0f}₫".format(gia).replace(",", ".")
    except:
        pass
    return "Liên hệ"

def tao_web_html(products):
    """Tạo giao diện web (Có tự động nhận diện Logo)"""
    
    # --- LOGIC XỬ LÝ LOGO ---
    # Mặc định là hiện chữ nếu không có ảnh
    logo_html = '<h1>VPP TỊNH</h1><p class="slogan">🌿 Bình An Trao Tay 🌿</p>' 
    
    # Kiểm tra xem có file ảnh logo không (ưu tiên png rồi đến jpg)
    if os.path.exists("logo.png"):
        logo_html = '<img src="logo.png" alt="VPP Tịnh" class="logo-img">'
    elif os.path.exists("logo.jpg"):
        logo_html = '<img src="logo.jpg" alt="VPP Tịnh" class="logo-img">'
    # ------------------------

    html = f"""
    <!DOCTYPE html>
    <html lang="vi">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <meta name="referrer" content="no-referrer"> 
        <title>VPP Tịnh - Bình An Trao Tay</title>
        <style>
            :root {{ --primary-color: #2a9d8f; --bg-color: #fefae0; --text-color: #333; }}
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: var(--bg-color); margin: 0; padding: 20px; color: var(--text-color); }}
            
            /* HEADER STYLE */
            header {{ 
                text-align: center; 
                margin-bottom: 30px; 
                background: #fff; 
                padding: 30px 20px; 
                border-radius: 20px; 
                box-shadow: 0 10px 25px rgba(0,0,0,0.05); 
            }}
            .logo-img {{
                max-height: 100px; /* Logo cao tối đa 100px */
                width: auto;
                display: block;
                margin: 0 auto;
            }}
            h1 {{ color: #e76f51; margin: 0; text-transform: uppercase; letter-spacing: 2px; }}
            .slogan {{ color: #264653; font-style: italic; margin-top: 10px; font-weight: 500; }}

            /* GRID SẢN PHẨM */
            .product-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(190px, 1fr)); gap: 25px; max-width: 1200px; margin: 0 auto; }}
            
            /* THẺ SẢN PHẨM */
            .product-card {{ 
                background: #fff; 
                border-radius: 15px; 
                overflow: hidden; 
                box-shadow: 0 4px 10px rgba(0,0,0,0.05); 
                transition: transform 0.3s ease, box-shadow 0.3s ease; 
                display: flex; flex-direction: column; 
            }}
            .product-card:hover {{ transform: translateY(-5px); box-shadow: 0 12px 20px rgba(0,0,0,0.1); }}
            
            .product-image {{ 
                width: 100%; 
                height: 190px; 
                object-fit: contain; 
                padding: 15px; 
                box-sizing: border-box; 
                background: #fff;
                border-bottom: 1px solid #f0f0f0;
            }}
            
            .product-info {{ padding: 15px; flex-grow: 1; display: flex; flex-direction: column; justify-content: space-between; }}
            .product-title {{ 
                font-size: 0.95em; 
                color: #333; 
                margin: 0 0 10px 0; 
                display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; 
                height: 2.8em; line-height: 1.4em;
                font-weight: 600;
            }}
            .product-price {{ font-size: 1.3em; color: #e63946; font-weight: bold; margin-bottom: 15px; }}
            
            .btn-buy {{ 
                display: block; width: 100%; padding: 12px 0; 
                background-color: var(--primary-color); 
                color: white; text-align: center; text-decoration: none; 
                border-radius: 8px; font-weight: bold; 
                transition: background 0.3s; 
            }}
            .btn-buy:hover {{ background-color: #21867a; }}
        </style>
    </head>
    <body>
        <header>
            {logo_html}
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
    print("🚀 ĐANG KHỞI ĐỘNG HỆ THỐNG (Phiên bản Logo + Bán chạy)...")
    
    try:
        print("⏳ Đang tải dữ liệu từ Shopee...")
        r = requests.get(LINK_CSV, timeout=60)
        r.encoding = 'utf-8'
        
        if r.status_code != 200:
            print("❌ Lỗi mạng! Không tải được file.")
            return

        reader = csv.DictReader(io.StringIO(r.text))
        
        all_products = []
        
        print("⚙️ Đang lọc sản phẩm VPP bán chạy nhất...")
        
        for row in reader:
            ten = row.get('name', '').lower()
            
            # --- BỘ LỌC KÉP ---
            # 1. Phải chứa từ khóa VPP
            la_vpp = any(word in ten for word in VPP_KEYWORDS)
            
            # 2. Tuyệt đối KHÔNG chứa từ cấm (Mỹ phẩm/Đồ ăn)
            khong_phai_rac = not any(bad in ten for bad in CANT_TAKE)

            # 3. Lọc giá (Bỏ hàng < 3k)
            try:
                gia = float(row.get('price', 0))
            except:
                gia = 0

            if la_vpp and khong_phai_rac and gia > 3000:
                # Lấy số lượng đã bán để sắp xếp
                try:
                    sales = int(row.get('sales', 0))
                except:
                    sales = 0
                
                # Tạo link luôn
                aff_link = tao_link_aff(row.get('url'))
                
                all_products.append({
                    "name": row.get('name'),
                    "price": xuly_gia(gia),
                    "sales": sales,
                    "image": row.get('image', '').split(',')[0].strip(' []"'),
                    "link": aff_link
                })

        # SẮP XẾP: Bán chạy nhất lên đầu
        all_products.sort(key=lambda x: x['sales'], reverse=True)

        # LẤY TOP 60
        top_60 = all_products[:60]

        # 1. Ghi file JSON
        with open(FILE_JSON, "w", encoding="utf-8") as f:
            json.dump(top_60, f, ensure_ascii=False, indent=4)
            
        # 2. Tạo file HTML (Lúc này sẽ tự check Logo)
        html_content = tao_web_html(top_60)
        with open("index.html", "w", encoding="utf-8") as f:
            f.write(html_content)
            
        print(f"✅ HOÀN TẤT! Đã tạo web với {len(top_60)} sản phẩm Hot nhất.")
        
        # 3. Đẩy lên mạng
        print("☁️ Đang đẩy lên Github...")
        os.system("git add .")
        os.system('git commit -m "Update web complete with logo"')
        os.system("git push")
        print("🎉 XONG! Bạn hãy vào web kiểm tra nhé!")

    except Exception as e:
        print(f"❌ Lỗi: {e}")

if __name__ == "__main__":
    chay_ngay_di()