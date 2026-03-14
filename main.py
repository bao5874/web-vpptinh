import csv
import json
import os
import re
import base64 
import time
import urllib.request
import io

try:
    from google import genai
    from google.genai import types
except ImportError:
    print("❌ THIẾU THƯ VIỆN AI!")
    exit()

URL_CSV_SAN_PHAM = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQzftzzjfyPE6MujJRirjKeXub0RmgpmAQNuTr9IjaLGe9BGukp4RnPisW7tZo3sDBBqiumtY3RWNbX/pub?gid=0&single=true&output=csv"
BASE_AFF_URL = "https://go.isclix.com/deep_link/v6/6906519896943843292/4751584435713464237?url_enc="
ZALO_NUMBER = "0931736266"

DANH_MUC_MAP = {
    "tho_cung": "Đồ Thờ Cúng", "dc_vs": "Dụng Cụ Vệ Sinh", 
    "vpp": "Văn Phòng Phẩm", "gia_dung": "Đồ Gia Dụng", 
    "me_be": "Mẹ & Bé", "khac": "Sản Phẩm Khác"
}

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CACHE_BAI_VIET = os.path.join(BASE_DIR, "bai_viet_tu_dong_cache.json")
THU_MUC_BAI_VIET = os.path.join(BASE_DIR, "bai-viet")

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    try:
        with open(os.path.join(BASE_DIR, "api_key.txt"), "r") as f:
            GEMINI_API_KEY = f.read().strip()
    except: pass

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

def goi_ai_tu_dong_viet_bai(ten_danh_muc, ten_sp_dau_tien):
    if not GEMINI_API_KEY: return {"tieu_de": "Chưa có API Key", "noi_dung_html": "<p>Vui lòng cài đặt AI.</p>"}
    print(f"✍️ AI đang viết bài cho nhóm '{ten_danh_muc}'...")
    prompt = f"""Bạn là Copywriter SEO chuyên nghiệp. Viết bài bán hàng dài khoảng 600 - 800 chữ cho nhóm "{ten_danh_muc}". Lấy sản phẩm "{ten_sp_dau_tien}" làm mồi câu. BẮT BUỘC TRẢ VỀ JSON: {{"tieu_de": "Tiêu đề (10-15 chữ)", "noi_dung_html": "Nội dung bài định dạng HTML (<h2>, <h3>, <p>, <ul>, <li>). Không chứa <html> body."}}"""
    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
        response = client.models.generate_content(model='gemini-2.5-flash', contents=prompt, config=types.GenerateContentConfig(temperature=0.8, response_mime_type="application/json"))
        return json.loads(response.text)
    except Exception as e:
        return {"tieu_de": f"Top sản phẩm {ten_danh_muc}", "noi_dung_html": "<p>Nội dung đang cập nhật...</p>"}

