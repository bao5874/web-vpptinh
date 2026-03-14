import csv
import json
import os
import re
import base64 
import time
import urllib.request
import io
import unicodedata

try:
    from google import genai
    from google.genai import types
except ImportError:
    print("❌ THIẾU THƯ VIỆN AI!")
    exit()

# ==========================================
# CẤU HÌNH HỆ THỐNG
# ==========================================
URL_CSV_SAN_PHAM = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQzftzzjfyPE6MujJRirjKeXub0RmgpmAQNuTr9IjaLGe9BGukp4RnPisW7tZo3sDBBqiumtY3RWNbX/pub?gid=0&single=true&output=csv"

# THAY MÃ ID ACCESSTRADE CỦA BẠN VÀO ĐÂY:
BASE_AFF_URL = "https://go.isclix.com/deep_link/v6/6906519896943843292/4751584435713464237?url_enc="

ZALO_NUMBER = "0931736266"

DANH_MUC_MAP = {
    "tho_cung": "Đồ Thờ Cúng", "dc_vs": "Dụng Cụ Vệ Sinh", 
    "vpp": "Văn Phòng Phẩm", "gia_dung": "Đồ Gia Dụng", 
    "me_be": "Mẹ & Bé", "khac": "Sản Phẩm Khác"
}

# ==========================================
# KHÔNG SỬA PHẦN DƯỚI NÀY
# ==========================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CACHE_BAI_VIET = os.path.join(BASE_DIR, "bai_viet_tu_dong_cache.json")
CACHE_SAN_PHAM = os.path.join(BASE_DIR, "san_pham_cache.json")
THU_MUC_BAI_VIET = os.path.join(BASE_DIR, "bai-viet")
THU_MUC_SAN_PHAM = os.path.join(BASE_DIR, "san-pham") # Thư mục mới chứa trang chi tiết SP

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    try:
        with open(os.path.join(BASE_DIR, "api_key.txt"), "r") as f: GEMINI_API_KEY = f.read().strip()
    except: pass

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
        response = urllib.request.urlopen(req)
        csv_data = response.read().decode('utf-8')
        return list(csv.DictReader(io.StringIO(csv_data)))
    except Exception as e:
        print(f"❌ LỖI ĐỌC GOOGLE SHEET: {e}")
        return []

# AI VIẾT BÀI CHUYÊN MỤC (Giữ nguyên)
def goi_ai_tu_dong_viet_bai(ten_danh_muc, ten_sp_dau_tien):
    if not GEMINI_API_KEY: return {"tieu_de": "Chưa có API Key", "noi_dung_html": "<p>Vui lòng cài đặt AI.</p>"}
    print(f"📰 AI đang viết bài Tạp chí cho nhóm '{ten_danh_muc}'...")
    prompt = f"""Bạn là Copywriter SEO. Viết bài bán hàng 600 chữ cho nhóm "{ten_danh_muc}". Lấy sản phẩm "{ten_sp_dau_tien}" làm mồi câu. BẮT BUỘC TRẢ VỀ JSON: {{"tieu_de": "Tiêu đề", "noi_dung_html": "HTML nội dung (<h2>, <p>, <ul>)"}}"""
    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
        response = client.models.generate_content(model='gemini-2.5-flash', contents=prompt, config=types.GenerateContentConfig(temperature=0.8, response_mime_type="application/json"))
        return json.loads(response.text)
    except Exception as e:
        return {"tieu_de": f"Top sản phẩm {ten_danh_muc}", "noi_dung_html": "<p>Đang cập nhật...</p>"}

# AI VIẾT MÔ TẢ CHO TỪNG SẢN PHẨM (Tính năng mới)
def goi_ai_viet_mo_ta_sp(ten_sp):
    if not GEMINI_API_KEY: return "<p>Mô tả đang cập nhật.</p>"
    print(f"📝 AI đang viết mô tả chi tiết cho SP: '{ten_sp}'...")
    prompt = f"Viết đoạn mô tả sản phẩm giới thiệu chi tiết, hấp dẫn (khoảng 150-200 chữ) cho sản phẩm: '{ten_sp}'. Nêu bật công dụng, lý do nên mua. Định dạng HTML (chỉ dùng thẻ <h3>, <p>, <ul>, <li>). Không xuất markdown."
    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
        response = client.models.generate_content(model='gemini-2.5-flash', contents=prompt, config=types.GenerateContentConfig(temperature=0.7))
        return response.text.replace("```html", "").replace("```", "").strip()
    except Exception as e:
        return f"<p>Sản phẩm {ten_sp} chất lượng cao, đang có ưu đãi lớn.</p>"

