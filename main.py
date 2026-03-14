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
    print("❌ THIẾU THƯ VIỆN AI! Hãy mở Terminal gõ lệnh: pip install google-genai")
    exit()

# ==========================================
# CẤU HÌNH HỆ THỐNG (BẠN ĐIỀN THÔNG TIN VÀO ĐÂY)
# ==========================================
# Link kho hàng của bạn (Đã điền sẵn)
URL_CSV_SAN_PHAM = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQzftzzjfyPE6MujJRirjKeXub0RmgpmAQNuTr9IjaLGe9BGukp4RnPisW7tZo3sDBBqiumtY3RWNbX/pub?gid=0&single=true&output=csv"

# BẠN HÃY THAY 2 CỤM "THAY_MA_CUA_BAN" THÀNH SỐ ID ACCESSTRADE CỦA BẠN NHÉ!
BASE_AFF_URL = "https://go.isclix.com/deep_link/v6/6906519896943843292/4751584435713464237?url_enc="

ZALO_NUMBER = "0931736266"

DANH_MUC_MAP = {
    "tho_cung": "Đồ Thờ Cúng", "dc_vs": "Dụng Cụ Vệ Sinh", 
    "vpp": "Văn Phòng Phẩm", "gia_dung": "Đồ Gia Dụng", 
    "me_be": "Mẹ & Bé", "khac": "Sản Phẩm Khác"
}

# ==========================================
# KHÔNG SỬA PHẦN DƯỚI NÀY NẾU KHÔNG RÀNH CODE
# ==========================================
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
    print(f"✍️ AI đang lấy '{ten_sp_dau_tien}' làm mồi câu để viết bài cho nhóm '{ten_danh_muc}'...")
    
    prompt = f"""Bạn là một Copywriter SEO chuyên nghiệp.
    Nhiệm vụ: Viết một bài bán hàng dài khoảng 600 - 800 chữ cho nhóm ngành hàng "{ten_danh_muc}".
    Chiến thuật bắt buộc: Lấy sản phẩm "{ten_sp_dau_tien}" làm "MỒI CÂU" để mở bài. Hãy khen ngợi sự tiện ích, thiết kế hoặc giá trị của sản phẩm này để thu hút người đọc. Sau đó dẫn dắt họ xem tiếp các sản phẩm khác cùng nhóm.
    
    BẮT BUỘC TRẢ VỀ CHÍNH XÁC ĐỊNH DẠNG JSON NHƯ SAU (Không thêm Markdown block ```json):
    {{
        "tieu_de": "Tiêu đề giật tít, chứa tên sản phẩm mồi và lợi ích (khoảng 10-15 chữ)",
        "noi_dung_html": "Nội dung bài định dạng HTML (chỉ dùng thẻ <h2>, <h3>, <p>, <ul>, <li>, <strong>). Không chứa thẻ <html> body."
    }}
    """
    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
        response = client.models.generate_content(
            model='gemini-2.5-flash', contents=prompt,
            config=types.GenerateContentConfig(temperature=0.8, response_mime_type="application/json")
        )
        data = json.loads(response.text)
        return data
    except Exception as e:
        print(f"Lỗi AI: {e}")
        return {"tieu_de": f"Top sản phẩm {ten_danh_muc} đáng mua", "noi_dung_html": f"<p>Giới thiệu siêu phẩm {ten_sp_dau_tien} và nhiều mặt hàng khác.</p>"}

