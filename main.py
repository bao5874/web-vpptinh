import csv
import json
import os
import re
import base64 
import time
import random
import webbrowser 
import unicodedata

try:
    from google import genai
    from google.genai import types
except ImportError:
    print("❌ THIẾU THƯ VIỆN AI! Hãy mở Terminal gõ lệnh: pip install google-genai")
    exit()

# ==========================================
# CẤU HÌNH HỆ THỐNG
# ==========================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FILE_CSV_LOCAL = os.path.join(BASE_DIR, "danh_sach_san_pham.csv")
FILE_JSON = os.path.join(BASE_DIR, "products.json")
THU_MUC_SAN_PHAM = os.path.join(BASE_DIR, "san-pham")

GA_ID = "G-XXXXXXXXXX"
LOGO_URL = "https://cdn-icons-png.flaticon.com/512/3225/3225194.png"
SHARE_IMAGE_URL = "https://vpptinh.com/static/images/tinh_radio_banner1.jpg"
BASE_AFF_URL = "https://go.isclix.com/deep_link/v6/6906519896943843292/4751584435713464237?sub4=oneatweb&utm_source=shopee&utm_campaign=sansale&url_enc="
ZALO_NUMBER = "0931736266" 

DANH_MUC_MAP = {
    "tho_cung": "Đồ Thờ Cúng", "dc_vs": "Dụng Cụ Vệ Sinh", 
    "vpp": "Văn Phòng Phẩm", "gia_dung": "Đồ Gia Dụng", 
    "me_be": "Mẹ & Bé", "khac": "Sản Phẩm Khác"
}

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    try:
        with open(os.path.join(BASE_DIR, "api_key.txt"), "r") as f:
            GEMINI_API_KEY = f.read().strip()
    except FileNotFoundError:
        print("⚠️ CHƯA CÓ FILE api_key.txt VÀ KHÔNG TÌM THẤY BIẾN MÔI TRƯỜNG!")

# ==========================================
# CÁC HÀM XỬ LÝ LÕI
# ==========================================
def tao_link_aff(url_goc):
    if not url_goc: return "#"
    if "shope.ee" in url_goc or "isclix.com" in url_goc or "c.lazada.vn" in url_goc: return url_goc
    try: return f"{BASE_AFF_URL}{base64.b64encode(url_goc.strip().encode('utf-8')).decode('utf-8')}"
    except: return url_goc

def tao_slug(chuoi):
    chuoi = str(chuoi)
    chuoi = unicodedata.normalize('NFKD', chuoi).encode('ascii', 'ignore').decode('utf-8')
    chuoi = re.sub(r'[^\w\s-]', '', chuoi).strip().lower()
    return re.sub(r'[-\s]+', '-', chuoi)

def goi_ai_viet_mo_ta_hang_loat(danh_sach_sp_thieu):
    if not GEMINI_API_KEY: return {}
    print(f"📦 Đang gửi {len(danh_sach_sp_thieu)} sản phẩm cho AI xử lý...")
    
    sp_text = "".join([f"- ID: {sp['id']} | Tên: {sp['name']} | Mô tả gốc: {sp['mo_ta_goc'][:300]}...\n" for sp in danh_sach_sp_thieu])

    prompt = f"""Bạn là Copywriter SEO đỉnh cao của VPP Tịnh Shop (chuyên văn phòng phẩm & đồ gia dụng).
    Dựa vào thông số trong "Mô tả gốc", hãy viết lại cho mỗi sản phẩm 1 đoạn văn (80 - 100 chữ) chốt sale.
    
    Quy tắc:
    1. Lọc sạch hashtag, số điện thoại, chính sách cũ của shop gốc.
    2. Chèn tự nhiên các từ khóa: "giá rẻ", "chính hãng", "văn phòng phẩm", "tiện ích".
    3. Trình bày 1 đoạn văn liền mạch. Kết thúc bằng 1 câu Call-to-action tạo sự khan hiếm (VD: Số lượng có hạn, săn deal ngay hôm nay!).
    
    BẮT BUỘC TRẢ VỀ JSON: {{"results": [{{"id": "id_sp", "mo_ta_ai": "nội dung..."}}]}}
    
    Sản phẩm:
    {sp_text}
    """

    for attempt in range(4):
        try:
            client = genai.Client(api_key=GEMINI_API_KEY)
            response = client.models.generate_content(
                model='gemini-2.5-flash', contents=prompt,
                config=types.GenerateContentConfig(temperature=0.7, response_mime_type="application/json")
            )
            data = json.loads(response.text)
            return {str(item["id"]): str(item["mo_ta_ai"]).strip() for item in data.get("results", [])}
        except Exception as e:
            thoi_gian_cho = (attempt + 1) * 15 
            print(f" ⏳ Lỗi API/Quá tải. Tự động chờ {thoi_gian_cho} giây... (Lần {attempt+1}/4)")
            time.sleep(thoi_gian_cho)
    return {}

