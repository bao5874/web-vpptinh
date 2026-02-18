import requests
import csv
import json
import os
import re
import base64 
import time
import webbrowser 

# --- CẤU HÌNH HỆ THỐNG VPP TỊNH ---
GA_ID = "G-XXXXXXXXXX"  # Thay mã GA của bạn vào đây
LOGO_URL = "https://cdn-icons-png.flaticon.com/512/2554/2554037.png" # Icon hoa sen
LINK_CSV = "http://datafeed.accesstrade.me/shopee.vn.csv"
BASE_AFF_URL = "https://go.isclix.com/deep_link/v6/6906519896943843292/4751584435713464237?sub4=vpptinh&utm_source=shopee&url_enc="

# 1. TỪ KHÓA MỤC TIÊU (CHỈ LẤY SẢN PHẨM CHỨA TỪ NÀY)
BUDDHIST_KEYWORDS = [
    "phật", "bồ tát", "quan âm", "di đà", "thích ca", 
    "trầm hương", "lư xông", "đèn thờ", "bàn thờ", "tượng", 
    "chép kinh", "sổ tay", "bút lông", "thư pháp", # Nhóm VPP
    "pháp phục", "áo lam", "tràng hạt", "chuỗi hạt", "vòng tay gỗ",
    "thiền", "yoga", "chuông gió", "mõ", "khánh", "đài niệm"
]

# 2. TỪ KHÓA LOẠI TRỪ (CHẶN RÁC TUYỆT ĐỐI)
JUNK_BLACKLIST = [
    "đồ lót", "gợi cảm", "hở hang", "sexy", "bao cao su", 
    "thịt", "cá", "mắm", "điện thoại", "laptop", "tai nghe", 
    "ốp lưng", "cường lực", "vệ sinh", "tẩy rửa"
]

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

# 3. PHÂN LOẠI MỚI THEO CHỦ ĐỀ PHẬT GIÁO
def phan_loai_danh_muc(ten_san_pham):
    ten = ten_san_pham.lower()
    
    # Nhóm 1: Không gian thờ tự
    if any(k in ten for k in ['đèn', 'tượng', 'bàn thờ', 'lư', 'xông', 'hoa sen', 'tháp']): 
        return 'khong-gian-tho'
    
    # Nhóm 2: Pháp phục & Trang sức
    if any(k in ten for k in ['áo', 'quần', 'lam', 'tràng', 'chuỗi', 'vòng', 'túi']): 
        return 'phap-phuc'
    
    # Nhóm 3: Văn phòng phẩm Tịnh (Sổ, bút, kinh)
    if any(k in ten for k in ['sổ', 'vở', 'bút', 'giấy', 'kinh', 'sách', 'tranh', 'thư pháp']): 
        return 'vpp-tinh'
    
    # Nhóm 4: Mùi hương & Thiền
    if any(k in ten for k in ['trầm', 'nhang', 'nụ', 'bột', 'tinh dầu', 'đài', 'loa']): 
        return 'huong-thien'
        
    return 'khac'

