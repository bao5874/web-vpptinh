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
# 1. CẤU HÌNH HỆ THỐNG & ĐỌC API TỪ .env
# ==========================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
URL_CSV_SAN_PHAM = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQzftzzjfyPE6MujJRirjKeXub0RmgpmAQNuTr9IjaLGe9BGukp4RnPisW7tZo3sDBBqiumtY3RWNbX/pub?gid=0&single=true&output=csv"
BASE_AFF_URL = "https://go.isclix.com/deep_link/v6/6906519896943843292/4751584435713464237?url_enc="

DOMAIN = "https://vpptinh.com"
ZALO_NUMBER = "0931736266"
PHONE_NUMBER = "0931736266"
SP_MOI_TRANG = 24

# ĐỌC DANH SÁCH API KEYS TỪ FILE .env
DANH_SACH_API_KEYS = []
env_path = os.path.join(BASE_DIR, ".env")
if os.path.exists(env_path):
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, val = line.split("=", 1)
                if "GEMINI_API_KEY" in key and val.strip():
                    DANH_SACH_API_KEYS.append(val.strip())

if not DANH_SACH_API_KEYS:
    print("⚠️ CẢNH BÁO: Không tìm thấy API Key nào trong file .env!")

vi_tri_sung_hien_tai = 0

DANH_MUC_MAP = {
    "tho_cung": "Đồ Thờ Cúng", "dc_vs": "Dụng Cụ Vệ Sinh", 
    "vpp": "Văn Phòng Phẩm", "gia_dung": "Đồ Gia Dụng", 
    "me_be": "Mẹ & Bé", "khac": "Sản Phẩm Khác"
}

CACHE_BAI_VIET = os.path.join(BASE_DIR, "bai_viet_tu_dong_cache.json")
CACHE_SAN_PHAM = os.path.join(BASE_DIR, "san_pham_cache.json")
THU_MUC_BAI_VIET = os.path.join(BASE_DIR, "bai-viet")
THU_MUC_SAN_PHAM = os.path.join(BASE_DIR, "san-pham")

# ==========================================
# 2. GIAO DIỆN & MÃ THEO DÕI (PIXEL)
# ==========================================
FB_PIXEL_CODE = """
<script>
!function(f,b,e,v,n,t,s)
{if(f.fbq)return;n=f.fbq=function(){n.callMethod?
n.callMethod.apply(n,arguments):n.queue.push(arguments)};
if(!f._fbq)f._fbq=n;n.push=n;n.loaded=!0;n.version='2.0';
n.queue=[];t=b.createElement(e);t.async=!0;
t.src=v;s=b.getElementsByTagName(e)[0];
s.parentNode.insertBefore(t,s)}(window, document,'script',
'https://connect.facebook.net/en_US/fbevents.js');
fbq('init', '257713642929755');
fbq('track', 'PageView');
</script>
<noscript><img height="1" width="1" style="display:none"
src="https://www.facebook.com/tr?id=257713642929755&ev=PageView&noscript=1"
/></noscript>
"""

UI_FOOTER = f"""
<footer style="background: #222; color: #ddd; padding: 40px 20px; margin-top: 50px; font-size: 14px;">
    <div style="max-width: 1000px; margin: 0 auto; display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 30px;">
        <div><h3 style="color: #fff;">VPP TỊNH SHOP</h3><p>Đối tác cung cấp văn phòng phẩm, đồ gia dụng và vật phẩm thờ cúng trọn gói, uy tín hàng đầu.</p></div>
        <div><h3 style="color: #fff;">LIÊN HỆ MUA SỈ</h3><p>📞 Hotline: {PHONE_NUMBER}<br>💬 Zalo: {ZALO_NUMBER}</p></div>
        <div><h3 style="color: #fff;">CHÍNH SÁCH</h3><p><a href="#" style="color:#ddd; text-decoration:none;">Chính sách giao hàng</a><br><a href="#" style="color:#ddd; text-decoration:none;">Đổi trả & Bảo mật</a></p></div>
    </div>
    <div style="text-align: center; border-top: 1px solid #444; margin-top: 30px; padding-top: 20px; color: #888;">&copy; 2026 VPP Tịnh. All rights reserved.</div>
</footer>
"""

