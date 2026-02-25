import csv
import json
import os
import re
import base64 
import time
import webbrowser 

# ==========================================
# CẤU HÌNH HỆ THỐNG
# ==========================================
GA_ID = "G-XXXXXXXXXX"
LOGO_URL = "https://cdn-icons-png.flaticon.com/512/3225/3225194.png"

# ĐƯỜNG DẪN FILE CSV CỦA BẠN TRÊN Ổ F:
FILE_CSV_LOCAL = r"F:\web-banhang\danh_sach_san_pham.csv" 
FILE_JSON = "products.json"

BASE_AFF_URL = "https://go.isclix.com/deep_link/v6/6906519896943843292/4751584435713464237?sub4=oneatweb&utm_source=shopee&utm_campaign=sansale&url_enc="

# ==========================================
# CÁC HÀM XỬ LÝ LÕI
# ==========================================
def tao_link_aff(url_goc):
    if not url_goc: return "#"
    if "shope.ee" in url_goc or "isclix.com" in url_goc or "c.lazada.vn" in url_goc:
        return url_goc
    try:
        encoded = base64.b64encode(url_goc.strip().encode("utf-8")).decode("utf-8")
        return f"{BASE_AFF_URL}{encoded}"
    except:
        return url_goc

def phan_loai_danh_muc(ten_san_pham):
    ten = ten_san_pham.lower()
    if any(k in ten for k in ['remote', 'điều khiển', 'pin', 'sạc', 'cáp', 'tai nghe', 'loa', 'chuột', 'phím', 'wifi', 'sim', 'ốp lưng', 'tivi', 'máy chiếu']): return 'dien-tu'
    if any(k in ten for k in ['túi', 'áo', 'quần', 'váy', 'đầm', 'kính', 'giày', 'dép', 'bông tai', 'dây chuyền', 'nhẫn', 'đồng hồ', 'mũ', 'nón', 'ví', 'balo']): return 'thoi-trang'
    if any(k in ten for k in ['đồ chơi', 'thú', 'gấu', 'búp bê', 'lắp ráp', 'lego', 'xe trượt', 'tã', 'bỉm', 'sữa', 'bé', 'trẻ', 'treo nôi']): return 'me-be'
    if any(k in ten for k in ['tranh', 'decal', 'kệ', 'hộp', 'bút', 'sổ', 'giấy', 'đèn', 'khay', 'bếp', 'nồi', 'chảo', 'dao', 'kéo', 'gối', 'chăn', 'ga', 'nhà', 'decor', 'nhang', 'trầm', 'lư']): return 'nha-cua'
    return 'khac'

