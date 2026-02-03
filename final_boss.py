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

# 1. TỪ KHÓA VPP (Lấy)
VPP_KEYWORDS = [
    "bút", "vở", "sổ", "giấy a4", "giấy in", "kẹp", "thước", "file", 
    "bìa", "băng dính", "ghim", "hộp bút", "balo", "cặp", "máy tính",
    "dập ghim", "hồ dán", "keo", "bảng", "phấn", "mực"
]

# 2. TỪ KHÓA CẤM (Chặn rác)
CANT_TAKE = [
    "hết hàng", "ngừng kinh doanh", "bỏ mẫu", "liên hệ", "tạm hết",
    "mắt", "mày", "môi", "mi", "son", "kem", "phấn", "makeup", "trang điểm", "da", "nám", "mụn", 
    "bánh", "kẹo", "đồ ăn", "thực phẩm", "mắm", "muối", "gia vị",
    "xe", "honda", "yamaha", "lốp", "nhớt",
    "áo", "quần", "váy", "giày", "dép", "túi xách", "thời trang"
]

def tao_link_aff(url_goc):
    if not url_goc: return "#"
    try:
        encoded = base64.b64encode(url_goc.strip().encode("utf-8")).decode("utf-8")
        return f"{BASE_AFF_URL}{encoded}"
    except:
        return url_goc

def xuly_gia_chuan(gia_raw):
    """
    Hàm xử lý giá phiên bản 6.0 - SIÊU AN TOÀN
    """
    try:
        # 1. Chuyển hết về chuỗi
        gia_str = str(gia_raw).strip()
        
        # 2. Nếu giá có dấu chấm (ví dụ 125.000), thay thế nó đi để thành số thuần (125000)
        # Lưu ý: Python hiểu 125.000 là float 125, nên ta phải xử lý chuỗi trước
        if "." in gia_str and len(gia_str.split(".")[1]) == 3:
             gia_str = gia_str.replace(".", "")
        
        # 3. Lọc bỏ mọi ký tự không phải số (như chữ đ, vnđ, ,)
        gia_clean = re.sub(r'[^\d]', '', gia_str)
        
        # 4. Chuyển sang số
        gia_val = float(gia_clean)
        
        # 5. Logic sửa sai: Nếu giá > 10 triệu (vô lý với cây bút), chia bớt cho 10
        # Đây là mẹo trị bệnh "thừa số 0"
        if gia_val > 10000000: 
            gia_val = gia_val / 10
            
        if gia_val < 1000: return "Liên hệ" # Rẻ quá cũng bỏ
        
        return "{:,.0f}₫".format(gia_val).replace(",", ".")
    except:
        return "Liên hệ"

def tao_web_html(products):
    # LOGO: Ép buộc hiển thị logo.png
    # Thêm onerror để nếu lỗi ảnh thì ẩn đi chứ không hiện icon gãy
    logo_html = '<img src="logo.png" alt="VPP Tịnh" class="logo-img" onerror="this.style.display=\'none\'">'
    
    html = f"""
    <!DOCTYPE html>
    <html lang="vi">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <meta name="referrer" content="no-referrer"> 
        <title>VPP Tịnh - Bình An Trao Tay</title>
        <link rel="icon" href="logo.png">
        <style>
            :root {{ --primary: #2a9d8f; --bg: #fefae0; --text: #333; }}
            body {{ font-family: sans-serif; background: var(--bg); padding: 20px; margin: 0; }}
            header {{ text-align: center; background: #fff; padding: 20px; border-radius: 15px; margin-bottom: 30px; box-shadow: 0 5px 15px rgba(0,0,0,0.05); }}
            
            .logo-img {{ max-height: 120px; width: auto; display: block; margin: 0 auto 10px; }}
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
            {logo_html}
            <h1>VPP TỊNH</h1>
            <p>🌿 Bình An Trao Tay 🌿</p>
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
    print("🚀 ĐANG KHỞI ĐỘNG BẢN 6.0 (FIX TRIỆT ĐỂ)...")
    
    try:
        print("⏳ Đang tải dữ liệu...")
        r = requests.get(LINK_CSV, timeout=60)
        r.encoding = 'utf-8'
        if r.status_code != 200: return

        reader = csv.DictReader(io.StringIO(r.text))
        all_products = []
        
        print("⚙️ Đang lọc (Điều kiện: VPP + Có bán + Giá hợp lý)...")
        
        for row in reader:
            ten = row.get('name', '').lower()
            
            # 1. LỌC TỪ KHÓA
            if not any(w in ten for w in VPP_KEYWORDS): continue
            if any(bad in ten for bad in CANT_TAKE): continue

            # 2. LỌC SALES: > 10 (Hạ chuẩn xuống để lấy được nhiều hàng hơn)
            try:
                sales = int(row.get('sales', 0))
            except:
                sales = 0
            
            if sales < 10: continue 

            # 3. LỌC GIÁ: Bỏ hàng < 2k
            try:
                # Lấy giá raw để check điều kiện lọc trước
                gia_check = float(str(row.get('price', 0)).replace(',', ''))
                if gia_check < 2000: continue
            except:
                continue

            all_products.append({
                "name": row.get('name'),
                "price": xuly_gia_chuan(row.get('price')), # Dùng hàm giá mới
                "sales": sales,
                "image": row.get('image', '').split(',')[0].strip(' []"'),
                "link": tao_link_aff(row.get('url'))
            })

        all_products.sort(key=lambda x: x['sales'], reverse=True)
        top_60 = all_products[:60]

        if len(top_60) == 0:
            print("❌ CẢNH BÁO: Không tìm thấy sản phẩm!")
        else:
            print(f"✅ Đã lọc được {len(top_60)} sản phẩm CHUẨN.")

        with open(FILE_JSON, "w", encoding="utf-8") as f:
            json.dump(top_60, f, ensure_ascii=False, indent=4)
        
        html_content = tao_web_html(top_60)
        with open("index.html", "w", encoding="utf-8") as f:
            f.write(html_content)
            
        print("☁️ Đang đẩy lên mạng (BẮT BUỘC ĐẨY LOGO)...")
        
        # --- CỤM LỆNH QUAN TRỌNG ĐỂ HIỆN LOGO ---
        # 1. Thêm tất cả file (bao gồm ảnh mới)
        os.system("git add .") 
        # 2. Ép thêm file logo.png cụ thể (để chắc chắn 100%)
        if os.path.exists("logo.png"):
            os.system("git add logo.png")
            print("📸 Đã tìm thấy logo.png và thêm vào gói hàng.")
        
        os.system('git commit -m "Final Fix 6.0"')
        os.system("git push")
        print("🎉 XONG! F5 trang web để xem kết quả.")

    except Exception as e:
        print(f"❌ Lỗi: {e}")

if __name__ == "__main__":
    chay_ngay_di()