UI_FLOATING = f"""
<style>
    .float-group {{ position: fixed; bottom: 20px; right: 20px; display: flex; flex-direction: column; gap: 15px; z-index: 1000; }}
    .f-btn {{ width: 50px; height: 50px; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: white; text-decoration: none; font-weight: bold; font-size: 20px; box-shadow: 0 4px 10px rgba(0,0,0,0.3); transition: transform 0.2s; }}
    .f-btn:hover {{ transform: scale(1.1); }}
    .f-zalo {{ background: #0068ff; animation: rung 1.5s infinite; font-size:12px; text-align:center; line-height:1.2;}}
    .f-call {{ background: #00b14f; }}
    .f-top {{ background: #555; display: none; cursor: pointer; }} 
    @keyframes rung {{ 0% {{transform: rotate(0deg);}} 10% {{transform: rotate(-15deg);}} 20% {{transform: rotate(15deg);}} 30% {{transform: rotate(-15deg);}} 40% {{transform: rotate(15deg);}} 50% {{transform: rotate(0deg);}} 100% {{transform: rotate(0deg);}} }}
</style>
<div class="float-group">
    <button class="f-btn f-top" id="btnTop" onclick="window.scrollTo({{top: 0, behavior: 'smooth'}});">⬆️</button>
    <a href="tel:{PHONE_NUMBER}" class="f-btn f-call">📞</a>
    <a href="https://zalo.me/{ZALO_NUMBER}" target="_blank" class="f-btn f-zalo">Chat<br>Zalo</a>
</div>
<script>window.onscroll = function() {{ document.getElementById("btnTop").style.display = (document.body.scrollTop > 300 || document.documentElement.scrollTop > 300) ? "flex" : "none"; }};</script>
"""

# ==========================================
# 3. CÁC HÀM XỬ LÝ LÕI (CÓ CƠ CHẾ TỰ ĐỘNG CHUYỂN SÚNG)
# ==========================================
def rut_sung_tiep_theo():
    global vi_tri_sung_hien_tai
    if not DANH_SACH_API_KEYS: return None
    sung = DANH_SACH_API_KEYS[vi_tri_sung_hien_tai]
    vi_tri_sung_hien_tai = (vi_tri_sung_hien_tai + 1) % len(DANH_SACH_API_KEYS)
    return sung

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
    if not DANH_SACH_API_KEYS: return {"tieu_de": "Chưa cài API Key", "meta_description": "", "noi_dung_html": ""}
    
    prompt = f"""Bạn là Chuyên gia Copywriter. Viết 1 bài SEO 500 chữ cho nhóm "{ten_danh_muc}". Lấy "{ten_sp_dau_tien}" làm mồi. 
    Yêu cầu: Nghiêm túc, chuyên nghiệp, KHÔNG đùa giỡn, tập trung đúng vào trọng tâm và giá trị thực tế của sản phẩm. Không viết lan man.
    BẮT BUỘC TRẢ VỀ JSON. TRONG HTML CHỈ DÙNG DẤU NHÁY ĐƠN ('). KHÔNG XUỐNG DÒNG (ENTER) TRONG TEXT.
    Cấu trúc: {{"tieu_de": "Tiêu đề (10-15 chữ)", "meta_description": "Mô tả SEO tóm tắt (150 ký tự)", "noi_dung_html": "HTML (<h2>, <p>)"}}"""
    
    # Vòng lặp: Nếu súng này hỏng, rút súng tiếp theo bắn ngay lập tức
    for _ in range(len(DANH_SACH_API_KEYS)):
        api_key = rut_sung_tiep_theo()
        print(f"📰 AI [Key ...{api_key[-4:]}] viết Tạp chí cho '{ten_danh_muc}'...")
        try:
            client = genai.Client(api_key=api_key)
            # Giảm temperature xuống 0.7 để văn phong nghiêm túc, chắc chắn hơn
            res = client.models.generate_content(model='gemini-2.5-flash', contents=prompt, config=types.GenerateContentConfig(temperature=0.7, response_mime_type="application/json"))
            time.sleep(2) 
            raw_json = res.text.replace("```json", "").replace("```", "").replace("\n", " ").replace("\r", " ").strip()
            return json.loads(raw_json, strict=False)
        except Exception as e:
            print(f"⚠️ Lỗi Key ...{api_key[-4:]} ({ten_danh_muc}): {e}. Đang tự động chuyển sang Key tiếp theo...")
            time.sleep(2) # Nghỉ nhẹ 2s trước khi đổi súng
            
    print(f"❌ TOÀN BỘ SÚNG ĐỀU LỖI khi viết Tạp chí {ten_danh_muc}!")
    return {"tieu_de": f"Top {ten_danh_muc} đáng mua", "meta_description": f"Khám phá ngay {ten_danh_muc} giá sỉ tốt nhất.", "noi_dung_html": "<p>Đang cập nhật...</p>"}

