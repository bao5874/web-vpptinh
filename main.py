import csv
import json
import os
import re
import base64 
import time
import urllib.request
import io
import unicodedata
import math

try:
    from google import genai
    from google.genai import types
except ImportError:
    print("❌ THIẾU THƯ VIỆN AI!")
    exit()

# ==========================================
# 1. CẤU HÌNH HỆ THỐNG
# ==========================================
URL_CSV_SAN_PHAM = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQzftzzjfyPE6MujJRirjKeXub0RmgpmAQNuTr9IjaLGe9BGukp4RnPisW7tZo3sDBBqiumtY3RWNbX/pub?gid=0&single=true&output=csv"

# THAY MÃ ID ACCESSTRADE CỦA BẠN VÀO ĐÂY:
BASE_AFF_URL = "https://go.isclix.com/deep_link/v6/6906519896943843292/4751584435713464237?url_enc="

ZALO_NUMBER = "0931736266"
PHONE_NUMBER = "0931736266" # Thêm số điện thoại gọi trực tiếp
SP_MOI_TRANG = 24 # Số lượng sản phẩm hiển thị trên 1 trang

DANH_MUC_MAP = {
    "tho_cung": "Đồ Thờ Cúng", "dc_vs": "Dụng Cụ Vệ Sinh", 
    "vpp": "Văn Phòng Phẩm", "gia_dung": "Đồ Gia Dụng", 
    "me_be": "Mẹ & Bé", "khac": "Sản Phẩm Khác"
}

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CACHE_BAI_VIET = os.path.join(BASE_DIR, "bai_viet_tu_dong_cache.json")
CACHE_SAN_PHAM = os.path.join(BASE_DIR, "san_pham_cache.json")
THU_MUC_BAI_VIET = os.path.join(BASE_DIR, "bai-viet")
THU_MUC_SAN_PHAM = os.path.join(BASE_DIR, "san-pham")

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    try:
        with open(os.path.join(BASE_DIR, "api_key.txt"), "r") as f: GEMINI_API_KEY = f.read().strip()
    except: pass

# ==========================================
# 2. GIAO DIỆN DÙNG CHUNG (UI COMPONENTS)
# ==========================================
# FOOTER CHUYÊN NGHIỆP
UI_FOOTER = f"""
<footer style="background: #222; color: #ddd; padding: 40px 20px; margin-top: 50px; font-size: 14px;">
    <div style="max-width: 1000px; margin: 0 auto; display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 30px;">
        <div><h3 style="color: #fff;">VPP TỊNH SHOP</h3><p>Đối tác cung cấp văn phòng phẩm, đồ gia dụng và vật phẩm thờ cúng trọn gói, uy tín hàng đầu.</p></div>
        <div><h3 style="color: #fff;">LIÊN HỆ MUA SỈ</h3><p>📍 Địa chỉ: Cập nhật sau<br>📞 Hotline: {PHONE_NUMBER}<br>💬 Zalo: {ZALO_NUMBER}</p></div>
        <div><h3 style="color: #fff;">CHÍNH SÁCH</h3><p><a href="#" style="color:#ddd; text-decoration:none;">Chính sách giao hàng</a><br><a href="#" style="color:#ddd; text-decoration:none;">Chính sách đổi trả</a><br><a href="#" style="color:#ddd; text-decoration:none;">Bảo mật thông tin</a></p></div>
    </div>
    <div style="text-align: center; border-top: 1px solid #444; margin-top: 30px; padding-top: 20px; color: #888;">&copy; 2026 VPP Tịnh. All rights reserved.</div>
</footer>
"""

