import json
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import converter  # <--- IMPORT MODULE CHUYỂN ĐỔI LINK

def run_spider_attach():
    print(f"🕷️ SPIDER ATTACH: Đang kết nối vào Chrome bạn đang mở (Port 9222)...")

    # Cấu hình để kết nối vào Chrome đang chạy
    chrome_options = Options()
    chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")

    try:
        driver = webdriver.Chrome(options=chrome_options)
        print("✅ Đã kết nối thành công!")
        print("👀 Đang quét sản phẩm trên màn hình hiện tại...")
        
        # 1. Tìm thẻ sản phẩm (Ưu tiên class phổ biến nhất hiện nay)
        items = driver.find_elements(By.CSS_SELECTOR, ".shopee-search-item-result__item")
        
        # Fallback: Nếu Shopee đổi class, tìm theo Data Attribute
        if len(items) == 0:
             items = driver.find_elements(By.CSS_SELECTOR, "[data-sqe='item']")

        print(f"🔎 Tìm thấy {len(items)} sản phẩm.")

        products_data = []
        # Lấy tối đa 20 sản phẩm đầu tiên để test
        for index, item in enumerate(items[:20]): 
            try:
                # --- A. BÓC TÁCH DỮ LIỆU CƠ BẢN ---
                
                # Lấy text thô để xử lý
                raw_text = item.text.split('\n')
                name = raw_text[0] if raw_text else "Sản phẩm Shopee"
                
                # Lấy giá (Tìm dòng có chứa ký tự tiền tệ)
                price = 0
                for line in raw_text:
                    if '₫' in line or ('đ' in line and any(c.isdigit() for c in line)):
                        temp = ''.join(filter(str.isdigit, line))
                        if temp:
                            price = int(temp)
                            break
                
                # Lấy ảnh
                image_url = "https://via.placeholder.com/300"
                try:
                    img_tag = item.find_element(By.TAG_NAME, "img")
                    src = img_tag.get_attribute("src")
                    if src: image_url = src
                except: pass

                # Lấy Link gốc (Link thường)
                original_link = "#"
                try:
                    a_tag = item.find_element(By.TAG_NAME, "a")
                    href = a_tag.get_attribute("href")
                    if href: original_link = href
                except: pass

                # --- B. XỬ LÝ LOGIC AFFILIATE (QUAN TRỌNG) ---
                if price > 0:
                    # Gọi hàm từ file converter.py để biến link thường thành link tiền
                    affiliate_link = converter.make_money_link(original_link)
                    
                    products_data.append({
                        "id": f"sp_{index}",
                        "name": name,
                        "price": price,
                        "image_url": image_url,
                        "shopee_link": affiliate_link, # Lưu link đã chuyển đổi
                        "lazada_link": None
                    })
                    print(f"   ✅ Lấy: {name[:15]}... | {price}đ | Link Affiliate: Đã tạo")

            except Exception as e:
                # Bỏ qua các thẻ lỗi (do quảng cáo hoặc load chậm)
                continue

        # --- C. LƯU FILE JSON ---
        if products_data:
            with open('data/products.json', 'w', encoding='utf-8') as f:
                json.dump(products_data, f, ensure_ascii=False, indent=4)
            print(f"\n🎉 XONG! Đã lưu {len(products_data)} sản phẩm vào 'data/products.json'")
            print("👉 Bước tiếp theo: Chạy lệnh 'python build.py' để cập nhật Web.")
        else:
            print("❌ Không tìm thấy sản phẩm nào. Hãy chắc chắn bạn đã cuộn trang Shopee xuống để ảnh hiện ra.")

    except Exception as e:
        print(f"❌ Lỗi kết nối: {e}")
        print("💡 Gợi ý: Hãy chắc chắn bạn đã mở Chrome bằng lệnh CMD: start chrome --remote-debugging-port=9222 ...")

if __name__ == "__main__":
    run_spider_attach()