def goi_ai_viet_mo_ta_sp(ten_sp):
    if not DANH_SACH_API_KEYS: return {"meta_description": "Đang cập nhật", "noi_dung_html": "<p>Mô tả cập nhật sau.</p>"}
    
    prompt = f"""Bạn là Sales Copywriter chuyên nghiệp. Sản phẩm: "{ten_sp}".
    Viết 1 đoạn chốt sale SIÊU NGẮN (100 - 150 chữ). Đánh thẳng vào 1 điểm "ăn tiền" nhất của sản phẩm. 
    Yêu cầu: Văn phong chuyên nghiệp, lịch sự, KHÔNG đùa giỡn, KHÔNG lan man, tập trung 100% vào lợi ích thực tế. KHÔNG liệt kê tính năng như cái máy.
    BẮT BUỘC TRẢ VỀ JSON. TRONG HTML CHỈ DÙNG DẤU NHÁY ĐƠN ('). KHÔNG XUỐNG DÒNG TRONG TEXT.
    Cấu trúc: {{"meta_description": "Câu tóm tắt chuẩn SEO (150 ký tự)", "noi_dung_html": "Mã HTML thuần (<h3>, <p>, <ul>)"}}"""
    
    # Vòng lặp Failover cho mô tả sản phẩm
    for _ in range(len(DANH_SACH_API_KEYS)):
        api_key = rut_sung_tiep_theo()
        print(f"📝 AI [Key ...{api_key[-4:]}] chốt sale: '{ten_sp}'...")
        try:
            client = genai.Client(api_key=api_key)
            # Giảm temperature xuống 0.7 
            res = client.models.generate_content(model='gemini-2.5-flash', contents=prompt, config=types.GenerateContentConfig(temperature=0.7, response_mime_type="application/json"))
            time.sleep(2) 
            raw_json = res.text.replace("```json", "").replace("```", "").replace("\n", " ").replace("\r", " ").strip()
            return json.loads(raw_json, strict=False)
        except Exception as e:
            print(f"⚠️ Lỗi Key ...{api_key[-4:]} ({ten_sp}): {e}. Đang tự động chuyển sang Key tiếp theo...")
            time.sleep(2)
            
    print(f"❌ TOÀN BỘ SÚNG ĐỀU LỖI khi viết mô tả {ten_sp}!")
    return {"meta_description": f"Mua {ten_sp} giá cực sốc.", "noi_dung_html": f"<p>Siêu phẩm <strong>{ten_sp}</strong> đang có ưu đãi lớn!</p>"}

