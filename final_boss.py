import requests
import csv
import json
import io
import os
import base64

# --- CẤU HÌNH ---
LINK_CSV = "http://datafeed.accesstrade.me/shopee.vn.csv"
FILE_JSON = "products.json"

# Thông tin Affiliate của bạn
ACCESSTRADE_ID = "4751584435713464237"
CAMPAIGN_ID = "6906519896943843292" 
# Link gốc bạn cung cấp (đã bỏ phần mã hóa ở đuôi để code tự điền sản phẩm vào)
BASE_AFF_URL = f"https://go.isclix.com/deep_link/v6/{CAMPAIGN_ID}/{ACCESSTRADE_ID}?sub4=oneatweb&utm_source=shopee&utm_campaign=v%C4%83n+ph%C3%B2ng+ph%E1%BA%A9m&url_enc="

def tao_link_aff(url_san_pham):
    # Mã hóa link sản phẩm cụ thể sang Base64
    url_bytes = url_san_pham.encode("utf-8")
    base64_url = base64.b64encode(url_bytes).decode("utf-8")
    return f"{BASE_AFF_URL}{base64_url}"

def chay_loc_chuan_100():
    print("🛡️ Đang lọc sản phẩm theo ngành hàng Văn Phòng Phẩm...")
    try:
        r = requests.get(LINK_CSV, timeout=60)
        r.encoding = 'utf-8'
        reader = csv.DictReader(io.StringIO(r.text))
        
        products = []
        count = 0
        
        for row in reader:
            ten = row.get('name', '').lower()
            cat = row.get('category', '').lower() # Cột danh mục
            
            # ĐIỀU KIỆN LỌC CỨNG: 
            # Chỉ lấy nếu trong 'category' có chữ 'Văn Phòng Phẩm' 
            # HOẶC 'Sách' HOẶC 'Quà Tặng'
            vpp_keywords = ['văn phòng phẩm', 'stationery', 'dụng cụ học tập', 'thiết bị trường học']
            la_vpp = any(word in cat for word in vpp_keywords)
            
            # LOẠI TRỪ MỸ PHẨM (Kẻ mắt, mày...)
            tu_cam = ['mắt', 'mày', 'son', 'phấn', 'kem', 'trang điểm', 'makeup']
            co_tu_cam = any(bad in ten for bad in tu_cam)

            if la_vpp and not co_tu_cam:
                url_goc = row.get('url')
                if url_goc:
                    products.append({
                        "name": row.get('name'),
                        "price": "{:,.0f}₫".format(float(row.get('price', 0))).replace(",", "."),
                        "image": row.get('image').split(',')[0].strip(' []"'),
                        "link": tao_link_aff(url_goc)
                    })
                    count += 1
            
            if count >= 80: break # Lấy 80 món đẹp nhất

        with open(FILE_JSON, "w", encoding="utf-8") as f:
            json.dump(products, f, ensure_ascii=False, indent=4)
        
        print(f"✅ Đã lọc xong! Tìm thấy {len(products)} món chuẩn VPP.")
        
        # Đẩy lên GitHub
        os.system("git add .")
        os.system('git commit -m "Loc bang Category ID triet de"')
        os.system("git push")

    except Exception as e:
        print(f"❌ Lỗi: {e}")

if __name__ == "__main__":
    chay_loc_chuan_100()