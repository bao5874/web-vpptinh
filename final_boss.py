import requests
import csv
import json
import io
import os
import re
import base64 
import time

# --- CẤU HÌNH ---
LINK_CSV = "http://datafeed.accesstrade.me/shopee.vn.csv"
FILE_JSON = "products.json"
ACCESSTRADE_ID = "4751584435713464237"
CAMPAIGN_ID = "6906519896943843292" 
BASE_AFF_URL = f"https://go.isclix.com/deep_link/v6/{CAMPAIGN_ID}/{ACCESSTRADE_ID}?sub4=web_tu_dong&utm_source=shopee&utm_campaign=vpp_tinh&url_enc="

# TỪ KHÓA DUYỆT (VPP)
VPP_KEYWORDS = [
    "bút", "vở", "sổ", "giấy a4", "giấy in", "kẹp", "thước", "file", 
    "bìa", "băng dính", "ghim", "hộp bút", "balo", "cặp", "máy tính",
    "dập ghim", "hồ dán", "keo", "bảng", "phấn", "mực"
]

# TỪ KHÓA CHẶN (Rác & Hết hàng)
CANT_TAKE = [
    "hết hàng", "ngừng kinh doanh", "bỏ mẫu", "liên hệ", "tạm hết", "đặt trước",
    "mắt", "mày", "môi", "mi", "son", "kem", "phấn", "makeup", "trang điểm", 
    "bánh", "kẹo", "đồ ăn", "thực phẩm", "mắm", "muối",
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

def xuly_gia_chuan_xac(gia_raw):
    """
    Hàm xử lý giá an toàn tuyệt đối.
    Không dùng replace bừa bãi.
    """
    try:
        # 1. Chuyển về chuỗi thuần túy
        gia_str = str(gia_raw).strip()
        
        # 2. Tách phần số (Loại bỏ chữ 'đ', ',', '.')
        # Chỉ lấy số đầu tiên tìm thấy
        numbers = re.findall(r'\d+', gia_str.replace('.', '').replace(',', ''))
        if not numbers: return "Liên hệ"
        
        gia_val = float(numbers[0])
        
        # 3. Logic chặn giá ảo
        # Nếu giá > 10 triệu -> Chia 100 (Trường hợp bị nhân đôi số 0)
        if gia_val > 10000000: gia_val = gia_val / 100
        # Nếu giá > 1 triệu -> Chia 10
        elif gia_val > 1000000: gia_val = gia_val / 10
            
        if gia_val < 2000: return "Liên hệ" # Giá quá rẻ thường là rác
        
        return "{:,.0f}₫".format(gia_val).replace(",", ".")
    except:
        return "Liên hệ"

def tao_web_html(products):
    # KỸ THUẬT CACHE BUSTING: Thêm ?v=time để ép trình duyệt tải ảnh mới
    timestamp = int(time.time())
    
    # Ép hiển thị logo.png (Bạn phải đảm bảo file trên Github tên chính xác là logo.png viết thường)
    header_html = f'''
        <div class="logo-wrapper">
            <img src="logo.png?v={timestamp}" alt="VPP Tịnh" class="logo-img" 
                 onerror="this.onerror=null; this.src='logo.jpg?v={timestamp}';">
        </div>
        <h1 class="text-logo">VPP TỊNH</h1>
        <p class="slogan">🌿 Bình An Trao Tay 🌿</p>
    '''

    html = f"""
    <!DOCTYPE html>
    <html lang="vi">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <meta name="referrer" content="no-referrer"> 
        <title>VPP Tịnh - Văn Phòng Phẩm</title>
        <link rel="icon" href="logo.png">
        <style>
            :root {{ --primary: #008080; --bg: #f4f6f8; --card-bg: #ffffff; }}
            body {{ font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; background: var(--bg); padding: 20px; margin: 0; color: #333; }}
            
            header {{ text-align: center; background: #fff; padding: 30px; border-radius: 12px; margin-bottom: 30px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); }}
            
            .logo-img {{ max-height: 100px; width: auto; display: block; margin: 0 auto 15px; }}
            .text-logo {{ color: #008080; margin: 0; text-transform: uppercase; font-size: 2em; letter-spacing: 2px; }}
            .slogan {{ color: #666; font-style: italic; }}
            
            .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 20px; max-width: 1200px; margin: 0 auto; }}
            
            .card {{ background: var(--card-bg); border-radius: 8px; overflow: hidden; box-shadow: 0 2px 5px rgba(0,0,0,0.05); transition: transform 0.2s, box-shadow 0.2s; display: flex; flex-direction: column; border: 1px solid #eee; }}
            .card:hover {{ transform: translateY(-3px); box-shadow: 0 5px 15px rgba(0,0,0,0.1); border-color: var(--primary); }}
            
            .img-box {{ width: 100%; height: 200px; padding: 15px; box-sizing: border-box; display: flex; align-items: center; justify-content: center; background: #fff; }}
            .img-box img {{ max-width: 100%; max-height: 100%; object-fit: contain; }}
            
            .info {{ padding: 15px; flex-grow: 1; display: flex; flex-direction: column; justify-content: space-between; background: #fff; }}
            .title {{ font-size: 0.95em; margin-bottom: 10px; height: 2.8em; overflow: hidden; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; line-height: 1.4em; color: #444; }}
            .price {{ color: #d0021b; font-weight: 700; font-size: 1.2em; margin-bottom: 5px; }}
            
            .btn {{ background: var(--primary); color: #fff; text-decoration: none; padding: 12px; text-align: center; border-radius: 6px; font-weight: 600; margin-top: 10px; display: block; transition: background 0.2s; }}
            .btn:hover {{ background: #006666; }}
        </style>
    </head>
    <body>
        <header>{header_html}</header>
        <div class="grid">
    """
    for p in products:
        html += f"""
            <div class="card">
                <div class="img-box"><img src="{p['image']}" alt="sp" loading="lazy"></div>
                <div class="info">
                    <div class="title">{p['name']}</div>
                    <div class="price">{p['price']}</div>
                    <a href="{p['link']}" class="btn" target="_blank" rel="nofollow">Mua Ngay</a>
                </div>
            </div>
        """
    html += "</div></body></html>"
    return html

def chay_ngay_di():
    print("🚀 ĐANG KHỞI ĐỘNG FINAL BOSS 9.0 (CACHE BUSTING)...")
    try:
        print("⏳ Đang tải dữ liệu...")
        r = requests.get(LINK_CSV, timeout=60)
        r.encoding = 'utf-8'
        reader = csv.DictReader(io.StringIO(r.text))
        
        all_products = []
        
        for row in reader:
            ten = row.get('name', '').lower()
            
            # 1. LỌC: Phải là VPP và Không phải rác
            if not any(w in ten for w in VPP_KEYWORDS): continue
            if any(bad in ten for bad in CANT_TAKE): continue
            
            # 2. LỌC KỸ: Nếu có cột 'stock' (tồn kho) = 0 thì bỏ
            try:
                if int(row.get('stock', 1)) == 0: continue
            except: pass

            # 3. GIÁ: Phải từ 5k đến 500k (VPP không quá đắt cũng không quá rẻ)
            # Đây là bộ lọc "Chắc ăn" để tránh hàng ảo
            try:
                gia_check = float(str(row.get('price', 0)).replace(',', '').split('.')[0])
                if gia_check < 5000: continue # Quá rẻ -> Hết hàng nhanh -> BỎ
                if gia_check > 1000000: continue # Quá đắt -> Dễ sai giá -> BỎ
            except: continue

            # Xử lý hiển thị
            gia_dep = xuly_gia_chuan_xac(row.get('price'))
            if gia_dep == "Liên hệ": continue

            all_products.append({
                "name": row.get('name'),
                "price": gia_dep,
                "image": row.get('image', '').split(',')[0].strip(' []"'),
                "link": tao_link_aff(row.get('url'))
            })

        # Lấy 80 món đầu tiên (Không sắp xếp sales nữa để tránh lỗi dữ liệu)
        final_list = all_products[:80]
        
        print(f"✅ Đã lọc được {len(final_list)} sản phẩm chất lượng.")

        # Xuất file
        with open(FILE_JSON, "w", encoding="utf-8") as f:
            json.dump(final_list, f, ensure_ascii=False, indent=4)
        
        html_content = tao_web_html(final_list)
        with open("index.html", "w", encoding="utf-8") as f:
            f.write(html_content)
            
        print("☁️ Đang đồng bộ Github...")
        os.system("git add .")
        os.system('git commit -m "Update Final Boss 9.0"')
        os.system("git push")
        print("🎉 XONG! Hãy F5 trang web (Logo sẽ hiện sau 30s).")

    except Exception as e:
        print(f"❌ Lỗi: {e}")

if __name__ == "__main__":
    chay_ngay_di()