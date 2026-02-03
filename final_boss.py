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

# 1. CHẶN THEO NGÀNH HÀNG (CATEGORY) - QUAN TRỌNG NHẤT
CATEGORY_CAM = [
    "sắc đẹp", "trang điểm", "mỹ phẩm", "chăm sóc da", "sức khỏe", # Chặn mỹ phẩm
    "xe", "mô tô", "ô tô", "phụ tùng", # Chặn xe
    "đồ chơi", "mẹ và bé", "thời trang", "giày", "dép", "túi", "ví", "quần", "áo",
    "điện thoại", "phụ kiện", "ốp lưng", "cáp sạc", "gia dụng", "nhà cửa"
]

# 2. CHẶN THEO TÊN (BLACKLIST CHI TIẾT)
NAME_CAM = [
    "kẻ mắt", "kẻ mày", "chân mày", "chuốt mi", "mascara", "eyeliner", "brow", "shadow", # Mỹ phẩm mắt
    "son", "lip", "phấn", "kem nền", "che khuyết điểm", "tẩy trang", "bông tẩy", "serum", "mụn",
    "bánh", "kẹo", "ăn vặt", "đồ ăn", "thực phẩm", "mắm", "muối",
    "honda", "yamaha", "winner", "exciter", "dream", "wave", # Xe cộ
    "lego", "robot", "siêu nhân", "lắp ráp"
]

# 3. CHỈ LẤY NHỮNG TỪ NÀY (WHITELIST)
TU_KHOA_DUYET = [
    "bút bi", "bút chì", "bút gel", "bút nước", "bút ký", "bút xóa", "bút nhớ", "bút dạ quang", "bút lông bảng", "ngòi bút",
    "giấy a4", "giấy in", "giấy photo", "giấy note", "giấy nhớ", "giấy bìa", "giấy than",
    "vở ô ly", "vở kẻ ngang", "vở học sinh", "vở ghi",
    "sổ tay", "sổ da", "sổ lò xo", "sổ ghi chép",
    "file còng", "file lá", "túi clear bag", "kẹp giấy", "kẹp bướm", "ghim bấm", "dập ghim",
    "băng dính", "băng keo", "hồ dán", "keo dán",
    "thước kẻ", "compa", "ê ke", "bộ thước",
    "máy tính bỏ túi", "máy tính casio", "máy tính vinacal",
    "bảng tên", "dây đeo thẻ", "khay đựng tài liệu", "hộp cắm bút", "balo", "cặp sách"
]

def check_hang_chuan(row):
    ten_sp = row.get('name', '').lower()
    danh_muc = row.get('category', '').lower()
    
    # BƯỚC 1: SOI NGÀNH HÀNG (CATEGORY)
    # Nếu ngành hàng chứa từ cấm (ví dụ: "Sức khỏe & Sắc đẹp") -> LOẠI NGAY
    for cat in CATEGORY_CAM:
        if cat in danh_muc:
            # print(f"❌ Loại vì sai ngành: {ten_sp} ({danh_muc})") # Bật dòng này nếu muốn xem chi tiết
            return False

    # BƯỚC 2: SOI TÊN SẢN PHẨM (BLACKLIST)
    # Nếu tên có "kẻ mắt", "kẻ mày"... -> LOẠI NGAY
    for bad_word in NAME_CAM:
        if bad_word in ten_sp:
            return False

    # BƯỚC 3: KIỂM TRA GIÁ
    try:
        gia = float(row.get('price', 0))
        if gia < 3000: return False 
    except:
        return False

    # BƯỚC 4: SOI TỪ KHÓA CHUẨN (WHITELIST)
    for good_word in TU_KHOA_DUYET:
        if good_word in ten_sp:
            return True # Đã qua 3 cửa ải trên mà có từ khóa này -> LẤY

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
    print("🚀 ĐANG CHẠY BỘ LỌC 'BỨC TƯỜNG LỬA' (Cực Gắt)...")
    
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
        
        print("⚙️ Đang quét và loại bỏ Mỹ Phẩm/Đồ Chơi/Xe Cộ...")
        
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
                    # In ra sản phẩm LẤY được để bạn yên tâm
                    print(f"✅ LẤY: {row.get('name')[:40]}...")
            
            if count >= 60: break # Lấy đủ 60 món thì dừng
            if tong_so > 30000: break # Quét tối đa 30k dòng

        print(f"\n📊 Kết quả: Quét {tong_so} dòng -> Lấy được {len(san_pham_list)} món VPP CHUẨN.")

        with open(FILE_JSON, "w", encoding="utf-8") as f:
            json.dump(san_pham_list, f, ensure_ascii=False, indent=4)
            
        html_content = tao_web_html(san_pham_list)
        with open("index.html", "w", encoding="utf-8") as f:
            f.write(html_content)
            
        print("☁️ Đang đẩy lên mạng...")
        os.system("git add .")
        os.system('git commit -m "Loc sach se 100%"')
        os.system("git push")
        print("🎉 XONG! Bạn vào web kiểm tra ngay nhé!")

    except Exception as e:
        print(f"❌ Lỗi: {e}")

if __name__ == "__main__":
    chay_ngay_di()