def sinh_the_san_pham_html(p, path_prefix=""):
    try: price = float(re.sub(r'[^\d]', '', str(p.get('new_price', '0')))) if re.sub(r'[^\d]', '', str(p.get('new_price', '0'))) else 0
    except: price = 0
    old_price = int(price * 1.25)
    link_sp = f"{path_prefix}san-pham/{p['slug']}.html"
    
    return f"""
    <div class="sp-card">
        <div class="sale-badge">-20%</div>
        <img src="{p.get('image', '')}" loading="lazy" alt="Giá sỉ {p.get('name', 'Sản phẩm').replace('"', "'")}">
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
# 4. HÀM TẠO TRANG HTML (SEO MASTER + PIXEL)
# ==========================================
def tao_trang_chi_tiet_sp(p, ai_data):
    slug = p['slug']
    link_aff = tao_link_aff(p.get('link', ''))
    try: price = float(re.sub(r'[^\d]', '', str(p.get('new_price', '0')))) if re.sub(r'[^\d]', '', str(p.get('new_price', '0'))) else 0
    except: price = 0
    old_price = int(price * 1.25)
    dm_name = DANH_MUC_MAP.get(p.get('danh_muc', 'khac'), 'Sản Phẩm')
    
    mo_ta_html = ai_data.get('noi_dung_html', '')
    meta_desc = ai_data.get('meta_description', p.get('name', ''))[:160].replace('"', "'")

    html = f"""<!DOCTYPE html><html lang="vi"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{p.get('name', '')} | Giá Sỉ Tốt Nhất</title>
    <meta name="description" content="{meta_desc}">
    <link rel="canonical" href="{DOMAIN}/san-pham/{slug}.html" />
    <meta property="og:title" content="{p.get('name', '')} - VPP Tịnh">
    <meta property="og:description" content="{meta_desc}">
    <meta property="og:image" content="{p.get('image', '')}">
    <script type="application/ld+json">
    {{
      "@context": "https://schema.org/",
      "@type": "Product",
      "name": "{p.get('name', '').replace('"', "'")}",
      "image": "{p.get('image', '')}",
      "description": "{meta_desc}",
      "offers": {{
        "@type": "Offer",
        "url": "{DOMAIN}/san-pham/{slug}.html",
        "priceCurrency": "VND",
        "price": "{int(price)}",
        "availability": "https://schema.org/InStock"
      }}
    }}
    </script>
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
        .desc-box h3 {{ color: var(--primary); margin-top:25px; }} 
        @media (max-width: 768px) {{ .product-top {{ flex-direction: column; }} .btn-buy {{ position: fixed; bottom: 0; left: 0; width: 100%; margin: 0; border-radius: 0; padding: 18px 0; z-index: 1000; font-size: 20px; }} }}
    </style>
    {FB_PIXEL_CODE}
    </head>
    <body>
    <div class="header"><a href="../index.html" class="btn-home">🔙 Về Trang Chủ</a><strong style="color:var(--primary); font-size: 18px; line-height: 36px;">VPP TỊNH SHOP</strong></div>
    <div class="breadcrumbs"><a href="../index.html">Trang chủ</a> > {dm_name} > {p.get('name', '')[:30]}...</div>
    <div class="container">
        <div class="product-top">
            <div class="product-img"><span class="sale-tag">🔥 HOT</span><img src="{p.get('image', '')}" alt="{p.get('name', '').replace('"', "'")}"></div>
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

