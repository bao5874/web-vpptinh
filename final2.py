import csv
import json
import os
import re
import base64 
import time
import webbrowser 

try:
    from google import genai
    from google.genai import types
except ImportError:
    print("❌ THIẾU THƯ VIỆN AI MỚI! Hãy mở Terminal gõ lệnh: pip install google-genai")
    exit()

# ==========================================
# CẤU HÌNH HỆ THỐNG & AI
# ==========================================
GA_ID = "G-XXXXXXXXXX"
LOGO_URL = "https://cdn-icons-png.flaticon.com/512/3225/3225194.png"
SHARE_IMAGE_URL = "https://vpptinh.com/static/images/tinh_radio_banner1.jpg"
FILE_CSV_LOCAL = r"F:\web-banhang\danh_sach_san_pham.csv" 
FILE_JSON = "products.json"
BASE_AFF_URL = "https://go.isclix.com/deep_link/v6/6906519896943843292/4751584435713464237?sub4=oneatweb&utm_source=shopee&utm_campaign=sansale&url_enc="

# 🔴 HỆ THỐNG ĐỌC API KEY TỪ FILE ẨN
GEMINI_API_KEY = ""
try:
    with open("api_key.txt", "r") as f:
        GEMINI_API_KEY = f.read().strip()
except FileNotFoundError:
    print("⚠️ CHƯA CÓ FILE api_key.txt! Vui lòng tạo file api_key.txt và dán mã API vào đó.")

# ==========================================
# CÁC HÀM XỬ LÝ LÕI
# ==========================================
def goi_ai_viet_mo_ta(ten_sp):
    if not GEMINI_API_KEY:
        return "Sản phẩm chính hãng chất lượng cao đang được ưu đãi. Bấm Xem Thêm để rinh ngay!"
    
    print(f"🤖 AI đang vắt óc sáng tạo mô tả cho: {ten_sp[:40]}...")
    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
        
        prompt = f"""Đóng vai một Copywriter bán hàng bậc thầy. Hãy viết đúng 1 đoạn văn (khoảng 50 - 70 chữ) cực kỳ cuốn hút để thuyết phục khách mua sản phẩm này: '{ten_sp}'.
        YÊU CẦU BẮT BUỘC:
        1. Đa dạng hóa: KHÔNG dùng lại các từ như "Khám phá ngay", "Sản phẩm chính hãng". 
        2. Bắt đầu bằng một câu 'Hook' (câu móc ngoặc) thật bắt tai.
        3. Văn phong tự nhiên như người đang tâm tình, tư vấn.
        4. Tuyệt đối KHÔNG sử dụng icon, KHÔNG gạch đầu dòng. Viết thành 1 đoạn văn liền mạch trôi chảy."""
        
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(temperature=0.9),
        )
        
        time.sleep(4)
        return response.text.replace('"', '').replace('\n', ' ').strip()
    except Exception as e:
        print(f"⚠️ AI lỗi nhẹ: {e}")
        return f"Bạn đang tìm kiếm {ten_sp}? Đây chính là lựa chọn hoàn hảo nhất với chất lượng vượt trội. Bấm Xem Thêm để rinh deal hời nhé!"

def tao_link_aff(url_goc):
    if not url_goc: return "#"
    if "shope.ee" in url_goc or "isclix.com" in url_goc or "c.lazada.vn" in url_goc: return url_goc
    try: return f"{BASE_AFF_URL}{base64.b64encode(url_goc.strip().encode('utf-8')).decode('utf-8')}"
    except: return url_goc

