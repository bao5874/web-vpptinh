import json
import time
import random
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

# CẤU HÌNH
KEYWORD = "văn phòng phẩm cute" # Từ khóa muốn tìm
LIMIT = 20 # Số lượng muốn cào

def run_spider():
    print(f"🕷️ Đang khởi động Spider để săn: '{KEYWORD}'...")

    # Cấu hình Chrome để chạy mượt hơn
    chrome_options = Options()
    # chrome_options.add_argument("--headless") # Bỏ comment dòng này nếu muốn chạy ngầm (không hiện cửa sổ)
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--window-size=1920,1080")
    
    # Mẹo quan trọng: Tắt chế độ 'Automation' để Shopee không phát hiện
    chrome_options.add_argument("--disable-blink-features=AutomationControlled") 
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)

    driver = webdriver.Chrome(options=chrome_options)

    try:
        # 1. Vào Shopee
        url = f"https://shopee.vn/search?keyword={KEYWORD.replace(' ', '%20')}"
        driver.get(url)
        print("⏳ Đang vào Shopee, đợi load trang...")
        time.sleep(5) # Đợi trang load

        # 2. Cuộn trang xuống để load thêm hình ảnh (Lazy load)
        print("⬇️ Đang cuộn trang để lấy hết ảnh...")
        for i in range(5):
            driver.execute_script(f"window.scrollTo(0, {i * 1000});")
            time.sleep(1)
        
        # 3. Tìm các thẻ sản phẩm
        items = driver.find_elements(By.CSS_SELECTOR, ".shopee-search-item-result__item")
        print(f"🔎 Tìm thấy {len(items)} sản phẩm. Đang lọc lấy {LIMIT} món...")

        products_data = []

        for index, item in enumerate(items[:LIMIT]):
            try:
                # Lấy dữ liệu từng món (Xử lý ngoại lệ nếu thiếu thông tin)
                name = item.find_element(By.CSS_SELECTOR, "div[data-sqe='name'] > div").text
                
                # Giá (Xử lý text để lấy số)
                price_text = item.find_element(By.CSS_SELECTOR, "span[class*='_29R_un']").text # Class giá của Shopee hay đổi
                if not price_text: # Fallback tìm class khác nếu Shopee đổi code
                     price_text = item.text.split('₫')[-1].replace('.', '').replace(',', '')
                
                # Làm sạch giá (chỉ lấy số)
                price = int(''.join(filter(str.isdigit, price_text)))

                # Ảnh
                img_tag = item.find_element(By.TAG_NAME, "img")
                image_url = img_tag.get_attribute("src")

                # Link gốc
                link_tag = item.find_element(By.TAG_NAME, "a")
                original_link = link_tag.get_attribute("href")

                # Tạo link Affiliate giả lập (Sau này bạn thay hàm convert API vào đây)
                affiliate_link = original_link # Tạm thời để link gốc

                products_data.append({
                    "id": f"sp_{index}",
                    "name": name,
                    "price": price,
                    "image_url": image_url,
                    "shopee_link": affiliate_link,
                    "lazada_link": None # Tạm thời để trống
                })
                
                print(f"   + Đã lấy: {name[:30]}...")

            except Exception as e:
                continue # Bỏ qua món lỗi

        # 4. Lưu vào file JSON
        if products_data:
            with open('data/products.json', 'w', encoding='utf-8') as f:
                json.dump(products_data, f, ensure_ascii=False, indent=4)
            print(f"✅ Đã lưu {len(products_data)} sản phẩm vào data/products.json")
        else:
            print("❌ Không lấy được sản phẩm nào. Có thể Shopee đã đổi class CSS.")

    except Exception as e:
        print(f"❌ Lỗi: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    run_spider()