def tao_trang_chi_tiet(p):
    slug = p['slug']
    chuoi_moi = re.sub(r'[^\d]', '', str(p['new_price']))
    moi = float(chuoi_moi) if chuoi_moi else 0
    new_price_format = f"{int(moi):,}₫".replace(",", ".")
    
    img_url = p['image'] if p['image'].startswith('http') else f"../{p['image']}"
    
    html = f"""<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{p['name']} | VPP Tịnh Shop</title>
    <meta name="description" content="{p['mo_ta_ai'][:150]}...">
    <link rel="canonical" href="https://vpptinh.com/san-pham/{slug}.html" />
    <style>
        body {{ font-family: sans-serif; background: #f5f5f5; margin: 0; padding: 20px; color: #333; }}
        .container {{ max-width: 800px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .breadcrumb {{ font-size: 14px; margin-bottom: 20px; color: #777; }}
        .breadcrumb a {{ color: #d0011b; text-decoration: none; }}
        .product-img {{ text-align: center; margin-bottom: 20px; }}
        .product-img img {{ max-width: 100%; max-height: 400px; border-radius: 8px; object-fit: contain; }}
        h1 {{ font-size: 24px; color: #222; margin-bottom: 10px; }}
        .price {{ font-size: 28px; color: #d0011b; font-weight: bold; margin-bottom: 20px; }}
        .desc {{ line-height: 1.6; color: #555; margin-bottom: 30px; white-space: pre-line; }}
        .btn-buy {{ display: block; background: #d0011b; color: white; text-align: center; padding: 15px; text-decoration: none; font-size: 18px; font-weight: bold; border-radius: 5px; }}
        .btn-buy:hover {{ background: #b00117; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="breadcrumb"><a href="../index.html">Trang chủ</a> / {DANH_MUC_MAP.get(p['danh_muc'], 'Sản phẩm')} / {p['name']}</div>
        <div class="product-img"><img src="{img_url}" alt="{p['name']} chính hãng giá rẻ"></div>
        <h1>{p['name']}</h1>
        <div class="price">{new_price_format}</div>
        <div class="desc">{p['mo_ta_ai']}</div>
        <a href="{p['link']}" class="btn-buy" target="_blank" rel="nofollow">ĐẾN NƠI BÁN / NHẬN ƯU ĐÃI NGAY</a>
    </div>
</body>
</html>"""
    
    with open(os.path.join(THU_MUC_SAN_PHAM, f"{slug}.html"), "w", encoding="utf-8") as f:
        f.write(html)

