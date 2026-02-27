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
# CẤU HÌNH HỆ THỐNG
# ==========================================
GA_ID = "G-XXXXXXXXXX"
LOGO_URL = "https://cdn-icons-png.flaticon.com/512/3225/3225194.png"
SHARE_IMAGE_URL = "https://vpptinh.com/static/images/tinh_radio_banner1.jpg"
FILE_CSV_LOCAL = r"F:\web-banhang\danh_sach_san_pham.csv" 
FILE_JSON = "products.json"
BASE_AFF_URL = "https://go.isclix.com/deep_link/v6/6906519896943843292/4751584435713464237?sub4=oneatweb&utm_source=shopee&utm_campaign=sansale&url_enc="

DANH_MUC_MAP = {
    "tho_cung": "Đồ Thờ Cúng",
    "dc_vs": "Dụng Cụ Vệ Sinh",
    "vpp": "Văn Phòng Phẩm",
    "gia_dung": "Đồ Gia Dụng",
    "me_be": "Mẹ & Bé",
    "khac": "Sản Phẩm Khác"
}

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
def tao_link_aff(url_goc):
    if not url_goc: return "#"
    if "shope.ee" in url_goc or "isclix.com" in url_goc or "c.lazada.vn" in url_goc: return url_goc
    try: return f"{BASE_AFF_URL}{base64.b64encode(url_goc.strip().encode('utf-8')).decode('utf-8')}"
    except: return url_goc

def goi_ai_viet_mo_ta_hang_loat(danh_sach_sp_thieu):
    """
    Tuyệt chiêu 'Gộp Đơn': Gửi 1 lần nhiều sản phẩm cho AI để tránh lỗi Quota 429
    Trả về một Dictionary map từ ID sản phẩm -> Mô tả AI
    """
    if not GEMINI_API_KEY:
        print("⚠️ Không có API Key, dùng câu dự phòng.")
        return {}

    print(f"📦 Đang đóng gói {len(danh_sach_sp_thieu)} sản phẩm gửi cho AI xử lý 1 lần duy nhất...")
    
    # Chuẩn bị danh sách dạng Text để gửi AI
    sp_text = ""
    for sp in danh_sach_sp_thieu:
        ten_dm = DANH_MUC_MAP.get(sp['danh_muc'], "Sản phẩm")
        sp_text += f"- ID: {sp['id']} | Tên: {sp['name']} | Thuộc nhóm: {ten_dm}\n"

    prompt = f"""Đóng vai một Copywriter bán hàng bậc thầy. Dưới đây là danh sách các sản phẩm cần viết mô tả (khoảng 80 - 100 chữ mỗi sản phẩm).
    
    Quy tắc viết bắt buộc:
    1. Đa dạng hóa: Vì có nhiều sản phẩm, hãy luân phiên các phong cách: Kể chuyện cảm xúc, Phân tích chuyên gia, Gợi mở nỗi đau, và Tạo sự khan hiếm (FOMO).
    2. Mỗi mô tả bắt đầu bằng một câu 'Hook' bắt tai. KHÔNG dùng icon, KHÔNG gạch đầu dòng. Viết thành 1 đoạn văn liền mạch trôi chảy.

    ĐÂY LÀ ĐIỀU QUAN TRỌNG NHẤT: Bạn BẮT BUỘC phải trả về kết quả dưới dạng JSON hợp lệ, với cấu trúc như sau:
    {{
        "results": [
            {{"id": "id_cua_san_pham_1", "mo_ta": "nội dung mô tả 1..."}},
            {{"id": "id_cua_san_pham_2", "mo_ta": "nội dung mô tả 2..."}}
        ]
    }}

    Danh sách sản phẩm:
    {sp_text}
    """

    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
        # Ép AI phải trả về định dạng JSON
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.8,
                response_mime_type="application/json" 
            ),
        )
        
        # Đọc dữ liệu JSON AI trả về
        data = json.loads(response.text)
        ket_qua = {}
        if "results" in data:
            for item in data["results"]:
                ket_qua[str(item["id"])] = str(item["mo_ta"]).strip()
        
        print("✅ AI đã xử lý xong toàn bộ đơn hàng sỉ!")
        return ket_qua

    except Exception as e:
        print(f"⚠️ Quá trình Gộp Đơn AI gặp lỗi: {e}")
        return {}

