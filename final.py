import csv
import json
import os
import re
import base64 
import time
import webbrowser 

# ==========================================
# CẤU HÌNH HỆ THỐNG
# ==========================================
GA_ID = "G-XXXXXXXXXX"
LOGO_URL = "https://cdn-icons-png.flaticon.com/512/3225/3225194.png"

# 🔴 HÌNH ẢNH KHI CHIA SẺ LÊN FACEBOOK/ZALO
# Bạn thay tên file "tinh_radio_banner.jpg" thành tên hình sản phẩm bạn muốn hiển thị nhé!
SHARE_IMAGE_URL = "https://vpptinh.com/static/images/tinh_radio_banner.jpg"

FILE_CSV_LOCAL = r"F:\web-banhang\danh_sach_san_pham.csv" 
FILE_JSON = "products.json"
BASE_AFF_URL = "https://go.isclix.com/deep_link/v6/6906519896943843292/4751584435713464237?sub4=oneatweb&utm_source=shopee&utm_campaign=sansale&url_enc="

# ==========================================
# CÁC HÀM XỬ LÝ LÕI
# ==========================================
def tao_link_aff(url_goc):
    if not url_goc: return "#"
    if "shope.ee" in url_goc or "isclix.com" in url_goc or "c.lazada.vn" in url_goc:
        return url_goc
    try:
        encoded = base64.b64encode(url_goc.strip().encode("utf-8")).decode("utf-8")
        return f"{BASE_AFF_URL}{encoded}"
    except:
        return url_goc

def tao_web_html(products):
    v = int(time.time())
    ga_script = ""
    if GA_ID != "G-XXXXXXXXXX":
        ga_script = f"""
        <script async src="https://www.googletagmanager.com/gtag/js?id={GA_ID}"></script>
        <script>
          window.dataLayer = window.dataLayer || [];
          function gtag(){{dataLayer.push(arguments);}}
          gtag('js', new Date());
          gtag('config', '{GA_ID}');
        </script>
        """

    html = f"""
    <!DOCTYPE html>
    <html lang="vi">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <meta name="referrer" content="no-referrer" />
        <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate" />
        
        <meta property="og:title" content="VPP Tịnh Shop - Săn Deal Giá Sốc" />
        <meta property="og:description" content="Chuyên săn deal giảm giá cực sốc các sản phẩm đồ gia dụng, văn phòng phẩm, mẹ và bé. Nhấn vào để xem ngay!" />
        <meta property="og:image" content="{SHARE_IMAGE_URL}" />
        <meta property="og:url" content="https://vpptinh.com/" />
        <meta property="og:type" content="website" />
        <meta name="twitter:card" content="summary_large_image">

        <title>Tịnh Shop - Săn Deal Giá Sốc Shopee</title>
        <link rel="icon" href="{LOGO_URL}">
        {ga_script}
        <style>
            :root {{ --primary: #d0011b; --bg: #f5f5f5; --text-gray: #555; }}
            body {{ font-family: sans-serif; background: var(--bg); margin: 0; padding: 0 0 40px 0; }}
            
            .header {{ text-align: center; background: white; padding: 0; border-bottom: 3px solid var(--primary); margin-bottom: 20px; position: relative; overflow: hidden; }}
            
            .header-bg {{ 
                width: 100%; 
                max-width: 1200px;
                margin: 0 auto;
                aspect-ratio: 1360 / 350; 
                background-image: url('static/images/tinh_radio_banner.jpg'); 
                background-size: cover; 
                background-position: center; 
                background-repeat: no-repeat;
                display: flex; align-items: center; justify-content: center; 
            }}
            @media (max-width: 630px) {{ .header-bg {{ aspect-ratio: 1360 / 600; min-height: 180px; }} }}
            .header-bg h1, .header-bg p {{ display: none; }}
            
            .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 10px; max-width: 1200px; margin: 0 auto; padding: 0 10px; }}
            .card {{ background: white; border-radius: 4px; overflow: hidden; display: flex; flex-direction: column; position: relative; box-shadow: 0 1px 2px rgba(0,0,0,0.1); transition: transform 0.2s; border: 1px solid #eee;}}
            .card:hover {{ transform: translateY(-2px); box-shadow: 0 4px 8px rgba(0,0,0,0.15); }}
            
            .discount-tag {{ position: absolute; top: 0; right: 0; background: #ffd424; color: #d0011b; padding: 4px 8px; font-weight: bold; font-size: 12px; z-index: 1; border-bottom-left-radius: 4px;}}
            .img-box {{ width: 100%; height: 190px; display: flex; align-items: center; justify-content: center; padding: 10px; box-sizing: border-box; background: white;}}
            .img-box img {{ max-width: 100%; max-height: 100%; object-fit: contain; }}
            .info {{ padding: 10px; display: flex; flex-direction: column; flex-grow: 1; justify-content: space-between; }}
            .title {{ font-size: 13px; color: #333; margin-bottom: 8px; height: 36px; line-height: 18px; overflow: hidden; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; }}
            .price-box {{ margin-bottom: 8px; }}
            .old-price {{ text-decoration: line-through; color: #999; font-size: 12px; margin-right: 5px; }}
            .new-price {{ color: var(--primary); font-weight: bold; font-size: 16px; }}
            .btn {{ background: var(--primary); color: white; text-decoration: none; padding: 8px; display: block; text-align: center; border-radius: 4px; font-weight: bold; font-size: 14px; }}
            .btn:hover {{ background: #b00117; }}
        </style>
    </head>
    <body>
        <div class="header header-bg"><div><p>VPP Tịnh Shop</p></div></div>
        
        <div class="grid">
    """
    
    for p in products:
        try:
            chuoi_goc = re.sub(r'[^\d]', '', str(p['old_price']))
            chuoi_moi = re.sub(r'[^\d]', '', str(p['new_price']))
            goc = float(chuoi_goc) if chuoi_goc else 0
            moi = float(chuoi_moi) if chuoi_moi else 0
            percent = int((goc - moi) / goc * 100) if goc > moi else 0
        except:
            goc, moi, percent = 0, 0, 0

        discount_html = f'<div class="discount-tag">-{percent}%</div>' if percent > 0 else ""
        old_price_html = f'<span class="old-price">{int(goc):,}₫</span>'.replace(",", ".") if percent > 0 else ""
        new_price_format = f"{int(moi):,}₫".replace(",", ".")
        
        html += f"""
            <div class="card">
                {discount_html}
                <div class="img-box"><img src="{p['image']}" loading="lazy" onerror="this.src='https://placehold.co/200x200?text=No+Image'"></div>
                <div class="info">
                    <div class="title">{p['name']}</div>
                    <div class="price-box">{old_price_html}<span class="new-price">{new_price_format}</span></div>
                    <a href="{p['link']}" class="btn" target="_blank">Mua Ngay</a>
                </div>
            </div>
        """
    
    html += """
        </div>
    </body></html>
    """
    return html

