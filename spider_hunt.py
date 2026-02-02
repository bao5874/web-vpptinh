import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import converter # Import module chuyển link

def run_spider_hunt():
    print(f"🕷️ SPIDER HUNT: Đang truy lùng theo 'Mùi Tiền' (Port 9222)...")

    chrome_options = Options()
    chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")

    try:
        driver = webdriver.Chrome(options=chrome_options)
        print("✅ Đã kết nối!")
        
        # CHIẾN THUẬT MỚI: TÌM THEO GIÁ TIỀN (XPATH)
        # Tìm tất cả các thẻ có chứa chữ '₫' hoặc 'đ'
        print("👀 Đang quét các vị trí có giá tiền...")
        price_elements = driver.find_elements(By.XPATH, "//*[contains(text(), '₫') or contains(text(), 'đ')]")
        
        print(f"🔎 Tìm thấy {len(price_elements)} vị trí có giá. Đang lọc sản phẩm...")

        products_data = []
        count = 0

        for price_tag in price_elements:
            if count >= 20: break # Lấy đủ 20 món thì dừng
            
            try:
                # Từ giá tiền, truy ngược lên thẻ cha (Container) chứa nó
                # Thường là thẻ <a> hoặc thẻ <div> bao quanh
                container = price_tag.find_element(By.XPATH, "./ancestor::a") 
                
                # 1. Lấy dữ liệu thô
                raw_text = container.text.split('\n')
                
                # 2. Lọc Giá (số nguyên)
                price_str = price_tag.text
                price = int(''.join(filter(str.isdigit, price_str)))
                
                # Nếu giá quá nhỏ (ví dụ 0đ hoặc quảng cáo rác), bỏ qua
                if price < 1000: continue

                # 3. Lấy Tên (Dòng đầu tiên thường là tên)
                name = raw_text[0] if len(raw_text) > 0 else "Sản phẩm Shopee"
                
                # 4. Lấy Ảnh (Tìm thẻ img bên trong container này)
                image_url = "https://via.placeholder.com/300"
                try:
                    img = container.find_element(By.TAG_NAME, "img")
                    src = img.get_attribute("src")
                    if src: image_url = src
                except: pass

                # 5. Lấy Link gốc
                original_link = container.get_attribute("href")
                
                # 6. Tạo Link Affiliate
                affiliate_link = converter.make_money_link(original_link)

                # Lưu vào danh sách (tránh trùng lặp)
                if not any(p['shopee_link'] == affiliate_link for p in products_data):
                    products_data.append({
                        "id": f"sp_{count}",
                        "name": name,
                        "price": price,
                        "image_url": image_url,
                        "shopee_link": affiliate_link,
                        "lazada_link": None
                    })
                    count += 1
                    print(f"   ✅ Bắt được: {name[:20]}... | {price}đ")

            except Exception:
                # Nếu thẻ giá đó không nằm trong thẻ A (ví dụ giá khuyến mãi nhỏ), bỏ qua
                continue

        # LƯU FILE
        if products_data:
            with open('data/products.json', 'w', encoding='utf-8') as f:
                json.dump(products_data, f, ensure_ascii=False, indent=4)
            print(f"\n🎉 THÀNH CÔNG! Đã săn được {len(products_data)} sản phẩm.")
            print("👉 Chạy 'python build.py' ngay đi!")
        else:
            print("❌ Vẫn chưa thấy. Bạn hãy chắc chắn đã cuộn trang xuống để giá tiền hiện ra.")

    except Exception as e:
        print(f"❌ Lỗi: {e}")

if __name__ == "__main__":
    run_spider_hunt()