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
# Logo Túi Mua Sắm (Sale)
LOGO_URL = "https://cdn-icons-png.flaticon.com/512/3225/3225194.png"
LINK_CSV = "http://datafeed.accesstrade.me/shopee.vn.csv"
FILE_JSON = "products.json"

# Link Affiliate của bạn
BASE_AFF_URL = "https://go.isclix.com/deep_link/v6/6906519896943843292/4751584435713464237?sub4=oneatweb&utm_source=shopee&utm_campaign=sansale&url_enc="

# 1. DANH SÁCH CẤM (BLACKLIST) - Đã NỚI LỎNG
# Đã XÓA quần áo, mỹ phẩm khỏi danh sách cấm để bán đa ngành
# Chỉ chặn những thứ khó bán online hoặc rác
JUNK_BLACKLIST = [
    "hết hàng", "bỏ mẫu", "ngừng kinh doanh", "tạm hết", "liên hệ", "đặt trước",
    "honda", "yamaha", "suzuki", "xe máy", "ô tô", "lốp", "nhớt", "pô", "gác chân", # Phụ tùng xe (khó bán)
    "mực khô", "mực rim", "hàng tươi sống", "đông lạnh", # Thực phẩm khó vận chuyển
    "voucher", "nạp thẻ", "sim", # Dịch vụ số (hoa hồng thấp)
    "sex toy", "người lớn" # Nhạy cảm
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
        
        # LỌC GIÁ:
        # Bỏ hàng < 10k (Hoa hồng quá ít, rác)
        if gia_val < 10000: return "Liên hệ"
        # Bỏ hàng > 5 triệu (Khách ít mua qua link lạ)
        if gia_val > 5000000: return "Liên hệ"
        
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
        <title>Tịnh Shop - Săn Deal Giá Sốc</title>
        <link rel="icon" href="{LOGO_URL}">
        <style>
            :root {{ --primary: #d32f2f; --bg: #ffebee; }} /* Màu ĐỎ cho Sale */
            body {{ font-family: 'Segoe UI', sans-serif; background: var(--bg); margin: 0; padding: 20px; }}
            
            .header {{ text-align: center; background: white; padding: 30px; border-radius: 15px; margin-bottom: 30px; border-bottom: 5px solid var(--primary); }}
            .logo-img {{ width: 80px; height: 80px; object-fit: contain; display: block; margin: 0 auto 10px; }}
            h1 {{ color: var(--primary); margin: 0; text-transform: uppercase; letter-spacing: 1px; font-weight: 900; }}
            .slogan {{ color: #444; font-weight: bold; margin-top: 5px; }}
            
            .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 15px; max-width: 1200px; margin: 0 auto; }}
            .card {{ background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 5px rgba(0,0,0,0.1); display: flex; flex-direction: column; transition: transform 0.2s; position: relative; }}
            .card:hover {{ transform: translateY(-5px); box-shadow: 0 8px 20px rgba(0,0,0,0.15); }}
            
            /* NHÃN GIẢM GIÁ NỔI BẬT */
            .discount-tag {{ position: absolute; top: 0; right: 0; background: #ffeb3b; color: red; padding: 5px 10px; font-weight: bold; font-size: 13px; border-bottom-left-radius: 10px; box-shadow: -2px 2px 5px rgba(0,0,0,0.1); }}
            
            .img-box {{ width: 100%; height: 180px; padding: 5px; display: flex; align-items: center; justify-content: center; border-bottom: 1px solid #eee; }}
            .img-box img {{ max-width: 100%; max-height: 100%; object-fit: contain; }}
            
            .title {{ font-size: 13px; color: #333; margin: 10px; height: 36px; overflow: hidden; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; padding: 0 10px; }}
            .price {{ color: var(--primary); font-weight: bold; font-size: 18px; margin: 0 10px 10px; }}
            .btn {{ background: var(--primary); color: white; text-decoration: none; padding: 10px; text-align: center; font-weight: bold; display: block; margin: 0 10px 10px; border-radius: 4px; }}
            .btn:hover {{ background: #b71c1c; }}
        </style>
    </head>
    <body>
        <div class="header">
            <img src="{LOGO_URL}" alt="Logo" class="logo-img">
            <h1>TỊNH SHOP</h1>
            <p class="slogan">🔥 TỔNG HỢP DEAL GIẢM GIÁ KHỦNG HÔM NAY 🔥</p>
        </div>
        <div class="grid">
    """
    for p in products:
        discount_html = f'<div class="discount-tag">-{int(p["discount"])}%</div>' if p["discount"] > 0 else ""
        html += f"""
            <div class="card">
                {discount_html}
                <div class="img-box"><img src="{p['image']}" loading="lazy"></div>
                <div class="title">{p['name']}</div>
                <div class="price">{p['price']}</div>
                <a href="{p['link']}" class="btn" target="_blank">Săn Ngay</a>
            </div>
        """
    html += "</div></body></html>"
    return html

def chay_ngay_di():
    print("🚀 ĐANG CHẠY FINAL BOSS 20.0 (CHẾ ĐỘ SĂN SALE TỔNG HỢP)...")
    try:
        print("⏳ Đang tải dữ liệu...")
        r = requests.get(LINK_CSV, timeout=60)
        
        lines = r.text.splitlines()
        header = [h.replace('"', '').strip() for h in lines[0].split(',')]
        reader = csv.DictReader(lines[1:], fieldnames=header)
        
        clean_products = []
        
        print("⚙️ Đang lọc (Lấy tất cả ngành hàng có giảm giá)...")
        for row in reader:
            ten = row.get('name', '').lower()
            
            # 1. BỎ BỘ LỌC VPP -> LẤY TẤT CẢ
            # Chỉ chặn danh sách đen (rác)
            if any(bad in ten for bad in JUNK_BLACKLIST): continue

            # 2. XỬ LÝ GIÁ
            gia_hien_thi = xuly_gia(row.get('price'))
            if gia_hien_thi == "Liên hệ": continue

            # 3. LẤY DISCOUNT ĐỂ SẮP XẾP
            try:
                giam_gia = float(row.get('discount', 0))
            except:
                giam_gia = 0
            
            # Chỉ lấy món có giảm giá (để đúng chất Săn Sale)
            # Nếu bạn muốn lấy cả hàng không giảm giá thì xóa dòng dưới đi
            if giam_gia < 10: continue # Lọc: Chỉ lấy món giảm trên 10%

            clean_products.append({
                "name": row.get('name'),
                "price": gia_hien_thi,
                "discount": giam_gia,
                "image": row.get('image', '').split(',')[0].strip(' []"'),
                "link": tao_link_aff(row.get('url'))
            })

        # SẮP XẾP: GIẢM GIÁ NHIỀU NHẤT LÊN ĐẦU
        clean_products.sort(key=lambda x: x['discount'], reverse=True)

        final_list = clean_products[:100]
        print(f"✅ Tìm thấy {len(final_list)} DEAL HOT (Đa ngành hàng).")

        with open(FILE_JSON, "w", encoding="utf-8") as f:
            json.dump(final_list, f, ensure_ascii=False, indent=4)
        
        with open("index.html", "w", encoding="utf-8") as f:
            f.write(tao_web_html(final_list))
        
        print("👉 Đang mở web kiểm tra...")
        webbrowser.open("file://" + os.path.realpath("index.html"))
        
        print("\n" + "="*50)
        print("WEB MÀU ĐỎ (SALE) ĐÃ HIỆN RA CHƯA?")
        print("Bạn sẽ thấy Quần áo, Mỹ phẩm, Đồ gia dụng... giảm giá.")
        print("="*50 + "\n")
        
        chon = input("Gõ 'y' và Enter để đẩy lên Github: ")
        if chon.lower() == 'y':
            print("☁️ Đang cập nhật lên Github...")
            os.system("git add .")
            os.system('git commit -m "Update V20 General Sale"')
            os.system("git push")
            print("✅ XONG! Nhớ F5 trang vpptinh.com nhé.")
        else:
            print("❌ Đã hủy.")

    except Exception as e:
        print(f"❌ Lỗi: {e}")

if __name__ == "__main__":
    chay_ngay_di()