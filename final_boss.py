import requests
import csv
import json
import os
import re
import base64 
import time
import webbrowser 

# --- CẤU HÌNH HỆ THỐNG VPP TỊNH ---
# 1. Thay mã G-XXXXXXXXXX của bạn vào dòng dưới đây:
GA_ID = "G-XMX55X9EJJ"  # Mã Google Analytics của bạn
LOGO_URL = "https://cdn-icons-png.flaticon.com/512/2554/2554037.png" # Icon Hoa Sen
LINK_CSV = "http://datafeed.accesstrade.me/shopee.vn.csv"
BASE_AFF_URL = "https://go.isclix.com/deep_link/v6/6906519896943843292/4751584435713464237?sub4=vpptinh&utm_source=shopee&url_enc="

# --- BỘ LỌC CỐT LÕI (CORE FILTER) ---

# 1. DANH SÁCH TỪ KHÓA BẮT BUỘC (WHITELIST)
# Sản phẩm PHẢI chứa ít nhất 1 từ trong nhóm này mới được lấy.
# Chiến thuật: Dùng từ ghép cụ thể, tránh dùng từ đơn như "tượng" (dễ dính tượng đồ chơi).
BUDDHIST_KEYWORDS = [
    # Nhóm Tượng & Thờ cúng
    "tượng phật", "phật bà", "quan âm", "thích ca", "di đà", "địa tạng", "dược sư", 
    "tây phương tam thánh", "di lặc", "chú tiểu", "tượng gốm tử sa", "tượng đồng",
    "bàn thờ", "tấm chống ám khói", "khung ảnh thờ", "bát hương", "lư hương",
    
    # Nhóm Đèn & Nến
    "đèn thờ", "đèn hoa sen", "đèn lưu ly", "đèn dầu", "đèn cầy", "nến bơ", "đèn hào quang",
    
    # Nhóm Hương & Trầm
    "trầm hương", "lư xông trầm", "nụ trầm", "thác khói", "nhang sạch", "bột trầm",
    
    # Nhóm Pháp phục & Trang sức
    "pháp phục", "áo lam", "áo đi chùa", "quần áo phật tử", 
    "chuỗi hạt", "vòng tay gỗ", "tràng hạt", "108 hạt", "gỗ sưa", "huyết rồng", "bồ đề",
    
    # Nhóm Văn hóa phẩm (VPP Tịnh)
    "chép kinh", "sổ tay chép kinh", "kinh phật", "máy niệm phật", "đài nghe pháp", "loa pháp",
    "thư pháp", "tranh phật", "khánh treo xe", "bao lì xì phật"
]

