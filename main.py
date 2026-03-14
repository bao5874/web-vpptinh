import csv
import json
import os
import re
import base64 
import time
import random
import urllib.request
import io

try:
    from google import genai
    from google.genai import types
except ImportError:
    print("❌ THIẾU THƯ VIỆN AI! Hãy mở Terminal gõ lệnh: pip install google-genai")
    exit()

# ==========================================
# CẤU HÌNH HỆ THỐNG (BẠN ĐIỀN THÔNG TIN VÀO ĐÂY)
# ==========================================
# 1. Dán Link CSV Tab "San_Pham"
URL_CSV_SAN_PHAM = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQzftzzjfyPE6MujJRirjKeXub0RmgpmAQNuTr9IjaLGe9BGukp4RnPisW7tZo3sDBBqiumtY3RWNbX/pub?gid=0&single=true&output=csv"

# 2. Dán Link CSV Tab "Bai_Viet"
URL_CSV_BAI_VIET = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQzftzzjfyPE6MujJRirjKeXub0RmgpmAQNuTr9IjaLGe9BGukp4RnPisW7tZo3sDBBqiumtY3RWNbX/pub?gid=624417606&single=true&output=csv"

# 3. Dán Link Base Accesstrade của bạn
BASE_AFF_URL = "https://go.isclix.com/deep_link/v6/6906519896943843292/4751584435713464237?url_enc="

# Số điện thoại Zalo của bạn
ZALO_NUMBER = "0931736266"

# ==========================================
# KHÔNG SỬA PHẦN DƯỚI NÀY NẾU KHÔNG BIẾT CODE
# ==========================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CACHE_BAI_VIET = os.path.join(BASE_DIR, "bai_viet_cache.json")
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
        print(f"❌ LỖI ĐỌC GOOGLE SHEET ({url[:30]}...): {e}")
        return []

def goi_ai_viet_bai_seo(tieu_de):
    if not GEMINI_API_KEY: return "<p>Nội dung đang cập nhật...</p>"
    print(f"✍️ Đang nhờ AI viết bài: {tieu_de}...")
    
    prompt = f"""Bạn là một chuyên gia Review và Copywriter xuất sắc. 
    Hãy viết một bài blog dài khoảng 600 - 800 chữ với tiêu đề: "{tieu_de}".
    Yêu cầu:
    1. Viết bài phân tích, hướng dẫn chọn mua, hoặc đánh giá sâu sắc. Giọng văn lôi cuốn, thuyết phục.
    2. BẮT BUỘC định dạng nội dung bằng HTML (chỉ dùng các thẻ <h2>, <h3>, <p>, <ul>, <li>, <strong>). KHÔNG DÙNG MARKDOWN (như ## hay **). KHÔNG xuất thẻ <html> hay <body>.
    3. Trình bày đẹp, có mở bài, thân bài (các luận điểm rõ ràng) và kết bài.
    """
    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
        response = client.models.generate_content(
            model='gemini-2.5-flash', contents=prompt,
            config=types.GenerateContentConfig(temperature=0.8)
        )
        # Lọc bỏ markdown block nếu AI lỡ sinh ra
        html_content = response.text.replace("```html", "").replace("```", "").strip()
        return html_content
    except Exception as e:
        print(f"Lỗi AI: {e}")
        return "<p>Hệ thống AI đang bận, vui lòng thử lại sau.</p>"