# BỘ NÚT NỔI (ZALO, CALL, TOP)
UI_FLOATING = f"""
<style>
    .float-group {{ position: fixed; bottom: 20px; right: 20px; display: flex; flex-direction: column; gap: 15px; z-index: 1000; }}
    .f-btn {{ width: 50px; height: 50px; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: white; text-decoration: none; font-weight: bold; font-size: 20px; box-shadow: 0 4px 10px rgba(0,0,0,0.3); transition: transform 0.2s; }}
    .f-btn:hover {{ transform: scale(1.1); }}
    .f-zalo {{ background: #0068ff; animation: rung 1.5s infinite; font-size:12px; text-align:center; line-height:1.2;}}
    .f-call {{ background: #00b14f; }}
    .f-top {{ background: #555; display: none; cursor: pointer; }} /* Ẩn nút top ban đầu */
    @keyframes rung {{ 0% {{transform: rotate(0deg);}} 10% {{transform: rotate(-15deg);}} 20% {{transform: rotate(15deg);}} 30% {{transform: rotate(-15deg);}} 40% {{transform: rotate(15deg);}} 50% {{transform: rotate(0deg);}} 100% {{transform: rotate(0deg);}} }}
</style>
<div class="float-group">
    <button class="f-btn f-top" id="btnTop" onclick="window.scrollTo({{top: 0, behavior: 'smooth'}});">⬆️</button>
    <a href="tel:{PHONE_NUMBER}" class="f-btn f-call">📞</a>
    <a href="https://zalo.me/{ZALO_NUMBER}" target="_blank" class="f-btn f-zalo">Chat<br>Zalo</a>
</div>
<script>
    window.onscroll = function() {{ document.getElementById("btnTop").style.display = (document.body.scrollTop > 300 || document.documentElement.scrollTop > 300) ? "flex" : "none"; }};
</script>
"""

# ==========================================
# 3. CÁC HÀM XỬ LÝ LÕI
# ==========================================
def tao_slug(text):
    text = unicodedata.normalize('NFKD', str(text)).encode('ascii', 'ignore').decode('utf-8')
    text = re.sub(r'[^\w\s-]', '', text).strip().lower()
    return re.sub(r'[-\s]+', '-', text) if text else "sp-khong-ten"

def tao_link_aff(url_goc):
    if not url_goc: return "#"
    if "shope.ee" in url_goc or "isclix.com" in url_goc or "c.lazada.vn" in url_goc: return url_goc
    try: return f"{BASE_AFF_URL}{base64.b64encode(url_goc.strip().encode('utf-8')).decode('utf-8')}"
    except: return url_goc

def lay_data_tu_google_sheet(url):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        csv_data = urllib.request.urlopen(req).read().decode('utf-8')
        return list(csv.DictReader(io.StringIO(csv_data)))
    except Exception as e:
        print(f"❌ LỖI SHEET: {e}")
        return []

def goi_ai_tu_dong_viet_bai(ten_danh_muc, ten_sp_dau_tien):
    if not GEMINI_API_KEY: return {"tieu_de": "Chưa cài API Key", "noi_dung_html": ""}
    print(f"📰 AI đang hóa thân SEOer viết Tạp chí cho '{ten_danh_muc}'...")
    prompt = f"""Bạn là Chuyên gia SEO & Bậc thầy Storytelling. Viết bài Advertorial 800 chữ cho "{ten_danh_muc}". Lấy "{ten_sp_dau_tien}" làm mồi câu, đánh trúng nỗi đau khách hàng. Tối ưu thẻ H2, H3. BẮT BUỘC TRẢ VỀ JSON: {{"tieu_de": "Tiêu đề giật tít (10-15 chữ)", "noi_dung_html": "HTML nội dung (không <html> body)."}}"""
    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
        res = client.models.generate_content(model='gemini-2.5-flash', contents=prompt, config=types.GenerateContentConfig(temperature=0.85, response_mime_type="application/json"))
        return json.loads(res.text)
    except Exception: return {"tieu_de": f"Bí quyết chọn {ten_danh_muc}", "noi_dung_html": "<p>Đang cập nhật...</p>"}

def goi_ai_viet_mo_ta_sp(ten_sp):
    if not GEMINI_API_KEY: return "<p>Mô tả cập nhật sau.</p>"
    print(f"📝 AI đang tung chiêu chốt sale cho: '{ten_sp}'...")
    prompt = f"Bạn là Sales Copywriter. Viết mô tả chuẩn SEO (250 chữ) cho: '{ten_sp}'. Biến tính năng thành Lợi ích. Kích thích FOMO. Định dạng HTML (<h3>, <p>, <ul>). Không xuất markdown."
    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
        return client.models.generate_content(model='gemini-2.5-flash', contents=prompt, config=types.GenerateContentConfig(temperature=0.75)).text.replace("```html", "").replace("```", "").strip()
    except Exception: return f"<p>Sản phẩm chất lượng cao: {ten_sp}.</p>"