# TẠO TRANG CHI TIẾT SẢN PHẨM (Trang mới hoàn toàn)
def tao_trang_chi_tiet_sp(p, mo_ta_html):
    slug = p['slug']
    link_aff = tao_link_aff(p.get('link', ''))
    try: moi = float(re.sub(r'[^\d]', '', str(p.get('new_price', '0')))) if re.sub(r'[^\d]', '', str(p.get('new_price', '0'))) else 0
    except: moi = 0
    
    html = f"""<!DOCTYPE html><html lang="vi"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>{p.get('name', 'Sản phẩm')} | VPP Tịnh</title>
    <style>:root {{ --primary: #d0011b; --bg: #f5f5f5; }} body {{ font-family: sans-serif; background: var(--bg); margin: 0; padding: 0; color: #333; }} .header {{ background: #fff; padding: 10px 25px; position: sticky; top: 0; z-index: 100; border-bottom: 1px solid #eee; display: flex; justify-content: space-between; }} .btn-home {{ background: #fff; color: var(--primary); border: 2px solid var(--primary); padding: 8px 15px; border-radius: 6px; text-decoration: none; font-weight: bold; }} .container {{ max-width: 800px; margin: 30px auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }} .product-top {{ display: flex; gap: 30px; margin-bottom: 30px; }} .product-img {{ flex: 1; text-align: center; }} .product-img img {{ max-width: 100%; max-height: 400px; border-radius: 8px; border: 1px solid #eee; padding: 10px; }} .product-info {{ flex: 1; display: flex; flex-direction: column; justify-content: center; }} .p-title {{ font-size: 24px; color: #222; margin-top: 0; }} .p-price {{ font-size: 28px; color: var(--primary); font-weight: bold; margin: 15px 0; }} .btn-buy {{ background: var(--primary); color: white; text-decoration: none; padding: 15px 20px; text-align: center; border-radius: 6px; font-weight: bold; font-size: 18px; box-shadow: 0 4px 15px rgba(208,1,27,0.3); transition: transform 0.2s; display: block; }} .btn-buy:hover {{ transform: scale(1.02); }} .desc-box {{ border-top: 2px dashed #eee; padding-top: 30px; line-height: 1.6; font-size: 16px; }} .desc-box h3 {{ color: var(--primary); }} 
    @media (max-width: 650px) {{ .product-top {{ flex-direction: column; }} }}</style></head>
    <body>
    <div class="header"><a href="../index.html" class="btn-home">🔙 Quay lại Trang Chủ</a><strong style="color:var(--primary); font-size: 18px; line-height: 36px;">VPP TỊNH SHOP</strong></div>
    <div class="container">
        <div class="product-top">
            <div class="product-img"><img src="{p.get('image', '')}"></div>
            <div class="product-info">
                <h1 class="p-title">{p.get('name', '')}</h1>
                <div class="p-price">{int(moi):,}₫</div>
                <a href="{link_aff}" target="_blank" rel="nofollow" class="btn-buy">🛒 MUA NGAY (XEM ƯU ĐÃI)</a>
            </div>
        </div>
        <div class="desc-box">
            <h2>📜 Thông tin chi tiết</h2>
            {mo_ta_html}
        </div>
    </div>
    </body></html>"""
    with open(os.path.join(THU_MUC_SAN_PHAM, f"{slug}.html"), "w", encoding="utf-8") as f: f.write(html)

