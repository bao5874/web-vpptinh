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
GA_ID = "G-XXXXXXXXXX"  # <--- Thay mã Google Analytics của bạn vào đây (nếu chưa có thì cứ để nguyên)
LOGO_URL = "https://cdn-icons-png.flaticon.com/512/3225/3225194.png"

# ĐƯỜNG DẪN FILE CSV CỦA BẠN TRÊN Ổ F:
FILE_CSV_LOCAL = r"F:\web-banhang\danh_sach_san_pham.csv" 
FILE_JSON = "products.json"

# Nút trung chuyển AccessTrade
BASE_AFF_URL = "https://go.isclix.com/deep_link/v6/6906519896943843292/4751584435713464237?sub4=oneatweb&utm_source=shopee&utm_campaign=sansale&url_enc="

# ==========================================
# CÁC HÀM XỬ LÝ LÕI
# ==========================================
def tao_link_aff(url_goc):
    if not url_goc: return "#"
    # Nếu link bạn nhập trong file Excel đã là link rút gọn (shope.ee) 
    # hoặc link AccessTrade rồi thì giữ nguyên
    if "shope.ee" in url_goc or "isclix.com" in url_goc or "c.lazada.vn" in url_goc:
        return url_goc
    
    # Nếu là link gốc shopee.vn dài thì bọc qua AccessTrade
    try:
        encoded = base64.b64encode(url_goc.strip().encode("utf-8")).decode("utf-8")
        return f"{BASE_AFF_URL}{encoded}"
    except:
        return url_goc