# 2. DANH SÁCH TỪ KHÓA CẤM (BLACKLIST) - SÁT THỦ DIỆT ANIME
# Nếu dính bất kỳ từ nào dưới đây -> LOẠI NGAY LẬP TỨC.
ANIME_BLACKLIST = [
    # Từ khóa chung về đồ chơi/mô hình
    "đồ chơi", "lắp ráp", "lego", "xếp hình", "trẻ em", "bé trai", "bé gái", 
    "mô hình", "figure", "action figure", "chibi", "cosplay", "game", "blind box", "pop mart",
    "standee", "poster", "truyện tranh", "móc khóa game", "nhựa pvc", "resin",
    
    # Tên các bộ Anime/Manga phổ biến (nguyên nhân chính gây rác)
    "anime", "manga", "one piece", "đảo hải tặc", "luffy", "zoro", "sanji", "nami", "chopper", "ace", "sabo",
    "dragon ball", "7 viên ngọc rồng", "songoku", "goku", "vegeta", "buu",
    "naruto", "sasuke", "kakashi", "boruto",
    "conan", "kaito kid", "doraemon", "nobita",
    "pokemon", "pikachu", "jujutsu", "kimetsu", "thanh gươm diệt quỷ", "nezuko",
    "genshin", "impact", "honkai", "liên minh", "lol", "yasuo",
    "marvel", "avenger", "iron man", "nhện", "batman", "superman",
    "gundam", "robot", "siêu nhân", "ultraman", "transformers",
    
    # Từ khóa rác cũ (giữ lại cho chắc)
    "đồ lót", "gợi cảm", "hở hang", "sexy", "bao cao su", 
    "thịt", "cá", "mắm", "điện thoại", "laptop", "tai nghe", "ốp lưng", "cường lực"
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

def phan_loai_danh_muc(ten_san_pham):
    ten = ten_san_pham.lower()
    if any(k in ten for k in ['đèn', 'tượng', 'bàn thờ', 'lư', 'xông', 'hoa sen', 'tháp']): return 'khong-gian-tho'
    if any(k in ten for k in ['áo', 'quần', 'lam', 'tràng', 'chuỗi', 'vòng', 'túi']): return 'phap-phuc'
    if any(k in ten for k in ['sổ', 'vở', 'bút', 'giấy', 'kinh', 'sách', 'tranh', 'thư pháp']): return 'vpp-tinh'
    if any(k in ten for k in ['trầm', 'nhang', 'nụ', 'bột', 'tinh dầu', 'đài', 'loa']): return 'huong-thien'
    return 'khac'

def tao_web_html(products):
    v = int(time.time())
    
    # Code theo dõi Google Analytics
    ga_script = ""
    if GA_ID != "G-XXXXXXXXXX":
        ga_script = f"""
        <script async src="https://www.googletagmanager.com/gtag/js?id={GA_ID}"></script>
        <script>
          window.dataLayer = window.dataLayer || [];
          function gtag(){{dataLayer.push(arguments);}}
          gtag('js', new Date());
          gtag('config', '{GA_ID}');
        </script>
        """

    html = f"""
    <!DOCTYPE html>
    <html lang="vi">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate" />
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
                text-align: center; padding: 60px 20px; 
                background: linear-gradient(rgba(0,0,0,0.5), rgba(0,0,0,0.5)), url('https://i.pinimg.com/originals/82/10/ec/8210ec997b69c27762699318d104618e.jpg'); 
                background-size: cover; background-position: center;
                border-radius: 8px; margin-bottom: 30px; color: white; text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            }}
            .header h1 {{ margin: 0; font-size: 2.5rem; letter-spacing: 2px; text-transform: uppercase; }}
            .header p {{ font-style: italic; opacity: 0.9; margin-top: 10px; font-size: 1.1rem; }}

            /* Menu nút bấm */
            .category-menu {{ display: flex; justify-content: center; flex-wrap: wrap; gap: 12px; margin-bottom: 30px; position: sticky; top: 10px; z-index: 99; }}
            .cat-btn {{ 
                padding: 10px 20px; border: 1px solid var(--primary); background: white; 
                color: var(--primary); cursor: pointer; border-radius: 25px; 
                font-family: 'Merriweather', serif; font-size: 14px; transition: 0.3s;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            }}
            .cat-btn:hover, .cat-btn.active {{ background: var(--primary); color: white; box-shadow: 0 4px 10px rgba(141, 110, 99, 0.4); }}

            /* Lưới sản phẩm */
            .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 20px; max-width: 1200px; margin: 0 auto; }}
            .card {{ 
                background: white; border-radius: 8px; overflow: hidden; 
                box-shadow: 0 2px 5px rgba(0,0,0,0.05); transition: 0.3s; 
                border: 1px solid #eee; display: flex; flex-direction: column;
            }}
            .card:hover {{ transform: translateY(-5px); box-shadow: 0 10px 20px rgba(0,0,0,0.1); border-color: var(--accent); }}
            .card.hide {{ display: none; }}
            
            .img-box {{ width: 100%; height: 200px; padding: 15px; box-sizing: border-box; display: flex; align-items: center; justify-content: center; background: #fff; }}
            .img-box img {{ max-width: 100%; max-height: 100%; object-fit: contain; }}
            
            .info {{ padding: 15px; text-align: center; flex-grow: 1; display: flex; flex-direction: column; justify-content: space-between; }}
            .title {{ font-size: 14px; margin-bottom: 8px; height: 40px; overflow: hidden; line-height: 1.4; opacity: 0.9; color: #333; }}
            .price-box {{ margin-bottom: 15px; }}
            .new-price {{ color: #bf360c; font-weight: bold; font-size: 18px; }}
            .old-price {{ text-decoration: line-through; color: #aaa; font-size: 13px; margin-left: 5px; }}
            
            .btn {{ 
                background: var(--primary); color: white; text-decoration: none; 
                padding: 10px 0; display: block; border-radius: 4px; 
                font-size: 13px; text-transform: uppercase; letter-spacing: 1px; font-weight: bold; transition: 0.2s;
            }}
            .btn:hover {{ background: var(--accent); color: #333; }}
            
            /* Responsive Mobile */
            @media (max-width: 600px) {{
                .header {{ padding: 40px 10px; }}
                .header h1 {{ font-size: 1.8rem; }}
                .grid {{ grid-template-columns: repeat(2, 1fr); gap: 10px; }}
                .card {{ border-radius: 4px; }}
                .img-box {{ height: 160px; padding: 5px; }}
                .title {{ font-size: 12px; height: 34px; }}
                .new-price {{ font-size: 15px; }}
                .btn {{ padding: 8px 0; font-size: 11px; }}
            }}
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
        discount_html = f'<div class="discount-tag">-{int(p["percent"])}%</div>' if p["percent"] > 0 else ""
        old_price_html = f'<span class="old-price">{p["old_price"]}</span>' if p["percent"] > 0 else ""
        category_code = phan_loai_danh_muc(p['name'])
        
        html += f"""
            <div class="card" data-category="{category_code}">
                <div class="img-box"><img src="{p['image']}" loading="lazy" alt="{p['name']}"></div>
                <div class="info">
                    <div class="title">{p['name']}</div>
                    <div class="price-box"><span class="new-price">{p['new_price']}</span> {old_price_html}</div>
                    <a href="{p['link']}" class="btn" target="_blank">Chi tiết</a>
                </div>
            </div>
        """
    html += """</div>
        <script>
            document.addEventListener('DOMContentLoaded', function() {
                const filterButtons = document.querySelectorAll('.cat-btn');
                const productCards = document.querySelectorAll('.card');

                filterButtons.forEach(button => {
                    button.addEventListener('click', () => {
                        // Xóa active cũ
                        filterButtons.forEach(btn => btn.classList.remove('active'));
                        // Thêm active mới
                        button.classList.add('active');
                        
                        const filterValue = button.getAttribute('data-filter');
                        
                        productCards.forEach(card => {
                            if (filterValue === 'all' || card.getAttribute('data-category') === filterValue) {
                                card.classList.remove('hide');
                            } else {
                                card.classList.add('hide');
                            }
                        });
                    });
                });
            });
        </script>
    </body></html>
    """
    return html

def chay_ngay_di():
    print("🙏 NAM MÔ A DI ĐÀ PHẬT - ĐANG KHỞI CHẠY HỆ THỐNG VPP TỊNH V3.0...")
    try:
        print("1. Đang tải dữ liệu từ AccessTrade (có thể mất 30s)...")
        r = requests.get(LINK_CSV, timeout=60)
        r.encoding = 'utf-8' 
        lines = r.text.splitlines()
        header = [h.replace('"', '').strip() for h in lines[0].split(',')]
        reader = csv.DictReader(lines[1:], fieldnames=header)
        
        clean_products = []
        count_passed = 0
        count_blocked = 0
        
        print("2. Đang lọc sản phẩm (Chế độ diệt Anime)...")
        for row in reader:
            ten = row.get('name', '').lower()
            
            # --- BƯỚC 1: LỌC RÁC (ANIME) ---
            # Nếu dính từ khóa đen -> Bỏ qua ngay lập tức
            if any(bad in ten for bad in ANIME_BLACKLIST):
                count_blocked += 1
                continue 

            # --- BƯỚC 2: LỌC TỪ KHÓA CHUẨN (BUDDHIST) ---
            # Nếu không có từ khóa Phật giáo -> Bỏ qua
            is_buddhist = any(kw in ten for kw in BUDDHIST_KEYWORDS)
            if not is_buddhist: 
                continue
            
            # --- BƯỚC 3: XỬ LÝ GIÁ ---
            price_raw = row.get('price', row.get('price_v2', '0'))
            disc_raw = row.get('discount', row.get('discount_rate', '0'))
            gia_goc, gia_giam, phan_tram = tinh_gia_thuc(price_raw, disc_raw)
            
            # Chỉ lấy hàng giá trị > 20k (để đỡ rác web) và < 20 triệu
            if gia_giam < 20000 or gia_giam > 20000000: continue
            
            clean_products.append({
                "name": row.get('name'),
                "old_price": "{:,.0f}đ".format(gia_goc).replace(",", "."),
                "new_price": "{:,.0f}đ".format(gia_giam).replace(",", "."),
                "percent": phan_tram,
                "image": row.get('image', '').split(',')[0].strip(' []"'),
                "link": tao_link_aff(row.get('url'))
            })
            count_passed += 1
            
        # Sắp xếp: Ưu tiên hàng giảm giá sâu lên đầu
        clean_products.sort(key=lambda x: x['percent'], reverse=True)
        
        # Chỉ lấy 250 sản phẩm tốt nhất để web nhẹ
        final_list = clean_products[:250]
        
        print(f"✅ KẾT QUẢ: Đã chặn {count_blocked} sản phẩm rác (Anime/Toy).")
        print(f"✅ KẾT QUẢ: Tìm thấy {len(final_list)} vật phẩm Tịnh độ chuẩn.")
        
        print("3. Đang tạo giao diện Web...")
        with open("index.html", "w", encoding="utf-8") as f:
            f.write(tao_web_html(final_list))
        
        print("👉 Đang mở web kiểm tra...")
        webbrowser.open("file://" + os.path.realpath("index.html"))
        
        print("⏳ 4. Đang tự động đẩy code lên Github...")
        time.sleep(2)
        os.system("git add .")
        os.system('git commit -m "Auto Update V3.0 - Clean Buddhist Filter"')
        os.system("git push")
        print("✅ HOÀN TẤT CÔNG ĐỨC! WEB ĐÃ LÊN SÓNG.")

    except Exception as e:
        print(f"❌ LỖI NGHIÊM TRỌNG: {e}")

if __name__ == "__main__":
    chay_ngay_di()