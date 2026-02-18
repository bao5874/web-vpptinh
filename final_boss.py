import requests
import csv
import os
import re
import base64 
import time
import webbrowser 
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# --- CẤU HÌNH ---
GA_ID = "G-XXXXXXXXXX" 
LOGO_URL = "https://cdn-icons-png.flaticon.com/512/2554/2554037.png"
LINK_CSV = "http://datafeed.accesstrade.me/shopee.vn.csv"
BASE_AFF_URL = "https://go.isclix.com/deep_link/v6/6906519896943843292/4751584435713464237?sub4=vpptinh&utm_source=shopee&url_enc="

# --- 1. LỌC DANH MỤC (CATEGORY FILTER) ---
# Nếu danh mục sản phẩm chứa bất kỳ từ nào dưới đây -> LOẠI NGAY
BAD_CATEGORIES = [
    "đồ chơi", "toy", "game", "trẻ em", "mẹ & bé", "mẹ và bé",
    "xe", "oto", "moto", "phụ tùng", "bảo hiểm",
    "điện thoại", "máy tính", "camera", "thiết bị số", "công nghệ",
    "thời trang", "quần áo", "giày dép", "túi ví", "đồng hồ", "trang sức", # Trừ chuỗi hạt sẽ lọc ở tên sau
    "mỹ phẩm", "làm đẹp", "sức khỏe", # Trừ tinh dầu/trầm
    "bách hóa", "ăn vặt", "thực phẩm", "điện gia dụng"
]

# --- 2. LỌC TỪ KHÓA (NAME FILTER) ---
BLACKLIST_PHRASE = [
    "mô hình", "figure", "anime", "manga", "cosplay", "one piece", "luffy", "goku", "naruto",
    "honda", "yamaha", "suzuki", "vision", "wave", "bàn thờ xe",
    "sex", "bao cao su", "gợi cảm"
]

WHITELIST_KEYWORDS = [
    "tượng phật", "phật bà", "quan âm", "thích ca", "di đà", "địa tạng", "dược sư", "tam thánh", "di lặc", "chú tiểu",
    "bàn thờ", "tủ thờ", "trang thờ", # Đã an toàn vì đã lọc danh mục Xe cộ ở trên
    "đèn thờ", "đèn hoa sen", "đèn lưu ly", "đèn hào quang", "đèn dầu", "nến bơ",
    "lư xông", "lư hương", "bát hương", "đỉnh đồng",
    "pháp phục", "áo lam", "áo đi chùa", "quần áo phật tử", 
    "chuỗi hạt", "vòng tay gỗ", "tràng hạt", "108 hạt", "bồ đề", "trầm hương",
    "mõ", "chuông", "khánh", "kinh phật", "sổ chép kinh", "tranh phật", "thư pháp",
    "máy niệm phật", "đài nghe pháp", "nhang", "nụ trầm", "thác khói"
]

def tao_link_aff(url_goc):
    if not url_goc: return "#"
    try:
        encoded = base64.b64encode(url_goc.strip().encode("utf-8")).decode("utf-8")
        return f"{BASE_AFF_URL}{encoded}"
    except: return url_goc

def tinh_gia_thuc(p_raw, d_raw):
    try:
        gia_str = str(p_raw).split('.')[0] 
        numbers = re.findall(r'\d+', gia_str)
        if not numbers: return 0, 0, 0
        gia_goc = float("".join(numbers))
        try:
            d_str = str(d_raw).replace('%', '')
            discount_val = float(d_str)
            if discount_val > 1: discount_val = discount_val / 100
        except: discount_val = 0
        gia_giam = gia_goc * (1 - discount_val)
        return gia_goc, gia_giam, discount_val * 100
    except: return 0, 0, 0

def check_product_hybrid(row):
    """Kiểm tra kết hợp cả Danh mục và Tên"""
    name = row.get('name', '').lower()
    category = row.get('category', '').lower()
    
    # BƯỚC 1: LỌC THEO DANH MỤC (QUAN TRỌNG NHẤT)
    # Nếu danh mục là "Xe cộ", "Đồ chơi" -> Loại ngay, không cần xem tên
    for bad_cat in BAD_CATEGORIES:
        if bad_cat in category:
            # print(f"   🚫 Loại theo danh mục [{category}]: {name}")
            return False

    # BƯỚC 2: LỌC THEO TÊN (BLACKLIST)
    # Chặn sót (ví dụ shop đăng sai danh mục)
    for bad in BLACKLIST_PHRASE:
        if bad in name: return False
        
    # BƯỚC 3: LỌC THEO TÊN (WHITELIST)
    # Phải chứa từ khóa Phật giáo
    is_valid = False
    for good in WHITELIST_KEYWORDS:
        if good in name:
            is_valid = True
            break
            
    return is_valid

