import requests
import csv
import json
import io
import os
import re
import base64 

# --- CẤU HÌNH ---
LINK_CSV = "http://datafeed.accesstrade.me/shopee.vn.csv"
FILE_JSON = "products.json"
ACCESSTRADE_ID = "4751584435713464237"
CAMPAIGN_ID = "6906519896943843292" 
BASE_AFF_URL = f"https://go.isclix.com/deep_link/v6/{CAMPAIGN_ID}/{ACCESSTRADE_ID}?sub4=web_tu_dong&utm_source=shopee&utm_campaign=vpp_tinh&url_enc="

# 1. TỪ KHÓA VPP (Giữ nguyên)
VPP_KEYWORDS = [
    "bút", "vở", "sổ", "giấy a4", "giấy in", "kẹp", "thước", "file", 
    "bìa", "băng dính", "ghim", "hộp bút", "balo", "cặp", "máy tính",
    "dập ghim", "hồ dán", "keo", "bảng", "phấn", "mực"
]

# 2. TỪ KHÓA CẤM (Vẫn chặn rác, nhưng bỏ chặn "hết hàng" để test xem có hàng không)
CANT_TAKE = [
    "mắt", "mày", "môi", "mi", "son", "kem", "phấn", "makeup", "trang điểm", "da", "nám", "mụn", 
    "bánh", "kẹo", "đồ ăn", "thực phẩm", "mắm", "muối", "gia vị",
    "xe", "honda", "yamaha", "lốp", "nhớt",
    "áo", "quần", "váy", "giày", "dép", "túi xách", "thời trang"
]

def tao_link_aff(url_goc):
    if not url_goc: return "#"
    try:
        encoded = base64.b64encode(url_goc.strip().encode("utf-8")).decode("utf-8")
        return f"{BASE_AFF_URL}{encoded}"
    except:
        return url_goc

def xuly_gia_thong_minh(gia_raw):
    """
    Hàm xử lý giá Logic 7.0:
    Tự động phát hiện giá ảo và sửa lại.
    """
    try:
        # Xóa hết ký tự không phải số
        gia_str = str(gia_raw).split('.')[0] # Lấy phần nguyên trước dấu chấm
        gia_clean = re.sub(r'[^\d]', '', gia_str)
        
        if not gia_clean: return "Liên hệ"
        
        gia_val = float(gia_clean)
        
        # LOGIC SỬA SAI:
        # Một món VPP bình thường không thể quá 500.000đ (trừ máy tính/balo xịn)
        # Nếu giá > 1 triệu mà tên sản phẩm là bút/vở -> Chia 10
        if gia_val > 1000000: 
            gia_val = gia_val / 10
            
        # Nếu vẫn > 1 triệu -> Chia tiếp (trường hợp bị nhân 100)
        if gia_val > 1000000:
            gia_val = gia_val / 10
            
        if gia_val < 1000: return "Liên hệ"
        
        return "{:,.0f}₫".format(gia_val).replace(",", ".")
    except:
        return "Liên hệ"