def tao_trang_lai_bai_viet(slug, ai_data, san_pham_lien_quan):
    html_sp = "".join([sinh_the_san_pham_html(p, "../") for p in san_pham_lien_quan])
    sp_moi = san_pham_lien_quan[0] if san_pham_lien_quan else {}
    img_moi = sp_moi.get('image', '')
    
    tieu_de = ai_data.get('tieu_de', 'Tạp chí VPP')
    noi_dung_html = ai_data.get('noi_dung_html', '')
    meta_desc = ai_data.get('meta_description', tieu_de)[:160].replace('"', "'")
    
    html = f"""<!DOCTYPE html><html lang="vi"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{tieu_de} | VPP Tịnh</title>
    <meta name="description" content="{meta_desc}">
    <link rel="canonical" href="{DOMAIN}/bai-viet/{slug}.html" />
    <meta property="og:title" content="{tieu_de}">
    <meta property="og:description" content="{meta_desc}">
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
    </style>
    {FB_PIXEL_CODE}
    </head>
    <body>
    <div class="header"><a href="../index.html" class="btn-home">🔙 Về Trang Chủ</a><strong style="color:var(--primary); font-size: 18px; line-height: 36px;">VPP TỊNH SHOP</strong></div>
    <div class="breadcrumbs"><a href="../index.html">Trang chủ</a> > Tạp chí > {tieu_de[:30]}...</div>
    <div class="container"><h1 style="text-align: center; margin-bottom: 20px;">{tieu_de}</h1><div class="article-column"><div class="featured-img-box"><img src="{img_moi}" alt="{tieu_de.replace('"', "'")}"></div>{noi_dung_html}</div><h2 class="showcase-title">🔥 CÁC SẢN PHẨM KHUYÊN DÙNG 🔥</h2><div class="grid">{html_sp}</div></div>
    {UI_FLOATING} {UI_FOOTER}
    </body></html>"""
    with open(os.path.join(THU_MUC_BAI_VIET, f"{slug}.html"), "w", encoding="utf-8") as f: f.write(html)

