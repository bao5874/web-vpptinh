import os
import json
import shutil # <--- Thư viện giúp copy file
from jinja2 import Environment, FileSystemLoader

def build_site():
    print("🔨 Đang xây dựng website...")

    # 1. Đọc dữ liệu sản phẩm
    products = []
    if os.path.exists('data/products.json'):
        with open('data/products.json', 'r', encoding='utf-8') as f:
            products = json.load(f)
    else:
        print("⚠️ Chưa có dữ liệu sản phẩm. Hãy chạy spider.py trước!")

    # 2. Cấu hình Jinja2 (Bộ máy ghép code)
    env = Environment(loader=FileSystemLoader('templates'))
    template = env.get_template('index.html')

    # 3. Tạo thư mục dist (Thùng hàng thành phẩm)
    if not os.path.exists('dist'):
        os.makedirs('dist')

    # --- TÍNH NĂNG MỚI: COPY FILE TĨNH (ẢNH, CSS) VÀO DIST ---
    # Copy thư mục static vào trong dist/static để web hiện được ảnh/màu
    if os.path.exists('dist/static'):
        shutil.rmtree('dist/static') # Xóa cái cũ đi
    
    if os.path.exists('static'):
        shutil.copytree('static', 'dist/static') # Copy cái mới vào
        print("📦 Đã đóng gói xong hình ảnh và giao diện!")
    # ---------------------------------------------------------

    # 4. Tạo file HTML
    output = template.render(products=products)
    with open('dist/index.html', 'w', encoding='utf-8') as f:
        f.write(output)

    print("✅ THÀNH CÔNG! Web đã có Logo mới. Mở dist/index.html để xem.")

if __name__ == "__main__":
    build_site()