def chay_he_thong():
    print(f"🚀 ĐANG KHỞI TẠO HỆ THỐNG TỪ FILE: {FILE_CSV_LOCAL}")
    try:
        if not os.path.exists(FILE_CSV_LOCAL):
            print(f"❌ LỖI: Không tìm thấy file CSV tại: {FILE_CSV_LOCAL}")
            return

        clean_products = []
        with open(FILE_CSV_LOCAL, mode='r', encoding='utf-8-sig') as f:
            first_line = f.readline()
            f.seek(0)
            dau_ngan_cach = ';' if ';' in first_line else ','
            
            reader = csv.DictReader(f, delimiter=dau_ngan_cach)
            field_map = {name: name.strip() for name in reader.fieldnames if name}
            
            for row in reader:
                row_clean = {field_map[k]: v for k, v in row.items() if k in field_map}
                
                name = row_clean.get('name')
                if not name: continue
                
                link_goc = row_clean.get('link', '#').strip()
                link_anh = row_clean.get('image', '').strip(' \'"[]')

                if not link_anh.startswith('http'):
                    ten_file_anh = link_anh.replace('\\', '/').split('/')[-1]
                    link_anh_chuan = f"static/images/{ten_file_anh}"
                    if not os.path.exists(link_anh_chuan):
                        print(f"⚠️ BÁO ĐỘNG: KHÔNG TÌM THẤY TẤM ẢNH '{ten_file_anh}'")
                    link_anh = link_anh_chuan
                
                clean_products.append({
                    "name": name.strip(),
                    "old_price": row_clean.get('old_price', '0').strip(),
                    "new_price": row_clean.get('new_price', '0').strip(),
                    "image": link_anh,
                    "link": tao_link_aff(link_goc)
                })

        print(f"✅ Đã đọc thành công {len(clean_products)} sản phẩm.")
        
        with open(FILE_JSON, "w", encoding="utf-8") as f:
            json.dump(clean_products, f, ensure_ascii=False, indent=4)
        
        with open("index.html", "w", encoding="utf-8") as f:
            f.write(tao_web_html(clean_products))
        
        print("\n⏳ Đang đẩy code lên kho chứa (Github)...")
        time.sleep(2)
        os.system("git add .")
        os.system('git commit -m "Them hinh anh chia se Facebook"')
        os.system("git push")
        print("✅ HOÀN TẤT! Web vpptinh.com đã lên sóng.")

    except Exception as e:
        print(f"❌ Có lỗi nghiêm trọng xảy ra: {e}")

if __name__ == "__main__":
    chay_he_thong()