import json
import time
import random
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# CẤU HÌNH
KEYWORD = "văn phòng phẩm cute"
LIMIT = 20

def run_spider():
    print(f"🕷️ SPIDER V2: Đang khởi động để săn '{KEYWORD}'...")

    chrome_options = Options()
    # Tắt dòng này để thấy trình duyệt chạy và kiểm tra xem có bị bắt nhập Captcha không
    # chrome_options.add_argument("--headless") 
    
    # Cấu hình chống phát hiện Bot
    chrome_options.add_argument("--disable-blink-features=AutomationControlled") 
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36")

    driver = webdriver.Chrome(options=chrome_options)

    try:
        url = f"https://shopee.vn/search?keyword={KEYWORD.replace(' ', '%20')}"
        driver.get(url)
        print("⏳ Đang vào Shopee...")
        
        # Đợi tối đa 10s cho đến khi sản phẩm xuất hiện
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[data-sqe='item']"))
            )
        except:
            print("⚠️ Cảnh báo: Web load chậm hoặc bị chặn Captcha. Hãy nhìn màn hình Chrome xem có bắt đăng nhập không.")

        # Cuộn trang từ từ (quan trọng để load ảnh)
        print("⬇️ Đang cuộn trang...")
        for i in range(10):
            driver.execute_script(f"window.scrollBy(0, 400);")
            time.sleep(0.5)
        
        # CHIẾN THUẬT MỚI: Tìm theo attribute [data-sqe='item'] (Bền vững hơn)
        items = driver.find_elements(By.CSS_SELECTOR, "[data-sqe='item']")
        print(f"🔎 Tìm thấy {len(items)} thẻ sản phẩm. Đang bóc tách dữ liệu...")

        products_data = []

        for index, item in enumerate(items[:LIMIT]):
            try:
                # 1. Lấy Tên (Tìm thẻ có chứa text bên trong item)
                # Thường tên nằm trong div > div > div... Chúng ta lấy thẻ a rồi lấy text
                link_tag = item.find_element(By.TAG_NAME, "a")
                
                # Mẹo: Lấy toàn bộ text của thẻ item rồi tách dòng
                raw_text = item.text.split('\n')
                name = raw_text[0] if len(raw_text) > 0 else "Sản phẩm không tên"
                
                # Thử tìm tên chính xác hơn nếu có
                try:
                    name_el = item.find_element(By.CSS_SELECTOR, "div[data-sqe='name']")
                    name = name_el.text
                except:
                    pass # Dùng tạm name lấy từ raw_text

                # 2. Lấy Giá
                price = 0
                price_text = "Liên hệ"
                # Tìm các element có chứa ký tự đ hoặc ₫
                all_spans = item.find_elements(By.TAG_NAME, "span")
                for span in all_spans:
                    if "₫" in span.text or "." in span.text and len(span.text) < 15:
                        price_text = span.text
                        # Làm sạch giá
                        temp_price = ''.join(filter(str.isdigit, price_text))
                        if temp_price:
                            price = int(temp_price)
                        break

                # 3. Lấy Ảnh
                image_url = "https://via.placeholder.com/300" # Ảnh mặc định
                try:
                    img_tag = item.find_element(By.TAG_NAME, "img")
                    image_url = img_tag.get_attribute("src")
                except:
                    pass

                # 4. Link gốc
                original_link = link_tag.get_attribute("href")

                # Bỏ qua nếu là tin quảng cáo (Ad) - thường không có giá hoặc tên lạ
                if price == 0: 
                    continue

                products_data.append({
                    "id": f"sp_{index}",
                    "name": name,
                    "price": price,
                    "image_url": image_url,
                    "shopee_link": original_link,
                    "lazada_link": None 
                })
                
                print(f"   ✅ Đã lấy: {name[:30]}... | {price}đ")

            except Exception as e:
                # print(f"Lỗi món {index}: {e}") # Bỏ comment để debug chi tiết
                continue 

        # Lưu file
        if products_data:
            with open('data/products.json', 'w', encoding='utf-8') as f:
                json.dump(products_data, f, ensure_ascii=False, indent=4)
            print(f"🎉 XONG! Đã lưu {len(products_data)} sản phẩm mới.")
        else:
            print("❌ Vẫn không lấy được. Khả năng cao Shopee hiện CAPTCHA.")

    except Exception as e:
        print(f"❌ Lỗi: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    run_spider()