def tao_web_html(products):
    v = int(time.time())
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
        <meta name="referrer" content="no-referrer" />
        <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate" />
        <title>Tịnh Shop - Săn Deal Giá Sốc Shopee</title>
        <link rel="icon" href="{LOGO_URL}">
        {ga_script}
        <style>
            :root {{ --primary: #d0011b; --bg: #f5f5f5; --text-gray: #555; }}
            body {{ font-family: sans-serif; background: var(--bg); margin: 0; padding: 0 0 40px 0; }}
            .header {{ text-align: center; background: white; padding: 0; border-bottom: 3px solid var(--primary); margin-bottom: 20px; position: relative; overflow: hidden; }}
            .header-bg {{ width: 100%; aspect-ratio: 1360 / 453; background-image: url('banner-top.jpg'); background-size: cover; background-position: center; display: flex; align-items: center; justify-content: center; }}
            @media (max-width: 630px) {{ .header-bg {{ aspect-ratio: unset; min-height: 150px; }} }}
            .header-bg h1, .header-bg p {{ display: none; }}
            .category-menu {{ display: flex; justify-content: center; flex-wrap: wrap; gap: 10px; margin-bottom: 25px; padding: 0 10px; position: sticky; top: 10px; z-index: 100; }}
            .cat-btn {{ padding: 8px 16px; border: 1px solid #ddd; background: white; color: var(--text-gray); cursor: pointer; border-radius: 20px; font-weight: 600; font-size: 14px; transition: all 0.3s ease; }}
            .cat-btn:hover {{ background: #eee; }}
            .cat-btn.active {{ background: var(--primary); color: white; border-color: var(--primary); }}
            .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 10px; max-width: 1200px; margin: 0 auto; padding: 0 10px; }}
            .card {{ background: white; border-radius: 4px; overflow: hidden; display: flex; flex-direction: column; position: relative; box-shadow: 0 1px 2px rgba(0,0,0,0.1); transition: transform 0.2s; border: 1px solid #eee;}}
            .card:hover {{ transform: translateY(-2px); box-shadow: 0 4px 8px rgba(0,0,0,0.15); }}
            .card.hide {{ display: none; }}
            .discount-tag {{ position: absolute; top: 0; right: 0; background: #ffd424; color: #d0011b; padding: 4px 8px; font-weight: bold; font-size: 12px; z-index: 1; border-bottom-left-radius: 4px;}}
            .img-box {{ width: 100%; height: 190px; display: flex; align-items: center; justify-content: center; padding: 10px; box-sizing: border-box; background: white;}}
            .img-box img {{ max-width: 100%; max-height: 100%; object-fit: contain; }}
            .info {{ padding: 10px; display: flex; flex-direction: column; flex-grow: 1; justify-content: space-between; }}
            .title {{ font-size: 13px; color: #333; margin-bottom: 8px; height: 36px; line-height: 18px; overflow: hidden; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; }}
            .price-box {{ margin-bottom: 8px; }}
            .old-price {{ text-decoration: line-through; color: #999; font-size: 12px; margin-right: 5px; }}
            .new-price {{ color: var(--primary); font-weight: bold; font-size: 16px; }}
            .btn {{ background: var(--primary); color: white; text-decoration: none; padding: 8px; display: block; text-align: center; border-radius: 4px; font-weight: bold; font-size: 14px; }}
            .btn:hover {{ background: #b00117; }}
        </style>
    </head>
    <body>
        <div class="header header-bg"><div><p>VPP Tịnh Shop</p></div></div>
        <div class="category-menu">
            <button class="cat-btn active" data-filter="all">Tất cả</button>
            <button class="cat-btn" data-filter="thoi-trang">Thời trang & Phụ kiện</button>
            <button class="cat-btn" data-filter="dien-tu">Điện tử & Remote</button>
            <button class="cat-btn" data-filter="nha-cua">Nhà cửa & Đời sống</button>
            <button class="cat-btn" data-filter="me-be">Mẹ & Bé / Đồ chơi</button>
        </div>
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
        category_code = phan_loai_danh_muc(p['name'])
        
        html += f"""
            <div class="card" data-category="{category_code}">
                {discount_html}
                <div class="img-box"><img src="{p['image']}" loading="lazy"></div>
                <div class="info">
                    <div class="title">{p['name']}</div>
                    <div class="price-box">{old_price_html}<span class="new-price">{new_price_format}</span></div>
                    <a href="{p['link']}" class="btn" target="_blank">Mua Ngay</a>
                </div>
            </div>
        """
    
    html += """
        </div>
        <script>
            document.addEventListener('DOMContentLoaded', function() {
                const filterButtons = document.querySelectorAll('.cat-btn');
                const productCards = document.querySelectorAll('.card');
                filterButtons.forEach(button => {
                    button.addEventListener('click', () => {
                        filterButtons.forEach(btn => btn.classList.remove('active'));
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

def chay_he_thong():
    print(f"🚀 ĐANG KHỞI TẠO HỆ THỐNG TỪ FILE: {FILE_CSV_LOCAL}")
    try:
        if not os.path.exists(FILE_CSV_LOCAL):
            print(f"❌ LỖI: Không tìm thấy file CSV tại: {FILE_CSV_LOCAL}")
            return

        clean_products = []
        with open(FILE_CSV_LOCAL, mode='r', encoding='utf-8-sig') as f:
            first_line = f.readline()
            f.seek(0)
            dau_ngan_cach = ';' if ';' in first_line else ','
            
            # Đọc file và tự động chuẩn hóa tên cột (xóa khoảng trắng thừa)
            reader = csv.DictReader(f, delimiter=dau_ngan_cach)
            
            # Tạo map chuẩn hóa tên cột
            field_map = {name: name.strip() for name in reader.fieldnames}
            
            for row in reader:
                # Lấy dữ liệu an toàn bằng tên cột đã chuẩn hóa
                # Code này chấp nhận cả " image" và "image"
                row_clean = {field_map[k]: v for k, v in row.items() if k in field_map}
                
                name = row_clean.get('name')
                new_price = row_clean.get('new_price')
                
                if not name or not new_price: continue
                
                link_goc = row_clean.get('link', '#').strip()
                link_anh = row_clean.get('image', '').strip(' \'"[]')
                
                clean_products.append({
                    "name": name.strip(),
                    "old_price": row_clean.get('old_price', '0').strip(),
                    "new_price": new_price.strip(),
                    "image": link_anh,
                    "link": tao_link_aff(link_goc)
                })

        print(f"✅ Đã đọc thành công {len(clean_products)} sản phẩm.")
        
        with open(FILE_JSON, "w", encoding="utf-8") as f:
            json.dump(clean_products, f, ensure_ascii=False, indent=4)
        
        with open("index.html", "w", encoding="utf-8") as f:
            f.write(tao_web_html(clean_products))
        
        print("👉 Đang mở web trên máy tính để kiểm tra...")
        webbrowser.open("file://" + os.path.realpath("index.html"))
        
        print("\n⏳ Đang đẩy code lên kho chứa (Github)...")
        time.sleep(2)
        os.system("git add .")
        os.system('git commit -m "Fix loi cot image co dau cach"')
        os.system("git push")
        print("✅ HOÀN TẤT! Web đã lên hình.")

    except Exception as e:
        print(f"❌ Có lỗi: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    chay_he_thong()