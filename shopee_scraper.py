#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Shopee Stationery Products Scraper
Retrieves office supply products from Shopee using Selenium + affiliate link conversion
"""

import requests
import json
import time
import base64
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from urllib.parse import unquote

# Configuration
AFFILIATE_BASE_URL = "https://go.isclix.com/deep_link/v6/6906519896943843292/4751584435713464237?sub4=oneatweb&utm_source=shopee&utm_campaign=vpp&url_enc="
SHOPEE_SEARCH_URL = "https://shopee.vn/search?keyword=van%20phong%20pham"

# Stationery Keywords (để filter products)
STATIONERY_KEYWORDS = [
    "bút", "giấy", "vở", "sổ", "kẹp", "ghim", "băng", "keo", "thước", "compa", "kéo",
    "hộp bút", "kệ", "hồ sơ", "bìa", "file", "tài liệu", "văn phòng"
]

OUT_OF_STOCK_KEYWORDS = [
    "hết hàng", "không còn", "bỏ mẫu", "liên hệ", "sold out", "tạm hết",
    "out of stock", "hết", "used", "vintage", "thanh lý"
]

def setup_chrome_driver(headless=True):
    """Setup Selenium Chrome driver"""
    print("[SETUP] Initializing Chrome driver...")
    chrome_options = Options()
    
    if headless:
        chrome_options.add_argument("--headless")
    
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
    chrome_options.add_argument("--disable-gpu")
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        print("[SUCCESS] Chrome driver ready")
        return driver
    except Exception as e:
        print(f"[ERROR] Failed to initialize Chrome: {e}")
        return None

def convert_to_affiliate_link(shopee_url):
    """Convert Shopee direct link to affiliate link"""
    try:
        encoded = base64.b64encode(shopee_url.strip().encode("utf-8")).decode("utf-8")
        return f"{AFFILIATE_BASE_URL}{encoded}"
    except:
        return shopee_url

def extract_price(price_text):
    """Extract numeric price from text"""
    if not price_text:
        return None
    try:
        price_str = price_text.replace(".", "").replace(",", "").replace("₫", "").strip()
        numbers = re.findall(r'\d+', price_str)
        if numbers:
            return int(numbers[0])
        return None
    except:
        return None

def is_valid_product(name, price):
    """Check if product is valid stationery item"""
    name_lower = name.lower()
    
    # Check out of stock
    if any(keyword in name_lower for keyword in OUT_OF_STOCK_KEYWORDS):
        return False
    
    # Check if it's stationery
    if not any(keyword in name_lower for keyword in STATIONERY_KEYWORDS):
        return False
    
    # Check if price is reasonable (> 1000 VND)
    if price and price < 1000:
        return False
    
    return True

def scrape_shopee_products(max_products=20):
    """Scrape products from Shopee"""
    driver = setup_chrome_driver(headless=True)
    if not driver:
        print("[ERROR] Cannot initialize driver, using fallback method")
        return scrape_from_csv_fallback()
    
    products = []
    try:
        print(f"[LOADING] Accessing Shopee: {SHOPEE_SEARCH_URL}")
        driver.get(SHOPEE_SEARCH_URL)
        
        # Wait for products to load
        wait = WebDriverWait(driver, 10)
        print("[WAITING] Waiting for products to load...")
        
        try:
            wait.until(EC.presence_of_all_elements_located(
                (By.CSS_SELECTOR, "div[data-sqe='item']")
            ))
        except TimeoutException:
            print("[WARNING] Timeout waiting for products, trying alternative selector")
        
        # Scroll to load more products
        for i in range(3):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
        
        # Extract products
        print("[EXTRACTING] Scraping product data...")
        product_elements = driver.find_elements(By.CSS_SELECTOR, "div[data-sqe='item']")
        
        if len(product_elements) == 0:
            print("[WARNING] No products found with primary selector, trying fallback")
            product_elements = driver.find_elements(By.CSS_SELECTOR, ".shopee-search-item-result__item")
        
        print(f"[FOUND] {len(product_elements)} products on page")
        
        for element in product_elements:
            if len(products) >= max_products:
                break
            
            try:
                # Extract product details
                name_elem = element.find_elements(By.CSS_SELECTOR, "div.line-clamp-2")
                price_elem = element.find_elements(By.CSS_SELECTOR, "span.shopee-money")
                image_elem = element.find_elements(By.CSS_SELECTOR, "img")
                link_elem = element.find_elements(By.CSS_SELECTOR, "a")
                
                if not name_elem or not price_elem:
                    continue
                
                name = name_elem[0].text.strip() if name_elem else "Unknown"
                price_text = price_elem[0].text.strip() if price_elem else "0"
                price = extract_price(price_text)
                image_url = image_elem[0].get_attribute("src") if image_elem else ""
                shopee_link = link_elem[0].get_attribute("href") if link_elem else ""
                
                # Validate product
                if not is_valid_product(name, price):
                    continue
                
                # Ensure full URL
                if shopee_link and not shopee_link.startswith("http"):
                    shopee_link = "https://shopee.vn" + shopee_link
                
                affiliate_link = convert_to_affiliate_link(shopee_link) if shopee_link else "#"
                
                product = {
                    "name": name,
                    "price": f"{price:,}VND" if price else "Contact",
                    "image": image_url,
                    "shopee_link": shopee_link,
                    "affiliate_link": affiliate_link
                }
                
                products.append(product)
                print(f"[OK] {len(products)}. {name[:50]}... - {price:,}VND")
                
            except Exception as e:
                print(f"[SKIP] Error extracting product: {e}")
                continue
        
        print(f"\n[SUCCESS] Extracted {len(products)} valid products")
        return products
        
    except Exception as e:
        print(f"[ERROR] Scraping error: {e}")
        return []
    finally:
        driver.quit()

def scrape_from_csv_fallback():
    """Fallback to CSV datafeed if Selenium scraping fails"""
    print("[FALLBACK] Using AccessTrade CSV datafeed...")
    try:
        import csv
        import io
        
        CSV_URL = "http://datafeed.accesstrade.me/shopee.vn.csv"
        response = requests.get(CSV_URL, timeout=30)
        
        if response.status_code != 200:
            print("[ERROR] CSV download failed")
            return []
        
        products = []
        reader = csv.DictReader(io.StringIO(response.text))
        
        for row in reader:
            name = row.get('name', '').lower()
            
            if any(keyword in name for keyword in OUT_OF_STOCK_KEYWORDS):
                continue
            
            if not any(keyword in name for keyword in STATIONERY_KEYWORDS):
                continue
            
            price_text = row.get('price', '0')
            price = extract_price(price_text)
            
            if not price or price < 1000:
                continue
            
            products.append({
                "name": row.get('name'),
                "price": f"{price:,}VND" if price else "Contact",
                "image": row.get('image', '').split(',')[0].strip(' []"'),
                "shopee_link": row.get('url', ''),
                "affiliate_link": convert_to_affiliate_link(row.get('url', ''))
            })
            
            if len(products) >= 20:
                break
        
        print(f"[SUCCESS] Retrieved {len(products)} products from CSV")
        return products
        
    except Exception as e:
        print(f"[ERROR] CSV fallback failed: {e}")
        return []

def save_products(products, filename="shopee_products.json"):
    """Save products to JSON file"""
    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(products, f, ensure_ascii=False, indent=4)
        print(f"[SAVED] {len(products)} products saved to {filename}")
    except Exception as e:
        print(f"[ERROR] Failed to save products: {e}")

def main():
    print("=" * 60)
    print("SHOPEE STATIONERY PRODUCTS SCRAPER")
    print("=" * 60 + "\n")
    
    # Try Selenium scraping first
    print("[ATTEMPT 1] Trying Selenium-based scraping...")
    products = scrape_shopee_products(max_products=30)
    
    # Fallback to CSV if Selenium fails
    if not products or len(products) < 10:
        print("\n[ATTEMPT 2] Selenium insufficient, using CSV fallback...")
        products = scrape_from_csv_fallback()
    
    if products:
        # Save products
        save_products(products, "shopee_products.json")
        
        # Display summary
        print("\n" + "=" * 60)
        print("PRODUCTS RETRIEVED:")
        print("=" * 60)
        for i, product in enumerate(products, 1):
            print(f"{i}. {product['name'][:60]}")
            print(f"   Price: {product['price']}")
            print(f"   Link: {product['affiliate_link'][:80]}...\n")
    else:
        print("\n[ERROR] Failed to retrieve any products")
    
    print("=" * 60)

if __name__ == "__main__":
    main()
