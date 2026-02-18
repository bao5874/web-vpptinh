import requests
import csv
import os
import re
import base64 
import time
import webbrowser 
from io import StringIO

# --- CẤU HÌNH ---
GA_ID = "G-XXXXXXXXXX" 
LOGO_URL = "https://cdn-icons-png.flaticon.com/512/2554/2554037.png"
# Link này có thể thay đổi tùy tài khoản AccessTrade của bạn
LINK_CSV = "https://datafeed.accesstrade.me/shopee.vn.csv" 
BASE_AFF_URL = "https://go.isclix.com/deep_link/v6/6906519896943843292/4751584435713464237?sub4=vpptinh&utm_source=shopee&url_enc="

# --- DỮ LIỆU GIẢ LẬP (ĐỂ TEST KHI MẠNG LỖI) ---
# Đây là danh sách hỗn hợp để kiểm tra bộ lọc hoạt động tốt không
MOCK_DATA = """name,price,image,url
"Tượng Phật Bà Quan Âm Gốm Tử Sa Cao Cấp",550000,"https://dummyimage.com/200x200/e0c097/fff&text=Tuong+Phat","http://shopee.vn/sp1"
"Mô hình Luffy Gear 5 Nika One Piece",150000,"https://dummyimage.com/200x200/ff0000/fff&text=Luffy","http://shopee.vn/sp2"
"Bàn thờ xe máy Honda Vision 2024",45000,"https://dummyimage.com/200x200/000/fff&text=Ban+tho+xe","http://shopee.vn/sp3"
"Chuỗi hạt gỗ trầm hương 108 hạt",250000,"https://dummyimage.com/200x200/8d6e63/fff&text=Tram+Huong","http://shopee.vn/sp4"
"Combo 10 cuốn vở chép kinh Địa Tạng in mờ",99000,"https://dummyimage.com/200x200/fff/000&text=Vo+Kinh","http://shopee.vn/sp5"
"Đồ chơi lắp ráp Gundam Robot",300000,"https://dummyimage.com/200x200/00f/fff&text=Gundam","http://shopee.vn/sp6"
"Áo lam đi chùa cách tân thêu hoa sen",180000,"https://dummyimage.com/200x200/eee/333&text=Ao+Lam","http://shopee.vn/sp7"
"""

# --- BỘ LỌC 3 LỚP (ANT-MAN FILTER) ---
BLACKLIST = [
    "mô hình", "figure", "anime", "manga", "cosplay", "game", "đồ chơi", 
    "one piece", "đảo hải tặc", "luffy", "zoro", "sanji", "nami", "chopper", "ace", "sabo", 
    "g5", "haki", "gear 5", "wano", "pop mart", "blind box",
    "dragon ball", "songoku", "goku", "vegeta", "buu", "7 viên ngọc rồng",
    "naruto", "sasuke", "kakashi", "conan", "doraemon", "nobita", 
    "jujutsu", "kaisen", "gojo", "kimetsu", "thanh gươm", "nezuko",
    "genshin", "impact", "honkai", "liên minh", "lol", "yasuo",
    "gundam", "robot", "siêu nhân", "ultraman", "marvel", "avenger", "iron man",
    "chibi", "pvc", "resin", "standee", "poster", "nhựa",
    "honda", "yamaha", "suzuki", "sym", "piaggio", "sh", "vision", "wave", "dream", 
    "sirius", "exciter", "winner", "airblade", "lead", "vario", "blade", "rsx",
    "xe máy", "ô tô", "mô tô", "phụ tùng", "linh kiện", "đồ chơi xe",
    "tay lái", "ốp đầu", "dàn áo", "tem xe", "nhớt", "lốp", "pô", "gương", "kính chiếu hậu", "phanh", "thắng",
    "bàn thờ xe", 
    "sex", "người lớn", "bao cao su", "gợi cảm", "hở hang", "đồ lót", "nội y",
    "điện thoại", "laptop", "tai nghe", "cường lực", "ốp lưng", "cáp sạc", "wifi", "sim",
    "thịt", "cá", "mắm", "khô", "đồ ăn", "voucher", "thẻ cào"
]