def tao_web_html(products):
    # LOGO: Kiểm tra kỹ xem file nào tồn tại
    logo_file = "logo.png" # Mặc định
    if os.path.exists("logo.jpg"): logo_file = "logo.jpg"
    
    # CSS onerror: Nếu ảnh lỗi thì ẩn đi, hiện chữ VPP TỊNH
    header_html = f'''
        <div class="logo-container">
            <img src="{logo_file}" alt="VPP Tịnh" class="logo-img" onerror="this.style.display='none'; document.getElementById('text-logo').style.display='block'">
            <h1 id="text-logo" style="display:none">VPP TỊNH</h1>
            <p class="slogan">🌿 Bình An Trao Tay 🌿</p>
        </div>
    '''
    
    # Nếu không tìm thấy file ảnh ngay trên máy, hiện chữ luôn
    if not os.path.exists(logo_file):
         header_html = '<h1>VPP TỊNH</h1><p class="slogan">🌿 Bình An Trao Tay 🌿</p>'

    html = f"""
    <!DOCTYPE html>
    <html lang="vi">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <meta name="referrer" content="no-referrer"> 
        <title>VPP Tịnh - Bình An Trao Tay</title>
        <link rel="icon" href="{logo_file}">
        <style>
            :root {{ --primary: #2a9d8f; --bg: #fdfcdc; --text: #333; }}
            body {{ font-family: 'Segoe UI', sans-serif; background: var(--bg); padding: 20px; margin: 0; }}
            header {{ text-align: center; background: #fff; padding: 20px; border-radius: 15px; margin-bottom: 30px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); }}
            .logo-img {{ max-height: 100px; width: auto; margin: 0 auto; }}
            h1 {{ color: #e76f51; margin: 10px 0 0; text-transform: uppercase; }}
            .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 20px; max-width: 1200px; margin: 0 auto; }}
            .card {{ background: #fff; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.1); display: flex; flex-direction: column; transition: transform 0.2s; }}
            .card:hover {{ transform: translateY(-5px); }}
            .img-box {{ width: 100%; height: 180px; padding: 10px; display: flex; align-items: center; justify-content: center; }}
            .img-box img {{ max-width: 100%; max-height: 100%; object-fit: contain; }}
            .info {{ padding: 15px; flex-grow: 1; display: flex; flex-direction: column; justify-content: space-between; }}
            .title {{ font-size: 0.9em; margin-bottom: 8px; height: 2.7em; overflow: hidden; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; }}
            .price {{ color: #e63946; font-weight: bold; font-size: 1.1em; }}
            .btn {{ background: var(--primary); color: #fff; text-decoration: none; padding: 10px; text-align: center; border-radius: 5px; font-weight: bold; margin-top: 10px; display: block; }}
            .btn:hover {{ background: #21867a; }}
        </style>
    </head>
    <body>
        <header>{header_html}</header>
        <div class="grid">
    """
    for p in products:
        html += f"""
            <div class="card">
                <div class="img-box"><img src="{p['image']}" alt="sp" loading="lazy"></div>
                <div class="info">
                    <div class="title">{p['name']}</div>
                    <div class="price">{p['price']}</div>
                    <a href="{p['link']}" class="btn" target="_blank" rel="nofollow">Mua Ngay</a>
                </div>
            </div>
        """
    html += "</div></body></html>"
    return html

def chay_ngay_di():
    print("🚀 ĐANG KHỞI ĐỘNG BẢN 7.0 (FIX TRẮNG TRANG + FIX GIÁ)...")
    try:
        print("⏳ Đang tải dữ liệu...")
        r = requests.get(LINK_CSV, timeout=60)
        r.encoding = 'utf-8'
        reader = csv.DictReader(io.StringIO(r.text))
        
        all_products = []
        print("⚙️ Đang lọc (Bỏ điều kiện Sales để cứu Web)...")
        
        for row in reader:
            ten = row.get('name', '').lower()
            
            # LỌC CƠ BẢN
            if not any(w in ten for w in VPP_KEYWORDS): continue
            if any(bad in ten for bad in CANT_TAKE): continue
            
            # XỬ LÝ GIÁ
            gia_hien_thi = xuly_gia_thong_minh(row.get('price', 0))
            if gia_hien_thi == "Liên hệ": continue

            all_products.append({
                "name": row.get('name'),
                "price": gia_hien_thi,
                "image": row.get('image', '').split(',')[0].strip(' []"'),
                "link": tao_link_aff(row.get('url'))
            })

        # Lấy tối đa 100 món (Không sắp xếp theo Sales nữa vì có thể cột Sales bị lỗi)
        final_list = all_products[:100]

        if not final_list:
            print("❌ VẪN KHÔNG CÓ HÀNG? Hãy kiểm tra lại file CSV nguồn!")
        else:
            print(f"✅ Đã tìm thấy {len(final_list)} sản phẩm.")

        with open(FILE_JSON, "w", encoding="utf-8") as f:
            json.dump(final_list, f, ensure_ascii=False, indent=4)
        
        html_content = tao_web_html(final_list)
        with open("index.html", "w", encoding="utf-8") as f:
            f.write(html_content)
            
        print("☁️ Đang đẩy lên mạng (BẮT BUỘC ĐẨY LOGO)...")
        
        # --- CƯỠNG CHẾ ĐẨY LOGO ---
        os.system("git add .") 
        if os.path.exists("logo.png"): os.system("git add logo.png")
        if os.path.exists("logo.jpg"): os.system("git add logo.jpg")
        
        os.system('git commit -m "Final Fix 7.0"')
        os.system("git push")
        print("🎉 XONG! Hãy F5 trang web (có thể cần đợi 1-2 phút).")

    except Exception as e:
        print(f"❌ Lỗi: {e}")

if __name__ == "__main__":
    chay_ngay_di()