def tao_trang_lai_bai_viet(bai_viet, san_pham_lien_quan):
    slug = bai_viet['slug']
    html_sp = ""
    
    # Tạo HTML cho Lưới sản phẩm chốt sale
    for p in san_pham_lien_quan:
        try: moi = float(re.sub(r'[^\d]', '', str(p.get('new_price', '0')))) if re.sub(r'[^\d]', '', str(p.get('new_price', '0'))) else 0
        except: moi = 0
        link_aff = tao_link_aff(p.get('link', ''))
        
        html_sp += f"""
        <div class="sp-card">
            <img src="{p.get('image', '')}" alt="{p.get('name', '')}">
            <div class="sp-info">
                <div class="sp-name">{p.get('name', '')}</div>
                <div class="sp-price">{int(moi):,}₫</div>
                <a href="{link_aff}" target="_blank" rel="nofollow" class="sp-btn">🛒 ĐẾN NƠI BÁN</a>
            </div>
        </div>
        """

    html = f"""<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{bai_viet['tieu_de']} | VPP Tịnh</title>
    <style>
        :root {{ --primary: #d0011b; --bg: #f5f5f5; }}
        body {{ font-family: sans-serif; background: var(--bg); margin: 0; padding: 0; color: #333; }}
        .header {{ background: var(--primary); color: white; padding: 15px; text-align: center; font-weight: bold; font-size: 18px; position: sticky; top: 0; z-index: 100; }}
        .header a {{ color: white; text-decoration: none; }}
        .container {{ max-width: 800px; margin: 20px auto; background: white; padding: 25px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        
        /* CSS Ẩn/Hiện bài viết */
        .article-wrapper {{ position: relative; max-height: 500px; overflow: hidden; transition: max-height 0.5s ease; line-height: 1.6; font-size: 16px; }}
        .article-wrapper.expanded {{ max-height: 10000px; }}
        .article-wrapper h2 {{ color: var(--primary); margin-top: 25px; font-size: 22px; }}
        .fade-out {{ position: absolute; bottom: 0; left: 0; width: 100%; height: 150px; background: linear-gradient(transparent, white); display: flex; align-items: flex-end; justify-content: center; padding-bottom: 20px; }}
        .expanded .fade-out {{ display: none; }}
        .btn-readmore {{ background: white; color: var(--primary); border: 2px solid var(--primary); padding: 12px 30px; border-radius: 25px; cursor: pointer; font-weight: bold; font-size: 16px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
        .btn-readmore:hover {{ background: var(--primary); color: white; }}
        
        /* CSS Lưới Sản Phẩm */
        .showcase-title {{ text-align: center; color: var(--primary); font-size: 24px; margin: 40px 0 20px; text-transform: uppercase; border-top: 2px dashed #eee; padding-top: 30px; }}
        .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 15px; }}
        .sp-card {{ border: 1px solid #eee; border-radius: 8px; padding: 10px; text-align: center; transition: transform 0.2s; }}
        .sp-card:hover {{ transform: translateY(-5px); box-shadow: 0 5px 15px rgba(0,0,0,0.1); }}
        .sp-card img {{ width: 100%; height: 180px; object-fit: contain; margin-bottom: 10px; }}
        .sp-name {{ font-size: 14px; height: 40px; overflow: hidden; margin-bottom: 10px; }}
        .sp-price {{ font-weight: bold; color: var(--primary); font-size: 18px; margin-bottom: 15px; }}
        .sp-btn {{ display: block; background: var(--primary); color: white; text-decoration: none; padding: 10px; border-radius: 5px; font-weight: bold; }}
        
        /* Zalo Button */
        .zalo-btn {{ position: fixed; bottom: 20px; right: 20px; background: #0068ff; color: white; width: 60px; height: 60px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 12px; font-weight: bold; text-decoration: none; box-shadow: 0 4px 10px rgba(0,0,0,0.3); animation: rung 1.5s infinite; z-index: 1000; text-align: center; line-height: 1.2;}}
        @keyframes rung {{ 0% {{transform: rotate(0deg);}} 10% {{transform: rotate(-15deg);}} 20% {{transform: rotate(15deg);}} 30% {{transform: rotate(-15deg);}} 40% {{transform: rotate(15deg);}} 50% {{transform: rotate(0deg);}} 100% {{transform: rotate(0deg);}} }}
    </style>
</head>
<body>
    <div class="header"><a href="../index.html">🏠 VPP TỊNH SHOP</a></div>
    
    <div class="container">
        <h1 style="font-size: 28px; text-align: center; margin-bottom: 30px;">{bai_viet['tieu_de']}</h1>
        
        <div class="article-wrapper" id="articleContent">
            {bai_viet['noi_dung_html']}
            <div class="fade-out" id="fadeCover">
                <button class="btn-readmore" onclick="showContent()">ĐỌC TIẾP NỘI DUNG 🔽</button>
            </div>
        </div>

        <h2 class="showcase-title">🔥 SẢN PHẨM KHUYÊN DÙNG 🔥</h2>
        <div class="grid">
            {html_sp if html_sp else "<p style='text-align:center; width:100%;'>Các sản phẩm đang được cập nhật...</p>"}
        </div>
    </div>
    
    <a href="https://zalo.me/{ZALO_NUMBER}" target="_blank" class="zalo-btn">Chat<br>Zalo</a>

    <script>
        function showContent() {{
            document.getElementById('articleContent').classList.add('expanded');
        }}
    </script>
</body>
</html>"""
    
    with open(os.path.join(THU_MUC_BAI_VIET, f"{slug}.html"), "w", encoding="utf-8") as f:
        f.write(html)

