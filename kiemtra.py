import json
import os

print("\n" + "="*30)
print("🔍 ĐANG KHÁM BỆNH CHO KHO HÀNG")
print("="*30)

# 1. Kiểm tra xem đang đứng ở đâu
print(f"📂 Thư mục hiện tại: {os.getcwd()}")

# 2. Kiểm tra file products.json có tồn tại không
if os.path.exists('products.json'):
    print("✅ Đã tìm thấy file 'products.json'")
    
    try:
        # 3. Đọc thử nội dung
        with open('products.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        # 4. Phân tích dữ liệu
        if isinstance(data, list):
            print(f"📊 Kết quả: Đây là một DANH SÁCH (List)")
            print(f"🔢 Số lượng: {len(data)} sản phẩm")
            
            if len(data) > 0:
                print("\n🧐 Soi thử sản phẩm đầu tiên xem nó viết thế nào:")
                print(data[0])
                print("\n👉 So sánh khóa (Key):")
                print(f"   Các tên gọi trong file là: {list(data[0].keys())}")
            else:
                print("⚠️ CẢNH BÁO: Danh sách rỗng (Không có hàng nào bên trong)!")
        else:
            print("❌ LỖI: Dữ liệu bị sai định dạng (Không phải danh sách)!")
            print(data)
            
    except Exception as e:
        print(f"❌ FILE HƯ HỎNG: Không đọc được ({e})")
else:
    print("❌ LỖI NGHIÊM TRỌNG: Không tìm thấy file 'products.json' đâu cả!")
    print("   -> Bạn có chắc là đã chạy spider_hunt.py thành công chưa?")

print("="*30 + "\n")