def tao_trang_lai_bai_viet(slug, tieu_de, noi_dung_html, san_pham_lien_quan):
    html_sp = ""
    sp_moi = san_pham_lien_quan[0] if san_pham_lien_quan else {}
    img_moi = sp_moi.get('image', '')
    link_aff_moi = tao_link_aff(sp_moi.get('link', ''))
    
    for p in san_pham_lien_quan:
        try: moi = float(re.sub(r'[^\d]', '', str(p.get('new_price', '0')))) if re.sub(r'[^\d]', '', str(p.get('new_price', '0'))) else 0
        except: moi = 0
        # NÚT ĐÃ SỬA THÀNH "XEM THÊM" TRỎ VỀ TRANG CHI TIẾT SP
        html_sp += f"""<div class="sp-card"><img src="{p.get('image', '')}"><div class="sp-info"><div class="sp-name">{p.get('name', '')}</div><div class="sp-price">{int(moi):,}₫</div><a href="../san-pham/{p['slug']}.html" class="sp-btn-xem">🔍 XEM THÊM</a></div></div>"""

    html = f"""<!DOCTYPE html><html lang="vi"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>{tieu_de} | VPP Tịnh</title>
    <style>:root {{ --primary: #d0011b; --bg: #f5f5f5; }} body {{ font-family: sans-serif; background: var(--bg); margin: 0; padding: 0; color: #333; }} .header {{ background: #fff; padding: 10px 25px; position: sticky; top: 0; z-index: 100; border-bottom: 1px solid #eee; display: flex; justify-content: space-between; }} .btn-home {{ background: #fff; color: var(--primary); border: 2px solid var(--primary); padding: 8px 15px; border-radius: 6px; text-decoration: none; font-weight: bold; }} .container {{ max-width: 800px; margin: 20px auto; background: white; padding: 25px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }} .article-column {{ max-width: 650px; margin: 0 auto; line-height: 1.6; font-size: 16px; }} .featured-img-box {{ text-align: center; margin: 20px 0; }} .featured-img-box img {{ max-width: 100%; max-height: 350px; border-radius: 8px; }} .showcase-title {{ text-align: center; color: var(--primary); margin: 40px 0 20px; border-top: 2px dashed #eee; padding-top: 30px; }} .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 15px; text-align: center; }} .sp-card {{ border: 1px solid #eee; border-radius: 8px; padding: 10px; background: white; }} .sp-card img {{ width: 100%; height: 180px; object-fit: contain; }} .sp-name {{ font-size: 14px; height: 40px; overflow: hidden; margin: 10px 0; }} .sp-price {{ font-weight: bold; color: var(--primary); font-size: 18px; margin-bottom: 10px; }} .sp-btn-xem {{ display: block; background: #fff; color: var(--primary); border: 1px solid var(--primary); padding: 10px; border-radius: 5px; text-decoration: none; font-weight: bold; transition: 0.2s;}} .sp-btn-xem:hover {{ background: var(--primary); color: #fff; }}</style></head>
    <body><div class="header"><a href="../index.html" class="btn-home">🔙 Quay lại Trang Chủ</a><strong style="color:var(--primary); font-size: 18px; line-height: 36px;">VPP TỊNH SHOP</strong></div>
    <div class="container"><h1 style="text-align: center; margin-bottom: 20px;">{tieu_de}</h1><div class="article-column"><div class="featured-img-box"><a href="{link_aff_moi}" target="_blank"><img src="{img_moi}"></a></div>{noi_dung_html}</div><h2 class="showcase-title">🔥 CÁC SẢN PHẨM KHUYÊN DÙNG 🔥</h2><div class="grid">{html_sp}</div></div></body></html>"""
    with open(os.path.join(THU_MUC_BAI_VIET, f"{slug}.html"), "w", encoding="utf-8") as f: f.write(html)

