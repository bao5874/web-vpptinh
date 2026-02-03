import time
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

def scan_sieu_toc():
    print("🚀 Đang kết nối với Chrome đang mở...")
    options = Options()
    options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    driver = webdriver.Chrome(options=options)

    print("👀 Đang quét toàn bộ trang web để tìm sản phẩm...")
    
    # Cuộn trang từ từ để Shopee nhả dữ liệu
    for i in range(3):
        driver.execute_script(f"window.scrollTo(0, {i * 1000});")
        time.sleep(2)

    san_pham_list = []
    
    # CHIẾN THUẬT VÉT CẠN: Tìm tất cả các thẻ có khả năng là sản phẩm
    # Shopee thường dùng các thẻ div có class chứa từ 'shopee-search-item-result__item'
    items = driver.find_elements(By.XPATH, "//div[contains(@class, 'shopee-search-item-result__item')]")
    
    if not items:
        # Nếu không tìm thấy bằng class, tìm theo cấu trúc thẻ A chứa ảnh và giá
        items = driver.find_elements(By.XPATH, "//a[contains(@href, '-i.')]")

    print(f"🔎 Tìm thấy {len(items)} mục nghi vấn là sản phẩm. Đang bóc tách...")

    for item in items:
        try:
            # Lấy toàn bộ chữ trong mục đó
            full_text = item.text.split('\n')
            if len(full_text) < 2: continue # Bỏ qua nếu quá ít thông tin

            # Tên thường là dòng dài nhất hoặc dòng đầu tiên sau chữ 'Yêu thích'
            name = ""
            for line in full_text:
                if len(line) > 15 and '₫' not in line:
                    name = line
                    break
            
            # Giá là dòng có chữ ₫
            price = "Liên hệ"
            for line in full_text:
                if '₫' in line:
                    price = line
                    break

            # Link và Ảnh
            link = item.get_attribute("href") if item.tag_name == 'a' else item.find_element(By.TAG_NAME, "a").get_attribute("href")
            img = item.find_element(By.TAG_NAME, "img").get_attribute("src")

            if name and img:
                san_pham_list.append({
                    "name": name,
                    "price": price,
                    "image": img,
                    "link": link
                })
                print(f"✅ Đã tóm được: {name[:30]}...")
        except:
            continue

    # Lưu dữ liệu
    with open("products.json", "w", encoding="utf-8") as f:
        json.dump(san_pham_list, f, ensure_ascii=False, indent=4)
    
    print(f"\n🎉 THÀNH CÔNG! Đã tìm thấy {len(san_pham_list)} sản phẩm thật.")

if __name__ == "__main__":
    scan_sieu_toc()