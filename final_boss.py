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
BASE_AFF_URL = f"https://go.isclix.com/deep_link/v6/{CAMPAIGN_ID}/{ACCESSTRADE_ID}?sub4=web_tu_dong&utm_source=shopee&utm_campaign=vpp_tinh&url_enc="

# 1. TỪ KHÓA VPP (Lấy chính xác)
VPP_KEYWORDS = [
    "bút", "vở", "sổ", "giấy a4", "giấy in", "kẹp", "thước", "file", 
    "bìa", "băng dính", "ghim", "hộp bút", "balo", "cặp", "máy tính",
    "dập ghim", "hồ dán", "keo", "bảng", "phấn", "mực"
]

# 2. TỪ KHÓA CẤM (Chặn rác + Chặn hàng hết)
CANT_TAKE = [
    # Hàng hết / Lỗi
    "hết hàng", "ngừng kinh doanh", "bỏ mẫu", "liên hệ", "tạm hết",
    # Rác Mỹ phẩm / Đồ ăn / Xe cộ
    "mắt", "mày", "môi", "mi", "son", "kem", "phấn", "makeup", "trang điểm", "da", "nám", "mụn", 
    "bánh", "kẹo", "đồ ăn", "thực phẩm", "mắm", "muối", "gia vị",
    "xe", "honda", "yamaha", "lốp", "nhớt",
    "áo", "quần", "váy", "giày", "dép", "túi xách"
]

def tao_link_aff(url_goc):
    if not url_goc: return "#"
    try:
        encoded = base64.b64encode(url_goc.strip().encode("utf-8")).decode("utf-8")
        return f"{BASE_AFF_URL}{encoded}"
    except:
        return url_goc

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

def tao_web_html(products):
    # LOGO CHECK: Tìm file ảnh và tạo thẻ HTML tương ứng
    logo_src = ""
    if os.path.exists("logo.png"): logo_src = "logo.png"
    elif os.path.exists("logo.jpg"): logo_src = "logo.jpg"
    elif os.path.exists("logo.jpeg"): logo_src = "logo.jpeg"

    if logo_src:
        # Nếu có ảnh -> Hiện ảnh
        header_content = f'<img src="{logo_src}" alt="VPP Tịnh" class="logo-img">'
    else:
        # Nếu không có ảnh -> Hiện chữ to
        header_content = '<h1>VPP TỊNH</h1><p class="slogan">🌿 Bình An Trao Tay 🌿</p>'

    html = f"""
    <!DOCTYPE html>
    <html lang="vi">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <meta name="referrer" content="no-referrer"> 
        <title>VPP Tịnh - Bình An Trao Tay</title>
        <link rel="icon" href="{logo_src if logo_src else 'data:,'}">
        <style>
            :root {{ --primary: #2a9d8f; --bg: #fefae0; --text: #333; }}
            body {{ font-family: sans-serif; background: var(--bg); padding: 20px; margin: 0; }}
            
            header {{ text-align: center; background: #fff; padding: 20px; border-radius: 15px; margin-bottom: 30px; box-shadow: 0 5px 15px rgba(0,0,0,0.05); }}
            .logo-img {{ max-height: 120px; width: auto; display: block; margin: 0 auto; }}
            h1 {{ color: #e76f51; margin: 0; text-transform: uppercase; }}
            
            .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 20px; max-width: 1200px; margin: 0 auto; }}
            .card {{ background: #fff; border-radius: 10px; overflow: hidden; box-shadow: 0 2px 5px rgba(0,0,0,0.1); display: flex; flex-direction: column; transition: transform 0.2s; }}
            .card:hover {{ transform: translateY(-5px); }}
            .img-box {{ width: 100%; height: 180px; padding: 10px; box-sizing: border-box; display: flex; align-items: center; justify-content: center; }}
            .img-box img {{ max-width: 100%; max-height: 100%; object-fit: contain; }}
            .info {{ padding: 15px; flex-grow: 1; display: flex; flex-direction: column; justify-content: space-between; }}
            .title {{ font-size: 0.9em; margin-bottom: 10px; height: 2.7em; overflow: hidden; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; }}
            .price {{ color: #e63946; font-weight: bold; font-size: 1.1em; margin-bottom: 5px; }}
            .sales {{ font-size: 0.8em; color: #666; margin-bottom: 10px; }}
            .btn {{ background: var(--primary); color: #fff; text-decoration: none; padding: 10px; text-align: center; border-radius: 5px; font-weight: bold; display: block; }}
            .btn:hover {{ background: #21867a; }}
        </style>
    </head>
    <body>
        <header>
            {header_content}
        </header>
        <div class="grid">
    """
    
    for p in products:
        html += f"""
            <div class="card">
                <div class="img-box">
                    <img src="{p['image']}" alt="{p['name']}" loading="lazy">
                </div>
                <div class="info">
                    <div class="title">{p['name']}</div>
                    <div>
                        <div class="price">{p['price']}</div>
                        <div class="sales">Đã bán: {p['sales']}</div>
                    </div>
                    <a href="{p['link']}" class="btn" target="_blank" rel="nofollow">Mua Ngay</a>
                </div>
            </div>
        """
    html += "</div></body></html>"
    return html

