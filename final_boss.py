import requests
import csv
import json
import os
import re
import base64 
import time
import webbrowser 

# --- CẤU HÌNH ---
LOGO_URL = "https://cdn-icons-png.flaticon.com/512/3225/3225194.png"
LINK_CSV = "http://datafeed.accesstrade.me/shopee.vn.csv" # Link CSV của bạn
FILE_JSON = "products.json"
BASE_AFF_URL = "https://go.isclix.com/deep_link/v6/6906519896943843292/4751584435713464237?sub4=oneatweb&utm_source=shopee&utm_campaign=sansale&url_enc="

# CHẶN RÁC
JUNK_BLACKLIST = [
    "hết hàng", "bỏ mẫu", "ngừng kinh doanh", "tạm hết", "liên hệ",
    "honda", "yamaha", "suzuki", "xe máy", "ô tô", "lốp", "nhớt", "pô",
    "mực khô", "mực rim", "hàng tươi sống", "đông lạnh",
    "voucher", "nạp thẻ", "sim", "sex toy", "người lớn"
]

# --- HÀM XỬ LÝ ---

def tao_link_aff(url_goc):
    if not url_goc: return "#"
    try:
        encoded = base64.b64encode(url_goc.strip().encode("utf-8")).decode("utf-8")
        return f"{BASE_AFF_URL}{encoded}"
    except:
        return url_goc

def tinh_gia_thuc(gia_goc_raw, discount_raw):
    try:
        gia_str = str(gia_goc_raw).split('.')[0] 
        numbers = re.findall(r'\d+', gia_str)
        if not numbers: return 0, 0, 0
        gia_goc = float("".join(numbers))
        
        try:
            d_str = str(discount_raw).replace('%', '')
            discount_val = float(d_str)
            if discount_val > 1: discount_val = discount_val / 100
        except:
            discount_val = 0

        gia_giam = gia_goc * (1 - discount_val)
        return gia_goc, gia_giam, discount_val * 100
    except:
        return 0, 0, 0

# --- HÀM MỚI: TỰ ĐỘNG PHÂN LOẠI SẢN PHẨM ---
def phan_loai_danh_muc(ten_san_pham):
    ten = ten_san_pham.lower()
    
    # 1. Điện tử & Remote
    keywords_dien_tu = ['remote', 'điều khiển', 'pin', 'sạc', 'cáp', 'tai nghe', 'loa', 'chuột', 'phím', 'wifi', 'sim', 'ốp lưng', 'cường lực']
    if any(k in ten for k in keywords_dien_tu): return 'dien-tu'
    
    # 2. Thời trang & Phụ kiện
    keywords_thoi_trang = ['túi', 'áo', 'quần', 'váy', 'đầm', 'kính', 'giày', 'dép', 'bông tai', 'dây chuyền', 'nhẫn', 'đồng hồ', 'mũ', 'nón', 'ví']
    if any(k in ten for k in keywords_thoi_trang): return 'thoi-trang'
    
    # 3. Mẹ & Bé / Đồ chơi
    keywords_me_be = ['đồ chơi', 'thú', 'gấu', 'búp bê', 'lắp ráp', 'lego', 'xe trượt', 'tã', 'bỉm', 'sữa', 'bé', 'trẻ', 'treo nôi']
    if any(k in ten for k in keywords_me_be): return 'me-be'
    
    # 4. Nhà cửa & Đời sống
    keywords_nha_cua = ['tranh', 'decal', 'kệ', 'hộp', 'bút', 'sổ', 'giấy', 'đèn', 'khay', 'bếp', 'nồi', 'chảo', 'dao', 'kéo', 'gối', 'chăn', 'ga']
    if any(k in ten for k in keywords_nha_cua): return 'nha-cua'
    
    # Mặc định
    return 'khac'

