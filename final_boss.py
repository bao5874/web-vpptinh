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
BASE_AFF_URL = f"https://go.isclix.com/deep_link/v6/{CAMPAIGN_ID}/{ACCESSTRADE_ID}?sub4=web_tu_dong&url_enc="

# 1. DANH SÁCH DUYỆT (Ưu tiên những từ cụ thể)
TU_KHOA_DUYET = [
    "văn phòng phẩm", "nhà sách", "dụng cụ học sinh", "bút", "giấy a4", "giấy in", 
    "vở", "sổ tay", "file hồ sơ", "bìa còng", "kẹp giấy", "ghim bấm", "băng keo", 
    "thước kẻ", "mực viết", "kéo giấy", "hồ dán", "keo nước", "đế cắm bút", "khay tài liệu",
    "balo học sinh", "cặp sách", "gọt chì", "tẩy", "hộp bút", "giấy note"
]

# 2. DANH SÁCH CẤM (BLACKLIST) - NHÌN LÀ XÓA NGAY
# Dựa trên ảnh bạn gửi, mình đã thêm: xe, honda, bánh, đồ chơi, siêu nhân...
TU_KHOA_CAM = [
    # Đồ ăn / Thực phẩm
    "bánh", "kẹo", "thực phẩm", "ăn vặt", "mắm", "muối", "khô", "cơm", "sấy", "hạt", "trà", "sữa",
    # Xe cộ / Phụ tùng
    "xe", "honda", "yamaha", "phụ tùng", "lốp", "nhớt", "gác chân", "pô", "đèn", "còi", "pas", "ốc",
    # Đồ chơi / Trẻ em
    "đồ chơi", "siêu nhân", "lắp ghép", "robot", "búp bê", "thú bông", "lego",
    # Thời trang / Mỹ phẩm
    "áo", "quần", "váy", "giày", "dép", "túi xách", "son", "phấn", "kem", "dưỡng", "tóc", "ngực",
    # Đồ gia dụng / Tạp hóa
    "bếp", "nồi", "chảo", "dao", "thớt", "vệ sinh", "tắm", "gội", "giặt"
]

def check_hang_chuan(row):
    """Hàm kiểm tra kỹ lưỡng: Phải ĐÚNG VPP và KHÔNG PHẢI RÁC"""
    ten_sp = row.get('name', '').lower()
    danh_muc = row.get('category', '').lower() # Cột Danh mục
    
    # 1. BƯỚC LOẠI TRỪ (QUAN TRỌNG NHẤT)
    # Nếu tên sản phẩm chứa BẤT KỲ từ cấm nào -> XÓA NGAY
    for tu_cam in TU_KHOA_CAM:
        if tu_cam in ten_sp:
            return False
            
    # 2. KIỂM TRA GIÁ & TRẠNG THÁI
    # Loại bỏ hàng giá = 0 hoặc quá rẻ (thường là lỗi)
    try:
        gia = float(row.get('price', 0))
        if gia < 2000: return False # Dưới 2k thường là rác
    except:
        return False

    # Nếu tên có chữ "hết hàng" -> XÓA
    if "hết hàng" in ten_sp: return False

    # 3. BƯỚC CHỌN LỌC (Kết hợp Danh mục & Tên)
    # Cách 1: Nếu Cột Danh Mục có chữ "văn phòng phẩm" hoặc "nhà sách" -> LẤY
    if "văn phòng phẩm" in danh_muc or "nhà sách" in danh_muc:
        return True
        
    # Cách 2: Nếu tên sản phẩm chứa từ khóa duyệt
    for tu_khoa in TU_KHOA_DUYET:
        if tu_khoa in ten_sp:
            # Check lại lần cuối để tránh "Kẹp tóc" lọt lưới (dù đã lọc ở bước 1)
            if "tóc" in ten_sp or "xinh" in ten_sp: return False
            return True

    return False

def tao_link_kiem_tien(link_goc):
    if not link_goc: return "#"
    try:
        link_bytes = link_goc.strip().encode("utf-8")
        base64_str = base64.b64encode(link_bytes).decode("utf-8")
        return f"{BASE_AFF_URL}{base64_str}"
    except:
        return link_goc 

def xuly_gia(gia_raw):
    try:
        numbers = re.findall(r'\d+', str(gia_raw).replace('.', '').replace(',', ''))
        if numbers:
            gia = float(numbers[0])
            return "{:,.0f}₫".format(gia).replace(",", ".")
    except:
        pass
    return "Liên hệ"