def tao_trang_lai_bai_viet(slug, tieu_de, noi_dung_html, san_pham_lien_quan):
    html_sp = ""
    sp_moi = san_pham_lien_quan[0] if san_pham_lien_quan else {}
    img_moi = sp_moi.get('image', '')
    link_aff_moi = tao_link_aff(sp_moi.get('link', ''))
    
    for p in san_pham_lien_quan:
        try: moi = float(re.sub(r'[^\d]', '', str(p.get('new_price', '0')))) if re.sub(r'[^\d]', '', str(p.get('new_price', '0'))) else 0
        except: moi = 0
        html_sp += f"""<div class="sp-card"><img src="{p.get('image', '')}"><div class="sp-info"><div class="sp-name">{p.get('name', '')}</div><div class="sp-price">{int(moi):,}₫</div><a href="{tao_link_aff(p.get('link', ''))}" target="_blank" rel="nofollow" class="sp-btn">🛒 ĐẾN NƠI BÁN</a></div></div>"""

    html = f"""<!DOCTYPE html><html lang="vi"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>{tieu_de} | VPP Tịnh</title>
    <style>:root {{ --primary: #d0011b; --bg: #f5f5f5; }} body {{ font-family: sans-serif; background: var(--bg); margin: 0; padding: 0; color: #333; }} .header {{ background: #fff; padding: 10px 25px; position: sticky; top: 0; z-index: 100; border-bottom: 1px solid #eee; display: flex; justify-content: space-between; }} .btn-home {{ background: #fff; color: var(--primary); border: 2px solid var(--primary); padding: 8px 15px; border-radius: 6px; text-decoration: none; font-weight: bold; }} .container {{ max-width: 800px; margin: 20px auto; background: white; padding: 25px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }} .article-column {{ max-width: 650px; margin: 0 auto; line-height: 1.6; font-size: 16px; }} .featured-img-box {{ text-align: center; margin: 20px 0; }} .featured-img-box img {{ max-width: 100%; max-height: 350px; border-radius: 8px; }} .showcase-title {{ text-align: center; color: var(--primary); margin: 40px 0 20px; border-top: 2px dashed #eee; padding-top: 30px; }} .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 15px; text-align: center; }} .sp-card {{ border: 1px solid #eee; border-radius: 8px; padding: 10px; background: white; }} .sp-card img {{ width: 100%; height: 180px; object-fit: contain; }} .sp-name {{ font-size: 14px; height: 40px; overflow: hidden; margin: 10px 0; }} .sp-price {{ font-weight: bold; color: var(--primary); font-size: 18px; margin-bottom: 10px; }} .sp-btn {{ display: block; background: var(--primary); color: white; padding: 10px; border-radius: 5px; text-decoration: none; font-weight: bold; }}</style></head>
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
        html_sp_all += f"""<div class="sp-card"><img src="{p.get('image', '')}" loading="lazy"><div class="sp-info"><div class="sp-name">{p.get('name', '')}</div><div class="sp-price">{int(moi):,}₫</div><a href="{tao_link_aff(p.get('link', ''))}" target="_blank" rel="nofollow" class="sp-btn">🛒 ĐẾN NƠI BÁN</a></div></div>"""

    html = f"""<!DOCTYPE html><html lang="vi"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>VPP Tịnh | Trang Chủ</title>
    <style>:root {{ --primary: #d0011b; --bg: #f5f5f5; }} body {{ font-family: sans-serif; background: var(--bg); margin: 0; padding: 0; }} .header-bg {{ width: 100%; max-width: 1200px; margin: 0 auto; aspect-ratio: 1360/350; background-image: url('static/images/tinh_radio_banner1.jpg'); background-size: cover; background-position: center; }} .ticker-wrap {{ width: 100%; max-width: 1200px; margin: 0 auto 30px auto; background-color: var(--primary); padding: 12px 0; overflow: hidden; color: white; font-weight: bold; font-size: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }} .ticker {{ display: inline-block; white-space: nowrap; padding-right: 100%; animation: ticker 25s linear infinite; }} @keyframes ticker {{ 0% {{ transform: translate3d(100%, 0, 0); }} 100% {{ transform: translate3d(-100%, 0, 0); }} }} .container {{ max-width: 1000px; margin: 0 auto; padding: 0 20px; }} .section-title {{ text-align: center; margin: 40px 0 30px; color: #333; text-transform: uppercase; border-bottom: 2px solid var(--primary); display: inline-block; padding-bottom: 10px; font-size: 26px; }}
    /* BÀI VIẾT DỌC CÓ HÌNH BÊN TRÁI */
    .blog-list-vertical {{ display: flex; flex-direction: column; gap: 20px; }} .blog-card-vertical {{ display: flex; flex-direction: row; background: white; border-radius: 10px; overflow: hidden; text-decoration: none; color: #333; box-shadow: 0 3px 15px rgba(0,0,0,0.05); border: 1px solid #eee; }} .blog-img {{ width: 250px; height: 180px; object-fit: contain; border-right: 1px solid #eee; padding: 10px; }} .blog-content {{ padding: 20px; display: flex; flex-direction: column; justify-content: center; flex: 1; }} .blog-tag {{ background: #ffeeee; color: var(--primary); padding: 5px 10px; border-radius: 20px; font-size: 12px; font-weight: bold; align-self: flex-start; margin-bottom: 10px; }} .blog-content h3 {{ color: var(--primary); margin: 0 0 10px 0; font-size: 20px; }}
    /* LƯỚI SẢN PHẨM */
    .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 15px; text-align: center; padding-bottom: 60px; }} .sp-card {{ border: 1px solid #eee; border-radius: 8px; padding: 10px; background: white; transition: transform 0.2s; }} .sp-card img {{ width: 100%; height: 180px; object-fit: contain; margin-bottom: 10px; }} .sp-name {{ font-size: 14px; height: 40px; overflow: hidden; margin-bottom: 10px; }} .sp-price {{ font-weight: bold; color: var(--primary); font-size: 18px; margin-bottom: 15px; }} .sp-btn {{ display: block; background: var(--primary); color: white; padding: 10px; border-radius: 5px; text-decoration: none; font-weight: bold; }}
    @media (max-width: 650px) {{ .blog-card-vertical {{ flex-direction: column; }} .blog-img {{ width: 100%; border-right: none; border-bottom: 1px solid #eee; }} }}</style></head>
    <body><div class="header-bg"></div><div class="ticker-wrap"><div class="ticker">🔥 CHÀO MỪNG ĐẾN VỚI VPP TỊNH - ĐỐI TÁC CUNG CẤP VĂN PHÒNG PHẨM TRỌN GÓI 🔥 | 🚚 FREESHIP TỪ 500K | 📞 ZALO SỈ: {ZALO_NUMBER}</div></div>
    <div class="container"><div style="text-align: center;"><h2 class="section-title">📰 TƯ VẤN SẢN PHẨM</h2></div><div class="blog-list-vertical">{html_links if html_links else "<p>Đang cập nhật...</p>"}</div>
    <div style="text-align: center; margin-top: 50px;"><h2 class="section-title">🛍️ TẤT CẢ SẢN PHẨM TẠI SHOP</h2></div><div class="grid">{html_sp_all}</div></div></body></html>"""
    with open(os.path.join(BASE_DIR, "index.html"), "w", encoding="utf-8") as f: f.write(html)

def chay_he_thong():
    print("🚀 ĐANG TẢI DỮ LIỆU TỪ GOOGLE SHEETS...")
    data_san_pham = lay_data_tu_google_sheet(URL_CSV_SAN_PHAM)
    if not data_san_pham: return print("❌ Dữ liệu rỗng!")
    os.makedirs(THU_MUC_BAI_VIET, exist_ok=True)
    gom_nhom = {}
    for p in data_san_pham:
        dm = p.get('danh_muc', 'khac').strip()
        if not dm: dm = 'khac'
        if dm not in gom_nhom: gom_nhom[dm] = []
        gom_nhom[dm].append(p)

    cache_ai = {}
    if os.path.exists(CACHE_BAI_VIET):
        with open(CACHE_BAI_VIET, "r", encoding="utf-8") as f: cache_ai = json.load(f)

    danh_sach_hub = []
    for dm, ds_sp in gom_nhom.items():
        if not ds_sp: continue
        sp_dau_tien = ds_sp[0]
        ten_moi = sp_dau_tien.get('name', 'Sản phẩm')
        img_moi = sp_dau_tien.get('image', '')
        ten_dm = DANH_MUC_MAP.get(dm, dm.title())
        slug = f"chuyen-muc-{dm}"

        if dm not in cache_ai:
            ket_qua_ai = goi_ai_tu_dong_viet_bai(ten_dm, ten_moi)
            cache_ai[dm] = ket_qua_ai
            with open(CACHE_BAI_VIET, "w", encoding="utf-8") as f: json.dump(cache_ai, f, ensure_ascii=False, indent=2)
            time.sleep(2)

        tieu_de = cache_ai[dm].get('tieu_de', f'Top sản phẩm {ten_dm}')
        noi_dung = cache_ai[dm].get('noi_dung_html', '')
        tao_trang_lai_bai_viet(slug, tieu_de, noi_dung, ds_sp)
        danh_sach_hub.append({"slug": slug, "tieu_de": tieu_de, "ten_danh_muc": ten_dm, "img_dai_dien": img_moi})

    print(f"✅ Đã tạo {len(danh_sach_hub)} bài viết.")
    tao_trang_chu(danh_sach_hub, data_san_pham)
    print("🎉 HOÀN TẤT TẠO GIAO DIỆN ENDLESS SCROLL!")

if __name__ == "__main__":
    chay_he_thong()