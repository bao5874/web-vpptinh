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
BASE_AFF_URL = f"https://go.isclix.com/deep_link/v6/{CAMPAIGN_ID}/{ACCESSTRADE_ID}?sub4=oneatweb&url_enc="

# Từ khóa để nhận diện Văn Phòng Phẩm (VPP)
VPP_KEYWORDS = ["bút", "vở", "sổ", "giấy", "kẹp", "thước", "túi", "balo", "máy tính", "băng dính", "ghim", "hộp bút"]
# Từ khóa loại trừ để tránh "Bút kẻ mắt"
CANT_TAKE = ["mắt", "mày", "môi", "son", "kem", "makeup", "trang điểm", "da", "nám", "mụn"]

def tao_link_aff(url_goc):
    if not url_goc: return "#"
    encoded = base64.b64encode(url_goc.strip().encode("utf-8")).decode("utf-8")
    return f"{BASE_AFF_URL}{encoded}"

def chay_lay_top_60():
    print("🔥 ĐANG SĂN 60 MẶT HÀNG VPP BÁN CHẠY NHẤT...")
    try:
        r = requests.get(LINK_CSV, timeout=60)
        r.encoding = 'utf-8'
        reader = csv.DictReader(io.StringIO(r.text))
        
        all_products = []
        
        for row in reader:
            ten = row.get('name', '').lower()
            # Lấy số lượng đã bán (Cột này thường tên là 'sales' hoặc 'total_sales')
            # Nếu không có, chúng ta sẽ lọc theo độ ưu tiên trong file
            sales_raw = row.get('sales', '0') 
            try:
                sales = int(sales_raw)
            except:
                sales = 0

            # KIỂM TRA ĐIỀU KIỆN
            la_vpp = any(word in ten for word in VPP_KEYWORDS)
            khong_phai_my_pham = not any(bad in ten for bad in CANT_TAKE)

            if la_vpp and khong_phai_my_pham:
                all_products.append({
                    "name": row.get('name'),
                    "price": row.get('price', '0'),
                    "sales": sales, # Lưu lại để sắp xếp
                    "image": row.get('image', '').split(',')[0].strip(' []"'),
                    "url": row.get('url')
                })

        # SẮP XẾP THEO SỐ LƯỢNG BÁN (Cao nhất lên đầu)
        # Nếu file không có cột sales, nó sẽ giữ nguyên thứ tự ưu tiên của Shopee
        all_products.sort(key=lambda x: x['sales'], reverse=True)

        # CHỈ LẤY 60 MÓN ĐẦU BẢNG
        top_60 = []
        for p in all_products[:60]:
            top_60.append({
                "name": p['name'],
                "price": "{:,.0f}₫".format(float(p['price'])).replace(",", "."),
                "image": p['image'],
                "link": tao_link_aff(p['url'])
            })

        with open(FILE_JSON, "w", encoding="utf-8") as f:
            json.dump(top_60, f, ensure_ascii=False, indent=4)
        
        print(f"✅ Thành công! Đã hốt được {len(top_60)} siêu phẩm bán chạy.")
        
        # Đẩy lên GitHub
        os.system("git add .")
        os.system('git commit -m "Cap nhat Top 60 ban chay"')
        os.system("git push")

    except Exception as e:
        print(f"❌ Lỗi: {e}")

if __name__ == "__main__":
    chay_lay_top_60()