import json
import re

def parse_shopee_data():
    try:
        with open("data.txt", "r", encoding="utf-8") as f:
            content = f.read()
        
        # Tách nội dung thành từng dòng
        lines = content.split('\n')
        products = []
        
        print("🔍 Đang bóc tách dữ liệu từ file...")

        # Thuật toán tìm Tên và Giá dựa trên cấu trúc text copy
        for i in range(len(lines)):
            line = lines[i].strip()
            
            # Nếu thấy dòng có chứa chữ ₫, khả năng cao đó là Giá
            if '₫' in line:
                price = line
                # Thường Tên sản phẩm sẽ nằm ở vài dòng phía trước đó
                # Chúng ta sẽ lấy dòng nào dài và có ý nghĩa nhất
                name = "Sản phẩm Shopee"
                for j in range(1, 10):
                    prev_line = lines[i-j].strip()
                    if len(prev_line) > 20 and '₫' not in prev_line and 'Đã bán' not in prev_line:
                        name = prev_line
                        break
                
                products.append({
                    "name": name,
                    "price": price,
                    "image": "https://via.placeholder.com/150", # Do copy tay nên không có link ảnh gốc
                    "link": "https://shopee.vn"
                })

        # Xóa bớt các mục trùng lặp
        unique_products = {p['name']: p for p in products}.values()
        final_list = list(unique_products)[:20]

        with open("products.json", "w", encoding="utf-8") as f:
            json.dump(final_list, f, ensure_ascii=False, indent=4)
            
        print(f"✅ THÀNH CÔNG! Đã tìm thấy {len(final_list)} sản phẩm.")
        print("👉 Bây giờ bạn chỉ cần chạy 'python build.py' là xong!")

    except Exception as e:
        print(f"❌ Lỗi: {e}")

if __name__ == "__main__":
    parse_shopee_data()