# Sinh thẻ HTML cho 1 Sản Phẩm dùng trong Lưới (Grid)
def sinh_the_san_pham_html(p, path_prefix=""):
    try: price = float(re.sub(r'[^\d]', '', str(p.get('new_price', '0')))) if re.sub(r'[^\d]', '', str(p.get('new_price', '0'))) else 0
    except: price = 0
    old_price = int(price * 1.25) # Tạo giá ảo cao hơn 25%
    link_sp = f"{path_prefix}san-pham/{p['slug']}.html"
    
    return f"""
    <div class="sp-card">
        <div class="sale-badge">-20%</div>
        <img src="{p.get('image', '')}" loading="lazy" alt="{p.get('name', '')}">
        <div class="sp-info">
            <div class="sp-name">{p.get('name', '')}</div>
            <div class="sp-price-box">
                <span class="sp-price">{int(price):,}₫</span>
                <span class="sp-old-price">{int(old_price):,}₫</span>
            </div>
            <a href="{link_sp}" class="sp-btn-xem">🔍 XEM CHI TIẾT</a>
        </div>
    </div>
    """

# ==========================================
# 4. HÀM TẠO TRANG HTML (RENDER)
# ==========================================
def tao_trang_chi_tiet_sp(p, mo_ta_html):
    slug = p['slug']
    link_aff = tao_link_aff(p.get('link', ''))
    try: price = float(re.sub(r'[^\d]', '', str(p.get('new_price', '0')))) if re.sub(r'[^\d]', '', str(p.get('new_price', '0'))) else 0
    except: price = 0
    old_price = int(price * 1.25)
    dm_name = DANH_MUC_MAP.get(p.get('danh_muc', 'khac'), 'Sản Phẩm')

    html = f"""<!DOCTYPE html><html lang="vi"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{p.get('name', '')} | Mua sỉ giá tốt</title>
    <meta property="og:title" content="{p.get('name', '')} - VPP Tịnh">
    <meta property="og:image" content="{p.get('image', '')}">
    <style>
        :root {{ --primary: #d0011b; --bg: #f5f5f5; }} body {{ font-family: sans-serif; background: var(--bg); margin: 0; padding: 0; color: #333; padding-bottom: 80px; }} 
        .header {{ background: #fff; padding: 10px 25px; position: sticky; top: 0; z-index: 100; border-bottom: 1px solid #eee; display: flex; justify-content: space-between; }} 
        .btn-home {{ background: #fff; color: var(--primary); border: 2px solid var(--primary); padding: 8px 15px; border-radius: 6px; text-decoration: none; font-weight: bold; }} 
        .breadcrumbs {{ max-width: 900px; margin: 15px auto 0; font-size: 14px; color: #666; padding: 0 20px; }}
        .breadcrumbs a {{ color: var(--primary); text-decoration: none; }}
        .container {{ max-width: 900px; margin: 15px auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }} 
        .product-top {{ display: flex; gap: 30px; margin-bottom: 30px; }} 
        .product-img {{ flex: 1; text-align: center; position: relative; }} 
        .product-img img {{ max-width: 100%; max-height: 400px; border-radius: 8px; border: 1px solid #eee; padding: 10px; }} 
        .sale-tag {{ position: absolute; top: 10px; left: 10px; background: var(--primary); color: white; padding: 5px 10px; border-radius: 5px; font-weight: bold; }}
        .product-info {{ flex: 1; display: flex; flex-direction: column; justify-content: center; }} 
        .p-title {{ font-size: 24px; color: #222; margin-top: 0; line-height: 1.3; }} 
        .p-price-box {{ margin: 15px 0; }}
        .p-price {{ font-size: 32px; color: var(--primary); font-weight: bold; }} 
        .p-old-price {{ font-size: 18px; color: #999; text-decoration: line-through; margin-left: 10px; }}
        .btn-buy {{ background: var(--primary); color: white; text-decoration: none; padding: 15px 20px; text-align: center; border-radius: 6px; font-weight: bold; font-size: 18px; box-shadow: 0 4px 15px rgba(208,1,27,0.3); display: block; }} 
        .desc-box {{ border-top: 2px dashed #eee; padding-top: 30px; line-height: 1.6; font-size: 16px; }} 
        .desc-box h3 {{ color: var(--primary); }} 
        @media (max-width: 768px) {{ 
            .product-top {{ flex-direction: column; }} 
            .btn-buy {{ position: fixed; bottom: 0; left: 0; width: 100%; margin: 0; border-radius: 0; padding: 18px 0; z-index: 1000; font-size: 20px; }}
        }}
    </style></head>
    <body>
    <div class="header"><a href="../index.html" class="btn-home">🔙 Về Trang Chủ</a><strong style="color:var(--primary); font-size: 18px; line-height: 36px;">VPP TỊNH SHOP</strong></div>
    <div class="breadcrumbs"><a href="../index.html">Trang chủ</a> > {dm_name} > {p.get('name', '')[:30]}...</div>
    <div class="container">
        <div class="product-top">
            <div class="product-img"><span class="sale-tag">🔥 HOT</span><img src="{p.get('image', '')}"></div>
            <div class="product-info">
                <h1 class="p-title">{p.get('name', '')}</h1>
                <div class="p-price-box"><span class="p-price">{int(price):,}₫</span><span class="p-old-price">{int(old_price):,}₫</span></div>
                <div style="margin-bottom: 20px; color: #555;">✔️ Cam kết chính hãng<br>✔️ Hỗ trợ xuất VAT cho khách sỉ<br>✔️ Giao hàng toàn quốc</div>
                <a href="{link_aff}" target="_blank" rel="nofollow" class="btn-buy">🛒 MUA NGAY TRÊN SHOPEE</a>
            </div>
        </div>
        <div class="desc-box"><h2>📜 Thông tin chi tiết</h2>{mo_ta_html}</div>
    </div>
    {UI_FLOATING} {UI_FOOTER}
    </body></html>"""
    with open(os.path.join(THU_MUC_SAN_PHAM, f"{slug}.html"), "w", encoding="utf-8") as f: f.write(html)