def tao_web_html(products):
    v = int(time.time())
    ga_script = f"""<script async src="https://www.googletagmanager.com/gtag/js?id={GA_ID}"></script><script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments);}}gtag('js',new Date());gtag('config','{GA_ID}');</script>""" if GA_ID != "G-XXXXXXXXXX" else ""

    html = f"""
    <!DOCTYPE html>
    <html lang="vi">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <meta name="referrer" content="no-referrer" />
        <link rel="canonical" href="https://vpptinh.com/" />
        <meta name="description" content="VPP Tịnh Shop chuyên săn deal giảm giá cực sốc đồ gia dụng, văn phòng phẩm." />
        <meta property="og:title" content="VPP Tịnh Shop - Săn Deal Giá Sốc" />
        <meta property="og:image" content="{SHARE_IMAGE_URL}" />
        <title>VPP Tịnh Shop | Săn Deal Đồ Gia Dụng & Văn Phòng Phẩm</title>
        <link rel="icon" href="{LOGO_URL}">
        {ga_script}
        <style>
            :root {{ --primary: #d0011b; --bg: #f5f5f5; --text-gray: #555; }}
            body {{ font-family: sans-serif; background: var(--bg); margin: 0; padding: 0 0 40px 0; }}
            .header-bg {{ width: 100%; max-width: 1200px; margin: 0 auto; aspect-ratio: 1360 / 350; background-image: url('static/images/tinh_radio_banner1.jpg'); background-size: cover; background-position: center; }}
            @media (max-width: 630px) {{ .header-bg {{ aspect-ratio: 1360 / 600; min-height: 180px; }} }}
            .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 10px; max-width: 1200px; margin: 20px auto; padding: 0 10px; }}
            .card {{ background: white; border-radius: 4px; overflow: hidden; display: flex; flex-direction: column; position: relative; box-shadow: 0 1px 2px rgba(0,0,0,0.1); transition: transform 0.2s; border: 1px solid #eee;}}
            .card:hover {{ transform: translateY(-2px); box-shadow: 0 4px 8px rgba(0,0,0,0.15); }}
            .discount-tag {{ position: absolute; top: 0; right: 0; background: #ffd424; color: #d0011b; padding: 4px 8px; font-weight: bold; font-size: 12px; z-index: 1; border-bottom-left-radius: 4px;}}
            .img-box {{ width: 100%; height: 190px; display: flex; align-items: center; justify-content: center; padding: 10px; box-sizing: border-box; background: white; cursor: pointer; }}
            .img-box img {{ max-width: 100%; max-height: 100%; object-fit: contain; transition: transform 0.3s; }}
            .img-box:hover img {{ transform: scale(1.05); }}
            .info {{ padding: 10px; display: flex; flex-direction: column; flex-grow: 1; justify-content: space-between; }}
            .title {{ font-size: 13px; color: #333; margin-bottom: 8px; height: 36px; line-height: 18px; overflow: hidden; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; }}
            .price-box {{ margin-bottom: 8px; }}
            .old-price {{ text-decoration: line-through; color: #999; font-size: 12px; margin-right: 5px; }}
            .new-price {{ color: var(--primary); font-weight: bold; font-size: 16px; }}
            .btn {{ background: var(--primary); color: white; text-decoration: none; padding: 8px; display: block; text-align: center; border-radius: 4px; font-weight: bold; font-size: 14px; cursor: pointer; border: none; width: 100%; box-sizing: border-box; }}
            .btn:hover {{ background: #b00117; }}
            .seo-content {{ max-width: 1200px; margin: 40px auto; padding: 20px; background: white; border-radius: 8px; color: #444; line-height: 1.6; font-size: 14px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }}
            
            .modal-overlay {{ display: none; position: fixed; z-index: 1000; left: 0; top: 0; width: 100%; height: 100%; background-color: rgba(0,0,0,0.6); backdrop-filter: blur(3px); align-items: center; justify-content: center; }}
            .modal-content {{ background-color: #fff; padding: 20px; border-radius: 8px; max-width: 500px; width: 90%; position: relative; animation: slideDown 0.3s ease-out; box-shadow: 0 10px 25px rgba(0,0,0,0.2); max-height: 90vh; overflow-y: auto; display: flex; flex-direction: column; }}
            @keyframes slideDown {{ from {{ transform: translateY(-30px); opacity: 0; }} to {{ transform: translateY(0); opacity: 1; }} }}
            .close-btn {{ position: absolute; top: 10px; right: 15px; color: #aaa; font-size: 28px; font-weight: bold; cursor: pointer; line-height: 1; z-index: 10; }}
            .close-btn:hover {{ color: #333; }}
            .modal-img-wrapper {{ width: 100%; height: 250px; text-align: center; margin-bottom: 15px; background: #f9f9f9; border-radius: 4px; padding: 10px; box-sizing: border-box; }}
            .modal-img-wrapper img {{ max-width: 100%; max-height: 100%; object-fit: contain; }}
            .modal-title {{ font-size: 16px; color: #333; margin-top: 0; margin-bottom: 10px; line-height: 1.4; }}
            .modal-price {{ font-size: 20px; color: var(--primary); font-weight: bold; margin-bottom: 15px; border-bottom: 1px dashed #ddd; padding-bottom: 10px; }}
            .modal-desc {{ font-size: 14px; color: #555; line-height: 1.6; margin-bottom: 25px; white-space: pre-line; flex-grow: 1; }}
            .modal-buttons {{ display: flex; gap: 10px; width: 100%; }}
            .modal-btn-buy {{ background: var(--primary); color: white; text-decoration: none; padding: 12px; text-align: center; border-radius: 4px; font-weight: bold; font-size: 15px; cursor: pointer; border: none; flex: 1; text-transform: uppercase; }}
            .modal-btn-buy:hover {{ background: #b00117; }}
            .modal-btn-back {{ background: #e0e0e0; color: #333; text-decoration: none; padding: 12px; text-align: center; border-radius: 4px; font-weight: bold; font-size: 15px; cursor: pointer; border: none; flex: 1; }}
            .modal-btn-back:hover {{ background: #ccc; }}
            @media (max-width: 400px) {{ .modal-buttons {{ flex-direction: column; }} }}
        </style>
    </head>
    <body>
        <div class="header-bg"><h1 style="display:none;">VPP Tịnh Shop</h1></div>
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
        
        safe_title = str(p['name']).replace('"', '&quot;').replace("'", "&#39;")
        safe_desc = str(p['mo_ta']).replace('"', '&quot;').replace("'", "&#39;")
        
        html += f"""
            <div class="card">
                {discount_html}
                <div class="img-box" onclick="openModal('{safe_title}', '{p['image']}', '{new_price_format}', '{safe_desc}', '{p['link']}')">
                    <img src="{p['image']}" alt="{safe_title}" loading="lazy" onerror="this.src='https://placehold.co/200x200?text=No+Image'">
                </div>
                <div class="info">
                    <div class="title" onclick="openModal('{safe_title}', '{p['image']}', '{new_price_format}', '{safe_desc}', '{p['link']}')" style="cursor:pointer;">{p['name']}</div>
                    <div class="price-box">{old_price_html}<span class="new-price">{new_price_format}</span></div>
                    <button class="btn" onclick="openModal('{safe_title}', '{p['image']}', '{new_price_format}', '{safe_desc}', '{p['link']}')">Xem Thêm</button>
                </div>
            </div>
        """
    
    html += """
        </div>
        
        <div class="seo-content">
            <h2>Về VPP Tịnh Shop - Săn deal giá rẻ mỗi ngày</h2>
            <p>Chào mừng bạn đến với <strong>VPP Tịnh Shop</strong>. Chúng tôi là nền tảng chuyên tổng hợp và cập nhật liên tục các deal giảm giá cực sốc, mã freeship và voucher khuyến mãi tốt nhất từ Shopee.</p>
        </div>

        <div id="productModal" class="modal-overlay">
            <div class="modal-content">
                <span class="close-btn" onclick="closeModal()">&times;</span>
                <div class="modal-img-wrapper"><img id="m-img" src="" alt="Product"></div>
                <h3 id="m-title" class="modal-title"></h3>
                <div id="m-price" class="modal-price"></div>
                <div id="m-desc" class="modal-desc"></div>
                <div class="modal-buttons">
                    <button class="modal-btn-back" onclick="closeModal()">Quay Lại Xem Tiếp</button>
                    <a id="m-link" href="#" class="modal-btn-buy" target="_blank" rel="nofollow">Mua Ngay</a>
                </div>
            </div>
        </div>

        <script>
            const modal = document.getElementById("productModal");
            function openModal(title, img, price, desc, link) {
                document.getElementById("m-title").innerText = title;
                document.getElementById("m-img").src = img;
                document.getElementById("m-price").innerText = price;
                document.getElementById("m-desc").innerText = desc;
                document.getElementById("m-link").href = link;
                modal.style.display = "flex"; document.body.style.overflow = "hidden";
            }
            function closeModal() {
                modal.style.display = "none"; document.body.style.overflow = "auto";
            }
            window.onclick = function(event) { if (event.target == modal) { closeModal(); } }
        </script>
    </body></html>
    """
    return html

def chay_he_thong():
    print(f"🚀 ĐANG KHỞI TẠO HỆ THỐNG TỪ FILE: {FILE_CSV_LOCAL}")
    try:
        if not os.path.exists(FILE_CSV_LOCAL):
            print(f"❌ LỖI: Không tìm thấy file CSV tại: {FILE_CSV_LOCAL}")
            return

        raw_data = []
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
                
                mo_ta = row_clean.get('mo_ta', '').strip()
                if not mo_ta or "Bạn đang tìm kiếm" in mo_ta or "Sản phẩm chính hãng" in mo_ta:
                    mo_ta = goi_ai_viet_mo_ta(name)
                    row_clean['mo_ta'] = mo_ta

                raw_data.append(row_clean)
                
                link_goc = row_clean.get('link', '#').strip()
                link_anh = row_clean.get('image', '').strip(' \'"[]')
                if not link_anh.startswith('http'):
                    ten_file_anh = link_anh.replace('\\', '/').split('/')[-1]
                    link_anh = f"static/images/{ten_file_anh}"
                
                clean_products.append({
                    "name": name.strip(),
                    "old_price": row_clean.get('old_price', '0').strip(),
                    "new_price": row_clean.get('new_price', '0').strip(),
                    "image": link_anh,
                    "link": tao_link_aff(link_goc),
                    "mo_ta": mo_ta
                })

        print("💾 Đang lưu mô tả AI vào lại file Excel...")
        with open(FILE_CSV_LOCAL, mode='w', encoding='utf-8-sig', newline='') as f:
            all_fields = list(field_map.values())
            if 'mo_ta' not in all_fields:
                all_fields.append('mo_ta')
                
            writer = csv.DictWriter(f, fieldnames=all_fields, delimiter=dau_ngan_cach)
            writer.writeheader()
            for r in raw_data:
                writer.writerow(r)

        print(f"✅ Đã xử lý thành công {len(clean_products)} sản phẩm.")
        
        with open(FILE_JSON, "w", encoding="utf-8") as f:
            json.dump(clean_products, f, ensure_ascii=False, indent=4)
        
        with open("index.html", "w", encoding="utf-8") as f:
            f.write(tao_web_html(clean_products))
        
        print("👉 Đang mở web trên máy tính để kiểm tra...")
        webbrowser.open("file://" + os.path.realpath("index.html"))
        
        print("\n⏳ Đang đẩy code lên kho chứa (Github)...")
        time.sleep(2)
        os.system("git add .")
        os.system('git commit -m "Fix AI Leaked Key & Use api_key.txt"')
        os.system("git push")
        print("✅ HOÀN TẤT! Chìa khóa AI đã được bảo mật an toàn tuyệt đối.")

    except Exception as e:
        print(f"❌ Có lỗi nghiêm trọng xảy ra: {e}")

if __name__ == "__main__":
    chay_he_thong()