def tao_web_html(products):
    ga_script = ""
    if GA_ID != "G-XXXXXXXXXX":
        ga_script = f"""<script async src="https://www.googletagmanager.com/gtag/js?id={GA_ID}"></script><script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments);}}gtag('js',new Date());gtag('config','{GA_ID}');</script>"""

    html = f"""
    <!DOCTYPE html>
    <html lang="vi">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>VPP Tịnh - Vật Phẩm Phật Giáo & Không Gian Thiền</title>
        <link rel="icon" href="{LOGO_URL}">
        {ga_script}
        <link href="https://fonts.googleapis.com/css2?family=Merriweather:wght@300;700&display=swap" rel="stylesheet">
        <style>
            :root {{ 
                --primary: #8d6e63; /* Màu Nâu đất */
                --accent: #fbc02d; /* Màu Vàng kim */
                --bg: #fdfbf7; /* Màu kem giấy gió */
                --text: #4e342e;
            }}
            body {{ font-family: 'Merriweather', serif; background: var(--bg); color: var(--text); margin: 0; padding: 20px; }}
            
            /* Header phong cách Tịnh */
            .header {{ 
                text-align: center; padding: 40px 20px; 
                background: url('https://i.pinimg.com/originals/82/10/ec/8210ec997b69c27762699318d104618e.jpg'); 
                background-size: cover; background-position: center;
                border-radius: 8px; margin-bottom: 30px; color: white; text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            }}
            .header h1 {{ margin: 0; font-size: 2.5rem; letter-spacing: 2px; }}
            .header p {{ font-style: italic; opacity: 0.9; margin-top: 10px; }}

            /* Menu nút bấm */
            .category-menu {{ display: flex; justify-content: center; flex-wrap: wrap; gap: 12px; margin-bottom: 30px; position: sticky; top: 10px; z-index: 99; }}
            .cat-btn {{ 
                padding: 10px 20px; border: 1px solid var(--primary); background: white; 
                color: var(--primary); cursor: pointer; border-radius: 25px; 
                font-family: 'Merriweather', serif; font-size: 14px; transition: 0.3s;
            }}
            .cat-btn:hover, .cat-btn.active {{ background: var(--primary); color: white; box-shadow: 0 4px 10px rgba(141, 110, 99, 0.4); }}

            /* Lưới sản phẩm */
            .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(190px, 1fr)); gap: 15px; max-width: 1200px; margin: 0 auto; }}
            .card {{ 
                background: white; border-radius: 8px; overflow: hidden; 
                box-shadow: 0 2px 5px rgba(0,0,0,0.05); transition: 0.3s; 
                border: 1px solid #eee;
            }}
            .card:hover {{ transform: translateY(-3px); box-shadow: 0 5px 15px rgba(0,0,0,0.1); border-color: var(--accent); }}
            .card.hide {{ display: none; }}
            
            .img-box {{ width: 100%; height: 200px; padding: 15px; box-sizing: border-box; display: flex; align-items: center; justify-content: center; }}
            .img-box img {{ max-width: 100%; max-height: 100%; object-fit: contain; mix-blend-mode: multiply; }}
            
            .info {{ padding: 15px; text-align: center; }}
            .title {{ font-size: 13px; margin-bottom: 8px; height: 36px; overflow: hidden; line-height: 1.4; opacity: 0.9; }}
            .price-box {{ margin-bottom: 10px; }}
            .new-price {{ color: #bf360c; font-weight: bold; font-size: 16px; }}
            .old-price {{ text-decoration: line-through; color: #aaa; font-size: 12px; margin-left: 5px; }}
            
            .btn {{ 
                background: var(--primary); color: white; text-decoration: none; 
                padding: 8px 15px; display: inline-block; border-radius: 4px; 
                font-size: 12px; text-transform: uppercase; letter-spacing: 1px;
            }}
            .btn:hover {{ background: var(--text); }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>VPP TỊNH</h1>
            <p>Gieo duyên lành - Kiến tạo không gian thanh tịnh</p>
        </div>
        
        <div class="category-menu">
            <button class="cat-btn active" data-filter="all">Tất cả</button>
            <button class="cat-btn" data-filter="vpp-tinh">Sổ Kinh & Thư Pháp</button>
            <button class="cat-btn" data-filter="khong-gian-tho">Đèn & Tượng Thờ</button>
            <button class="cat-btn" data-filter="phap-phuc">Pháp Phục & Chuỗi</button>
            <button class="cat-btn" data-filter="huong-thien">Trầm Hương & Thiền</button>
        </div>

        <div class="grid">
    """
    
    for p in products:
        old_p = f'<span class="old-price">{p["old_price"]}</span>' if p["percent"] > 0 else ""
        cat = phan_loai_danh_muc(p['name'])
        html += f"""
            <div class="card" data-category="{cat}">
                <div class="img-box"><img src="{p['image']}" loading="lazy" alt="{p['name']}"></div>
                <div class="info">
                    <div class="title">{p['name']}</div>
                    <div class="price-box"><span class="new-price">{p['new_price']}</span> {old_p}</div>
                    <a href="{p['link']}" class="btn" target="_blank">Chi tiết</a>
                </div>
            </div>
        """
        
    html += """</div>
        <script>
            document.querySelectorAll('.cat-btn').forEach(btn => {
                btn.addEventListener('click', () => {
                    document.querySelectorAll('.cat-btn').forEach(b => b.classList.remove('active'));
                    btn.classList.add('active');
                    const filter = btn.dataset.filter;
                    document.querySelectorAll('.card').forEach(card => {
                        card.classList.toggle('hide', filter !== 'all' && card.dataset.category !== filter);
                    });
                });
            });
        </script>
    </body></html>"""
    return html