def tao_trang_lai_bai_viet(slug, tieu_de, noi_dung_html, san_pham_lien_quan):
    html_sp = "".join([sinh_the_san_pham_html(p, "../") for p in san_pham_lien_quan])
    sp_moi = san_pham_lien_quan[0] if san_pham_lien_quan else {}
    img_moi = sp_moi.get('image', '')
    
    html = f"""<!DOCTYPE html><html lang="vi"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{tieu_de} | VPP Tịnh</title>
    <meta property="og:title" content="{tieu_de}">
    <meta property="og:image" content="{img_moi}">
    <style>
        :root {{ --primary: #d0011b; --bg: #f5f5f5; }} body {{ font-family: sans-serif; background: var(--bg); margin: 0; padding: 0; color: #333; }} 
        .header {{ background: #fff; padding: 10px 25px; position: sticky; top: 0; z-index: 100; border-bottom: 1px solid #eee; display: flex; justify-content: space-between; }} 
        .btn-home {{ background: #fff; color: var(--primary); border: 2px solid var(--primary); padding: 8px 15px; border-radius: 6px; text-decoration: none; font-weight: bold; }} 
        .breadcrumbs {{ max-width: 800px; margin: 15px auto 0; font-size: 14px; color: #666; padding: 0 20px; }}
        .breadcrumbs a {{ color: var(--primary); text-decoration: none; }}
        .container {{ max-width: 800px; margin: 15px auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }} 
        .article-column {{ max-width: 650px; margin: 0 auto; line-height: 1.6; font-size: 16px; }} 
        .featured-img-box {{ text-align: center; margin: 20px 0; }} .featured-img-box img {{ max-width: 100%; max-height: 350px; border-radius: 8px; }} 
        .showcase-title {{ text-align: center; color: var(--primary); margin: 40px 0 20px; border-top: 2px dashed #eee; padding-top: 30px; }} 
        /* CSS Dùng chung cho Lưới SP */
        .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 15px; text-align: center; }} 
        .sp-card {{ border: 1px solid #eee; border-radius: 8px; padding: 10px; background: white; position: relative; display: flex; flex-direction: column; justify-content: space-between;}} 
        .sale-badge {{ position: absolute; top: 10px; right: 10px; background: var(--primary); color: white; padding: 3px 8px; font-size: 12px; border-radius: 4px; font-weight: bold; }}
        .sp-card img {{ width: 100%; height: 160px; object-fit: contain; }} 
        .sp-name {{ font-size: 14px; height: 40px; overflow: hidden; margin: 10px 0; }} 
        .sp-price-box {{ margin-bottom: 15px; }}
        .sp-price {{ font-weight: bold; color: var(--primary); font-size: 18px; }} 
        .sp-old-price {{ font-size: 13px; color: #999; text-decoration: line-through; margin-left: 5px; }}
        .sp-btn-xem {{ display: block; background: #fff; color: var(--primary); border: 1px solid var(--primary); padding: 8px; border-radius: 5px; text-decoration: none; font-weight: bold; transition: 0.2s;}} 
        .sp-btn-xem:hover {{ background: var(--primary); color: #fff; }}
    </style></head>
    <body>
    <div class="header"><a href="../index.html" class="btn-home">🔙 Về Trang Chủ</a><strong style="color:var(--primary); font-size: 18px; line-height: 36px;">VPP TỊNH SHOP</strong></div>
    <div class="breadcrumbs"><a href="../index.html">Trang chủ</a> > Tạp chí > {tieu_de[:30]}...</div>
    <div class="container"><h1 style="text-align: center; margin-bottom: 20px;">{tieu_de}</h1><div class="article-column"><div class="featured-img-box"><img src="{img_moi}"></div>{noi_dung_html}</div><h2 class="showcase-title">🔥 CÁC SẢN PHẨM KHUYÊN DÙNG 🔥</h2><div class="grid">{html_sp}</div></div>
    {UI_FLOATING} {UI_FOOTER}
    </body></html>"""
    with open(os.path.join(THU_MUC_BAI_VIET, f"{slug}.html"), "w", encoding="utf-8") as f: f.write(html)