def tao_trang_chu(danh_sach_bai_viet):
    html_links = ""
    for bv in danh_sach_bai_viet:
        html_links += f"""
        <a href="bai-viet/{bv['slug']}.html" class="blog-card">
            <h3>{bv['tieu_de']}</h3>
            <p>Khám phá bí quyết và nhận ưu đãi sản phẩm ngay hôm nay! Đọc tiếp ➡️</p>
        </a>
        """

    html = f"""<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>VPP Tịnh | Kiến thức & Mua sắm thông minh</title>
    <style>
        body {{ font-family: sans-serif; background: #f5f5f5; margin: 0; padding: 0; }}
        /* Dòng chữ chạy (News Ticker) */
        .ticker-wrap {{ width: 100%; background-color: #333; padding: 8px 0; overflow: hidden; color: white; font-weight: bold; font-size: 14px; box-shadow: 0 2px 5px rgba(0,0,0,0.2);}}
        .ticker {{ display: inline-block; white-space: nowrap; padding-right: 100%; box-sizing: content-box; animation: ticker 25s linear infinite; }}
        @keyframes ticker {{ 0% {{ transform: translate3d(100%, 0, 0); }} 100% {{ transform: translate3d(-100%, 0, 0); }} }}
        
        .header-bg {{ background: #d0011b; color: white; text-align: center; padding: 40px 20px; margin-bottom: 30px; }}
        .header-bg h1 {{ margin: 0; font-size: 32px; text-transform: uppercase; }}
        .container {{ max-width: 900px; margin: 0 auto; padding: 0 20px; }}
        
        .blog-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; padding-bottom: 50px; }}
        .blog-card {{ background: white; padding: 20px; border-radius: 8px; text-decoration: none; color: #333; box-shadow: 0 2px 10px rgba(0,0,0,0.1); border-left: 5px solid #d0011b; transition: transform 0.2s; }}
        .blog-card:hover {{ transform: scale(1.02); }}
        .blog-card h3 {{ color: #d0011b; margin-top: 0; }}
        
        /* Zalo Button */
        .zalo-btn {{ position: fixed; bottom: 20px; right: 20px; background: #0068ff; color: white; width: 60px; height: 60px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 12px; font-weight: bold; text-decoration: none; box-shadow: 0 4px 10px rgba(0,0,0,0.3); animation: rung 1.5s infinite; z-index: 1000; text-align: center; line-height: 1.2;}}
        @keyframes rung {{ 0% {{transform: rotate(0deg);}} 10% {{transform: rotate(-15deg);}} 20% {{transform: rotate(15deg);}} 30% {{transform: rotate(-15deg);}} 40% {{transform: rotate(15deg);}} 50% {{transform: rotate(0deg);}} 100% {{transform: rotate(0deg);}} }}
    </style>
</head>
<body>
    <div class="ticker-wrap"><div class="ticker">
        🔥 CHÀO MỪNG ĐẾN VỚI VPP TỊNH - ĐỐI TÁC CUNG CẤP VĂN PHÒNG PHẨM TRỌN GÓI 🔥 | 🚚 FREESHIP CHO ĐƠN HÀNG TỪ 500K | 📞 MUA SỈ LIÊN HỆ ZALO: {ZALO_NUMBER} ĐỂ NHẬN BÁO GIÁ CHIẾT KHẤU CAO NHẤT!
    </div></div>
    
    <div class="header-bg">
        <h1>GÓC TƯ VẤN & SĂN DEAL VPP TỊNH</h1>
        <p>Kiến thức chuyên sâu - Mua sắm thông minh - Tiết kiệm tối đa</p>
    </div>
    
    <div class="container">
        <h2 style="text-align: center; margin-bottom: 30px; color: #333;">📚 BÀI VIẾT MỚI NHẤT</h2>
        <div class="blog-grid">
            {html_links if html_links else "<p>Đang cập nhật bài viết...</p>"}
        </div>
    </div>
    
    <a href="https://zalo.me/{ZALO_NUMBER}" target="_blank" class="zalo-btn">Chat<br>Zalo</a>
</body>
</html>"""
    with open(os.path.join(BASE_DIR, "index.html"), "w", encoding="utf-8") as f:
        f.write(html)