def tao_trang_chu(danh_sach_hub, tat_ca_san_pham):
    html_links = ""
    for hub in danh_sach_hub:
        html_links += f"""<a href="bai-viet/{hub['slug']}.html" class="blog-card-vertical"><img src="{hub['img_dai_dien']}" class="blog-img"><div class="blog-content"><span class="blog-tag">{hub['ten_danh_muc']}</span><h3>{hub['tieu_de']}</h3><p>Đọc đánh giá chi tiết và xem các sản phẩm cùng loại ➡️</p></div></a>"""

    html_sp_all = ""
    for p in tat_ca_san_pham:
        try: moi = float(re.sub(r'[^\d]', '', str(p.get('new_price', '0')))) if re.sub(r'[^\d]', '', str(p.get('new_price', '0'))) else 0
        except: moi = 0
        # NÚT ĐÃ SỬA THÀNH "XEM THÊM" TRỎ VỀ TRANG CHI TIẾT SP
        html_sp_all += f"""<div class="sp-card"><img src="{p.get('image', '')}" loading="lazy"><div class="sp-info"><div class="sp-name">{p.get('name', '')}</div><div class="sp-price">{int(moi):,}₫</div><a href="san-pham/{p['slug']}.html" class="sp-btn-xem">🔍 XEM THÊM</a></div></div>"""

    html = f"""<!DOCTYPE html><html lang="vi"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>VPP Tịnh | Trang Chủ</title>
    <style>:root {{ --primary: #d0011b; --bg: #f5f5f5; }} body {{ font-family: sans-serif; background: var(--bg); margin: 0; padding: 0; }} .header-bg {{ width: 100%; max-width: 1200px; margin: 0 auto; aspect-ratio: 1360/350; background-image: url('static/images/tinh_radio_banner1.jpg'); background-size: cover; background-position: center; }} .ticker-wrap {{ width: 100%; max-width: 1200px; margin: 0 auto 30px auto; background-color: var(--primary); padding: 12px 0; overflow: hidden; color: white; font-weight: bold; font-size: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }} .ticker {{ display: inline-block; white-space: nowrap; padding-right: 100%; animation: ticker 25s linear infinite; }} @keyframes ticker {{ 0% {{ transform: translate3d(100%, 0, 0); }} 100% {{ transform: translate3d(-100%, 0, 0); }} }} .container {{ max-width: 1000px; margin: 0 auto; padding: 0 20px; }} .section-title {{ text-align: center; margin: 40px 0 30px; color: #333; text-transform: uppercase; border-bottom: 2px solid var(--primary); display: inline-block; padding-bottom: 10px; font-size: 26px; }}
    .blog-list-vertical {{ display: flex; flex-direction: column; gap: 20px; }} .blog-card-vertical {{ display: flex; flex-direction: row; background: white; border-radius: 10px; overflow: hidden; text-decoration: none; color: #333; box-shadow: 0 3px 15px rgba(0,0,0,0.05); border: 1px solid #eee; }} .blog-img {{ width: 250px; height: 180px; object-fit: contain; border-right: 1px solid #eee; padding: 10px; }} .blog-content {{ padding: 20px; display: flex; flex-direction: column; justify-content: center; flex: 1; }} .blog-tag {{ background: #ffeeee; color: var(--primary); padding: 5px 10px; border-radius: 20px; font-size: 12px; font-weight: bold; align-self: flex-start; margin-bottom: 10px; }} .blog-content h3 {{ color: var(--primary); margin: 0 0 10px 0; font-size: 20px; }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 15px; text-align: center; padding-bottom: 60px; }} .sp-card {{ border: 1px solid #eee; border-radius: 8px; padding: 10px; background: white; transition: transform 0.2s; }} .sp-card img {{ width: 100%; height: 180px; object-fit: contain; margin-bottom: 10px; }} .sp-name {{ font-size: 14px; height: 40px; overflow: hidden; margin-bottom: 10px; }} .sp-price {{ font-weight: bold; color: var(--primary); font-size: 18px; margin-bottom: 15px; }} .sp-btn-xem {{ display: block; background: #fff; color: var(--primary); border: 1px solid var(--primary); padding: 10px; border-radius: 5px; text-decoration: none; font-weight: bold; transition: 0.2s;}} .sp-btn-xem:hover {{ background: var(--primary); color: #fff; }}
    @media (max-width: 650px) {{ .blog-card-vertical {{ flex-direction: column; }} .blog-img {{ width: 100%; border-right: none; border-bottom: 1px solid #eee; }} }}</style></head>
    <body><div class="header-bg"></div><div class="ticker-wrap"><div class="ticker">🔥 CHÀO MỪNG ĐẾN VỚI VPP TỊNH - ĐỐI TÁC CUNG CẤP VĂN PHÒNG PHẨM TRỌN GÓI 🔥 | 📞 ZALO SỈ: {ZALO_NUMBER}</div></div>
    <div class="container"><div style="text-align: center;"><h2 class="section-title">📰 TƯ VẤN SẢN PHẨM</h2></div><div class="blog-list-vertical">{html_links if html_links else "<p>Đang cập nhật...</p>"}</div>
    <div style="text-align: center; margin-top: 50px;"><h2 class="section-title">🛍️ TẤT CẢ SẢN PHẨM TẠI SHOP</h2></div><div class="grid">{html_sp_all}</div></div></body></html>"""
    with open(os.path.join(BASE_DIR, "index.html"), "w", encoding="utf-8") as f: f.write(html)

