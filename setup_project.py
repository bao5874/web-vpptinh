import os

# Cấu trúc nội dung file (Tôi đã nhúng sẵn code mẫu vào đây luôn)
files_content = {
    # 1. FILE CẤU HÌNH
    "build.py": """import json
import os
import shutil
from jinja2 import Environment, FileSystemLoader

# Cấu hình
OUTPUT_DIR = 'dist'

def build():
    # 1. Khởi tạo môi trường
    if not os.path.exists('data/products.json'):
        print("❌ Lỗi: Thiếu file data/products.json")
        return

    env = Environment(loader=FileSystemLoader('templates'))
    
    # 2. Đọc dữ liệu
    print("📂 Đang đọc dữ liệu...")
    with open('data/products.json', 'r', encoding='utf-8') as f:
        products = json.load(f)

    # 3. Render HTML
    print(f"🔨 Đang build {len(products)} sản phẩm...")
    template = env.get_template('index.html')
    html_output = template.render(products=products)

    # 4. Xuất file
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Ghi index.html
    with open(os.path.join(OUTPUT_DIR, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(html_output)
    
    # Copy CSS
    css_dest = os.path.join(OUTPUT_DIR, 'static', 'css')
    os.makedirs(css_dest, exist_ok=True)
    shutil.copy('static/css/style.css', os.path.join(css_dest, 'style.css'))

    print(f"✅ THÀNH CÔNG! Mở file {OUTPUT_DIR}/index.html để xem.")

if __name__ == "__main__":
    build()
""",

    # 2. DỮ LIỆU GIẢ
    "data/products.json": """[
    {
        "id": "sku01",
        "name": "Sổ Tay Bullet Journal Bìa Cứng Dotgrid (Mẫu Demo)",
        "price": 125000,
        "image_url": "https://down-vn.img.susercontent.com/file/vn-11134207-7r98o-lm0y3z5q3z5q4a",
        "shopee_link": "https://shopee.vn",
        "lazada_link": "https://lazada.vn"
    },
    {
        "id": "sku02",
        "name": "Bút Gel Đi Nét Mực Đen Ngòi 0.5mm (Hộp 12 Cây)",
        "price": 45000,
        "image_url": "",
        "shopee_link": "https://shopee.vn",
        "lazada_link": null
    }
]""",

    # 3. CSS STYLE
    "static/css/style.css": """body { font-family: sans-serif; background: #f7f9fc; margin: 0; padding: 20px; }
.container { max-width: 1000px; margin: 0 auto; }
.product-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); gap: 20px; }
.card { background: white; padding: 15px; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
.card img { width: 100%; height: 200px; object-fit: cover; background: #eee; }
.btn-group { display: flex; gap: 5px; margin-top: 10px; }
.btn { flex: 1; padding: 10px; text-align: center; text-decoration: none; color: white; border-radius: 4px; font-size: 14px; }
.shopee { background: #ee4d2d; }
.lazada { background: #0f146d; }""",

    # 4. TEMPLATES
    "templates/base.html": """<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}VPP Tịnh{% endblock %}</title>
    <link rel="stylesheet" href="static/css/style.css">
</head>
<body>
    <div class="container">
        <header style="text-align:center; padding: 20px;">
            <h1 style="color: #2c7a7b;">VPP TỊNH .</h1>
        </header>
        {% block content %}{% endblock %}
    </div>
</body>
</html>""",

    "templates/index.html": """{% extends "base.html" %}
{% block content %}
    <div class="product-grid">
        {% for item in products %}
        <div class="card">
            <img src="{{ item.image_url or 'https://via.placeholder.com/300' }}">
            <h3>{{ item.name }}</h3>
            <p style="color:red; font-weight:bold">{{ "{:,.0f}".format(item.price) }}đ</p>
            <div class="btn-group">
                {% if item.shopee_link %}<a href="{{ item.shopee_link }}" class="btn shopee">Shopee</a>{% endif %}
                {% if item.lazada_link %}<a href="{{ item.lazada_link }}" class="btn lazada">Lazada</a>{% endif %}
            </div>
        </div>
        {% endfor %}
    </div>
{% endblock %}"""
}

def create_structure():
    print("🚀 Đang khởi tạo dự án VPPTinh...")
    
    for filepath, content in files_content.items():
        # Tạo thư mục cha nếu chưa có
        dir_name = os.path.dirname(filepath)
        if dir_name:
            os.makedirs(dir_name, exist_ok=True)
        
        # Ghi file
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"   + Đã tạo: {filepath}")

    print("\n✅ HOÀN TẤT! Cấu trúc dự án đã sẵn sàng.")
    print("👉 Bước tiếp theo: Chạy lệnh 'python build.py'")

if __name__ == "__main__":
    create_structure()