def phan_loai_danh_muc(ten):
    ten = ten.lower()
    if any(k in ten for k in ['đèn', 'tượng', 'bàn thờ', 'lư', 'xông', 'hoa sen', 'tháp']): return 'khong-gian-tho'
    if any(k in ten for k in ['áo', 'quần', 'lam', 'tràng', 'chuỗi', 'vòng', 'túi', 'nón']): return 'phap-phuc'
    if any(k in ten for k in ['sổ', 'vở', 'bút', 'giấy', 'kinh', 'sách', 'tranh', 'thư pháp', 'máy', 'đài', 'loa']): return 'vpp-tinh'
    if any(k in ten for k in ['trầm', 'nhang', 'nụ', 'bột', 'tinh dầu']): return 'huong-thien'
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
            :root {{ --primary: #8d6e63; --accent: #fbc02d; --bg: #fdfbf7; --text: #4e342e; }}
            body {{ font-family: 'Merriweather', serif; background: var(--bg); color: var(--text); margin: 0; padding: 20px; }}
            .header {{ 
                text-align: center; padding: 50px 20px; 
                background: linear-gradient(rgba(0,0,0,0.6), rgba(0,0,0,0.6)), url('https://i.pinimg.com/originals/82/10/ec/8210ec997b69c27762699318d104618e.jpg'); 
                background-size: cover; background-position: center; border-radius: 8px; margin-bottom: 30px; color: white;
            }}
            .header h1 {{ margin: 0; font-size: 2.2rem; text-transform: uppercase; letter-spacing: 2px; }}
            .header p {{ font-style: italic; margin-top: 10px; font-size: 1.1rem; }}
            .category-menu {{ display: flex; justify-content: center; flex-wrap: wrap; gap: 10px; margin-bottom: 30px; position: sticky; top: 10px; z-index: 99; }}
            .cat-btn {{ 
                padding: 10px 18px; border: 1px solid var(--primary); background: white; color: var(--primary); cursor: pointer; 
                border-radius: 20px; font-family: 'Merriweather', serif; font-size: 14px; transition: 0.3s;
            }}
            .cat-btn.active, .cat-btn:hover {{ background: var(--primary); color: white; }}
            .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 15px; max-width: 1200px; margin: 0 auto; }}
            .card {{ background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 5px rgba(0,0,0,0.1); transition: 0.3s; display: flex; flex-direction: column; }}
            .card:hover {{ transform: translateY(-5px); box-shadow: 0 10px 20px rgba(0,0,0,0.15); }}
            .card.hide {{ display: none; }}
            .img-box {{ height: 200px; padding: 10px; display: flex; align-items: center; justify-content: center; background: #fff; }}
            .img-box img {{ max-width: 100%; max-height: 100%; object-fit: contain; }}
            .info {{ padding: 15px; text-align: center; flex-grow: 1; display: flex; flex-direction: column; justify-content: space-between; }}
            .title {{ font-size: 13px; height: 38px; overflow: hidden; line-height: 1.4; color: #333; margin-bottom: 10px; }}
            .new-price {{ color: #bf360c; font-weight: bold; font-size: 16px; }}
            .old-price {{ text-decoration: line-through; color: #999; font-size: 12px; margin-left: 5px; }}
            .btn {{ background: var(--primary); color: white; text-decoration: none; padding: 10px; display: block; border-radius: 4px; font-size: 12px; text-transform: uppercase; font-weight: bold; margin-top: 10px; }}
            .btn:hover {{ background: var(--accent); color: #333; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>VPP Tịnh</h1>
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
    html += """</div><script>
        const btns = document.querySelectorAll('.cat-btn'); const cards = document.querySelectorAll('.card');
        btns.forEach(btn => btn.addEventListener('click', () => {
            btns.forEach(b => b.classList.remove('active')); btn.classList.add('active');
            const f = btn.dataset.filter;
            cards.forEach(c => c.classList.toggle('hide', f !== 'all' && c.dataset.category !== f));
        }));
    </script></body></html>"""
    return html

def chay_ngay_di():
    print("🙏 VPP TỊNH FINAL - HYBRID FILTER MODE...")
    
    session = requests.Session()
    retry = Retry(connect=3, backoff_factor=1)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    
    products = []
    
    try:
        print("🌐 Đang kết nối AccessTrade (Stream)...")
        with session.get(LINK_CSV, stream=True, timeout=30) as r:
            r.raise_for_status()
            lines = (line.decode('utf-8') for line in r.iter_lines())
            
            # Đọc CSV - Tự động nhận diện header "category"
            reader = csv.DictReader(lines)
            
            count_checked = 0
            count_passed = 0
            
            print("🔍 Đang lọc dữ liệu (KẾT HỢP DANH MỤC + TỪ KHÓA)...")
            for row in reader:
                count_checked += 1
                if count_checked % 5000 == 0: print(f"   ...Đã quét {count_checked} sản phẩm...")
                
                # --- GỌI HÀM LỌC KÉP ---
                if not check_product_hybrid(row):
                    continue
                
                # LỌC GIÁ
                p_raw = row.get('price', row.get('price_v2', '0'))
                d_raw = row.get('discount', row.get('discount_rate', '0'))
                gia_goc, gia_giam, phan_tram = tinh_gia_thuc(p_raw, d_raw)
                
                if gia_giam < 20000: continue
                
                products.append({
                    "name": row.get('name'),
                    "old_price": "{:,.0f}đ".format(gia_goc).replace(",", "."),
                    "new_price": "{:,.0f}đ".format(gia_giam).replace(",", "."),
                    "percent": phan_tram,
                    "image": row.get('image', '').split(',')[0].strip(' []"'),
                    "link": tao_link_aff(row.get('url'))
                })
                count_passed += 1
                
                if count_passed >= 1000: break

        products.sort(key=lambda x: x['percent'], reverse=True)
        final_list = products[:250]
        
        print(f"✅ HOÀN TẤT! Tìm thấy {len(final_list)} vật phẩm chuẩn.")
        
        with open("index.html", "w", encoding="utf-8") as f: f.write(tao_web_html(final_list))
        print("👉 Đang mở web...")
        webbrowser.open("file://" + os.path.realpath("index.html"))
        
        print("⏳ Đang đẩy lên Github (Auto-Retry)...")
        for i in range(3):
            try:
                os.system("git add .")
                os.system('git commit -m "Hybrid Filter Update"')
                if os.system("git push") == 0:
                    print("✅ PUSH THÀNH CÔNG!")
                    break
                else:
                    print(f"⚠️ Thử lại lần {i+1}...")
                    time.sleep(5)
            except: pass

    except Exception as e:
        print(f"❌ LỖI: {e}")

if __name__ == "__main__":
    chay_ngay_di()