def tao_trang_chu_phan_trang(danh_sach_hub, tat_ca_san_pham):
    tong_sp = len(tat_ca_san_pham)
    tong_trang = math.ceil(tong_sp / SP_MOI_TRANG)
    if tong_trang == 0: tong_trang = 1

    html_menu = "<div class='category-nav'>"
    html_menu += "<a href='#' class='cat-btn active' onclick='filterCat(\"all\", event)'>Tất cả</a>"
    danh_muc_co_sp = set([p.get('danh_muc', 'khac') for p in tat_ca_san_pham])
    for ma_dm in danh_muc_co_sp:
        ten_dm = DANH_MUC_MAP.get(ma_dm, ma_dm.title())
        html_menu += f"<a href='#' class='cat-btn' onclick='filterCat(\"{ma_dm}\", event)'>{ten_dm}</a>"
    html_menu += "</div>"

    html_links = ""
    for hub in danh_sach_hub:
        html_links += f"""<a href="bai-viet/{hub['slug']}.html" class="blog-card-vertical"><img src="{hub['img_dai_dien']}" class="blog-img" alt="{hub['tieu_de']}"><div class="blog-content"><span class="blog-tag">{hub['ten_danh_muc']}</span><h3>{hub['tieu_de']}</h3><p>{hub['meta_desc']} ➡️</p></div></a>"""

    for trang in range(1, tong_trang + 1):
        ten_file = "index.html" if trang == 1 else f"page-{trang}.html"
        sp_bat_dau = (trang - 1) * SP_MOI_TRANG
        sp_ket_thuc = sp_bat_dau + SP_MOI_TRANG
        sp_tren_trang = tat_ca_san_pham[sp_bat_dau:sp_ket_thuc]

        html_sp_grid = ""
        for p in sp_tren_trang:
            dm = p.get('danh_muc', 'khac')
            html_the = sinh_the_san_pham_html(p, "").replace('class="sp-card"', f'class="sp-card mix-{dm}"')
            html_sp_grid += html_the

        html_pagination = "<div class='pagination'>"
        for i in range(1, tong_trang + 1):
            link = "index.html" if i == 1 else f"page-{i}.html"
            active = "active" if i == trang else ""
            html_pagination += f"<a href='{link}' class='page-num {active}'>{i}</a>"
        html_pagination += "</div>"

        html_bai_viet_section = f"""<div style="text-align: center;"><h2 class="section-title">📰 TƯ VẤN SẢN PHẨM</h2></div><div class="blog-list-vertical">{html_links}</div>""" if trang == 1 else ""

        html = f"""<!DOCTYPE html><html lang="vi"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>VPP Tịnh | Trang Chủ (Trang {trang})</title>
        <meta name="description" content="VPP Tịnh - Đối tác cung cấp văn phòng phẩm, đồ gia dụng, vật phẩm thờ cúng sỉ lẻ toàn quốc giá tốt nhất. Freeship từ 500k.">
        <link rel="canonical" href="{DOMAIN}/{ten_file}" />
        <meta property="og:title" content="VPP Tịnh - Đối tác cung cấp sỉ lẻ toàn quốc">
        <style>:root {{ --primary: #d0011b; --bg: #f5f5f5; }} body {{ font-family: sans-serif; background: var(--bg); margin: 0; padding: 0; scroll-behavior: smooth;}} 
        .header-bg {{ width: 100%; max-width: 1200px; margin: 0 auto; aspect-ratio: 1360/350; background-image: url('static/images/tinh_radio_banner1.jpg'); background-size: cover; background-position: center; }} 
        .ticker-wrap {{ width: 100%; max-width: 1200px; margin: 0 auto; background-color: var(--primary); padding: 12px 0; overflow: hidden; color: white; font-weight: bold; font-size: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }} .ticker {{ display: inline-block; white-space: nowrap; padding-right: 100%; animation: ticker 25s linear infinite; }} @keyframes ticker {{ 0% {{ transform: translate3d(100%, 0, 0); }} 100% {{ transform: translate3d(-100%, 0, 0); }} }} 
        .container {{ max-width: 1100px; margin: 0 auto; padding: 0 15px; }} 
        .section-title {{ text-align: center; margin: 40px 0 20px; color: #333; text-transform: uppercase; border-bottom: 2px solid var(--primary); display: inline-block; padding-bottom: 10px; font-size: 24px; }}
        
        .tools-bar {{ display: flex; justify-content: space-between; align-items: center; margin: 20px 0 30px 0; background: #fff; padding: 15px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.08); flex-wrap: wrap; gap: 15px; border-left: 5px solid var(--primary); }}
        .category-nav {{ display: flex; gap: 10px; flex-wrap: wrap; }}
        .cat-btn {{ padding: 8px 15px; background: #eee; color: #333; text-decoration: none; border-radius: 20px; font-size: 14px; font-weight: bold; transition: 0.2s; border: 1px solid transparent; }}
        .cat-btn:hover, .cat-btn.active {{ background: #ffeeee; color: var(--primary); border-color: var(--primary); box-shadow: 0 2px 5px rgba(208,1,27,0.2);}}
        .search-box {{ display: flex; box-shadow: 0 2px 5px rgba(0,0,0,0.1); border-radius: 20px; }} 
        .search-box input {{ padding: 12px 20px; border: 1px solid #ddd; border-radius: 25px 0 0 25px; outline: none; width: 250px; font-size: 15px; border-right: none; }} 
        .search-box input:focus {{ border-color: var(--primary); }}
        .search-box button {{ padding: 12px 25px; border: 1px solid var(--primary); background: var(--primary); color: #fff; border-radius: 0 25px 25px 0; cursor: pointer; font-weight: bold; font-size: 15px; transition: 0.2s; }}
        .search-box button:hover {{ background: #a80015; }}
        
        .blog-list-vertical {{ display: flex; flex-direction: column; gap: 20px; }} .blog-card-vertical {{ display: flex; flex-direction: row; background: white; border-radius: 10px; overflow: hidden; text-decoration: none; color: #333; box-shadow: 0 3px 15px rgba(0,0,0,0.05); border: 1px solid #eee; }} .blog-img {{ width: 250px; height: 180px; object-fit: contain; border-right: 1px solid #eee; padding: 10px; }} .blog-content {{ padding: 20px; display: flex; flex-direction: column; justify-content: center; flex: 1; }} .blog-tag {{ background: #ffeeee; color: var(--primary); padding: 5px 10px; border-radius: 20px; font-size: 12px; font-weight: bold; align-self: flex-start; margin-bottom: 10px; }} .blog-content h3 {{ color: var(--primary); margin: 0 0 10px 0; font-size: 20px; }}
        .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 15px; text-align: center; }} 
        .sp-card {{ border: 1px solid #eee; border-radius: 8px; padding: 10px; background: white; position: relative; display: flex; flex-direction: column; justify-content: space-between;}} .sale-badge {{ position: absolute; top: 10px; right: 10px; background: var(--primary); color: white; padding: 3px 8px; font-size: 12px; border-radius: 4px; font-weight: bold; }} .sp-card img {{ width: 100%; height: 160px; object-fit: contain; }} .sp-name {{ font-size: 14px; height: 40px; overflow: hidden; margin: 10px 0; }} .sp-price-box {{ margin-bottom: 15px; }} .sp-price {{ font-weight: bold; color: var(--primary); font-size: 18px; }} .sp-old-price {{ font-size: 13px; color: #999; text-decoration: line-through; margin-left: 5px; }} .sp-btn-xem {{ display: block; background: #fff; color: var(--primary); border: 1px solid var(--primary); padding: 8px; border-radius: 5px; text-decoration: none; font-weight: bold; transition: 0.2s;}} .sp-btn-xem:hover {{ background: var(--primary); color: #fff; }}
        
        .pagination {{ display: flex; justify-content: center; margin: 40px 0; gap: 10px; }}
        .page-num {{ display: inline-block; width: 40px; height: 40px; line-height: 40px; text-align: center; background: #fff; border: 1px solid #ddd; border-radius: 50%; text-decoration: none; color: #333; font-weight: bold; transition: 0.2s; }}
        .page-num.active, .page-num:hover {{ background: var(--primary); color: #fff; border-color: var(--primary); box-shadow: 0 4px 10px rgba(208,1,27,0.3); }}
        
        @media (max-width: 650px) {{ .blog-card-vertical {{ flex-direction: column; }} .blog-img {{ width: 100%; border-right: none; border-bottom: 1px solid #eee; }} .tools-bar {{ justify-content: center; flex-direction: column-reverse; }} .search-box {{ width: 100%; }} .search-box input {{ width: 100%; border-radius: 25px; border-right: 1px solid #ddd; margin-bottom: 10px;}} .search-box button {{ width: 100%; border-radius: 25px; }} .search-box {{ flex-direction: column; box-shadow: none;}} }}
        </style>
        {FB_PIXEL_CODE}
        </head>
        <body><div class="header-bg"></div><div class="ticker-wrap"><div class="ticker">🔥 ĐỐI TÁC CUNG CẤP VĂN PHÒNG PHẨM TRỌN GÓI 🔥 | 🚚 FREESHIP TỪ 500K | 📞 ZALO SỈ: {ZALO_NUMBER}</div></div>
        
        <div class="container">
            <div class="tools-bar">
                {html_menu}
                <div class="search-box">
                    <input type="text" id="searchInput" placeholder="Tìm kiếm sản phẩm..." onkeyup="if(event.key === 'Enter') searchSP()">
                    <button onclick="searchSP()">Tìm Kiếm</button>
                </div>
            </div>

            {html_bai_viet_section}
            
            <div style="text-align: center; margin-top: 50px; padding-top: 20px;"><h2 class="section-title" id="khu-vuc-sp">🛍️ SIÊU THỊ SẢN PHẨM</h2></div>

            <div class="grid" id="productGrid">{html_sp_grid}</div>
            {html_pagination}
        </div>
        
        {UI_FLOATING} {UI_FOOTER}
        
        <script>
            function filterCat(cat, event) {{
                if(event) event.preventDefault();
                let btns = document.getElementsByClassName('cat-btn');
                for(let b of btns) b.classList.remove('active');
                if(event) event.target.classList.add('active');

                let cards = document.getElementsByClassName('sp-card');
                for (let i = 0; i < cards.length; i++) {{
                    if (cat === 'all' || cards[i].classList.contains('mix-' + cat)) cards[i].style.display = 'flex';
                    else cards[i].style.display = 'none';
                }}
                document.getElementById('khu-vuc-sp').scrollIntoView({{behavior: "smooth", block: "start"}});
            }}

            function searchSP() {{
                let input = document.getElementById('searchInput').value.toLowerCase();
                let cards = document.getElementsByClassName('sp-card');
                for (let i = 0; i < cards.length; i++) {{
                    let title = cards[i].querySelector('.sp-name').innerText.toLowerCase();
                    if (title.includes(input)) cards[i].style.display = 'flex';
                    else cards[i].style.display = 'none';
                }}
                document.getElementById('khu-vuc-sp').scrollIntoView({{behavior: "smooth", block: "start"}});
            }}
        </script>
        </body></html>"""
        with open(os.path.join(BASE_DIR, ten_file), "w", encoding="utf-8") as f: f.write(html)

