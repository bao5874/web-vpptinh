import requests
import csv
import json
import io
import os
import re
import base64 
import time

# --- CẤU HÌNH ---
# 1. Dán Link Logo của bạn vào giữa 2 dấu ngoặc kép bên dưới
LOGO_URL = "https://i.postimg.cc/6qhFryp7/logo.png" 
# (Nếu chưa có logo, cứ để nguyên link trên, nó là icon cái bút đẹp)

LINK_CSV = "http://datafeed.accesstrade.me/shopee.vn.csv"
FILE_JSON = "products.json"
ACCESSTRADE_ID = "4751584435713464237"
CAMPAIGN_ID = "6906519896943843292" 
BASE_AFF_URL = f"https://go.isclix.com/deep_link/v6/{CAMPAIGN_ID}/{ACCESSTRADE_ID}?sub4=web_tu_dong&utm_source=shopee&utm_campaign=vpp_tinh&url_enc="

def tao_link_aff(url_goc):
    if not url_goc: return "#"
    try:
        encoded = base64.b64encode(url_goc.strip().encode("utf-8")).decode("utf-8")
        return f"{BASE_AFF_URL}{encoded}"
    except:
        return url_goc

def xuly_gia_debug(gia_raw, ten_sp):
    """
    Hàm xử lý giá có báo cáo lỗi
    """
    try:
        gia_str = str(gia_raw).strip()
        # Lấy số đầu tiên tìm thấy
        numbers = re.findall(r'\d+', gia_str.replace('.', '').replace(',', ''))
        if not numbers: return 0
        
        gia_val = float(numbers[0])
        
        # Logic sửa giá ảo (quan trọng)
        # Nếu > 10 triệu -> chia 100
        if gia_val > 10000000: gia_val /= 100
        # Nếu > 2 triệu -> chia 10
        elif gia_val > 2000000: gia_val /= 10
            
        return gia_val
    except:
        return 0

def tao_web_html(products):
    timestamp = int(time.time()) # Kỹ thuật chống lưu cache
    
    html = f"""
    <!DOCTYPE html>
    <html lang="vi">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>VPP Tịnh - Văn Phòng Phẩm (Cập nhật: {timestamp})</title>
        <link rel="icon" href="{LOGO_URL}">
        <style>
            body {{ font-family: sans-serif; background: #f4f4f4; padding: 20px; }}
            .header {{ text-align: center; background: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; }}
            .logo {{ max-height: 100px; display: block; margin: 0 auto 10px; }}
            .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 15px; max-width: 1200px; margin: 0 auto; }}
            .card {{ background: white; padding: 10px; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); display: flex; flex-direction: column; }}
            .card img {{ width: 100%; height: 180px; object-fit: contain; }}
            .title {{ font-size: 14px; margin: 10px 0; height: 38px; overflow: hidden; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; }}
            .price {{ color: red; font-weight: bold; font-size: 16px; }}
            .btn {{ background: #2a9d8f; color: white; text-align: center; padding: 8px; text-decoration: none; border-radius: 5px; margin-top: auto; display: block; }}
        </style>
    </head>
    <body>
        <div class="header">
            <img src="{LOGO_URL}" alt="Logo" class="logo">
            <h1>VPP TỊNH</h1>
            <p>Danh sách cập nhật lúc: {timestamp}</p>
        </div>
        <div class="grid">
    """
    for p in products:
        html += f"""
            <div class="card">
                <img src="{p['image']}" loading="lazy">
                <div class="title">{p['name']}</div>
                <div class="price">{p['price_display']}</div>
                <a href="{p['link']}" class="btn" target="_blank">Mua Ngay</a>
            </div>
        """
    html += "</div></body></html>"
    return html

def chay_ngay_di():
    print("🔍 BẮT ĐẦU QUÉT LỖI...")
    
    try:
        print("⏳ Đang tải CSV...")
        r = requests.get(LINK_CSV, timeout=60)
        r.encoding = 'utf-8'
        reader = csv.DictReader(io.StringIO(r.text))
        
        good_products = []
        count_vpp = 0
        count_rac = 0
        count_gia_sai = 0
        
        # TỪ KHÓA AN TOÀN
        whitelist = ["bút", "giấy a4", "vở", "sổ", "kẹp", "thước", "băng dính", "hồ dán", "mực", "file", "bìa"]
        blacklist = ["kẻ mắt", "trang điểm", "son", "quần", "áo", "xe", "bánh", "kẹo", "hết hàng"]

        for row in reader:
            ten = row.get('name', '').lower()
            
            # 1. LỌC: Phải có từ khóa VPP
            if not any(w in ten for w in whitelist): 
                continue 
            
            # 2. CHẶN: Rác
            if any(bad in ten for bad in blacklist):
                count_rac += 1
                continue

            # 3. XỬ LÝ GIÁ
            gia_val = xuly_gia_debug(row.get('price'), ten)
            
            # Lọc giá: Chỉ lấy từ 2k đến 1 triệu
            if gia_val < 2000 or gia_val > 1000000:
                count_gia_sai += 1
                continue

            # NẾU QUA ĐƯỢC HẾT CÁC CỬA ẢI:
            count_vpp += 1
            good_products.append({
                "name": row.get('name'),
                "price_val": gia_val,
                "price_display": "{:,.0f}₫".format(gia_val).replace(",", "."),
                "image": row.get('image', '').split(',')[0].strip(' []"'),
                "link": tao_link_aff(row.get('url'))
            })

        # Lấy 60 món đầu tiên tìm thấy
        final_list = good_products[:60]
        
        print("-" * 30)
        print(f"📊 BÁO CÁO KẾT QUẢ QUÉT:")
        print(f"❌ Số món bị loại vì là Rác/Mỹ phẩm: {count_rac}")
        print(f"❌ Số món bị loại vì Giá ảo/Quá rẻ: {count_gia_sai}")
        print(f"✅ SỐ MÓN VPP CHUẨN TÌM THẤY: {count_vpp}")
        print("-" * 30)

        if len(final_list) == 0:
            print("⚠️ CẢNH BÁO: Không tìm thấy món nào! Có thể file CSV bị lỗi.")
        else:
            print(f"💾 Đang lưu {len(final_list)} sản phẩm vào web...")
            
            with open(FILE_JSON, "w", encoding="utf-8") as f:
                json.dump(final_list, f, ensure_ascii=False, indent=4)
            
            html_content = tao_web_html(final_list)
            with open("index.html", "w", encoding="utf-8") as f:
                f.write(html_content)
                
            print("🚀 ĐANG ĐẨY LÊN GITHUB (BẮT BUỘC)...")
            os.system("git add .")
            os.system('git commit -m "Force update with online logo"')
            os.system("git push")
            print("✅ XONG! Đợi 2 phút rồi vào web bấm CTRL + F5.")

    except Exception as e:
        print(f"❌ Lỗi nghiêm trọng: {e}")

if __name__ == "__main__":
    chay_ngay_di()