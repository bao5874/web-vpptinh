import json
import os

# --- CẤU HÌNH QUAN TRỌNG ---
DATA_FILE = 'products.json'
# Sửa đường dẫn để ghi đè đúng vào file bạn đang xem trong thư mục dist
OUTPUT_FILE = 'dist/index.html' 

def load_products():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def generate_html(products):
    # Đảm bảo thư mục dist tồn tại
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

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
            <h1>VPP Tịnh</h1>
            <p class="slogan">🌿 Bình An Trao Tay 🌿</p>
        </header>

        <div class="product-grid">
    """

    for p in products:
        # THÊM referrerpolicy VÀO THẺ IMG
        html_content += f"""
            <div class="product-card">
                <img src="{p['image']}" referrerpolicy="no-referrer" alt="{p['name']}" class="product-image" loading="lazy">
                <div class="product-info">
                    <h3 class="product-title">{p['name']}</h3>
                    <div class="product-price">{p['price']}</div>
                    <a href="{p['link']}" class="btn-buy" target="_blank">Mua Ngay</a>
                </div>
            </div>
        """

    html_content += """
        </div>

        <div class="floating-contact">
            <a href="https://zalo.me/0931736266" class="contact-btn zalo-btn" target="_blank">Z</a>
            <a href="tel:0931736266" class="contact-btn phone-btn">📞</a>
        </div>

    </body>
    </html>
    """
    
    return html_content

def main():
    print("🔨 Đang xây dựng web (Ghi đè vào thư mục dist)...")
    products = load_products()
    html = generate_html(products)
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"✅ XONG! Đã cập nhật file: {OUTPUT_FILE}")
    print("👉 Bạn hãy quay lại trình duyệt và tải lại trang (F5) ngay nhé!")

if __name__ == "__main__":
    main()