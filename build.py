import json
import os
from jinja2 import Environment, FileSystemLoader

# 1. Khởi tạo Jinja2
env = Environment(loader=FileSystemLoader('templates'))

# 2. Đọc dữ liệu
print("📂 Đang đọc dữ liệu sản phẩm...")
try:
    with open('data/products.json', 'r', encoding='utf-8') as f:
        products = json.load(f)
except FileNotFoundError:
    print("❌ Lỗi: Không tìm thấy file data/products.json")
    products = []

# 3. Render file index.html
print(f"🔨 Đang build web với {len(products)} sản phẩm...")
template = env.get_template('index.html')

# Output ra thư mục gốc (hoặc thư mục public/output tùy bạn cấu hình trên Cloudflare)
# Ở đây tôi xuất ra thư mục 'dist' để gọn gàng
output_dir = 'dist'
os.makedirs(output_dir, exist_ok=True)

with open(f'{output_dir}/index.html', 'w', encoding='utf-8') as f:
    f.write(template.render(products=products))

# Copy css sang thư mục dist (Trong thực tế nên dùng lệnh copy của OS hoặc thư viện shutil)
import shutil
os.makedirs(f'{output_dir}/static/css', exist_ok=True)
shutil.copy('static/css/style.css', f'{output_dir}/static/css/style.css')

print("✅ THÀNH CÔNG! Website đã được tạo tại thư mục /dist")
print("👉 Hãy mở file dist/index.html bằng trình duyệt để xem thử.")