def chay_he_thong():
    print("🚀 ĐANG TẢI DỮ LIỆU TỪ GOOGLE SHEETS...")
    data_san_pham = lay_data_tu_google_sheet(URL_CSV_SAN_PHAM)
    if not data_san_pham: return print("❌ Dữ liệu rỗng!")
    
    os.makedirs(THU_MUC_BAI_VIET, exist_ok=True)
    os.makedirs(THU_MUC_SAN_PHAM, exist_ok=True) # Tạo thư mục chứa SP
    
    # Tạo slug duy nhất cho từng sản phẩm
    for p in data_san_pham:
        p['slug'] = tao_slug(p.get('name', ''))

    # QUẢN LÝ BỘ NHỚ ĐỆM (CACHE)
    cache_bai_viet, cache_san_pham = {}, {}
    if os.path.exists(CACHE_BAI_VIET):
        with open(CACHE_BAI_VIET, "r", encoding="utf-8") as f: cache_bai_viet = json.load(f)
    if os.path.exists(CACHE_SAN_PHAM):
        with open(CACHE_SAN_PHAM, "r", encoding="utf-8") as f: cache_san_pham = json.load(f)

    # 1. AI VIẾT MÔ TẢ CHO TỪNG SẢN PHẨM
    print("--- BẮT ĐẦU XỬ LÝ SẢN PHẨM ---")
    for p in data_san_pham:
        slug_sp = p['slug']
        if slug_sp not in cache_san_pham:
            mo_ta = goi_ai_viet_mo_ta_sp(p.get('name', ''))
            cache_san_pham[slug_sp] = mo_ta
            with open(CACHE_SAN_PHAM, "w", encoding="utf-8") as f: json.dump(cache_san_pham, f, ensure_ascii=False, indent=2)
            time.sleep(3) # Nghỉ 3 giây để AI không bị khóa do quá tải
        
        # Tạo luôn trang HTML cho sản phẩm này
        tao_trang_chi_tiet_sp(p, cache_san_pham[slug_sp])
    
    print(f"✅ Đã tạo xong {len(data_san_pham)} trang chi tiết sản phẩm.")

    # 2. XỬ LÝ BÀI VIẾT CHUYÊN MỤC
    print("--- BẮT ĐẦU XỬ LÝ CHUYÊN MỤC ---")
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
            ket_qua_ai = goi_ai_tu_dong_viet_bai(ten_dm, sp_dau_tien.get('name', ''))
            cache_bai_viet[dm] = ket_qua_ai
            with open(CACHE_BAI_VIET, "w", encoding="utf-8") as f: json.dump(cache_bai_viet, f, ensure_ascii=False, indent=2)
            time.sleep(3)

        tieu_de = cache_bai_viet[dm].get('tieu_de', f'Top sản phẩm {ten_dm}')
        noi_dung = cache_bai_viet[dm].get('noi_dung_html', '')
        tao_trang_lai_bai_viet(slug_dm, tieu_de, noi_dung, ds_sp)
        danh_sach_hub.append({"slug": slug_dm, "tieu_de": tieu_de, "ten_danh_muc": ten_dm, "img_dai_dien": sp_dau_tien.get('image', '')})

    print("--- HOÀN THIỆN GIAO DIỆN ---")
    tao_trang_chu(danh_sach_hub, data_san_pham)
    print("🎉 TẤT CẢ ĐÃ XONG! HÃY ĐẨY LÊN GITHUB NÀO!")

if __name__ == "__main__":
    chay_he_thong()