def chay_ngay_di():
    print("🚀 ĐANG KHỞI ĐỘNG FINAL BOSS 4.0...")
    
    try:
        print("⏳ Đang tải dữ liệu...")
        r = requests.get(LINK_CSV, timeout=60)
        r.encoding = 'utf-8'
        if r.status_code != 200: return

        reader = csv.DictReader(io.StringIO(r.text))
        all_products = []
        
        print("⚙️ Đang lọc: Chỉ lấy món VPP bán chạy (>50 lượt bán)...")
        
        for row in reader:
            ten = row.get('name', '').lower()
            
            # 1. LỌC TỪ KHÓA VPP & CHẶN RÁC
            if not any(w in ten for w in VPP_KEYWORDS): continue
            if any(bad in ten for bad in CANT_TAKE): continue

            # 2. LỌC SỐ LƯỢNG BÁN (QUAN TRỌNG ĐỂ TRÁNH HÀNG CHẾT)
            # Chỉ lấy những món đã bán được trên 50 cái
            try:
                sales = int(row.get('sales', 0))
            except:
                sales = 0
            
            if sales < 50: continue # Ít người mua quá -> Dễ là hàng cũ/hết hàng -> BỎ

            # 3. Lọc giá (Bỏ hàng rác < 5k)
            try:
                gia = float(row.get('price', 0))
            except:
                gia = 0
            if gia < 5000: continue

            # NẾU QUA HẾT CÁC CỬA ẢI TRÊN -> LẤY
            all_products.append({
                "name": row.get('name'),
                "price": xuly_gia(gia),
                "sales": sales,
                "image": row.get('image', '').split(',')[0].strip(' []"'),
                "link": tao_link_aff(row.get('url'))
            })

        # Sắp xếp bán chạy nhất lên đầu
        all_products.sort(key=lambda x: x['sales'], reverse=True)
        
        # Lấy Top 60
        top_60 = all_products[:60]

        # Tạo file JSON và HTML
        with open(FILE_JSON, "w", encoding="utf-8") as f:
            json.dump(top_60, f, ensure_ascii=False, indent=4)
            
        html_content = tao_web_html(top_60)
        with open("index.html", "w", encoding="utf-8") as f:
            f.write(html_content)
            
        print(f"✅ Đã lọc được {len(top_60)} sản phẩm CHẤT (Bán chạy > 50).")
        
        # --- QUAN TRỌNG: LỆNH ĐẨY LOGO LÊN MẠNG ---
        print("☁️ Đang đẩy code và LOGO lên mạng...")
        os.system("git add .") 
        # Lệnh này sẽ tự tìm logo.png/jpg và thêm vào kho
        os.system('git commit -m "Fix logo va loc hang ton"')
        os.system("git push")
        print("🎉 XONG! Hãy vào web kiểm tra ngay.")

    except Exception as e:
        print(f"❌ Lỗi: {e}")

if __name__ == "__main__":
    chay_ngay_di()