def tao_trang_chu_phan_trang(danh_sach_hub, tat_ca_san_pham):
    tong_sp = len(tat_ca_san_pham)
    tong_trang = math.ceil(tong_sp / SP_MOI_TRANG)
    if tong_trang == 0: tong_trang = 1

    # Tạo Menu Danh Mục
    html_menu = "<div class='category-nav'>"
    html_menu += "<a href='index.html' class='cat-btn active'>Tất cả</a>"
    danh_muc_co_sp = set([p.get('danh_muc', 'khac') for p in tat_ca_san_pham])
    for ma_dm in danh_muc_co_sp:
        ten_dm = DANH_MUC_MAP.get(ma_dm, ma_dm.title())
        html_menu += f"<a href='#' class='cat-btn' onclick='filterCat(\"{ma_dm}\")'>{ten_dm}</a>"
    html_menu += "</div>"

    html_links = ""
    for hub in danh_sach_hub:
        html_links += f"""<a href="bai-viet/{hub['slug']}.html" class="blog-card-vertical"><img src="{hub['img_dai_dien']}" class="blog-img"><div class="blog-content"><span class="blog-tag">{hub['ten_danh_muc']}</span><h3>{hub['tieu_de']}</h3><p>Đọc đánh giá chi tiết ➡️</p></div></a>"""

    for trang in range(1, tong_trang + 1):
        ten_file = "index.html" if trang == 1 else f"page-{trang}.html"
        sp_bat_dau = (trang - 1) * SP_MOI_TRANG
        sp_ket_thuc = sp_bat_dau + SP_MOI_TRANG
        sp_tren_trang = tat_ca_san_pham[sp_bat_dau:sp_ket_thuc]

        # Sinh lưới sản phẩm cho trang này
        html_sp_grid = ""
        for p in sp_tren_trang:
            dm = p.get('danh_muc', 'khac')
            # Thêm data-cat để JS có thể lọc
            html_the = sinh_the_san_pham_html(p, "").replace('class="sp-card"', f'class="sp-card mix-{dm}"')
            html_sp_grid += html_the

        # Thanh phân trang (Pagination UI)
        html_pagination = "<div class='pagination'>"
        for i in range(1, tong_trang + 1):
            link = "index.html" if i == 1 else f"page-{i}.html"
            active = "active" if i == trang else ""
            html_pagination += f"<a href='{link}' class='page-num {active}'>{i}</a>"
        html_pagination += "</div>"

        # Chỉ hiển thị bài viết ở Trang 1
        html_bai_viet_section = f"""<div style="text-align: center;"><h2 class="section-title">📰 TƯ VẤN SẢN PHẨM</h2></div><div class="blog-list-vertical">{html_links}</div>""" if trang == 1 else ""

        html = f"""<!DOCTYPE html><html lang="vi"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>VPP Tịnh | Trang Chủ (Trang {trang})</title>
        <meta property="og:title" content="VPP Tịnh - Đối tác cung cấp sỉ lẻ toàn quốc">
        <style>:root {{ --primary: #d0011b; --bg: #f5f5f5; }} body {{ font-family: sans-serif; background: var(--bg); margin: 0; padding: 0; }} 
        .header-bg {{ width: 100%; max-width: 1200px; margin: 0 auto; aspect-ratio: 1360/350; background-image: url('static/images/tinh_radio_banner1.jpg'); background-size: cover; background-position: center; }} 
        .ticker-wrap {{ width: 100%; max-width: 1200px; margin: 0 auto; background-color: var(--primary); padding: 12px 0; overflow: hidden; color: white; font-weight: bold; font-size: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }} .ticker {{ display: inline-block; white-space: nowrap; padding-right: 100%; animation: ticker 25s linear infinite; }} @keyframes ticker {{ 0% {{ transform: translate3d(100%, 0, 0); }} 100% {{ transform: translate3d(-100%, 0, 0); }} }} 
        .container {{ max-width: 1100px; margin: 0 auto; padding: 0 15px; }} 
        .section-title {{ text-align: center; margin: 40px 0 20px; color: #333; text-transform: uppercase; border-bottom: 2px solid var(--primary); display: inline-block; padding-bottom: 10px; font-size: 24px; }}
        
        /* THANH TÌM KIẾM & DANH MỤC */
        .tools-bar {{ display: flex; justify-content: space-between; align-items: center; margin: 30px 0; background: #fff; padding: 15px; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.05); flex-wrap: wrap; gap: 15px; }}
        .category-nav {{ display: flex; gap: 10px; flex-wrap: wrap; }}
        .cat-btn {{ padding: 8px 15px; background: #eee; color: #333; text-decoration: none; border-radius: 20px; font-size: 14px; font-weight: bold; transition: 0.2s; border: 1px solid transparent; }}
        .cat-btn:hover, .cat-btn.active {{ background: #ffeeee; color: var(--primary); border-color: var(--primary); }}
        .search-box {{ display: flex; }} .search-box input {{ padding: 10px 15px; border: 1px solid #ddd; border-radius: 20px 0 0 20px; outline: none; width: 200px; }} .search-box button {{ padding: 10px 20px; border: none; background: var(--primary); color: #fff; border-radius: 0 20px 20px 0; cursor: pointer; font-weight: bold; }}
        
        /* BÀI VIẾT & SẢN PHẨM */
        .blog-list-vertical {{ display: flex; flex-direction: column; gap: 20px; }} .blog-card-vertical {{ display: flex; flex-direction: row; background: white; border-radius: 10px; overflow: hidden; text-decoration: none; color: #333; box-shadow: 0 3px 15px rgba(0,0,0,0.05); border: 1px solid #eee; }} .blog-img {{ width: 250px; height: 180px; object-fit: contain; border-right: 1px solid #eee; padding: 10px; }} .blog-content {{ padding: 20px; display: flex; flex-direction: column; justify-content: center; flex: 1; }} .blog-tag {{ background: #ffeeee; color: var(--primary); padding: 5px 10px; border-radius: 20px; font-size: 12px; font-weight: bold; align-self: flex-start; margin-bottom: 10px; }} .blog-content h3 {{ color: var(--primary); margin: 0 0 10px 0; font-size: 20px; }}
        .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 15px; text-align: center; }} 
        .sp-card {{ border: 1px solid #eee; border-radius: 8px; padding: 10px; background: white; position: relative; display: flex; flex-direction: column; justify-content: space-between;}} .sale-badge {{ position: absolute; top: 10px; right: 10px; background: var(--primary); color: white; padding: 3px 8px; font-size: 12px; border-radius: 4px; font-weight: bold; }} .sp-card img {{ width: 100%; height: 160px; object-fit: contain; }} .sp-name {{ font-size: 14px; height: 40px; overflow: hidden; margin: 10px 0; }} .sp-price-box {{ margin-bottom: 15px; }} .sp-price {{ font-weight: bold; color: var(--primary); font-size: 18px; }} .sp-old-price {{ font-size: 13px; color: #999; text-decoration: line-through; margin-left: 5px; }} .sp-btn-xem {{ display: block; background: #fff; color: var(--primary); border: 1px solid var(--primary); padding: 8px; border-radius: 5px; text-decoration: none; font-weight: bold; transition: 0.2s;}} .sp-btn-xem:hover {{ background: var(--primary); color: #fff; }}
        
        /* PHÂN TRANG */
        .pagination {{ display: flex; justify-content: center; margin: 40px 0; gap: 10px; }}
        .page-num {{ display: inline-block; width: 40px; height: 40px; line-height: 40px; text-align: center; background: #fff; border: 1px solid #ddd; border-radius: 50%; text-decoration: none; color: #333; font-weight: bold; transition: 0.2s; }}
        .page-num.active, .page-num:hover {{ background: var(--primary); color: #fff; border-color: var(--primary); box-shadow: 0 4px 10px rgba(208,1,27,0.3); }}
        
        @media (max-width: 650px) {{ .blog-card-vertical {{ flex-direction: column; }} .blog-img {{ width: 100%; border-right: none; border-bottom: 1px solid #eee; }} .tools-bar {{ justify-content: center; }} .search-box input {{ width: 150px; }} }}
        </style></head>
        <body><div class="header-bg"></div><div class="ticker-wrap"><div class="ticker">🔥 ĐỐI TÁC CUNG CẤP VĂN PHÒNG PHẨM TRỌN GÓI 🔥 | 🚚 FREESHIP TỪ 500K | 📞 ZALO SỈ: {ZALO_NUMBER}</div></div>
        <div class="container">
            {html_bai_viet_section}
            
            <div style="text-align: center; margin-top: 50px;"><h2 class="section-title" id="khu-vuc-sp">🛍️ SIÊU THỊ SẢN PHẨM</h2></div>
            
            <div class="tools-bar">
                {html_menu}
                <div class="search-box">
                    <input type="text" id="searchInput" placeholder="Tìm trên trang này...">
                    <button onclick="searchSP()">Tìm</button>
                </div>
            </div>

            <div class="grid" id="productGrid">{html_sp_grid}</div>
            {html_pagination}
        </div>
        
        {UI_FLOATING} {UI_FOOTER}
        
        <script>
            // JS Lọc danh mục cơ bản trên trang
            function filterCat(cat) {{
                event.preventDefault();
                let cards = document.getElementsByClassName('sp-card');
                for (let i = 0; i < cards.length; i++) {{
                    if (cards[i].classList.contains('mix-' + cat)) cards[i].style.display = 'flex';
                    else cards[i].style.display = 'none';
                }}
            }}
            // JS Tìm kiếm cơ bản trên trang
            function searchSP() {{
                let input = document.getElementById('searchInput').value.toLowerCase();
                let cards = document.getElementsByClassName('sp-card');
                for (let i = 0; i < cards.length; i++) {{
                    let title = cards[i].querySelector('.sp-name').innerText.toLowerCase();
                    if (title.includes(input)) cards[i].style.display = 'flex';
                    else cards[i].style.display = 'none';
                }}
            }}
        </script>
        </body></html>"""
        with open(os.path.join(BASE_DIR, ten_file), "w", encoding="utf-8") as f: f.write(html)