def tao_web_html(products):
    v = int(time.time())
    ga_script = f"""<script async src="https://www.googletagmanager.com/gtag/js?id={GA_ID}"></script><script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments);}}gtag('js',new Date());gtag('config','{GA_ID}');</script>""" if GA_ID != "G-XXXXXXXXXX" else ""

    unique_cats = []
    for p in products:
        c = p.get('danh_muc', 'khac')
        if c not in unique_cats: unique_cats.append(c)
    
    menu_html = '<div class="category-menu">'
    menu_html += '<button class="cat-btn active" onclick="filterCategory(\'all\', this)">Tất Cả</button>'
    for cat in unique_cats:
        display_name = DANH_MUC_MAP.get(cat, cat.replace("_", " ").title())
        menu_html += f'<button class="cat-btn" onclick="filterCategory(\'{cat}\', this)">{display_name}</button>'
    menu_html += '</div>'

    schema_list = []
    for p in products:
        try:
            moi = float(re.sub(r'[^\d]', '', str(p['new_price']))) if re.sub(r'[^\d]', '', str(p['new_price'])) else 0
        except: moi = 0
        
        img_url = p['image'] if p['image'].startswith('http') else f"https://vpptinh.com/{p['image']}"
        schema_list.append({
            "@context": "https://schema.org/",
            "@type": "Product",
            "name": p['name'],
            "image": img_url,
            "description": p['mo_ta'],
            "offers": {
                "@type": "Offer",
                "url": p['link'],
                "priceCurrency": "VND",
                "price": moi,
                "availability": "https://schema.org/InStock"
            }
        })
    json_ld_script = f'<script type="application/ld+json">\n{json.dumps(schema_list, ensure_ascii=False, indent=2)}\n</script>'

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
        {json_ld_script}
        <style>
            :root {{ --primary: #d0011b; --bg: #f5f5f5; --text-gray: #555; }}
            body {{ font-family: sans-serif; background: var(--bg); margin: 0; padding: 0 0 40px 0; }}
            .header-bg {{ width: 100%; max-width: 1200px; margin: 0 auto; aspect-ratio: 1360 / 350; background-image: url('static/images/tinh_radio_banner1.jpg'); background-size: cover; background-position: center; margin-bottom: 20px;}}
            @media (max-width: 630px) {{ .header-bg {{ aspect-ratio: 1360 / 600; min-height: 180px; }} }}
            .category-menu {{ display: flex; justify-content: center; gap: 10px; margin: 0 auto 20px; max-width: 1200px; padding: 0 10px; flex-wrap: wrap; }}
            .cat-btn {{ background: white; color: #555; border: 1px solid #ddd; padding: 8px 20px; border-radius: 20px; cursor: pointer; font-weight: bold; font-size: 14px; transition: all 0.3s; white-space: nowrap; }}
            .cat-btn:hover {{ border-color: var(--primary); color: var(--primary); }}
            .cat-btn.active {{ background: var(--primary); color: white; border-color: var(--primary); box-shadow: 0 4px 6px rgba(208,1,27,0.2); }}
            .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 10px; max-width: 1200px; margin: 0 auto 20px; padding: 0 10px; }}
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
        {menu_html}
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
            <div class="card" data-category="{p.get('danh_muc', 'khac')}">
                {discount_html}
                <div class="img-box" onclick="openModal('{safe_title}', '{p['image']}', '{new_price_format}', '{safe_desc}', '{p['link']}')">
                    <img src="{p['image']}" alt="{safe_title} giá rẻ" loading="lazy" onerror="this.src='https://placehold.co/200x200?text=No+Image'">
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
            <p>Chào mừng bạn đến với <strong>VPP Tịnh Shop</strong>. Chúng tôi là nền tảng chuyên tổng hợp và cập nhật liên tục các deal giảm giá cực sốc, mã freeship và voucher khuyến mãi tốt nhất từ Shopee. Mọi sản phẩm đều được chọn lọc kỹ lưỡng, đảm bảo uy tín và chất lượng.</p>
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
            function filterCategory(cat, btn) {
                document.querySelectorAll('.cat-btn').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                document.querySelectorAll('.card').forEach(card => {
                    if (cat === 'all' || card.getAttribute('data-category') === cat) {
                        card.style.display = 'flex';
                    } else {
                        card.style.display = 'none';
                    }
                });
            }
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
        danh_sach_sp_thieu = [] # Danh sách lưu các SP cần viết mô tả
        
        # 1. ĐỌC EXCEL VÀ LỌC CÁC SẢN PHẨM CẦN VIẾT BÀI
        with open(FILE_CSV_LOCAL, mode='r', encoding='utf-8-sig') as f:
            first_line = f.readline()
            f.seek(0)
            dau_ngan_cach = ';' if ';' in first_line else ','
            
            reader = csv.DictReader(f, delimiter=dau_ngan_cach)
            field_map = {name: name.strip() for name in reader.fieldnames if name}
            
            for idx, row in enumerate(reader):
                row_clean = {field_map[k]: v for k, v in row.items() if k in field_map}
                name = row_clean.get('name')
                if not name: continue
                
                # Cấp ID tạm thời cho mỗi sản phẩm để lúc AI trả về biết của ai
                row_clean['_id'] = str(idx) 

                danh_muc = row_clean.get('danh_muc', '').strip()
                if not danh_muc: danh_muc = "khac"
                row_clean['danh_muc'] = danh_muc

                mo_ta = row_clean.get('mo_ta', '').strip()
                cau_du_phong = ["Bạn đang tìm kiếm", "Sản phẩm chính hãng", "Deal hời", "Đừng bỏ lỡ"]
                
                # Nếu trống hoặc có chứa văn mẫu -> Cho vào danh sách gửi sỉ
                if not mo_ta or any(cau in mo_ta for cau in cau_du_phong):
                    danh_sach_sp_thieu.append({
                        "id": str(idx),
                        "name": name,
                        "danh_muc": danh_muc
                    })

                raw_data.append(row_clean)

        # 2. GỌI AI XỬ LÝ SỈ (GỘP ĐƠN)
        ket_qua_ai = {}
        if danh_sach_sp_thieu:
            # Nếu có nhiều hơn 15 sản phẩm, ta chia mẻ ra gọi (để AI không bị ngợp)
            # Ở đây bạn có 18 SP, chia mỗi mẻ 10 SP thì chỉ mất đúng 2 lượt gọi API, siêu tốc!
            chunk_size = 10 
            for i in range(0, len(danh_sach_sp_thieu), chunk_size):
                batch = danh_sach_sp_thieu[i : i+chunk_size]
                batch_result = goi_ai_viet_mo_ta_hang_loat(batch)
                ket_qua_ai.update(batch_result)
                if i + chunk_size < len(danh_sach_sp_thieu):
                    time.sleep(3) # Nghỉ nhẹ giữa các mẻ

        # 3. LẮP RÁP KẾT QUẢ VÀO DANH SÁCH CHÍNH
        clean_products = []
        for r in raw_data:
            sp_id = r['_id']
            # Cập nhật mô tả mới nếu AI có viết
            if sp_id in ket_qua_ai:
                r['mo_ta'] = ket_qua_ai[sp_id]
            
            # Nếu AI bị lỗi, dùng tạm câu này để web không bị chết
            if not r.get('mo_ta'):
                r['mo_ta'] = f"Đừng bỏ lỡ {r['name']} với mức giá siêu ưu đãi hôm nay. Bấm Xem Thêm để rinh deal hời nhé!"
            
            link_goc = r.get('link', '#').strip()
            link_anh = r.get('image', '').strip(' \'"[]')
            if not link_anh.startswith('http'):
                ten_file_anh = link_anh.replace('\\', '/').split('/')[-1]
                link_anh = f"static/images/{ten_file_anh}"
            
            clean_products.append({
                "name": r['name'].strip(),
                "old_price": r.get('old_price', '0').strip(),
                "new_price": r.get('new_price', '0').strip(),
                "image": link_anh,
                "link": tao_link_aff(link_goc),
                "mo_ta": r['mo_ta'],
                "danh_muc": r['danh_muc']
            })
            # Xóa ID tạm đi trước khi lưu Excel
            del r['_id']

        # 4. LƯU EXCEL VÀ ĐẨY LÊN MẠNG
        print("💾 Đang lưu thông tin vào lại file Excel...")
        with open(FILE_CSV_LOCAL, mode='w', encoding='utf-8-sig', newline='') as f:
            all_fields = list(field_map.values())
            if 'mo_ta' not in all_fields: all_fields.append('mo_ta')
            if 'danh_muc' not in all_fields: all_fields.append('danh_muc')
                
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
        os.system('git commit -m "Chien thuat Gop Don AI + SEO Schema"')
        os.system("git push")
        print("✅ HOÀN TẤT! Siêu hệ thống đã sẵn sàng chinh phục khách hàng.")

    except Exception as e:
        print(f"❌ Có lỗi nghiêm trọng xảy ra: {e}")

if __name__ == "__main__":
    chay_he_thong()