def tao_web_html(products):
    ga_script = f"""<script async src="https://www.googletagmanager.com/gtag/js?id={GA_ID}"></script><script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments);}}gtag('js',new Date());gtag('config','{GA_ID}');</script>""" if GA_ID != "G-XXXXXXXXXX" else ""

    unique_cats = list(set([p.get('danh_muc', 'khac') for p in products]))
    
    menu_html = '<div class="category-menu"><button class="cat-btn active" onclick="setCategory(\'all\', this)">Tất Cả</button>'
    for cat in unique_cats:
        menu_html += f'<button class="cat-btn" onclick="setCategory(\'{cat}\', this)">{DANH_MUC_MAP.get(cat, cat.title())}</button>'
    menu_html += '</div>'

    html = f"""<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="canonical" href="https://vpptinh.com/" />
    <title>VPP Tịnh Shop | Săn Deal Đồ Gia Dụng & Văn Phòng Phẩm</title>
    {ga_script}
    <style>
        :root {{ --primary: #d0011b; --bg: #f5f5f5; }}
        body {{ font-family: sans-serif; background: var(--bg); margin: 0; padding: 0 0 40px 0; }}
        .header-bg {{ width: 100%; max-width: 1200px; margin: 0 auto; aspect-ratio: 1360/350; background-image: url('static/images/tinh_radio_banner1.jpg'); background-size: cover; background-position: center; margin-bottom: 20px;}}
        .sr-only {{ position: absolute; width: 1px; height: 1px; padding: 0; margin: -1px; overflow: hidden; clip: rect(0,0,0,0); border: 0; }}
        .search-container {{ max-width: 600px; margin: 0 auto 20px; padding: 0 15px; text-align: center; }}
        .search-input {{ width: 100%; padding: 12px 20px; border: 2px solid #ddd; border-radius: 30px; font-size: 15px; outline: none; }}
        .category-menu {{ display: flex; justify-content: center; gap: 10px; margin: 0 auto 20px; max-width: 1200px; flex-wrap: wrap; }}
        .cat-btn {{ background: white; border: 1px solid #ddd; padding: 8px 20px; border-radius: 20px; cursor: pointer; font-weight: bold; }}
        .cat-btn.active {{ background: var(--primary); color: white; border-color: var(--primary); }}
        .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 10px; max-width: 1200px; margin: 0 auto 20px; padding: 0 10px; }}
        .card {{ background: white; border-radius: 4px; overflow: hidden; display: none; flex-direction: column; position: relative; border: 1px solid #eee; }}
        .card.show {{ display: flex; }}
        .img-box {{ width: 100%; height: 190px; display: flex; align-items: center; justify-content: center; padding: 10px; box-sizing: border-box; }}
        .img-box img {{ max-width: 100%; max-height: 100%; object-fit: contain; }}
        .info {{ padding: 10px; display: flex; flex-direction: column; flex-grow: 1; }}
        .title {{ font-size: 13px; color: #333; margin-bottom: 5px; height: 36px; overflow: hidden; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; text-decoration: none;}}
        .rating {{ font-size: 11px; color: #ffc107; margin-bottom: 8px; }}
        .price-box {{ margin-bottom: 8px; }}
        .new-price {{ color: var(--primary); font-weight: bold; font-size: 16px; }}
        .btn {{ background: var(--primary); color: white; text-decoration: none; padding: 8px; text-align: center; border-radius: 4px; font-weight: bold; font-size: 14px; margin-top: auto;}}
        .load-more-container {{ text-align: center; margin: 20px 0; }}
        .btn-load-more {{ background: white; border: 2px solid var(--primary); color: var(--primary); padding: 10px 30px; border-radius: 25px; cursor: pointer; font-weight: bold; }}
    </style>
</head>
<body>
    <div class="header-bg"><h1 class="sr-only">VPP Tịnh Shop - Chuyên Sỉ Lẻ Văn Phòng Phẩm & Đồ Gia Dụng</h1></div>
    <div class="search-container"><input type="text" id="searchInput" class="search-input" onkeyup="filterProducts()" placeholder="🔍 Tìm kiếm sản phẩm..."></div>
    {menu_html}
    <div class="grid" id="productGrid">
"""
    
    for p in products:
        try: moi = float(re.sub(r'[^\d]', '', str(p['new_price']))) if re.sub(r'[^\d]', '', str(p['new_price'])) else 0
        except: moi = 0

        new_price_format = f"{int(moi):,}₫".replace(",", ".")
        fake_sold = random.randint(120, 3500) 
        link_chi_tiet = f"san-pham/{p['slug']}.html"

        html += f"""
        <div class="card" data-category="{p.get('danh_muc', 'khac')}" data-title="{p['name'].lower()}">
            <a href="{link_chi_tiet}" class="img-box"><img src="{p['image']}" alt="{p['name']} giá rẻ" loading="lazy" onerror="this.src='https://placehold.co/200x200?text=No+Image'"></a>
            <div class="info">
                <a href="{link_chi_tiet}" class="title">{p['name']}</a>
                <div class="rating">⭐⭐⭐⭐⭐ (Đã bán {fake_sold})</div>
                <div class="price-box"><span class="new-price">{new_price_format}</span></div>
                <a href="{link_chi_tiet}" class="btn">Xem Thêm</a>
            </div>
        </div>
        """
    
    html += """
    </div>
    <div class="load-more-container" id="loadMoreBox"><button class="btn-load-more" onclick="loadMore()">Xem thêm sản phẩm ⬇️</button></div>

    <script>
        let currentCat = 'all';
        let itemsToShow = 20; 
        
        function updateDisplay() {
            let cards = document.querySelectorAll('.card');
            let query = document.getElementById('searchInput').value.toLowerCase();
            let visibleCount = 0;
            let totalMatch = 0;

            cards.forEach(card => {
                let matchCat = (currentCat === 'all' || card.getAttribute('data-category') === currentCat);
                let matchSearch = card.getAttribute('data-title').includes(query);
                
                if (matchCat && matchSearch) {
                    totalMatch++;
                    if (visibleCount < itemsToShow) {
                        card.classList.add('show');
                        visibleCount++;
                    } else {
                        card.classList.remove('show');
                    }
                } else {
                    card.classList.remove('show');
                }
            });

            document.getElementById('loadMoreBox').style.display = (totalMatch > itemsToShow) ? 'block' : 'none';
        }

        function setCategory(cat, btn) {
            document.querySelectorAll('.cat-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            currentCat = cat;
            itemsToShow = 20; 
            updateDisplay();
        }

        function filterProducts() { itemsToShow = 20; updateDisplay(); }
        function loadMore() { itemsToShow += 20; updateDisplay(); }

        updateDisplay();
    </script>
</body></html>
"""
    return html

