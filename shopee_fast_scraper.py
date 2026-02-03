#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Shopee Stationery Scraper - Fast CSV-based version
Retrieves office supply products from AccessTrade Shopee datafeed
"""

import requests
import json
import csv
import io
import base64
import re
from urllib.parse import quote

# Configuration
AFFILIATE_BASE_URL = "https://go.isclix.com/deep_link/v6/6906519896943843292/4751584435713464237?sub4=oneatweb&utm_source=shopee&utm_campaign=vpp&url_enc="
CSV_URL = "http://datafeed.accesstrade.me/shopee.vn.csv"

# Product filtering
STATIONERY_KEYWORDS = [
    "bút bi", "bút chì", "bút gel", "bút dạ", "bút lông", "bút nước",
    "giấy a4", "giấy in", "giấy note", "giấy kraft",
    "vở kẻ", "vở ô ly", "sổ tay", "sổ lò xo",
    "kẹp giấy", "kẹp bướm", "ghim", "dập ghim",
    "băng dính", "băng keo", "keo dán",
    "thước", "ê ke", "compa", "kéo cắt",
    "hộp bút", "kệ đựng", "khay", "hồ sơ", "bìa", "file"
]

OUT_OF_STOCK_KEYWORDS = [
    "hết hàng", "không còn", "bỏ mẫu", "liên hệ", "sold out", "tạm hết",
    "out of stock", "hết", "used", "vintage", "thanh lý", "xả kho",
    "order trước", "contact", "inquire", "unavailable"
]

def convert_to_affiliate_link(shopee_url):
    """Convert Shopee link to affiliate link via base64 encoding"""
    if not shopee_url:
        return "#"
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
        price_str = str(price_text).replace(".", "").replace(",", "").replace("₫", "").strip()
        numbers = re.findall(r'\d+', price_str)
        if numbers:
            price = int(numbers[0])
            # Fix inflated prices
            if price > 5000000:
                price = price // 10
            return price if price >= 1000 else None
        return None
    except:
        return None

def is_valid_product(name, price):
    """Check if product is valid stationery"""
    if not name or not price:
        return False
    
    name_lower = name.lower()
    
    # Block out of stock items
    if any(keyword in name_lower for keyword in OUT_OF_STOCK_KEYWORDS):
        return False
    
    # Must contain stationery keyword
    if not any(keyword in name_lower for keyword in STATIONERY_KEYWORDS):
        return False
    
    # Price must be reasonable
    if price < 1000:
        return False
    
    return True

def fetch_shopee_products(limit=30):
    """Fetch products from AccessTrade CSV datafeed"""
    print("[LOADING] Downloading Shopee product feed...")
    print(f"[URL] {CSV_URL}\n")
    
    try:
        response = requests.get(CSV_URL, timeout=60)
        
        if response.status_code != 200:
            print(f"[ERROR] HTTP {response.status_code}")
            return []
        
        print("[PARSING] Reading CSV data...")
        reader = csv.DictReader(io.StringIO(response.text))
        products = []
        filtered_out = 0
        
        for row in reader:
            if len(products) >= limit:
                break
            
            try:
                name = row.get('name', '').strip()
                price_raw = row.get('price', '')
                price = extract_price(price_raw)
                image_url = row.get('image', '').split(',')[0].strip(' []"')
                shopee_url = row.get('url', '').strip()
                
                # Validate
                if not is_valid_product(name, price):
                    filtered_out += 1
                    continue
                
                # Create affiliate link
                affiliate_link = convert_to_affiliate_link(shopee_url)
                
                product = {
                    "name": name,
                    "price": f"{price:,}₫" if price else "Contact",
                    "price_vnd": price,
                    "image": image_url,
                    "shopee_link": shopee_url,
                    "affiliate_link": affiliate_link
                }
                
                products.append(product)
                print(f"[OK] {len(products)}. {name[:60]:<60} | {price:>9,}₫")
                
            except Exception as e:
                filtered_out += 1
                continue
        
        print(f"\n[SUMMARY] Found {len(products)} valid products (filtered {filtered_out})")
        return products
        
    except requests.exceptions.Timeout:
        print("[ERROR] Request timeout - CSV feed may be slow")
        return []
    except Exception as e:
        print(f"[ERROR] {e}")
        return []

def save_to_json(products, filename="shopee_products.json"):
    """Save products to JSON"""
    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(products, f, ensure_ascii=False, indent=2)
        print(f"[SAVED] {len(products)} products → {filename}")
        return True
    except Exception as e:
        print(f"[ERROR] Save failed: {e}")
        return False

def save_to_products_json(products):
    """Update main products.json with affiliate links"""
    try:
        # Keep top 15 most valuable products
        sorted_products = sorted(products, key=lambda x: x['price_vnd'] or 0, reverse=True)[:15]
        
        # Format for build.py compatibility
        formatted = [
            {
                "name": p['name'],
                "price": p['price'],
                "image": p['image'],
                "link": p['affiliate_link']
            }
            for p in sorted_products
        ]
        
        with open("products.json", "w", encoding="utf-8") as f:
            json.dump(formatted, f, ensure_ascii=False, indent=2)
        
        print(f"[UPDATED] products.json with top 15 products")
        return True
    except Exception as e:
        print(f"[ERROR] Failed to update products.json: {e}")
        return False

def main():
    print("=" * 80)
    print(" " * 15 + "SHOPEE STATIONERY PRODUCTS SCRAPER")
    print("=" * 80 + "\n")
    
    # Fetch products
    products = fetch_shopee_products(limit=50)
    
    if not products:
        print("\n[FATAL] No products retrieved")
        return
    
    # Save results
    print("\n" + "=" * 80)
    print("[SAVING] Writing results...\n")
    
    save_to_json(products, "shopee_products.json")
    save_to_products_json(products)
    
    # Display summary
    print("\n" + "=" * 80)
    print("TOP PRODUCTS:")
    print("=" * 80)
    
    top_products = sorted(products, key=lambda x: x['price_vnd'] or 0, reverse=True)[:10]
    for i, p in enumerate(top_products, 1):
        print(f"{i:2}. {p['name'][:65]:<65} | {p['price']:>10}")
    
    print("\n" + "=" * 80)
    print(f"Total retrieved: {len(products)} products")
    print("=" * 80 + "\n")

if __name__ == "__main__":
    main()
