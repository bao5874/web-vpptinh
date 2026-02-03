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

# 1. TỪ KHÓA DUYỆT (Bắt buộc phải là CỤM TỪ RÕ RÀNG)
# Tuyệt đối không để từ đơn như "bút", "giấy", "kẹp" đứng một mình
TU_KHOA_DUYET = [
    # Nhóm Bút
    "bút bi", "bút chì", "bút gel", "bút nước", "bút lông", "bút dạ", "bút xóa", "bút nhớ", "bút highlight", "ngòi bút", "hộp bút",
    # Nhóm Giấy/Vở
    "giấy a4", "giấy in", "giấy note", "giấy nhớ", "giấy than", "giấy bìa", "vở kẻ ngang", "vở ô ly", "vở học sinh", "sổ tay", "sổ lò xo", "sổ da",
    # Nhóm File/Kẹp
    "file còng", "file lá", "file đục lỗ", "túi clear bag", "bìa hồ sơ", "bìa trình ký", "bìa nút", "kẹp giấy", "kẹp bướm", "kẹp tài liệu", "ghim bấm", "ghim cài",
    # Nhóm Dụng cụ
    "băng keo văn phòng", "băng dính trong", "hồ dán giấy", "keo dán giấy", "thước kẻ", "thước eke", "compa", "gọt chì", "chuốt chì", "tẩy chì", "gôm tẩy",
    # Nhóm Máy/Khác
    "máy tính bỏ túi", "máy tính casio", "máy tính vinacal", "khay đựng tài liệu", "hộp cắm bút", "bảng tên", "dây đeo thẻ"
]

# 2. TỪ KHÓA CẤM (BLACKLIST) - Gặp là diệt
TU_KHOA_CAM = [
    # Đồ ăn (Diệt bánh sandwich, kẹo, mắm...)
    "bánh", "kẹo", "ăn vặt", "thực phẩm", "mắm", "muối", "gia vị", "đồ ăn", "nấu", "bếp", "nướng", "chiên", "sữa", "trà", "cà phê",
    # Xe cộ (Diệt phụ tùng Honda, Yamaha...)
    "xe máy", "ô tô", "honda", "yamaha", "phụ tùng", "lốp", "nhớt", "gác chân", "pô", "đèn xe", "còi", "xi nhan", "baga", "tay thắng",
    # Đồ chơi (Diệt siêu nhân, robot...)
    "đồ chơi", "siêu nhân", "lắp ráp", "lego", "robot", "búp bê", "thú bông", "game",
    # Thời trang/Mỹ phẩm (Diệt kẹp tóc, quần áo...)
    "tóc", "dầu gội", "sữa tắm", "kem dưỡng", "son", "phấn", "áo", "quần", "váy", "giày", "dép", "túi xách", "thời trang", "trang sức",
    # Khác
    "vệ sinh", "tã", "bỉm", "khăn ướt", "giấy vệ sinh"
]

def check_hang_chuan(row):
    ten_sp = row.get('name', '').lower()
    danh_muc = row.get('category', '').lower()
    
    # 1. BƯỚC LOẠI TRỪ (QUAN TRỌNG NHẤT)
    for tu_cam in TU_KHOA_CAM:
        if tu_cam in ten_sp:
            return False # Có từ cấm -> Vứt
            
    # 2. LOẠI HÀNG GIÁ RẺ BÈO (Thường là rác phụ kiện)
    try:
        gia = float(row.get('price', 0))
        if gia < 3000: return False # Dưới 3k vứt
    except:
        return False

    if "hết hàng" in ten_sp: return False

    # 3. BƯỚC DUYỆT (Phải khớp chính xác CỤM TỪ)
    
    # Ưu tiên 1: Nếu danh mục chuẩn xác
    if "văn phòng phẩm" in danh_muc or "thiết bị văn phòng" in danh_muc or "dụng cụ học sinh" in danh_muc:
        # Vẫn phải check lại tên để tránh "kẹp tóc" lọt vào danh mục VPP (Shopee hay xếp sai)
        if "tóc" in ten_sp or "xe" in ten_sp: return False
        return True

    # Ưu tiên 2: Soi tên sản phẩm với danh sách DUYỆT (từ khóa kép)
    for tu_khoa in TU_KHOA_DUYET:
        if tu_khoa in ten_sp:
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
    print("🚀 ĐANG CHẠY CHẾ ĐỘ 'BỘ LỌC QUÂN ĐỘI'...")
    
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
        
        print("⚙️ Đang lọc cực gắt (Chỉ lấy Từ Khóa Kép)...")
        
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

        print(f"📊 Đã quét {tong_so} món. Lấy được {len(san_pham_list)} món CHUẨN.")

        with open(FILE_JSON, "w", encoding="utf-8") as f:
            json.dump(san_pham_list, f, ensure_ascii=False, indent=4)
            
        html_content = tao_web_html(san_pham_list)
        with open("index.html", "w", encoding="utf-8") as f:
            f.write(html_content)
            
        print("☁️ Đang đẩy lên mạng...")
        os.system("git add .")
        os.system('git commit -m "Loc bang tu khoa kep"')
        os.system("git push")
        print("🎉 XONG! Vào kiểm tra lại xem còn sót tên giặc nào không!")

    except Exception as e:
        print(f"❌ Lỗi: {e}")

if __name__ == "__main__":
    chay_ngay_di()