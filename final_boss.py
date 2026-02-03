import requests
import csv
import json
import io
import os
import re
import base64 
import time

# --- CẤU HÌNH ---
LINK_CSV = "http://datafeed.accesstrade.me/shopee.vn.csv"
FILE_JSON = "products.json"
ACCESSTRADE_ID = "4751584435713464237"
CAMPAIGN_ID = "6906519896943843292" 
BASE_AFF_URL = f"https://go.isclix.com/deep_link/v6/{CAMPAIGN_ID}/{ACCESSTRADE_ID}?sub4=web_tu_dong&utm_source=shopee&utm_campaign=vpp_tinh&url_enc="

# LOGO ONLINE (Link trực tiếp ổn định - Biểu tượng văn phòng phẩm)
LOGO_URL = "https://cdn-icons-png.flaticon.com/512/3135/3135715.png"

def tao_link_aff(url_goc):
    if not url_goc: return "#"
    try:
        encoded = base64.b64encode(url_goc.strip().encode("utf-8")).decode("utf-8")
        return f"{BASE_AFF_URL}{encoded}"
    except:
        return url_goc

def xuly_gia_chuan(gia_raw):
    """Xử lý giá tiền: Chuyển 125.000 -> 125000 chuẩn xác"""
    try:
        gia_str = str(gia_raw).strip()
        # Chỉ lấy số
        numbers = re.findall(r'\d+', gia_str.replace('.', '').replace(',', ''))
        if not numbers: return 0
        
        gia_val = float(numbers[0])
        
        # Logic sửa giá ảo (Nếu > 10 triệu -> Chia 100)
        if gia_val > 10000000: gia_val /= 100
        elif gia_val > 2000000: gia_val /= 10
            
        return gia_val
    except:
        return 0

def tao_web_html(products):
    # Thêm timestamp để ép trình duyệt không lưu cache cũ
    v = int(time.time())
    
    html = f"""
    <!DOCTYPE html>
    <html lang="vi">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate" />
        <meta http-equiv="Pragma" content="no-cache" />
        <meta http-equiv="Expires" content="0" />
        <title>VPP Tịnh - Văn Phòng Phẩm</title>
        <link rel="icon" href="{LOGO_URL}">
        <style>
            :root {{ --primary: #008080; --bg: #f4f6f8; }}
            body {{ font-family: sans-serif; background: var(--bg); padding: 20px; margin: 0; }}
            .header {{ text-align: center; background: #fff; padding: 25px; border-radius: 10px; margin-bottom: 30px; border-bottom: 4px solid var(--primary); }}
            .logo-img {{ width: 80px; height: 80px; display: block; margin: 0 auto 10px; }}
            h1 {{ color: var(--primary); margin: 0; text-transform: uppercase; letter-spacing: 1px; }}
            .slogan {{ color: #666; font-style: italic; font-size: 14px; margin-top: 5px; }}
            
            .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(190px, 1fr)); gap: 20px; max-width: 1200px; margin: 0 auto; }}
            .card {{ background: #fff; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 5px rgba(0,0,0,0.05); display: flex; flex-direction: column; transition: transform 0.2s; }}
            .card:hover {{ transform: translateY(-5px); box-shadow: 0 5px 15px rgba(0,0,0,0.15); }}
            
            .img-box {{ width: 100%; height: 190px; padding: 10px; display: flex; align-items: center; justify-content: center; border-bottom: 1px solid #eee; }}
            .img-box img {{ max-width: 100%; max-height: 100%; object-fit: contain; }}
            
            .info {{ padding: 15px; flex-grow: 1; display: flex; flex-direction: column; justify-content: space-between; }}
            .title {{ font-size: 14px; color: #333; margin-bottom: 10px; height: 40px; overflow: hidden; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; }}
            .price {{ color: #d0021b; font-weight: bold; font-size: 18px; }}
            
            .btn {{ background: var(--primary); color: #fff; text-decoration: none; padding: 10px; text-align: center; border-radius: 5px; font-weight: 600; margin-top: 10px; display: block; }}
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
                    <div class="price">{p['price_display']}</div>
                    <a href="{p['link']}" class="btn" target="_blank">Mua Ngay</a>
                </div>
            </div>
        """
    html += "</div></body></html>"
    return html

