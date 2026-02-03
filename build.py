import json
import os
import shutil

def tim_kho_hang():
    """Hàm này sẽ đi lùng sục khắp nơi để tìm file products.json"""
    cac_cho_co_the_giau = [
        'products.json',           # Tìm ở ngay bên ngoài
        'data/products.json',      # Tìm trong thư mục data
        'web-banhang/products.json' # Tìm kỹ hơn chút nữa
    ]
    
    for duong_dan in cac_cho_co_the_giau:
        if os.path.exists(duong_dan):
            print(f"✅ ĐÃ TÌM THẤY KHO HÀNG TẠI: {duong_dan}")
            return duong_dan
            
    return None

def load_products(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            print(f"📊 Đã đọc được {len(data)} sản phẩm.")
            return data
    except Exception as e:
        print(f"❌ File có lỗi, không đọc được: {e}")
        return []

def generate_html(products):
    # CSS và HTML giao diện (Giữ nguyên giao diện đẹp)
    css = """
    <style>
        :root { --primary-color: #d4a373; --bg-color: #fefae0; --text-color: #333; --card-bg: #fff; }
        body { font-family: 'Segoe UI', sans-serif; background-color: var(--bg-color); margin: 0; padding: 20px; color: var(--text-color); }
        header { text-align: center; margin-bottom: 40px; padding: 20px; background: #fff; border-radius: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }
        h1 { color: #8B4513; margin: 0; font-size: 2.5em; text-transform: uppercase; letter-spacing: 2px; }
        .slogan { font-style: italic; color: #666; margin-top: 5px; font-size: 1.1em; }
        .product-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 20px; max-width: 1200px; margin: 0 auto; }
        .product-card { background: var(--card-bg); border-radius: 12px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.1); transition: transform 0.3s ease; display: flex; flex-direction: column; border: 1px solid #eee; }
        .product-card:hover { transform: translateY(-5px); box-shadow: 0 8px 15px rgba(0,0,0,0.15); }
        .product-image { width: 100%; height: 160px; object-fit: contain; padding: 10px; background: #fff; box-sizing: border-box; }
        .product-info { padding: 15px; flex-grow: 1; display: flex; flex-direction: column; justify-content: space-between; }
        .product-title { font-size: 1em; margin: 0 0 10px 0; color: #333; line-height: 1.4; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
        .product-price { font-size: 1.2em; color: #e63946; font-weight: bold; margin-bottom: 15px; }
        .btn-buy { display: block; width: 100%; padding: 10px; background-color: #2a9d8f; color: white; text-align: center; text-decoration: none; border-radius: 6px; font-weight: bold; transition: background 0.2s; }
        .btn-buy:hover { background-color: #21867a; }
        .floating-contact { position: fixed; bottom: 20px; right: 20px; z-index: 1000; display: flex; flex-direction: column; gap: 10px; }
        .contact-btn { width: 55px; height: 55px; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: white; text-decoration: none; box-shadow: 0 4px 10px rgba(0,0,0,0.3); font-weight: bold; font-size: 24px; transition: transform 0.2s; }
        .contact-btn:hover { transform: scale(1.1); }
        .zalo-btn { background-color: #0068FF; border: 2px solid white; }
        .phone-btn { background-color: #008000; border: 2px solid white; animation: shake 2s infinite; }
        @keyframes shake { 0%, 100% { transform: rotate(0deg); } 25% { transform: rotate(-10deg); } 75% { transform: rotate(10deg); } }
        @media (max-width: 600px) { .product-grid { grid-template-columns: repeat(2, 1fr); gap: 10px; } .product-image { height: 140px; } h1 { font-size: 1.8em; } }
    </style>
    """

    html_content = f"""
    <!DOCTYPE html>
    <html lang="vi">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <meta name="referrer" content="no-referrer"> 
        <title>VPP Tịnh - Bình An Trao Tay</title>
        {css}
    </head>
    <body>
        <header>
            <div style="display:flex;align-items:center;justify-content:center;gap:12px;">
                <img src="data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNTAiIGhlaWdodD0iNTAiIHZpZXdCb3g9IjAgMCA1MCA1MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48ZGVmcz48bGluZWFyR3JhZGllbnQgaWQ9ImcxIiB4MT0iMCUiIHkxPSIwJSIgeDI9IjEwMCUiIHkyPSIxMDAlIj48c3RvcCBvZmZzZXQ9IjAlIiBzdHlsZT0ic3RvcC1jb2xvcjojZDRhMzcyO3N0b3Atb3BhY2l0eToxIiAvPjxzdG9wIG9mZnNldD0iMTAwJSIgc3R5bGU9InN0b3AtY29sb3I6IzhCNDUxMztzdG9wLW9wYWNpdHk6MSIgLz48L2xpbmVhckdyYWRpZW50PjwvZGVmcz48Y2lyY2xlIGN4PSIyNSIgY3k9IjI1IiByPSIyNCIgZmlsbD0idXJsKCNnMSkiIHN0cm9rZT0iIzY1NDMyMSIgc3Ryb2tlLXdpZHRoPSIxIi8+PGNpcmNsZSBjeD0iMjUiIGN5PSIyNSIgcj0iMjIiIGZpbGw9IiNmNWU2ZDMiIG9wYWNpdHk9IjAuOSIvPjxwYXRoIGQ9Ik0yMCAzMCBMMzAgMTUiIHN0cm9rZT0iIzhCNDUxMyIgc3Ryb2tlLXdpZHRoPSIyIiBmaWxsPSJub25lIiBzdHJva2UtbGluZWNhcD0icm91bmQiLz48Y2lyY2xlIGN4PSIzMCIgY3k9IjE1IiByPSIyIiBmaWxsPSIjOEI0NTEzIi8+PHJlY3QgeD0iMTUiIHk9IjIwIiB3aWR0aD0iOCIgaGVpZ2h0PSIxMiIgZmlsbD0ibm9uZSIgc3Ryb2tlPSIjOEI0NTEzIiBzdHJva2Utd2lkdGg9IjEuNSIvPjxsaW5lIHgxPSIxNyIgeTE9IjIzIiB4Mj0iMjEiIHkyPSIyMyIgc3Ryb2tlPSIjOEI0NTEzIiBzdHJva2Utd2lkdGg9IjEiLz48bGluZSB4MT0iMTciIHkxPSIyNiIgeDI9IjIxIiB5Mj0iMjYiIHN0cm9rZT0iIzhCNDUxMyIgc3Ryb2tlLXdpZHRoPSIxIi8+PHJlY3QgeD0iMjgiIHk9IjI3IiB3aWR0aD0iMTAiIGhlaWdodD0iMyIgZmlsbD0ibm9uZSIgc3Ryb2tlPSIjOEI0NTEzIiBzdHJva2Utd2lkdGg9IjEuNSIvPjxsaW5lIHgxPSIzMCIgeTE9IjI2IiB4Mj0iMzAiIHkyPSIzMSIgc3Ryb2tlPSIjOEI0NTEzIiBzdHJva2Utd2lkdGg9IjEiLz48bGluZSB4MT0iMzMiIHkxPSIyNiIgeDI9IjMzIiB5Mj0iMzEiIHN0cm9rZT0iIzhCNDUxMyIgc3Ryb2tlLXdpZHRoPSIxIi8+PGxpbmUgeDE9IjM2IiB5MT0iMjYiIHgyPSIzNiIgeTI9IjMxIiBzdHJva2U9IiM4QjQ1MTMiIHN0cm9rZS13aWR0aD0iMSIvPjwvc3ZnPg==" alt="VPP Tịnh" style="height:50px;width:auto;">
                <div>
                    <h1>VPP Tịnh</h1>
                    <p class="slogan">🌿 Bình An Trao Tay 🌿</p>
                </div>
            </div>
        </header>

        <div class="product-grid">
    """

    count = 0
    for p in products:
        name = p.get('name', p.get('title', 'Sản phẩm không tên'))
        price = p.get('price', 'Liên hệ')
        image = p.get('image', p.get('img', 'https://via.placeholder.com/150'))
        link = p.get('link', p.get('url', '#'))
        
        html_content += f"""
            <div class="product-card">
                <img src="{image}" referrerpolicy="no-referrer" alt="{name}" class="product-image" loading="lazy">
                <div class="product-info">
                    <h3 class="product-title">{name}</h3>
                    <div class="product-price">{price}</div>
                    <a href="{link}" class="btn-buy" target="_blank">Mua Ngay</a>
                </div>
            </div>
        """
        count += 1

    html_content += """
        </div>
        <div class="floating-contact">
            <a href="https://zalo.me/0931736266" class="contact-btn zalo-btn" target="_blank">Z</a>
            <a href="tel:0931736266" class="contact-btn phone-btn">📞</a>
        </div>
    </body>
    </html>
    """
    return html_content, count

def main():
    print("🚀 BẮT ĐẦU XÂY DỰNG WEB...")
    
    # 1. Tìm kho hàng
    file_kho = tim_kho_hang()
    if not file_kho:
        print("❌ LỖI TO: Vẫn không tìm thấy file products.json đâu cả!")
        print("👉 GỢI Ý: Bạn hãy thử kéo file products.json ra thư mục ngoài cùng xem sao.")
        return

    # 2. Đọc dữ liệu
    products = load_products(file_kho)
    
    # 3. Tạo nội dung web
    html, count = generate_html(products)
    
    # 4. Ghi file ra 2 chỗ (Cho chắc ăn)
    # Chỗ 1: Ngay thư mục gốc
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html)
    
    # Chỗ 2: Trong thư mục dist (Nếu có)
    if os.path.exists('dist'):
        # ensure dist exists and write index
        with open('dist/index.html', 'w', encoding='utf-8') as f:
            f.write(html)

        # copy static assets into dist so logo and css are available
        dist_static = os.path.join('dist', 'static')
        try:
            if os.path.exists(dist_static):
                shutil.rmtree(dist_static)
            if os.path.exists('static'):
                shutil.copytree('static', dist_static)
        except Exception as e:
            print(f"⚠️ Không thể copy static vào dist/: {e}")

        print("✅ Đã lưu thêm một bản vào thư mục dist/index.html và copy static/")
    
    print(f"🎉 THÀNH CÔNG! Đã đưa {count} sản phẩm lên web.")
    print("👉 Hãy mở file index.html lên xem ngay nhé!")

if __name__ == "__main__":
    main()