def xuly_anh(anh_raw):
    if not anh_raw: return "https://via.placeholder.com/150"
    if "," in anh_raw: anh_raw = anh_raw.split(",")[0]
    if "|" in anh_raw: anh_raw = anh_raw.split("|")[0]
    anh_raw = anh_raw.replace('["', '').replace('"]', '').replace('"', '').strip()
    if anh_raw.startswith("http://"):
        anh_raw = anh_raw.replace("http://", "https://")
    return anh_raw

def tao_web_html(products):
    html = """
    <!DOCTYPE html>
    <html lang="vi">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <meta name="referrer" content="no-referrer"> 
        <title>VPP Tịnh - Bình An Trao Tay</title>
        <style>
            :root { --primary-color: #d4a373; --bg-color: #fefae0; }
            body { font-family: 'Segoe UI', sans-serif; background-color: var(--bg-color); margin: 0; padding: 20px; }
            header { text-align: center; margin-bottom: 40px; background: #fff; padding: 20px; border-radius: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }
            h1 { color: #8B4513; margin: 0; text-transform: uppercase; }
            .product-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 20px; max-width: 1200px; margin: 0 auto; }
            .product-card { background: #fff; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.1); transition: transform 0.2s; display: flex; flex-direction: column; }
            .product-card:hover { transform: translateY(-5px); }
            .product-image { width: 100%; height: 180px; object-fit: contain; padding: 10px; box-sizing: border-box; }
            .product-info { padding: 15px; flex-grow: 1; display: flex; flex-direction: column; justify-content: space-between; }
            .product-title { font-size: 0.95em; color: #333; margin: 0 0 10px 0; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; height: 2.8em; }
            .product-price { font-size: 1.2em; color: #e63946; font-weight: bold; margin-bottom: 10px; }
            .btn-buy { display: block; width: 100%; padding: 10px 0; background-color: #ee4d2d; color: white; text-align: center; text-decoration: none; border-radius: 4px; font-weight: bold; }
            .btn-buy:hover { background-color: #d73211; }
        </style>
    </head>
    <body>
        <header>
            <h1>VPP Tịnh</h1>
            <p>🌿 Chuyên Văn Phòng Phẩm Chất Lượng 🌿</p>
        </header>
        <div class="product-grid">
    """
    for p in products:
        html += f"""
            <div class="product-card">
                <img src="{p['image']}" alt="{p['name']}" class="product-image" loading="lazy">
                <div class="product-info">
                    <h3 class="product-title">{p['name']}</h3>
                    <div class="product-price">{p['price']}</div>
                    <a href="{p['link']}" class="btn-buy" target="_blank" rel="nofollow">Mua Ngay</a>
                </div>
            </div>
        """
    html += "</div></body></html>"
    return html

def chay_ngay_di():
    print("🚀 ĐANG CHẠY CHẾ ĐỘ 'KỶ LUẬT THÉP'...")
    
    try:
        print("⏳ Đang tải dữ liệu...")
        r = requests.get(LINK_CSV)
        r.encoding = 'utf-8'
        if r.status_code != 200: return
            
        f = io.StringIO(r.text)
        reader = csv.DictReader(f)
        
        san_pham_list = []
        count = 0
        tong_so = 0
        
        print("⚙️ Đang lọc bỏ Bánh kẹo, Xe cộ, Đồ chơi...")
        
        for row in reader:
            tong_so += 1
            if check_hang_chuan(row):
                link_goc = row.get('url', '')
                if link_goc:
                    san_pham_list.append({
                        "name": row.get('name', ''),
                        "price": xuly_gia(row.get('price', '0')),
                        "image": xuly_anh(row.get('image', '')),
                        "link": tao_link_kiem_tien(link_goc)
                    })
                    count += 1
            if count >= 60: break 

        print(f"📊 Đã quét {tong_so} món. Lấy được {len(san_pham_list)} món VPP SẠCH.")

        with open(FILE_JSON, "w", encoding="utf-8") as f:
            json.dump(san_pham_list, f, ensure_ascii=False, indent=4)
            
        html_content = tao_web_html(san_pham_list)
        with open("index.html", "w", encoding="utf-8") as f:
            f.write(html_content)
            
        # Tự động đẩy lên mạng
        print("☁️ Đang đẩy lên mạng...")
        os.system("git add .")
        os.system('git commit -m "Update loc sach 100 phan tram"')
        os.system("git push")
        print("🎉 XONG! Bạn hãy vào kiểm tra lại web nhé!")

    except Exception as e:
        print(f"❌ Lỗi: {e}")

if __name__ == "__main__":
    chay_ngay_di()