def chay_he_thong():
    print("🚀 ĐANG TẢI DỮ LIỆU TỪ GOOGLE SHEETS...")
    if "DÁN_LINK_CSV" in URL_CSV_SAN_PHAM or "DÁN_LINK_CSV" in URL_CSV_BAI_VIET:
        return print("❌ LỖI: Bạn chưa dán Link Google Sheet vào dòng 23 và 26 của file main.py!")

    os.makedirs(THU_MUC_BAI_VIET, exist_ok=True)
    
    # Lấy data
    data_san_pham = lay_data_tu_google_sheet(URL_CSV_SAN_PHAM)
    data_bai_viet = lay_data_tu_google_sheet(URL_CSV_BAI_VIET)
    
    if not data_san_pham or not data_bai_viet:
        return print("❌ Dữ liệu rỗng, vui lòng kiểm tra lại link Google Sheets.")

    # Đọc Cache Bài Viết (Tránh AI viết đi viết lại tốn thời gian)
    cache_ai = {}
    if os.path.exists(CACHE_BAI_VIET):
        with open(CACHE_BAI_VIET, "r", encoding="utf-8") as f:
            cache_ai = json.load(f)

    # Xử lý từng bài viết
    danh_sach_hoan_thien = []
    for bv in data_bai_viet:
        slug = bv.get('slug', '').strip()
        tieu_de = bv.get('tieu_de', '').strip()
        danh_muc_sp = bv.get('danh_muc_sp', '').strip()
        
        if not slug or not tieu_de: continue

        # Nếu bài viết chưa có trong cache -> Gọi AI viết
        if slug not in cache_ai:
            noi_dung = goi_ai_viet_bai_seo(tieu_de)
            cache_ai[slug] = noi_dung
            # Lưu lại cache ngay lập tức để lỡ đứt mạng không bị mất
            with open(CACHE_BAI_VIET, "w", encoding="utf-8") as f:
                json.dump(cache_ai, f, ensure_ascii=False, indent=2)
            time.sleep(2) # Nghỉ chút cho API đỡ quá tải

        bv['noi_dung_html'] = cache_ai[slug]
        
        # Lọc ra các sản phẩm thuộc danh mục của bài viết này
        sp_lien_quan = [p for p in data_san_pham if p.get('danh_muc', '').strip() == danh_muc_sp]
        
        # Tạo trang HTML cho bài viết này
        tao_trang_lai_bai_viet(bv, sp_lien_quan)
        danh_sach_hoan_thien.append(bv)

    print(f"✅ Đã tạo {len(danh_sach_hoan_thien)} Trang Quảng Cáo (Hybrid Page).")
    
    # Tạo trang chủ
    tao_trang_chu(danh_sach_hoan_thien)
    
    print("🎉 HOÀN TẤT! HỆ THỐNG VPP TỊNH 3.0 ĐÃ SẴN SÀNG!")

if __name__ == "__main__":
    chay_he_thong()