def chay_ngay_di():
    print("🚀 ĐANG KHỞI ĐỘNG FINAL BOSS 10.0 (SIÊU LỌC)...")
    
    try:
        print("⏳ Đang tải dữ liệu...")
        r = requests.get(LINK_CSV, timeout=60)
        r.encoding = 'utf-8'
        reader = csv.DictReader(io.StringIO(r.text))
        
        clean_products = []
        
        # 1. WHITELIST (TỪ KHÓA KÉP - CHỈ LẤY NẾU CHÍNH XÁC)
        # Bỏ các từ đơn như "Kẹp", "Mực" để tránh dính Honda, Đồ ăn
        WHITE_LIST = [
            "bút bi", "bút chì", "bút gel", "bút nước", "bút xóa", "bút nhớ", "bút dạ", "bút lông",
            "giấy a4", "giấy in", "giấy note", "giấy bìa", "giấy than",
            "vở ô ly", "vở kẻ ngang", "vở học sinh", "sổ tay", "sổ da", "sổ lò xo",
            "file còng", "file lá", "túi clear bag", "bìa hồ sơ", 
            "kẹp giấy", "kẹp bướm", "kẹp tài liệu", "ghim bấm", "dập ghim",
            "băng dính", "băng keo", "hồ dán", "keo dán giấy", "thước kẻ", "gọt chì", "tẩy chì",
            "máy tính bỏ túi", "hộp bút", "balo học sinh"
        ]

        # 2. BLACKLIST (DANH SÁCH CẤM - KHÔI PHỤC ĐẦY ĐỦ)
        BLACK_LIST = [
            "honda", "yamaha", "suzuki", "xe máy", "ô tô", "phụ tùng", "lốp", "nhớt", "gác chân", "pô xe",
            "mực khô", "mực rim", "mực tẩm", "râu mực", "ăn vặt", "bánh", "kẹo", "thực phẩm", "đồ ăn", "mắm", "muối",
            "kẻ mắt", "kẻ mày", "trang điểm", "son", "phấn", "kem", "serum", "dưỡng da",
            "áo", "quần", "váy", "giày", "dép", "thời trang", "túi xách",
            "đồ chơi", "siêu nhân", "robot", "lego", "búp bê",
            "hết hàng", "bỏ mẫu", "liên hệ"
        ]

        print("⚙️ Đang lọc kỹ từng món (Chỉ lấy Từ Khóa Kép)...")

        for row in reader:
            ten = row.get('name', '').lower()
            
            # KIỂM TRA 1: PHẢI CÓ TỪ KHÓA CHUẨN (WHITELIST)
            if not any(good in ten for good in WHITE_LIST):
                continue # Không có từ chuẩn -> Bỏ qua
            
            # KIỂM TRA 2: KHÔNG ĐƯỢC CÓ TỪ CẤM (BLACKLIST)
            if any(bad in ten for bad in BLACK_LIST):
                continue # Dính từ cấm -> Bỏ qua ngay

            # KIỂM TRA 3: GIÁ TIỀN
            gia_val = xuly_gia_chuan(row.get('price'))
            if gia_val < 3000: continue # Quá rẻ (Rác)
            if gia_val > 1000000: continue # Quá đắt (Giá ảo/Sai lệch)

            # ĐẠT CHUẨN -> THÊM VÀO DANH SÁCH
            clean_products.append({
                "name": row.get('name'),
                "price_val": gia_val,
                "price_display": "{:,.0f}₫".format(gia_val).replace(",", "."),
                "image": row.get('image', '').split(',')[0].strip(' []"'),
                "link": tao_link_aff(row.get('url'))
            })

        # Lấy 100 món đầu tiên
        final_list = clean_products[:100]
        
        print(f"✅ Đã tìm thấy {len(final_list)} món VPP SẠCH SẼ (Không Honda/Không Râu mực).")

        # Lưu file
        with open(FILE_JSON, "w", encoding="utf-8") as f:
            json.dump(final_list, f, ensure_ascii=False, indent=4)
        
        html_content = tao_web_html(final_list)
        with open("index.html", "w", encoding="utf-8") as f:
            f.write(html_content)
            
        print("☁️ Đang cập nhật lên Github...")
        os.system("git add .")
        os.system('git commit -m "Final Boss 10.0 Clean"')
        os.system("git push")
        print("🎉 XONG! Vui lòng đợi 2 phút rồi vào web bấm CTRL + F5.")

    except Exception as e:
        print(f"❌ Lỗi: {e}")

if __name__ == "__main__":
    chay_ngay_di()