def chay_ngay_di():
    print("🙏 NAM MÔ A DI ĐÀ PHẬT - ĐANG KHỞI CHẠY HỆ THỐNG VPP TỊNH...")
    try:
        r = requests.get(LINK_CSV, timeout=60)
        r.encoding = 'utf-8' 
        lines = r.text.splitlines()
        header = [h.replace('"', '').strip() for h in lines[0].split(',')]
        reader = csv.DictReader(lines[1:], fieldnames=header)
        
        clean_products = []
        for row in reader:
            ten = row.get('name', '').lower()
            
            # 4. BỘ LỌC CHUYÊN SÂU: CHỈ LẤY NẾU CÓ TỪ KHÓA PHẬT GIÁO
            is_buddhist = any(kw in ten for kw in BUDDHIST_KEYWORDS)
            if not is_buddhist: continue # Bỏ qua nếu không liên quan
            
            # Vẫn lọc rác lần 2 cho chắc chắn
            if any(bad in ten for bad in JUNK_BLACKLIST): continue

            price_raw = row.get('price', row.get('price_v2', '0'))
            disc_raw = row.get('discount', row.get('discount_rate', '0'))
            gia_goc, gia_giam, phan_tram = tinh_gia_thuc(price_raw, disc_raw)
            
            if gia_giam < 10000: continue # Bỏ hàng quá rẻ (dưới 10k)
            
            clean_products.append({
                "name": row.get('name'),
                "old_price": "{:,.0f}đ".format(gia_goc).replace(",", "."),
                "new_price": "{:,.0f}đ".format(gia_giam).replace(",", "."),
                "percent": phan_tram,
                "image": row.get('image', '').split(',')[0].strip(' []"'),
                "link": tao_link_aff(row.get('url'))
            })
            
        # Sắp xếp: Ưu tiên hàng có chữ "Kinh" hoặc "Tượng" lên đầu (Tuỳ biến)
        clean_products.sort(key=lambda x: x['percent'], reverse=True)
        final_list = clean_products[:200] # Lấy 200 sản phẩm đẹp nhất
        
        print(f"✅ Đã tìm thấy {len(final_list)} vật phẩm Tịnh độ.")
        
        with open("index.html", "w", encoding="utf-8") as f:
            f.write(tao_web_html(final_list))
        
        print("👉 Đang mở web kiểm tra...")
        webbrowser.open("file://" + os.path.realpath("index.html"))
        
        # Auto Push Github (Giữ nguyên)
        print("⏳ Đang cập nhật lên Github...")
        time.sleep(1)
        os.system("git add .")
        os.system('git commit -m "Update VPP Tinh Product List"')
        os.system("git push")
        print("✅ HOÀN TẤT CÔNG ĐỨC!")

    except Exception as e:
        print(f"❌ Có lỗi xảy ra: {e}")

if __name__ == "__main__":
    chay_ngay_di()