def tao_web_html(products):
    v = int(time.time())
    html = f"""
    <!DOCTYPE html>
    <html lang="vi">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate" />
        <title>Tịnh Shop - Săn Deal Giá Sốc</title>
        <link rel="icon" href="{LOGO_URL}">
        <style>
            :root {{ --primary: #d0011b; --bg: #f5f5f5; --text-gray: #555; }}
            body {{ font-family: sans-serif; background: var(--bg); margin: 0; padding: 20px; }}
            
            /* Header & Banner */
            .header {{ text-align: center; background: white; padding: 0; border-bottom: 3px solid var(--primary); margin-bottom: 20px; position: relative; overflow: hidden; }}
            .header-bg {{
                width: 100%;
                aspect-ratio: 1360 / 453; 
                background-image: url('/banner-top.jpg'); 
                background-size: cover;
                background-position: center;
                background-repeat: no-repeat;
                display: flex; align-items: center; justify-content: center;
            }}
            @media (max-width: 630px) {{
                .header-bg {{ aspect-ratio: unset; min-height: 150px; }}
            }}
            .header-bg h1, .header-bg p {{ display: none; }}

            /* Menu Danh Mục */
            .category-menu {{
                display: flex;
                justify-content: center;
                flex-wrap: wrap;
                gap: 10px;
                margin-bottom: 25px;
                position: sticky;
                top: 10px;
                z-index: 100;
            }}
            .cat-btn {{
                padding: 8px 16px;
                border: 1px solid #ddd;
                background: white;
                color: var(--text-gray);
                cursor: pointer;
                border-radius: 20px;
                font-weight: 600;
                font-size: 14px;
                transition: all 0.3s ease;
                box-shadow: 0 2px 5px rgba(0,0,0,0.05);
            }}
            .cat-btn:hover {{ background: #eee; }}
            .cat-btn.active {{
                background: var(--primary);
                color: white;
                border-color: var(--primary);
                box-shadow: 0 4px 8px rgba(208, 1, 27, 0.3);
            }}

            /* Grid & Card */
            .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 10px; max-width: 1200px; margin: 0 auto; }}
            .card {{ 
                background: white; border-radius: 4px; overflow: hidden; display: flex; flex-direction: column; position: relative; 
                box-shadow: 0 1px 2px rgba(0,0,0,0.1); transition: transform 0.2s;
            }}
            .card:hover {{ transform: translateY(-2px); }}
            .card.hide {{ display: none; }}
            
            .discount-tag {{ position: absolute; top: 0; right: 0; background: #ffd424; color: #d0011b; padding: 4px 8px; font-weight: bold; font-size: 12px; z-index: 1; }}
            .img-box {{ width: 100%; height: 190px; display: flex; align-items: center; justify-content: center; padding: 10px; box-sizing: border-box; }}
            .img-box img {{ max-width: 100%; max-height: 100%; object-fit: contain; }}
            .info {{ padding: 10px; }}
            .title {{ font-size: 12px; color: #333; margin-bottom: 5px; height: 32px; overflow: hidden; line-height: 16px; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; }}
            .old-price {{ text-decoration: line-through; color: #999; font-size: 12px; margin-right: 5px; }}
            .new-price {{ color: var(--primary); font-weight: bold; font-size: 16px; }}
            .btn {{ background: var(--primary); color: white; text-decoration: none; padding: 8px; display: block; text-align: center; margin-top: 5px; border-radius: 2px; font-weight: bold; font-size: 13px; }}
        </style>
    </head>
    <body>
        <div class="header header-bg">
            <div><p>VPP Tịnh Shop</p></div>
        </div>

        <div class="category-menu">
            <button class="cat-btn active" data-filter="all">Tất cả</button>
            <button class="cat-btn" data-filter="thoi-trang">Thời trang & Phụ kiện</button>
            <button class="cat-btn" data-filter="dien-tu">Điện tử & Remote</button>
            <button class="cat-btn" data-filter="nha-cua">Nhà cửa & Đời sống</button>
            <button class="cat-btn" data-filter="me-be">Mẹ & Bé / Đồ chơi</button>
        </div>

        <div class="grid">
    """
    
    for p in products:
        discount_html = f'<div class="discount-tag">-{int(p["percent"])}%</div>' if p["percent"] > 0 else ""
        old_price_html = f'<span class="old-price">{p["old_price"]}</span>' if p["percent"] > 0 else ""
        
        # TỰ ĐỘNG PHÂN LOẠI
        category_code = phan_loai_danh_muc(p['name'])
        
        html += f"""
            <div class="card" data-category="{category_code}">
                {discount_html}
                <div class="img-box"><img src="{p['image']}" loading="lazy"></div>
                <div class="info">
                    <div class="title">{p['name']}</div>
                    <div>
                        {old_price_html}
                        <span class="new-price">{p['new_price']}</span>
                    </div>
                    <a href="{p['link']}" class="btn" target="_blank">Mua Ngay</a>
                </div>
            </div>
        """
    
    html += """
        </div>
        
        <script>
            document.addEventListener('DOMContentLoaded', function() {
                const filterButtons = document.querySelectorAll('.cat-btn');
                const productCards = document.querySelectorAll('.card');

                filterButtons.forEach(button => {
                    button.addEventListener('click', () => {
                        filterButtons.forEach(btn => btn.classList.remove('active'));
                        button.classList.add('active');
                        const filterValue = button.getAttribute('data-filter');

                        productCards.forEach(card => {
                            if (filterValue === 'all' || card.getAttribute('data-category') === filterValue) {
                                card.classList.remove('hide');
                            } else {
                                card.classList.add('hide');
                            }
                        });
                    });
                });
            });
        </script>
    </body></html>
    """
    return html