def chay_he_thong():
    print("🚀 ĐANG TẢI DỮ LIỆU TỪ GOOGLE SHEETS...")
    data_san_pham = lay_data_tu_google_sheet(URL_CSV_SAN_PHAM)
    if not data_san_pham: return print("❌ Dữ liệu rỗng!")
    
    os.makedirs(THU_MUC_BAI_VIET, exist_ok=True)
    os.makedirs(THU_MUC_SAN_PHAM, exist_ok=True)
    
    for p in data_san_pham: p['slug'] = tao_slug(p.get('name', ''))

    cache_bai_viet, cache_san_pham = {}, {}
    if os.path.exists(CACHE_BAI_VIET):
        with open(CACHE_BAI_VIET, "r", encoding="utf-8") as f: cache_bai_viet = json.load(f)
    if os.path.exists(CACHE_SAN_PHAM):
        with open(CACHE_SAN_PHAM, "r", encoding="utf-8") as f: cache_san_pham = json.load(f)

    print("--- 1. AI VIẾT MÔ TẢ CHO TỪNG SẢN PHẨM ---")
    for p in data_san_pham:
        slug_sp = p['slug']
        if slug_sp not in cache_san_pham:
            cache_san_pham[slug_sp] = goi_ai_viet_mo_ta_sp(p.get('name', ''))
            with open(CACHE_SAN_PHAM, "w", encoding="utf-8") as f: json.dump(cache_san_pham, f, ensure_ascii=False, indent=2)
            time.sleep(3)
        tao_trang_chi_tiet_sp(p, cache_san_pham[slug_sp])
    
    print("--- 2. AI VIẾT TẠP CHÍ CHUYÊN MỤC ---")
    gom_nhom = {}
    for p in data_san_pham:
        dm = p.get('danh_muc', 'khac').strip()
        if not dm: dm = 'khac'
        if dm not in gom_nhom: gom_nhom[dm] = []
        gom_nhom[dm].append(p)

    danh_sach_hub = []
    for dm, ds_sp in gom_nhom.items():
        if not ds_sp: continue
        sp_dau_tien = ds_sp[0]
        ten_dm = DANH_MUC_MAP.get(dm, dm.title())
        slug_dm = f"chuyen-muc-{dm}"

        if dm not in cache_bai_viet:
            cache_bai_viet[dm] = goi_ai_tu_dong_viet_bai(ten_dm, sp_dau_tien.get('name', ''))
            with open(CACHE_BAI_VIET, "w", encoding="utf-8") as f: json.dump(cache_bai_viet, f, ensure_ascii=False, indent=2)
            time.sleep(3)

        tieu_de = cache_bai_viet[dm].get('tieu_de', f'Top sản phẩm {ten_dm}')
        noi_dung = cache_bai_viet[dm].get('noi_dung_html', '')
        tao_trang_lai_bai_viet(slug_dm, tieu_de, noi_dung, ds_sp)
        danh_sach_hub.append({"slug": slug_dm, "tieu_de": tieu_de, "ten_danh_muc": ten_dm, "img_dai_dien": sp_dau_tien.get('image', '')})

    print("--- 3. HOÀN THIỆN PHÂN TRANG & GIAO DIỆN ---")
    tao_trang_chu_phan_trang(danh_sach_hub, data_san_pham)
    print("🎉 TẤT CẢ ĐÃ XONG! HỆ THỐNG CMS 8.0 SẴN SÀNG!")

if __name__ == "__main__":
    chay_he_thong()