def tao_sitemap_va_robots(products):
    """Tạo Tự động Sitemap.xml và Robots.txt cho SEO"""
    print("🗺️ Đang tạo Sitemap và Robots.txt chuẩn SEO...")
    
    # 1. Tạo file robots.txt
    robots_content = "User-agent: *\nAllow: /\nSitemap: https://vpptinh.com/sitemap.xml\n"
    with open(os.path.join(BASE_DIR, "robots.txt"), "w", encoding="utf-8") as f:
        f.write(robots_content)

    # 2. Tạo file sitemap.xml
    ngay_hien_tai = time.strftime("%Y-%m-%d")
    sitemap_xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
    sitemap_xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    
    # URL Trang chủ
    sitemap_xml += f'  <url>\n    <loc>https://vpptinh.com/</loc>\n    <lastmod>{ngay_hien_tai}</lastmod>\n    <changefreq>daily</changefreq>\n    <priority>1.0</priority>\n  </url>\n'
    
    # URL Từng trang sản phẩm
    for p in products:
        loc = f"https://vpptinh.com/san-pham/{p['slug']}.html"
        sitemap_xml += f'  <url>\n    <loc>{loc}</loc>\n    <lastmod>{ngay_hien_tai}</lastmod>\n    <changefreq>weekly</changefreq>\n    <priority>0.8</priority>\n  </url>\n'
    
    sitemap_xml += '</urlset>'
    
    with open(os.path.join(BASE_DIR, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write(sitemap_xml)
    print("✅ Đã tạo xong bản đồ Sitemap!")

def chay_he_thong():
    print(f"🚀 KHỞI ĐỘNG HỆ THỐNG SEO ĐA TRANG")
    os.makedirs(THU_MUC_SAN_PHAM, exist_ok=True) 

    try:
        if not os.path.exists(FILE_CSV_LOCAL): return print(f"❌ KHÔNG TÌM THẤY: {FILE_CSV_LOCAL}")

        raw_data, danh_sach_sp_thieu = [], []
        
        with open(FILE_CSV_LOCAL, mode='r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f, delimiter=';' if ';' in f.readline() else ',')
            f.seek(0); next(reader) 
            
            for idx, row in enumerate(reader):
                if not row.get('name'): continue
                row['_id'] = str(idx)
                row['danh_muc'] = row.get('danh_muc', 'khac') or 'khac'
                row['slug'] = tao_slug(row['name']) 
                
                mo_ta_ai = row.get('mo_ta_ai', '').strip()
                if not mo_ta_ai or "Đừng bỏ lỡ" in mo_ta_ai:
                    danh_sach_sp_thieu.append({"id": str(idx), "name": row['name'], "mo_ta_goc": row.get('mo_ta', '')})
                raw_data.append(row)

        ket_qua_ai = {}
        if danh_sach_sp_thieu:
            for i in range(0, len(danh_sach_sp_thieu), 10):
                ket_qua_ai.update(goi_ai_viet_mo_ta_hang_loat(danh_sach_sp_thieu[i:i+10]))
                time.sleep(2)

        clean_products = []
        for r in raw_data:
            sp_id = r['_id']
            if sp_id in ket_qua_ai: r['mo_ta_ai'] = ket_qua_ai[sp_id]
            if not r.get('mo_ta_ai'): r['mo_ta_ai'] = f"Siêu phẩm {r['name']} giá cực tốt tại VPP Tịnh Shop. Mua ngay kẻo lỡ!"
            
            link_anh = r.get('image', '').strip(' \'"[]')
            if not link_anh.startswith('http'): link_anh = f"static/images/{link_anh.split('/')[-1]}"

            sp_sach = {
                "name": r['name'].strip(), "slug": r['slug'],
                "new_price": r.get('new_price', '0').strip(),
                "image": link_anh, "link": tao_link_aff(r.get('link', '')),
                "mo_ta_ai": r['mo_ta_ai'], "danh_muc": r['danh_muc']
            }
            clean_products.append(sp_sach)
            tao_trang_chi_tiet(sp_sach) 

        print(f"✅ Đã tạo {len(clean_products)} trang sản phẩm con.")
        
        # GỌI HÀM TẠO SITEMAP Ở ĐÂY
        tao_sitemap_va_robots(clean_products)
        
        with open(os.path.join(BASE_DIR, "index.html"), "w", encoding="utf-8") as f:
            f.write(tao_web_html(clean_products))
        
        with open(FILE_CSV_LOCAL, mode='w', encoding='utf-8-sig', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=raw_data[0].keys() - {'_id', 'slug'})
            writer.writeheader()
            for r in raw_data: 
                r.pop('_id', None); r.pop('slug', None)
                writer.writerow(r)

        print("🎉 HOÀN TẤT BUILD WEBSITE LÊN LOCAL!")
        
        if not os.environ.get("GITHUB_ACTIONS"):
            webbrowser.open("file://" + os.path.realpath(os.path.join(BASE_DIR, "index.html")))

    except Exception as e: print(f"❌ Lỗi: {e}")

if __name__ == "__main__":
    chay_he_thong()