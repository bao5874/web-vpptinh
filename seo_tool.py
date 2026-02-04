import json
import datetime

# CẤU HÌNH CƠ BẢN
DOMAIN = "https://vpptinh.com"
INPUT_FILE = "products.json"  # Tên file dữ liệu sản phẩm của bạn
OUTPUT_SITEMAP = "sitemap.xml"
OUTPUT_ROBOTS = "robots.txt"
OUTPUT_SCHEMA = "schema_snippet.html" # File này chứa code để bạn nhét vào index.html

def generate_seo_files():
    try:
        # 1. Đọc dữ liệu từ file products.json
        with open(INPUT_FILE, 'r', encoding='utf-8') as f:
            products = json.load(f)
            print(f"📦 Đã tìm thấy {len(products)} sản phẩm.")
    except FileNotFoundError:
        print(f"❌ Lỗi: Không tìm thấy file {INPUT_FILE}. Hãy chắc chắn bạn đã chạy tool cào dữ liệu trước.")
        return

    # --- PHẦN 1: TẠO SITEMAP.XML ---
    print("Dang tao sitemap...")
    sitemap_content = '<?xml version="1.0" encoding="UTF-8"?>\n'
    sitemap_content += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'

    # 1.1 Thêm trang chủ
    sitemap_content += '  <url>\n'
    sitemap_content += f'    <loc>{DOMAIN}/</loc>\n'
    sitemap_content += f'    <lastmod>{datetime.date.today()}</lastmod>\n'
    sitemap_content += '    <priority>1.0</priority>\n'
    sitemap_content += '  </url>\n'

    # 1.2 Nếu web bạn có trang chi tiết (vd: detail.html?id=...), hãy bỏ comment dòng dưới
    # for p in products:
    #     link = f"{DOMAIN}/san-pham/{p.get('itemid')}" # Sửa lại theo cấu trúc link của bạn
    #     sitemap_content += f'  <url><loc>{link}</loc><priority>0.8</priority></url>\n'

    sitemap_content += '</urlset>'
    
    with open(OUTPUT_SITEMAP, 'w', encoding='utf-8') as f:
        f.write(sitemap_content)
    print(f"✅ Đã tạo: {OUTPUT_SITEMAP}")

    # --- PHẦN 2: TẠO SCHEMA JSON-LD (Hiện giá trên Google) ---
    print("Dang tao Schema Markup...")
    
    # Tạo danh sách sản phẩm theo chuẩn Google
    schema_items = []
    for p in products:
        # Lưu ý: Sửa các key ('name', 'price', 'image') khớp với file json của bạn
        item = {
            "@context": "https://schema.org/",
            "@type": "Product",
            "name": p.get('name', 'Sản phẩm VPP Tịnh'),
            "image": [p.get('image', '')],
            "description": "Sản phẩm chất lượng cao từ VPP Tịnh.",
            "sku": str(p.get('itemid', '')),
            "offers": {
                "@type": "Offer",
                "url": DOMAIN, # Hoặc link chi tiết sản phẩm
                "priceCurrency": "VND",
                "price": str(p.get('price', 0)).replace(".","").replace("₫",""), # Làm sạch giá
                "availability": "https://schema.org/InStock",
                "itemCondition": "https://schema.org/NewCondition"
            }
        }
        schema_items.append(item)

    # Xuất ra file HTML nhỏ để bạn include vào
    schema_html = '<script type="application/ld+json">\n'
    schema_html += json.dumps(schema_items, ensure_ascii=False, indent=2)
    schema_html += '\n</script>'

    with open(OUTPUT_SCHEMA, 'w', encoding='utf-8') as f:
        f.write(schema_html)
    print(f"✅ Đã tạo: {OUTPUT_SCHEMA} (Hãy copy nội dung file này vào thẻ <head> của index.html)")

    # --- PHẦN 3: TẠO ROBOTS.TXT ---
    robots_content = f"User-agent: *\nAllow: /\nSitemap: {DOMAIN}/sitemap.xml"
    with open(OUTPUT_ROBOTS, 'w', encoding='utf-8') as f:
        f.write(robots_content)
    print(f"✅ Đã tạo: {OUTPUT_ROBOTS}")

if __name__ == "__main__":
    generate_seo_files()