def tao_trang_lai_bai_viet(slug, tieu_de, noi_dung_html, san_pham_lien_quan):
    html_sp = ""
    
    # Bóc tách sản phẩm "Mồi câu" (Sản phẩm đầu tiên) để lấy ảnh chèn lên đầu bài
    sp_moi = san_pham_lien_quan[0] if san_pham_lien_quan else {}
    img_moi = sp_moi.get('image', '')
    ten_moi = sp_moi.get('name', 'Sản phẩm')
    link_aff_moi = tao_link_aff(sp_moi.get('link', ''))
    
    # Quét toàn bộ sản phẩm để làm Lưới sản phẩm bên dưới
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
    <title>{tieu_de} | VPP Tịnh</title>
    <style>
        :root {{ --primary: #d0011b; --bg: #f5f5f5; }}
        body {{ font-family: sans-serif; background: var(--bg); margin: 0; padding: 0; color: #333; }}
        
        .header {{ background: #fff; color: var(--primary); padding: 0; position: sticky; top: 0; z-index: 100; border-bottom: 1px solid #eee; }}
        .nav-bar {{ max-width: 1200px; margin: 0 auto; display: flex; align-items: center; justify-content: space-between; padding: 10px 25px; }}
        .btn-home {{ display: inline-flex; align-items: center; justify-content: center; background: #fff; color: var(--primary); border: 2px solid var(--primary); padding: 10px 20px; border-radius: 6px; text-decoration: none; font-weight: bold; font-size: 15px; transition: all 0.3s; }}
        .btn-home:hover {{ background: var(--primary); color: #fff; }}
        .shop-title {{ color: var(--primary); text-decoration: none; font-weight: bold; font-size: 18px; }}
        
        .container {{ max-width: 800px; margin: 20px auto; background: white; padding: 25px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); text-align: center; }}
        
        /* CỘT BÀI VIẾT DỌC CHUYÊN NGHIỆP */
        .article-column {{ max-width: 650px; margin: 0 auto; text-align: left; }}
        
        /* ẢNH SẢN PHẨM MỒI CHÈN VÀO BÀI VIẾT */
        .featured-img-box {{ text-align: center; margin: 20px 0 30px 0; background: #fff; padding: 10px; border-radius: 8px; border: 1px solid #eee; }}
        .featured-img-box img {{ max-width: 100%; max-height: 350px; object-fit: contain; border-radius: 4px; transition: transform 0.3s; }}
        .featured-img-box img:hover {{ transform: scale(1.02); }}
        .img-caption {{ font-size: 14px; color: #777; font-style: italic; margin-top: 10px; }}
        
        /* HIỆU ỨNG ĐỌC TIẾP */
        .article-wrapper {{ position: relative; max-height: 500px; overflow: hidden; transition: max-height 0.5s ease; line-height: 1.6; font-size: 16px; }}
        .article-wrapper.expanded {{ max-height: 10000px; }}
        .article-wrapper h2 {{ color: var(--primary); margin-top: 25px; font-size: 22px; }}
        .fade-out {{ position: absolute; bottom: 0; left: 0; width: 100%; height: 150px; background: linear-gradient(transparent, white); display: flex; align-items: flex-end; justify-content: center; padding-bottom: 20px; }}
        .expanded .fade-out {{ display: none; }}
        .btn-readmore {{ background: white; color: var(--primary); border: 2px solid var(--primary); padding: 12px 30px; border-radius: 25px; cursor: pointer; font-weight: bold; font-size: 16px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); transition: background 0.3s;}}
        .btn-readmore:hover {{ background: var(--primary); color: white; }}
        
        /* LƯỚI SẢN PHẨM DƯỚI CÙNG */
        .showcase-title {{ text-align: center; color: var(--primary); font-size: 24px; margin: 40px 0 20px; text-transform: uppercase; border-top: 2px dashed #eee; padding-top: 30px; }}
        .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 15px; text-align: center; }}
        .sp-card {{ border: 1px solid #eee; border-radius: 8px; padding: 10px; text-align: center; transition: transform 0.2s; background: white;}}
        .sp-card:hover {{ transform: translateY(-5px); box-shadow: 0 5px 15px rgba(0,0,0,0.1); }}
        .sp-card img {{ width: 100%; height: 180px; object-fit: contain; margin-bottom: 10px; }}
        .sp-name {{ font-size: 14px; height: 40px; overflow: hidden; margin-bottom: 10px; }}
        .sp-price {{ font-weight: bold; color: var(--primary); font-size: 18px; margin-bottom: 15px; }}
        .sp-btn {{ display: block; background: var(--primary); color: white; text-decoration: none; padding: 10px; border-radius: 5px; font-weight: bold; }}
        
        /* NÚT ZALO */
        .zalo-btn {{ position: fixed; bottom: 20px; right: 20px; background: #0068ff; color: white; width: 60px; height: 60px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 12px; font-weight: bold; text-decoration: none; box-shadow: 0 4px 10px rgba(0,0,0,0.3); animation: rung 1.5s infinite; z-index: 1000; text-align: center; line-height: 1.2;}}
        @keyframes rung {{ 0% {{transform: rotate(0deg);}} 10% {{transform: rotate(-15deg);}} 20% {{transform: rotate(15deg);}} 30% {{transform: rotate(-15deg);}} 40% {{transform: rotate(15deg);}} 50% {{transform: rotate(0deg);}} 100% {{transform: rotate(0deg);}} }}
    </style>
</head>
<body>
    <div class="header">
        <div class="nav-bar">
            <a href="../index.html" class="btn-home">🔙 Quay lại Trang Chủ</a>
            <a href="../index.html" class="shop-title">🏠 VPP TỊNH SHOP</a>
        </div>
    </div>
    
    <div class="container">
        <h1 style="font-size: 28px; text-align: center; margin-bottom: 20px; color: #222;">{tieu_de}</h1>
        
        <div class="article-column">
            <div class="featured-img-box">
                <a href="{link_aff_moi}" target="_blank" rel="nofollow">
                    <img src="{img_moi}" alt="{ten_moi}">
                </a>
                <div class="img-caption">Sản phẩm đánh giá nổi bật: {ten_moi}</div>
            </div>

            <div class="article-wrapper" id="articleContent">
                {noi_dung_html}
                <div class="fade-out" id="fadeCover">
                    <button class="btn-readmore" onclick="showContent()">ĐỌC TIẾP NỘI DUNG 🔽</button>
                </div>
            </div>
        </div>

        <h2 class="showcase-title">🔥 CÁC SẢN PHẨM KHUYÊN DÙNG KHÁC 🔥</h2>
        <div class="grid">
            {html_sp}
        </div>
    </div>
    
    <a href="[https://zalo.me/](https://zalo.me/){ZALO_NUMBER}" target="_blank" class="zalo-btn">Chat<br>Zalo</a>

    <script>function showContent() {{ document.getElementById('articleContent').classList.add('expanded'); }}</script>
</body>
</html>"""
    with open(os.path.join(THU_MUC_BAI_VIET, f"{slug}.html"), "w", encoding="utf-8") as f:
        f.write(html)

def tao_trang_chu(danh_sach_hub):
    html_links = ""
    for hub in danh_sach_hub:
        html_links += f"""
        <a href="bai-viet/{hub['slug']}.html" class="blog-card">
            <h3>{hub['tieu_de']}</h3>
            <p>Nhấn vào để khám phá đánh giá chi tiết và nhận ưu đãi sản phẩm {hub['ten_danh_muc']} ngay hôm nay! ➡️</p>
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
        .header-bg {{ width: 100%; max-width: 1200px; margin: 0 auto; aspect-ratio: 1360/350; background-image: url('static/images/tinh_radio_banner1.jpg'); background-size: cover; background-position: center; }}
        .ticker-wrap {{ width: 100%; max-width: 1200px; margin: 0 auto 30px auto; background-color: #d0011b; padding: 12px 0; overflow: hidden; color: white; font-weight: bold; font-size: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
        .ticker {{ display: inline-block; white-space: nowrap; padding-right: 100%; box-sizing: content-box; animation: ticker 25s linear infinite; }}
        @keyframes ticker {{ 0% {{ transform: translate3d(100%, 0, 0); }} 100% {{ transform: translate3d(-100%, 0, 0); }} }}
        .container {{ max-width: 900px; margin: 0 auto; padding: 0 20px; }}
        .section-title {{ text-align: center; margin-bottom: 30px; color: #333; text-transform: uppercase; border-bottom: 2px solid #d0011b; display: inline-block; padding-bottom: 10px; font-size: 24px; }}
        .blog-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; padding-bottom: 50px; text-align: left; }}
        .blog-card {{ background: white; padding: 20px; border-radius: 8px; text-decoration: none; color: #333; box-shadow: 0 2px 10px rgba(0,0,0,0.1); border-left: 5px solid #d0011b; transition: transform 0.2s; }}
        .blog-card:hover {{ transform: translateY(-5px); box-shadow: 0 5px 15px rgba(0,0,0,0.2); }}
        .blog-card h3 {{ color: #d0011b; margin-top: 0; line-height: 1.4; }}
        .zalo-btn {{ position: fixed; bottom: 20px; right: 20px; background: #0068ff; color: white; width: 60px; height: 60px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 12px; font-weight: bold; text-decoration: none; box-shadow: 0 4px 10px rgba(0,0,0,0.3); animation: rung 1.5s infinite; z-index: 1000; text-align: center; line-height: 1.2;}}
        @keyframes rung {{ 0% {{transform: rotate(0deg);}} 10% {{transform: rotate(-15deg);}} 20% {{transform: rotate(15deg);}} 30% {{transform: rotate(-15deg);}} 40% {{transform: rotate(15deg);}} 50% {{transform: rotate(0deg);}} 100% {{transform: rotate(0deg);}} }}
    </style>
</head>
<body>
    <div class="header-bg"></div>
    <div class="ticker-wrap"><div class="ticker">
        🔥 CHÀO MỪNG ĐẾN VỚI VPP TỊNH - ĐỐI TÁC CUNG CẤP VĂN PHÒNG PHẨM TRỌN GÓI 🔥 | 🚚 FREESHIP CHO ĐƠN HÀNG TỪ 500K | 📞 MUA SỈ LIÊN HỆ ZALO: {ZALO_NUMBER} ĐỂ NHẬN BÁO GIÁ CHIẾT KHẤU CAO NHẤT!
    </div></div>
    <div class="container" style="text-align: center;">
        <h2 class="section-title">📚 CHUYÊN MỤC TƯ VẤN & SĂN DEAL</h2>
        <div class="blog-grid">
            {html_links if html_links else "<p style='text-align:center; width:100%;'>Đang cập nhật bài viết...</p>"}
        </div>
    </div>
    <a href="[https://zalo.me/](https://zalo.me/){ZALO_NUMBER}" target="_blank" class="zalo-btn">Chat<br>Zalo</a>
</body>
</html>"""
    with open(os.path.join(BASE_DIR, "index.html"), "w", encoding="utf-8") as f:
        f.write(html)

def chay_he_thong():
    print("🚀 ĐANG TẢI DỮ LIỆU TỪ GOOGLE SHEETS...")
    data_san_pham = lay_data_tu_google_sheet(URL_CSV_SAN_PHAM)
    
    if not data_san_pham:
        return print("❌ Dữ liệu rỗng!")

    os.makedirs(THU_MUC_BAI_VIET, exist_ok=True)
    
    gom_nhom = {}
    for p in data_san_pham:
        dm = p.get('danh_muc', 'khac').strip()
        if not dm: dm = 'khac'
        if dm not in gom_nhom: gom_nhom[dm] = []
        gom_nhom[dm].append(p)

    cache_ai = {}
    if os.path.exists(CACHE_BAI_VIET):
        with open(CACHE_BAI_VIET, "r", encoding="utf-8") as f:
            cache_ai = json.load(f)

    danh_sach_hub = []

    for dm, ds_sp in gom_nhom.items():
        if not ds_sp: continue
        
        sp_dau_tien = ds_sp[0].get('name', 'Sản phẩm mới')
        ten_dm = DANH_MUC_MAP.get(dm, dm.title())
        slug = f"chuyen-muc-{dm}"

        if dm not in cache_ai:
            ket_qua_ai = goi_ai_tu_dong_viet_bai(ten_dm, sp_dau_tien)
            cache_ai[dm] = ket_qua_ai
            
            with open(CACHE_BAI_VIET, "w", encoding="utf-8") as f:
                json.dump(cache_ai, f, ensure_ascii=False, indent=2)
            time.sleep(2)

        tieu_de = cache_ai[dm].get('tieu_de', f'Top sản phẩm {ten_dm}')
        noi_dung = cache_ai[dm].get('noi_dung_html', '')

        tao_trang_lai_bai_viet(slug, tieu_de, noi_dung, ds_sp)
        danh_sach_hub.append({"slug": slug, "tieu_de": tieu_de, "ten_danh_muc": ten_dm})

    print(f"✅ Đã tạo {len(danh_sach_hub)} Trang Chuyên Mục (Hybrid Page).")
    tao_trang_chu(danh_sach_hub)
    print("🎉 HOÀN TẤT TỰ ĐỘNG HÓA 100%!")

if __name__ == "__main__":
    chay_he_thong()