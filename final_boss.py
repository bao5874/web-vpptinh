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
# Dùng link logo online (Icon văn phòng phẩm cực đẹp) - ĐẢM BẢO KHÔNG LỖI
LOGO_URL = "https://cdn-icons-png.flaticon.com/512/3135/3135715.png"

LINK_CSV = "http://datafeed.accesstrade.me/shopee.vn.csv"
FILE_JSON = "products.json"

# Link Affiliate của bạn (Đã cắt đuôi mã hóa)
BASE_AFF_URL = "https://go.isclix.com/deep_link/v6/6906519896943843292/4751584435713464237?sub4=oneatweb&utm_source=shopee&utm_campaign=vpp&url_enc="

# 1. BỘ TỪ KHÓA KÉP - CHỈ LẤY VĂN PHÒNG PHẨM THỰC SỰ
VPP_WHITELIST = [
    "bút bi", "bút chì", "bút gel", "bút nước", "bút dạ", "bút xóa", "bút nhớ", "bút lông", "ngòi bút", "bút dạ quang",
    "giấy a4", "giấy in", "giấy note", "giấy than", "giấy bìa", "giấy vẽ", "giấy in ảnh", "giấy kraft",
    "vở học sinh", "vở kẻ ngang", "vở ô ly", "sổ tay", "sổ lò xo", "sổ da", "sổ ghi chép",
    "kẹp giấy", "kẹp bướm", "kẹp tài liệu", "ghim bấm", "dập ghim", "ghim cài", "kẹp sắt",
    "bìa hồ sơ", "bìa còng", "bìa lá", "file lá", "túi clear bag", "cặp tài liệu", "file nhựa",
    "băng dính", "băng keo", "hồ dán", "keo dán", "băng trong suốt", "keo cơ khí",
    "thước kẻ", "ê ke", "compa", "hộp bút", "dao rọc giấy", "lưỡi dao", "kéo cắt",
    "khay đựng bút", "khay tài liệu", "kệ đựng hồ sơ", "khay để bàn", "hộp đựng", "tủ tài liệu"
]

# 2. BLACKLIST - LỌC BỎ SẢN PHẨM KHÔNG PHẢI VĂN PHÒNG PHẨM
JUNK_BLACKLIST = [
    "honda", "yamaha", "suzuki", "xe máy", "ô tô", "phụ tùng", "lốp", "nhớt", "pô", "gác chân", "bánh xe",
    "mực khô", "ăn vặt", "bánh", "kẹo", "thực phẩm", "mắm", "muối", "cơm", "mì", "tương", "rượu", "bia",
    "kẻ mắt", "kẻ mày", "trang điểm", "son môi", "phấn", "kem dưỡng", "serum", "mụn", "makeup", "mỹ phẩm",
    "áo sơ mi", "áo thun", "áo khoác", "quần jeans", "quần tây", "váy", "giày thể thao", "dép", "túi xách", "thời trang",
    "đồ chơi", "siêu nhân", "lắp ráp", "robot", "máy chơi game",
    "hết hàng", "bỏ mẫu", "liên hệ", "out of stock"
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
        # Xóa dấu chấm phẩy để lấy số thuần
        gia_str = str(gia_raw).replace('.', '').replace(',', '')
        numbers = re.findall(r'\d+', gia_str)
        if not numbers: return "Liên hệ"
        gia_val = float(numbers[0])
        
        # Sửa giá ảo
        if gia_val > 5000000: gia_val /= 10
        if gia_val < 1000: return "Liên hệ" 
        
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
        <title>VPP Tịnh - Văn Phòng Phẩm</title>
        <link rel="icon" href="{LOGO_URL}">
        <style>
            /* QUAY VỀ MÀU VÀNG KEM THÂN THIỆN */
            :root {{ --primary: #008080; --bg: #fdfcdc; }}
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
                    <div class="title">{p['name']}</div>
                    <div class="price">{p['price']}</div>
                    <a href="{p['link']}" class="btn" target="_blank">Mua Ngay</a>
                </div>
            </div>
        """
    html += "</div></body></html>"
    return html

def chay_ngay_di():
    print("🚀 ĐANG CHẠY FINAL BOSS 14.0 (FIX LOGO & LỌC)...")
    try:
        print("⏳ Đang tải dữ liệu...")
        r = requests.get(LINK_CSV, timeout=60)
        
        if r.status_code != 200:
            print("❌ Lỗi tải file CSV!")
            return
            
        reader = csv.DictReader(io.StringIO(r.text))
        clean_products = []
        
        print("⚙️ Đang lọc...")
        excluded_count = 0
        for row in reader:
            ten = row.get('name', '').lower()
            stock = str(row.get('stock', '1')).lower().strip()
            
            # 0. KIỂM TRA HẾT HÀNG
            if any(x in stock for x in ['0', 'hết', 'out', 'không có']):
                excluded_count += 1
                continue
            
            # 1. BỘ LỌC KÉP - PHẢI CÓ TỪ KHÓA VĂN PHÒNG PHẨM
            if not any(good in ten for good in VPP_WHITELIST): continue
            
            # 2. BLACKLIST - BỎ SẢN PHẨM KHÔNG PHẢI VĂN PHÒNG PHẨM
            if any(bad in ten for bad in JUNK_BLACKLIST): 
                excluded_count += 1
                continue

            # 3. GIÁ - PHẢI CÓ GIÁ HỢP LỆ
            gia_hien_thi = xuly_gia(row.get('price'))
            if gia_hien_thi == "Liên hệ": 
                excluded_count += 1
                continue

            clean_products.append({
                "name": row.get('name'),
                "price": gia_hien_thi,
                "image": row.get('image', '').split(',')[0].strip(' []"'),
                "link": tao_link_aff(row.get('url'))
            })
        
        print(f"⚠️ Đã loại bỏ {excluded_count} sản phẩm (hết hàng hoặc không phải VPP)")

        final_list = clean_products[:100]
        print(f"✅ Tìm thấy {len(final_list)} sản phẩm hợp lệ (đã loại bỏ {excluded_count} sản phẩm không phù hợp).")

        # LƯU FILE
        with open(FILE_JSON, "w", encoding="utf-8") as f:
            json.dump(final_list, f, ensure_ascii=False, indent=4)
        
        with open("index.html", "w", encoding="utf-8") as f:
            f.write(tao_web_html(final_list))
        
        # TỰ ĐỘNG MỞ TRÌNH DUYỆT ĐỂ BẠN KIỂM TRA TRƯỚC
        print("👉 Đang mở web kiểm tra...")
        url_file = "file://" + os.path.realpath("index.html")
        webbrowser.open(url_file)
        
        # XÁC NHẬN ĐẨY LÊN
        print("\n" + "="*50)
        print("Hãy nhìn trình duyệt vừa bật lên.")
        print("Logo cây bút có hiện không? Khay makeup đã mất chưa?")
        print("="*50 + "\n")
        
        chon = input("Nếu Web OK thì bấm phím 'y' rồi Enter để đẩy lên mạng: ")
        
        if chon.lower() == 'y':
            print("☁️ Đang cập nhật lên Github...")
            os.system("git add .")
            os.system('git commit -m "Final 14 Fix Logo"')
            os.system("git push")
            print("✅ XONG! Đợi 3 phút rồi vào vpptinh.com kiểm tra.")
        else:
            print("❌ Đã hủy.")

    except Exception as e:
        print(f"❌ Lỗi: {e}")

if __name__ == "__main__":
    chay_ngay_di()