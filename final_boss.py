import requests
import csv
import json
import io
import os
import re
import base64 
import time
import webbrowser 

# --- CẤU HÌNH ---
LOGO_URL = "https://cdn-icons-png.flaticon.com/512/3135/3135715.png"
LINK_CSV = "http://datafeed.accesstrade.me/shopee.vn.csv"
FILE_JSON = "products.json"

# CẬP NHẬT LINK TRACKING CỦA BẠN
BASE_AFF_URL = "https://go.isclix.com/deep_link/v6/6906519896943843292/4751584435713464237?sub4=oneatweb&utm_source=shopee&utm_campaign=vpp&url_enc="

# 1. DANH MỤC HỢP LỆ (Dựa trên cột 'category')
# Chỉ lấy sản phẩm nằm trong các ngành hàng này
VALID_CATEGORIES = [
    "văn phòng phẩm", "nhà sách", "dụng cụ học sinh", "thiết bị văn phòng", 
    "giấy in", "sổ tay", "bút viết", "họa cụ", "stationery", "school", "office"
]

# 2. TỪ KHÓA CẤM (Vẫn giữ để chặn rác nếu category bị sai)
JUNK_BLACKLIST = [
    "hết hàng", "bỏ mẫu", "liên hệ", "tạm hết",
    "honda", "yamaha", "xe máy", "phụ tùng", "lốp", "nhớt",
    "mực khô", "ăn vặt", "bánh", "kẹo", "thực phẩm",
    "kẻ mắt", "trang điểm", "son", "kem", "mỹ phẩm", "makeup",
    "áo", "quần", "váy", "giày", "dép", "túi xách"
]

def tao_link_aff(url_goc):
    if not url_goc: return "#"
    try:
        encoded = base64.b64encode(url_goc.strip().encode("utf-8")).decode("utf-8")
        return f"{BASE_AFF_URL}{encoded}"
    except:
        return url_goc

def xuly_gia(gia_raw):
    try:
        gia_str = str(gia_raw).replace('.', '').replace(',', '')
        numbers = re.findall(r'\d+', gia_str)
        if not numbers: return "Liên hệ"
        gia_val = float(numbers[0])
        
        # CHẶN HÀNG RÁC/HẾT HÀNG BẰNG GIÁ
        # Giá < 3.000đ -> Thường là phụ kiện rác hoặc hàng hết để giá ảo -> LOẠI
        if gia_val < 3000: return "Liên hệ"
        
        # Giá > 2.000.000đ -> VPP hiếm khi đắt thế (trừ máy in) -> LOẠI CHO AN TOÀN
        if gia_val > 2000000: return "Liên hệ"
        
        return "{:,.0f}₫".format(gia_val).replace(",", ".")
    except:
        return "Liên hệ"

def tao_web_html(products):
    v = int(time.time())
    html = f"""
    <!DOCTYPE html>
    <html lang="vi">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate" />
        <title>VPP Tịnh - Văn Phòng Phẩm</title>
        <link rel="icon" href="{LOGO_URL}">
        <style>
            :root {{ --primary: #008080; --bg: #e0f2f1; }}
            body {{ font-family: 'Segoe UI', sans-serif; background: var(--bg); margin: 0; padding: 20px; }}
            .header {{ text-align: center; background: white; padding: 30px; border-radius: 15px; margin-bottom: 30px; border-bottom: 4px solid var(--primary); }}
            .logo-img {{ width: 80px; height: 80px; object-fit: contain; display: block; margin: 0 auto 10px; }}
            h1 {{ color: var(--primary); margin: 0; text-transform: uppercase; letter-spacing: 1px; }}
            .slogan {{ color: #666; font-style: italic; font-size: 14px; margin-top: 5px; }}
            .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(190px, 1fr)); gap: 20px; max-width: 1200px; margin: 0 auto; }}
            .card {{ background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.05); display: flex; flex-direction: column; transition: transform 0.2s; }}
            .card:hover {{ transform: translateY(-5px); box-shadow: 0 5px 15px rgba(0,0,0,0.1); }}
            .img-box {{ width: 100%; height: 180px; padding: 10px; display: flex; align-items: center; justify-content: center; border-bottom: 1px solid #eee; }}
            .img-box img {{ max-width: 100%; max-height: 100%; object-fit: contain; }}
            .info {{ padding: 15px; flex-grow: 1; display: flex; flex-direction: column; justify-content: space-between; }}
            .title {{ font-size: 14px; color: #333; margin: 0 0 10px 0; height: 40px; overflow: hidden; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; }}
            .price {{ color: #d0021b; font-weight: bold; font-size: 16px; margin-bottom: 10px; }}
            .cate {{ font-size: 11px; color: #888; margin-bottom: 5px; background: #eee; padding: 2px 5px; border-radius: 3px; width: fit-content; }}
            .btn {{ background: var(--primary); color: white; text-decoration: none; padding: 10px; text-align: center; border-radius: 5px; font-weight: 600; display: block; }}
            .btn:hover {{ background: #006666; }}
        </style>
    </head>
    <body>
        <div class="header">
            <img src="{LOGO_URL}" alt="Logo" class="logo-img">
            <h1>VPP TỊNH</h1>
            <p class="slogan">🌿 Bình An Trao Tay - Cập nhật lúc {v} 🌿</p>
        </div>
        <div class="grid">
    """
    for p in products:
        html += f"""
            <div class="card">
                <div class="img-box"><img src="{p['image']}" loading="lazy"></div>
                <div class="info">
                    <div class="cate">{p['category']}</div>
                    <div class="title">{p['name']}</div>
                    <div class="price">{p['price']}</div>
                    <a href="{p['link']}" class="btn" target="_blank">Mua Ngay</a>
                </div>
            </div>
        """
    html += "</div></body></html>"
    return html