def tao_sitemap_xml(danh_sach_hub, tat_ca_san_pham, tong_trang):
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    for i in range(1, tong_trang + 1):
        link = "index.html" if i == 1 else f"page-{i}.html"
        xml += f'  <url>\n    <loc>{DOMAIN}/{link}</loc>\n    <changefreq>daily</changefreq>\n    <priority>1.0</priority>\n  </url>\n'
    for hub in danh_sach_hub:
        xml += f'  <url>\n    <loc>{DOMAIN}/bai-viet/{hub["slug"]}.html</loc>\n    <changefreq>weekly</changefreq>\n    <priority>0.8</priority>\n  </url>\n'
    for p in tat_ca_san_pham:
        xml += f'  <url>\n    <loc>{DOMAIN}/san-pham/{p["slug"]}.html</loc>\n    <changefreq>weekly</changefreq>\n    <priority>0.9</priority>\n  </url>\n'
    xml += '</urlset>'
    
    with open(os.path.join(BASE_DIR, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write(xml)
    print("✅ Đã tạo tự động Sitemap.xml")

def tao_robots_txt():
    noi_dung = f"User-agent: *\nAllow: /\nSitemap: {DOMAIN}/sitemap.xml"
    with open(os.path.join(BASE_DIR, "robots.txt"), "w", encoding="utf-8") as f:
        f.write(noi_dung)
    print("✅ Đã tạo biển báo Robots.txt cho Googlebot")

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

    print("--- 1. AI VIẾT MÔ TẢ SIÊU NGẮN (CHỐT SALE) ---")
    for p in data_san_pham:
        slug_sp = p['slug']
        if slug_sp not in cache_san_pham:
            cache_san_pham[slug_sp] = goi_ai_viet_mo_ta_sp(p.get('name', ''))
            with open(CACHE_SAN_PHAM, "w", encoding="utf-8") as f: json.dump(cache_san_pham, f, ensure_ascii=False, indent=2)
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

        ai_data = cache_bai_viet[dm]
        tao_trang_lai_bai_viet(slug_dm, ai_data, ds_sp)
        danh_sach_hub.append({"slug": slug_dm, "tieu_de": ai_data.get('tieu_de', ''), "meta_desc": ai_data.get('meta_description', ''), "ten_danh_muc": ten_dm, "img_dai_dien": sp_dau_tien.get('image', '')})

    print("--- 3. HOÀN THIỆN PHÂN TRANG & GIAO DIỆN ---")
    tao_trang_chu_phan_trang(danh_sach_hub, data_san_pham)
    
    print("--- 4. TẠO SITEMAP.XML CHO GOOGLE ---")
    tong_trang = math.ceil(len(data_san_pham) / SP_MOI_TRANG)
    if tong_trang == 0: tong_trang = 1
    tao_sitemap_xml(danh_sach_hub, data_san_pham, tong_trang)
    tao_robots_txt()
    
    print("🎉 TẤT CẢ ĐÃ XONG! HỆ THỐNG TỰ CỨU KEY & AI NGHIÊM TÚC ĐÃ SẴN SÀNG!")

if __name__ == "__main__":
    chay_he_thong()