def phan_loai_danh_muc(ten_san_pham):
    ten = ten_san_pham.lower()
    
    # 1. Điện tử & Remote
    keywords_dien_tu = ['remote', 'điều khiển', 'pin', 'sạc', 'cáp', 'tai nghe', 'loa', 'chuột', 'phím', 'wifi', 'sim', 'ốp lưng', 'tivi', 'máy chiếu']
    if any(k in ten for k in keywords_dien_tu): return 'dien-tu'
    
    # 2. Thời trang & Phụ kiện
    keywords_thoi_trang = ['túi', 'áo', 'quần', 'váy', 'đầm', 'kính', 'giày', 'dép', 'bông tai', 'dây chuyền', 'nhẫn', 'đồng hồ', 'mũ', 'nón', 'ví', 'balo']
    if any(k in ten for k in keywords_thoi_trang): return 'thoi-trang'
    
    # 3. Mẹ & Bé / Đồ chơi
    keywords_me_be = ['đồ chơi', 'thú', 'gấu', 'búp bê', 'lắp ráp', 'lego', 'xe trượt', 'tã', 'bỉm', 'sữa', 'bé', 'trẻ', 'treo nôi']
    if any(k in ten for k in keywords_me_be): return 'me-be'
    
    # 4. Nhà cửa & Đời sống
    keywords_nha_cua = ['tranh', 'decal', 'kệ', 'hộp', 'bút', 'sổ', 'giấy', 'đèn', 'khay', 'bếp', 'nồi', 'chảo', 'dao', 'kéo', 'gối', 'chăn', 'ga', 'nhà', 'decor']
    if any(k in ten for k in keywords_nha_cua): return 'nha-cua'
    
    # Mặc định
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
        <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate" />
        <title>Tịnh Shop - Săn Deal Giá Sốc Shopee</title>
        <link rel="icon" href="{LOGO_URL}">
        {ga_script}
        <style>
            :root {{ --primary: #d0011b; --bg: #f5f5f5; --text-gray: #555; }}
            body {{ font-family: sans-serif; background: var(--bg); margin: 0; padding: 0 0 40px 0; }}
            
            .header {{ text-align: center; background: white; padding: 0; border-bottom: 3px solid var(--primary); margin-bottom: 20px; position: relative; overflow: hidden; }}
            .header-bg {{
                width: 100%; aspect-ratio: 1360 / 453; 
                background-image: url('banner-top.jpg'); background-size: cover; background-position: center; background-repeat: no-repeat;
                display: flex; align-items: center; justify-content: center;
            }}
            @media (max-width: 630px) {{ .header-bg {{ aspect-ratio: unset; min-height: 150px; }} }}
            .header-bg h1, .header-bg p {{ display: none; }}
            
            .category-menu {{ display: flex; justify-content: center; flex-wrap: wrap; gap: 10px; margin-bottom: 25px; padding: 0 10px; position: sticky; top: 10px; z-index: 100; }}
            .cat-btn {{ padding: 8px 16px; border: 1px solid #ddd; background: white; color: var(--text-gray); cursor: pointer; border-radius: 20px; font-weight: 600; font-size: 14px; transition: all 0.3s ease; box-shadow: 0 2px 5px rgba(0,0,0,0.05); }}
            .cat-btn:hover {{ background: #eee; }}
            .cat-btn.active {{ background: var(--primary); color: white; border-color: var(--primary); box-shadow: 0 4px 8px rgba(208, 1, 27, 0.3); }}
            
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
        <div class="header header-bg">
            <div><p>VPP Tịnh Shop</p></div>
        </div>

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
        # Tính % giảm giá tự động
        try:
            goc = float(p['old_price'])
            moi = float(p['new_price'])
            percent = int((goc - moi) / goc * 100) if goc > moi else 0
        except:
            percent = 0

        discount_html = f'<div class="discount-tag">-{percent}%</div>' if percent > 0 else ""
        # Format số tiền: 100000 -> 100.000₫
        old_price_html = f'<span class="old-price">{int(goc):,}₫</span>'.replace(",", ".") if percent > 0 else ""
        new_price_format = f"{int(moi):,}₫".replace(",", ".")
        
        category_code = phan_loai_danh_muc(p['name'])
        
        html += f"""
            <div class="card" data-category="{category_code}">
                {discount_html}
                <div class="img-box"><img src="{p['image']}" loading="lazy"></div>
                <div class="info">
                    <div class="title">{p['name']}</div>
                    <div class="price-box">
                        {old_price_html}
                        <span class="new-price">{new_price_format}</span>
                    </div>
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
    print(f"🚀 ĐANG KHỞI TẠO HỆ THỐNG SHOPEE TỪ FILE: {FILE_CSV_LOCAL}")
    try:
        # 1. Kiểm tra xem file có tồn tại ở ổ F không
        if not os.path.exists(FILE_CSV_LOCAL):
            print(f"❌ LỖI: Không tìm thấy file CSV tại: {FILE_CSV_LOCAL}")
            print("👉 Vui lòng kiểm tra lại đường dẫn xem có gõ sai tên hoặc quên đuôi .csv không!")
            return

        # 2. Đọc dữ liệu từ file CSV Local
        # Dùng utf-8-sig để đọc file Excel xuất ra mà không bị lỗi ký tự bom (\ufeff)
        clean_products = []
        with open(FILE_CSV_LOCAL, mode='r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if not row.get('name') or not row.get('new_price'): continue
                
                link_goc = row.get('link', '#').strip()
                
                clean_products.append({
                    "name": row.get('name').strip(),
                    "old_price": row.get('old_price', '0').strip(),
                    "new_price": row.get('new_price', '0').strip(),
                    "image": row.get('image', '').strip(),
                    "link": tao_link_aff(link_goc)
                })

        print(f"✅ Đã tải thành công {len(clean_products)} sản phẩm từ ổ F.")
        
        # 3. Tạo file JSON (để lưu trữ data) và HTML
        with open(FILE_JSON, "w", encoding="utf-8") as f:
            json.dump(clean_products, f, ensure_ascii=False, indent=4)
        
        with open("index.html", "w", encoding="utf-8") as f:
            f.write(tao_web_html(clean_products))
        
        print("👉 Đang mở web trên máy tính để kiểm tra...")
        webbrowser.open("file://" + os.path.realpath("index.html"))
        
        # 4. Tự động đẩy lên mạng
        print("\n⏳ Đang đẩy code lên kho chứa (Github)...")
        time.sleep(2)
        os.system("git add .")
        os.system('git commit -m "Cập nhật sản phẩm Shopee từ ổ F"')
        os.system("git push")
        print("✅ HOÀN TẤT! Web vpptinh.com đã được cập nhật sản phẩm mới.")

    except Exception as e:
        print(f"❌ Có lỗi nghiêm trọng xảy ra: {e}")

if __name__ == "__main__":
    chay_he_thong()