def chay_ngay_di():
    print("🚀 ĐANG CHẠY FINAL BOSS 17.0 (LỌC THEO DANH MỤC)...")
    try:
        print("⏳ Đang tải dữ liệu...")
        r = requests.get(LINK_CSV, timeout=60)
        
        # Xử lý dữ liệu CSV để tránh lỗi header
        lines = r.text.splitlines()
        # Đảm bảo header sạch sẽ (bỏ ngoặc kép thừa nếu có)
        header = [h.replace('"', '').strip() for h in lines[0].split(',')]
        
        reader = csv.DictReader(lines[1:], fieldnames=header)
        clean_products = []
        
        print("⚙️ Đang lọc theo Cột Category...")
        for row in reader:
            ten = row.get('name', '').lower()
            
            # Lấy danh mục, xử lý lỗi nếu không có cột category
            category = row.get('category', '').lower()
            
            # 1. BỘ LỌC CHÍNH: CATEGORY (Ngành hàng)
            # Nếu category chứa "văn phòng phẩm" hoặc "nhà sách" -> OK
            is_valid_cate = any(c in category for c in VALID_CATEGORIES)
            
            # Nếu không thuộc ngành hàng này -> BỎ QUA NGAY
            if not is_valid_cate:
                # CƠ HỘI CUỐI: Nếu category rỗng (lỗi file), thì check tên sản phẩm kỹ
                if category == "" and ("bút" in ten or "giấy" in ten or "sổ" in ten):
                    pass # Cho qua
                else:
                    continue 

            # 2. BỘ LỌC PHỤ: BLACKLIST (Chặn rác lọt lưới)
            if any(bad in ten for bad in JUNK_BLACKLIST): continue

            # 3. GIÁ (Chặn hàng hết/rác giá rẻ)
            gia_hien_thi = xuly_gia(row.get('price'))
            if gia_hien_thi == "Liên hệ": continue

            clean_products.append({
                "name": row.get('name'),
                "price": gia_hien_thi,
                "category": row.get('category', 'VPP'), # Lưu lại tên danh mục để hiện lên web
                "image": row.get('image', '').split(',')[0].strip(' []"'),
                "link": tao_link_aff(row.get('url'))
            })

        final_list = clean_products[:100]
        print(f"✅ Tìm thấy {len(final_list)} sản phẩm CHUẨN NGÀNH HÀNG.")

        with open(FILE_JSON, "w", encoding="utf-8") as f:
            json.dump(final_list, f, ensure_ascii=False, indent=4)
        
        with open("index.html", "w", encoding="utf-8") as f:
            f.write(tao_web_html(final_list))
        
        print("👉 Đang mở web kiểm tra...")
        webbrowser.open("file://" + os.path.realpath("index.html"))
        
        print("\n" + "="*50)
        print("BẠN HÃY XEM KỸ WEB VỪA BẬT LÊN.")
        print("Trên mỗi sản phẩm sẽ có dòng chữ nhỏ ghi Ngành Hàng (Category).")
        print("Nếu thấy OK, gõ 'y' và Enter.")
        print("="*50 + "\n")
        
        chon = input("Lựa chọn (y/n): ")
        if chon.lower() == 'y':
            print("☁️ Đang cập nhật lên Github...")
            os.system("git add .")
            os.system('git commit -m "Update V17 Category Filter"')
            os.system("git push")
            print("✅ XONG! Vào vpptinh.com kiểm tra (Nhớ F5).")
        else:
            print("❌ Đã hủy.")

    except Exception as e:
        print(f"❌ Lỗi: {e}")

if __name__ == "__main__":
    chay_ngay_di()