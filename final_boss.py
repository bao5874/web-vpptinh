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
LOGO_URL = "https://cdn-icons-png.flaticon.com/512/3225/3225194.png"
LINK_CSV = "http://datafeed.accesstrade.me/shopee.vn.csv"
FILE_JSON = "products.json"
BASE_AFF_URL = "https://go.isclix.com/deep_link/v6/6906519896943843292/4751584435713464237?sub4=oneatweb&utm_source=shopee&utm_campaign=sansale&url_enc="

# CHẶN RÁC
JUNK_BLACKLIST = [
    "hết hàng", "bỏ mẫu", "ngừng kinh doanh", "tạm hết", "liên hệ",
    "honda", "yamaha", "suzuki", "xe máy", "ô tô", "lốp", "nhớt", "pô",
    "mực khô", "mực rim", "hàng tươi sống", "đông lạnh",
    "voucher", "nạp thẻ", "sim", "sex toy", "người lớn"
]

def tao_link_aff(url_goc):
    if not url_goc: return "#"
    try:
        encoded = base64.b64encode(url_goc.strip().encode("utf-8")).decode("utf-8")
        return f"{BASE_AFF_URL}{encoded}"
    except:
        return url_goc

def tinh_gia_thuc(gia_goc_raw, discount_raw):
    """
    Hàm tính giá sau khi giảm
    Input: Giá gốc (100000), Discount (0.2 hoặc 20%)
    Output: Giá thực (80000)
    """
    try:
        # 1. Xử lý giá gốc
        gia_str = str(gia_goc_raw).split('.')[0] # Bỏ số thập phân thừa
        numbers = re.findall(r'\d+', gia_str)
        if not numbers: return 0
        gia_goc = float("".join(numbers))
        
        # 2. Xử lý phần trăm giảm
        try:
            d_str = str(discount_raw).replace('%', '')
            discount_val = float(d_str)
            # Nếu discount > 1 (ví dụ 20 nghĩa là 20%), ta chia 100
            if discount_val > 1:
                discount_val = discount_val / 100
        except:
            discount_val = 0

        # 3. Tính giá sau giảm
        gia_giam = gia_goc * (1 - discount_val)
        
        return gia_goc, gia_giam, discount_val * 100
    except:
        return 0, 0, 0

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
            :root {{ --primary: #d0011b; --bg: #f5f5f5; }}
            body {{ font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; background: var(--bg); margin: 0; padding: 20px; }}
            
            .header {{ text-align: center; background: white; padding: 20px; border-radius: 4px; margin-bottom: 20px; border-bottom: 3px solid var(--primary); }}
            .logo-img {{ width: 60px; height: 60px; object-fit: contain; display: block; margin: 0 auto 10px; }}
            h1 {{ color: var(--primary); margin: 0; font-size: 24px; text-transform: uppercase; }}
            
            .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(190px, 1fr)); gap: 10px; max-width: 1200px; margin: 0 auto; }}
            .card {{ background: white; border-radius: 2px; overflow: hidden; box-shadow: 0 1px 2px rgba(0,0,0,0.1); display: flex; flex-direction: column; transition: transform 0.1s; position: relative; }}
            .card:hover {{ transform: translateY(-2px); box-shadow: 0 4px 8px rgba(0,0,0,0.1); border: 1px solid var(--primary); }}
            
            .discount-tag {{ position: absolute; top: 0; right: 0; background: rgba(255,212,36,.9); color: #ec3814; padding: 4px 8px; font-weight: bold; font-size: 12px; }}
            
            .img-box {{ width: 100%; height: 190px; padding: 0; display: flex; align-items: center; justify-content: center; }}
            .img-box img {{ max-width: 100%; max-height: 100%; object-fit: cover; }}
            
            .info {{ padding: 10px; flex: 1; display: flex; flex-direction: column; justify-content: space-between; }}
            .title {{ font-size: 12px; color: #333; margin-bottom: 5px; line-height: 1.4em; height: 2.8em; overflow: hidden; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; }}
            
            .price-box {{ margin-bottom: 5px; }}
            .old-price {{ color: #999; text-decoration: line-through; font-size: 12px; margin-right: 5px; }}
            .new-price {{ color: var(--primary); font-weight: bold; font-size: 16px; }}
            
            .btn {{ background: var(--primary); color: white; text-decoration: none; padding: 8px; text-align: center; font-size: 14px; border-radius: 2px; display: block; }}
            .btn:hover {{ background: #a50216; }}
        </style>
    </head>
    <body>
        <div class="header">
            <img src="{LOGO_URL}" alt="Logo" class="logo-img">
            <h1>TỊNH SHOP DEAL HOT</h1>
            <p>Cập nhật lúc: {v}</p>
        </div>
        <div class="grid">
    """
    for p in products:
        discount_html = f'<div class="discount-tag">-{int(p["percent"])}%</div>' if p["percent"] > 0 else ""
        old_price_html = f'<span class="old-price">{p["old_price"]}</span>' if p["percent"] > 0 else ""
        
        html += f"""
            <div class="card">
                {discount_html}
                <div class="img-box"><img src="{p['image']}" loading="lazy"></div>
                <div class="info">
                    <div class="title">{p['name']}</div>
                    <div class="price-box">
                        {old_price_html}
                        <span class="new-price">{p['new_price']}</span>
                    </div>
                    <a href="{p['link']}" class="btn" target="_blank">Mua Ngay</a>
                </div>
            </div>
        """
    html += "</div></body></html>"
    return html

def chay_ngay_di():
    print("🚀 ĐANG CHẠY FINAL BOSS 22.0 (TÍNH LẠI GIÁ GIẢM)...")
    try:
        print("⏳ Đang tải dữ liệu...")
        r = requests.get(LINK_CSV, timeout=60)
        
        lines = r.text.splitlines()
        header = [h.replace('"', '').strip() for h in lines[0].split(',')]
        reader = csv.DictReader(lines[1:], fieldnames=header)
        
        clean_products = []
        
        print("⚙️ Đang tính toán giá thực tế...")
        
        count_debug = 0
        for row in reader:
            ten = row.get('name', '').lower()
            if any(bad in ten for bad in JUNK_BLACKLIST): continue

            # --- TÍNH TOÁN GIÁ ---
            gia_goc_raw = row.get('price')
            discount_raw = row.get('discount', 0)
            
            gia_goc, gia_giam, phan_tram = tinh_gia_thuc(gia_goc_raw, discount_raw)
            
            # LỌC:
            # Chỉ lấy món giá thực > 5k và < 10 triệu
            if gia_giam < 5000 or gia_giam > 10000000: continue
            # Chỉ lấy món có giảm giá (để hấp dẫn)
            if phan_tram < 1: continue 

            # Debug xem giá tính đúng chưa
            if count_debug < 3:
                print(f"💰 {row.get('name')[:20]}... | Gốc: {gia_goc:,.0f} | Giảm: {phan_tram:.0f}% -> Còn: {gia_giam:,.0f}")
                count_debug += 1

            clean_products.append({
                "name": row.get('name'),
                "old_price": "{:,.0f}₫".format(gia_goc).replace(",", "."),
                "new_price": "{:,.0f}₫".format(gia_giam).replace(",", "."),
                "percent": phan_tram,
                "image": row.get('image', '').split(',')[0].strip(' []"'),
                "link": tao_link_aff(row.get('url'))
            })

        # Sắp xếp: Ưu tiên giảm giá sâu nhất
        clean_products.sort(key=lambda x: x['percent'], reverse=True)

        final_list = clean_products[:100]
        print(f"✅ Tìm thấy {len(final_list)} sản phẩm ĐANG SALE.")

        with open(FILE_JSON, "w", encoding="utf-8") as f:
            json.dump(final_list, f, ensure_ascii=False, indent=4)
        
        with open("index.html", "w", encoding="utf-8") as f:
            f.write(tao_web_html(final_list))
        
        print("👉 Đang mở web kiểm tra...")
        webbrowser.open("file://" + os.path.realpath("index.html"))
        
        print("\n" + "="*50)
        print("HÃY KIỂM TRA GIÁ:")
        print("Bạn sẽ thấy giá cũ bị gạch ngang (ví dụ: 100.000₫)")
        print("Và giá mới màu đỏ to hơn (ví dụ: 80.000₫)")
        print("="*50 + "\n")
        
        chon = input("Gõ 'y' và Enter để đẩy lên Github: ")
        if chon.lower() == 'y':
            print("☁️ Đang cập nhật lên Github...")
            os.system("git add .")
            os.system('git commit -m "V22 Fix Discount Price"')
            os.system("git push")
            print("✅ XONG! F5 vpptinh.com nhé.")
        else:
            print("❌ Đã hủy.")

    except Exception as e:
        print(f"❌ Lỗi: {e}")

if __name__ == "__main__":
    chay_ngay_di()