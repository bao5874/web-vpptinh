import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

def run_spider_attach():
    print(f"🕷️ SPIDER ATTACH: Đang kết nối vào Chrome bạn đang mở...")

    chrome_options = Options()
    # Dòng lệnh thần thánh giúp Python kết nối vào trình duyệt có sẵn
    chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")

    try:
        driver = webdriver.Chrome(options=chrome_options)
        
        # Lúc này driver chính là cái trình duyệt bạn đang xem.
        # Không cần lệnh driver.get() nữa vì bạn đã mở sẵn trang rồi.

        print("✅ Đã kết nối thành công!")
        print("👀 Đang quét sản phẩm trên màn hình hiện tại...")
        
        # Tìm sản phẩm (Ưu tiên tìm theo thẻ bao quát nhất)
        items = driver.find_elements(By.CSS_SELECTOR, ".shopee-search-item-result__item")
        
        # Nếu không thấy (do Shopee đổi class), tìm theo Data Attribute
        if len(items) == 0:
             items = driver.find_elements(By.CSS_SELECTOR, "[data-sqe='item']")

        print(f"🔎 Tìm thấy {len(items)} sản phẩm.")

        products_data = []
        for index, item in enumerate(items[:20]): # Lấy 20 món
            try:
                # Lấy toàn bộ text để bóc tách
                raw_text = item.text.split('\n')
                name = raw_text[0] if raw_text else "Sản phẩm Shopee"
                
                # Bóc tách giá
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

                # Lấy Link
                link = "#"
                try:
                    a_tag = item.find_element(By.TAG_NAME, "a")
                    href = a_tag.get_attribute("href")
                    if href: link = href
                except: pass

                if price > 0:
                    products_data.append({
                        "id": f"sp_{index}",
                        "name": name,
                        "price": price,
                        "image_url": image_url,
                        "shopee_link": link,
                        "lazada_link": None
                    })
                    print(f"   + Đã lấy: {name[:20]}... | {price}đ")

            except Exception:
                continue

        # Lưu file
        if products_data:
            with open('data/products.json', 'w', encoding='utf-8') as f:
                json.dump(products_data, f, ensure_ascii=False, indent=4)
            print(f"🎉 XONG! Đã lưu {len(products_data)} sản phẩm vào data/products.json")
            print("👉 Giờ hãy chạy 'python build.py' để cập nhật web.")
        else:
            print("❌ Vẫn chưa tìm thấy sản phẩm. Hãy chắc chắn bạn đã cuộn trang để sản phẩm hiện ra.")

    except Exception as e:
        print(f"❌ Lỗi: {e}")

if __name__ == "__main__":
    run_spider_attach()