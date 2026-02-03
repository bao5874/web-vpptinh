import json
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import converter  # <--- Import affiliate link converter

def run_stationery_spider():
    print(f"🕷️ STATIONERY SPIDER: Đang lấy sản phẩm văn phòng phẩm từ Shopee...")

    # Cấu hình Chrome options
    chrome_options = Options()
    chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        print("✅ Đã kết nối thành công!")
        
        # Navigate to the stationery link
        stationery_url = "https://go.isclix.com/deep_link/v6/6906519896943843292/4751584435713464237?sub4=oneatweb&utm_source=shopee&utm_campaign=vpp&url_enc=aHR0cHM6Ly9zaG9wZWUudm4v"
        print(f"📍 Đang truy cập: {stationery_url[:60]}...")
        driver.get(stationery_url)
        
        # Wait for page to load and redirect
        time.sleep(3)
        
        # Get current URL after redirect
        current_url = driver.current_url
        print(f"🔗 Redirected to: {current_url[:80]}...")
        
        # Wait for product items to load
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".shopee-search-item-result__item"))
            )
        except:
            print("⏳ Timeout waiting for items, continuing anyway...")
        
        # Find product items
        items = driver.find_elements(By.CSS_SELECTOR, ".shopee-search-item-result__item")
        
        # Fallback selector
        if len(items) == 0:
            items = driver.find_elements(By.CSS_SELECTOR, "[data-sqe='item']")
        
        print(f"🔎 Tìm thấy {len(items)} sản phẩm văn phòng phẩm.")
        
        products_data = []
        
        # Extract product data (max 30 products)
        for index, item in enumerate(items[:30]):
            try:
                # Get raw text
                raw_text = item.text.split('\n')
                name = raw_text[0] if raw_text else "Sản phẩm Shopee"
                
                # Extract price (look for Vietnamese currency symbol)
                price = 0
                for line in raw_text:
                    if '₫' in line or ('đ' in line and any(c.isdigit() for c in line)):
                        temp = ''.join(filter(str.isdigit, line))
                        if temp:
                            price = int(temp)
                            break
                
                # Get image URL
                image_url = "https://via.placeholder.com/300"
                try:
                    img_tag = item.find_element(By.TAG_NAME, "img")
                    src = img_tag.get_attribute("src")
                    if src:
                        image_url = src
                except:
                    pass
                
                # Get product link
                original_link = "#"
                try:
                    a_tag = item.find_element(By.TAG_NAME, "a")
                    href = a_tag.get_attribute("href")
                    if href:
                        original_link = href
                except:
                    pass
                
                # Convert to affiliate link if price exists
                if price > 0:
                    affiliate_link = converter.make_money_link(original_link)
                    
                    products_data.append({
                        "id": f"stationery_{index}",
                        "name": name,
                        "price": price,
                        "image_url": image_url,
                        "shopee_link": affiliate_link,  # Pre-converted affiliate link
                        "lazada_link": None,
                        "category": "văn phòm phẩm"
                    })
                    print(f"   ✅ Lấy: {name[:20]}... | {price:,}đ")
            
            except Exception as e:
                # Skip failed items
                continue
        
        # Save to JSON
        if products_data:
            with open('data/products.json', 'w', encoding='utf-8') as f:
                json.dump(products_data, f, ensure_ascii=False, indent=4)
            print(f"\n🎉 XONG! Đã lưu {len(products_data)} sản phẩm văn phòng phẩm vào 'data/products.json'")
            print("👉 Bước tiếp theo: Chạy lệnh 'python build.py' để cập nhật Web.")
        else:
            print("❌ Không tìm thấy sản phẩm nào. Hãy kiểm tra lại link hoặc cuộn trang Shopee.")
        
        driver.quit()
    
    except Exception as e:
        print(f"❌ Lỗi: {e}")
        print("💡 Gợi ý: Hãy chắc chắn Chrome đã mở với lệnh: chrome --remote-debugging-port=9222")

if __name__ == "__main__":
    run_stationery_spider()