WHITELIST = [
    "tượng phật", "phật bà", "phật quan âm", "quan thế âm", "tượng thích ca", "tượng di đà", 
    "tượng địa tạng", "tượng dược sư", "tượng tam thánh", "tượng di lặc", "tượng bổn sư", 
    "tượng chú tiểu", "tượng đạt ma", "tượng gốm tử sa", "tượng đồng", "tượng lưu ly",
    "bàn thờ phật", "bàn thờ gia tiên", "bàn thờ thần tài", "bàn thờ ông địa", "bàn thờ treo", 
    "tủ thờ", "trang thờ", "ngai thờ", "khám thờ",
    "đèn thờ", "đèn hoa sen", "đèn lưu ly", "đèn hào quang", "đèn dầu cát tường", "đèn cầy", "nến bơ",
    "lư xông trầm", "lư hương", "bát hương", "đỉnh đồng", "chân nến", "tấm chống ám khói",
    "pháp phục", "áo lam", "áo tràng", "áo đi chùa", "quần áo phật tử", "nón lá",
    "chuỗi hạt", "tràng hạt", "vòng tay gỗ", "vòng 108 hạt", "chuỗi bồ đề", "vòng trầm hương",
    "mõ tụng kinh", "chuông gia trì", "khánh",
    "trầm hương", "nụ trầm", "nhang sạch", "bột trầm", "thác khói",
    "sổ chép kinh", "vở chép kinh", "kinh phật", "sách phật", "tranh phật", "thư pháp",
    "máy niệm phật", "đài nghe pháp", "loa pháp thoại"
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

def phan_loai_danh_muc(ten):
    ten = ten.lower()
    if any(k in ten for k in ['đèn', 'tượng', 'bàn thờ', 'lư', 'xông', 'hoa sen', 'tháp', 'đỉnh']): return 'khong-gian-tho'
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
            :root {{ 
                --primary: #8d6e63; --accent: #fbc02d; --bg: #fdfbf7; --text: #4e342e;
            }}
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
    print("🙏 NAM MÔ A DI ĐÀ PHẬT - ĐANG KHỞI CHẠY HỆ THỐNG V5.0 (RESILIENCE MODE)...")
    
    # 1. THỬ TẢI DỮ LIỆU TỪ MẠNG
    csv_content = ""
    try:
        print("🌐 Đang kết nối đến server AccessTrade...")
        # Thêm Headers để giả làm trình duyệt (Fix lỗi chặn bot)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        # Thử kết nối với timeout ngắn hơn
        r = requests.get(LINK_CSV, headers=headers, timeout=10)
        
        if r.status_code == 200:
            r.encoding = 'utf-8'
            csv_content = r.text
            print("✅ Tải dữ liệu thành công!")
        else:
            raise Exception(f"Server trả về mã lỗi: {r.status_code}")

    except Exception as e:
        print(f"⚠️ LỖI KẾT NỐI: {e}")
        print("🔄 Đang chuyển sang chế độ GIẢ LẬP DỮ LIỆU (Offline Mode) để kiểm tra bộ lọc...")
        csv_content = MOCK_DATA # Dùng dữ liệu giả để chạy tiếp

    # 2. XỬ LÝ DỮ LIỆU (Dù là mạng hay giả lập đều chạy qua đây)
    try:
        lines = csv_content.splitlines()
        header = [h.replace('"', '').strip() for h in lines[0].split(',')]
        reader = csv.DictReader(lines[1:], fieldnames=header)
        
        products, blocked_count = [], 0
        
        print("🔍 Đang lọc sản phẩm...")
        for row in reader:
            ten = row.get('name', '').lower()
            
            # --- LỚP 1: BLACKLIST (CHẶN RÁC) ---
            if any(bad in ten for bad in BLACKLIST):
                print(f"   ⛔ Đã chặn rác: {row.get('name')}")
                blocked_count += 1
                continue 

            # --- LỚP 2: WHITELIST (CHỈ LẤY ĐÚNG) ---
            if not any(good in ten for good in WHITELIST):
                # print(f"   ⚠️ Bỏ qua (Không đúng chủ đề): {row.get('name')}")
                continue
            
            # --- LỚP 3: GIÁ TIỀN (LỌC ĐỒ NHỰA RẺ TIỀN) ---
            p_raw = row.get('price', row.get('price_v2', '0'))
            d_raw = row.get('discount', row.get('discount_rate', '0'))
            gia_goc, gia_giam, phan_tram = tinh_gia_thuc(p_raw, d_raw)
            
            if gia_giam < 20000: continue
            
            print(f"   ✅ Đã duyệt: {row.get('name')}")
            products.append({
                "name": row.get('name'),
                "old_price": "{:,.0f}đ".format(gia_goc).replace(",", "."),
                "new_price": "{:,.0f}đ".format(gia_giam).replace(",", "."),
                "percent": phan_tram,
                "image": row.get('image', '').split(',')[0].strip(' []"'),
                "link": tao_link_aff(row.get('url'))
            })
            
        products.sort(key=lambda x: x['percent'], reverse=True)
        final_list = products[:200]
        
        print("-" * 30)
        print(f"📊 TỔNG KẾT:")
        print(f"   - Số lượng rác bị chặn: {blocked_count}")
        print(f"   - Số lượng hàng chuẩn Tịnh Độ: {len(final_list)}")
        
        with open("index.html", "w", encoding="utf-8") as f: f.write(tao_web_html(final_list))
        print("👉 Đang mở web...")
        webbrowser.open("file://" + os.path.realpath("index.html"))
        
        # Auto Push Github
        print("⏳ Đang cập nhật lên Github...")
        os.system("git add .")
        os.system('git commit -m "Auto Update V5 - Resilience Mode"')
        os.system("git push")
        print("✅ HOÀN TẤT CÔNG ĐỨC!")

    except Exception as e:
        print(f"❌ Lỗi xử lý dữ liệu: {e}")

if __name__ == "__main__":
    chay_ngay_di()