def chay_ngay_di():
    print("🚀 ĐANG CHẠY FINAL BOSS 22.0 (AUTO-CATEGORY)...")
    try:
        r = requests.get(LINK_CSV, timeout=60)
        # Fix lỗi encoding nếu có
        r.encoding = 'utf-8' 
        
        lines = r.text.splitlines()
        header = [h.replace('"', '').strip() for h in lines[0].split(',')]
        reader = csv.DictReader(lines[1:], fieldnames=header)
        
        clean_products = []
        for row in reader:
            ten = row.get('name', '').lower()
            if any(bad in ten for bad in JUNK_BLACKLIST): continue

            # Xử lý giá
            price_raw = row.get('price', row.get('price_v2', '0'))
            disc_raw = row.get('discount', row.get('discount_rate', '0'))
            
            gia_goc, gia_giam, phan_tram = tinh_gia_thuc(price_raw, disc_raw)
            
            if gia_giam < 5000 or gia_giam > 10000000: continue
            if phan_tram < 1: continue 

            clean_products.append({
                "name": row.get('name'),
                "old_price": "{:,.0f}₫".format(gia_goc).replace(",", "."),
                "new_price": "{:,.0f}₫".format(gia_giam).replace(",", "."),
                "percent": phan_tram,
                "image": row.get('image', '').split(',')[0].strip(' []"'),
                "link": tao_link_aff(row.get('url'))
            })

        clean_products.sort(key=lambda x: x['percent'], reverse=True)
        final_list = clean_products[:150] # Lấy 150 sản phẩm
        
        print(f"✅ Tìm thấy {len(final_list)} sản phẩm.")
        
        # Tạo file JSON
        with open(FILE_JSON, "w", encoding="utf-8") as f:
            json.dump(final_list, f, ensure_ascii=False, indent=4)
        
        # Tạo file HTML (có danh mục)
        with open("index.html", "w", encoding="utf-8") as f:
            f.write(tao_web_html(final_list))
        
        print("👉 Đang mở web kiểm tra...")
        webbrowser.open("file://" + os.path.realpath("index.html"))
        
        # Tự động đẩy lên Git luôn không cần hỏi
        print("⏳ Đang tự động đẩy code lên Github...")
        time.sleep(2)
        os.system("git add .")
        os.system('git commit -m "Auto Update V22 with Categories"')
        os.system("git push")
        print("✅ ĐÃ PUSH XONG! Hãy vào: vpptinh.com xem kết quả.")

    except Exception as e:
        print(f"❌ Lỗi: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    chay_ngay_di()