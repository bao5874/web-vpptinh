#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Shopee Stationery Cleaner - Filter and clean scraped products
"""

import json
import re

OUT_OF_STOCK_KEYWORDS = [
    "hết hàng", "không còn", "bỏ mẫu", "liên hệ", "sold out", "tạm hết",
    "out of stock", "hết", "used", "vintage", "thanh lý", "xả kho",
    "order trước", "contact", "inquire", "unavailable"
]

# More restrictive VPP keywords
STRICT_VPP_KEYWORDS = [
    "bút bi", "bút chì", "bút gel", "bút dạ", "bút lông", "bút nước",
    "giấy a4", "giấy in", "giấy note", "giấy kraft",
    "vở kẻ", "vở ô ly", "sổ tay", "sổ lò xo",
    "kẹp giấy", "kẹp bướm", "ghim", "dập ghim",
    "băng dính", "băng keo", "keo dán",
    "thước", "ê ke", "compa", "kéo cắt",
    "hộp bút", "kệ đựng", "khay", "hồ sơ", "bìa", "file",
    "giấy kraft"
]

# Block non-stationery
BLACKLIST = [
    "xe", "ô tô", "xe máy", "phụ tùng", "lốp", "nhớt",
    "đồ chơi", "siêu nhân", "lego", "robot", "máy chơi",
    "ăn vặt", "bánh", "kẹo", "thực phẩm", "mắm", "muối",
    "makeup", "mỹ phẩm", "kẻ mắt", "trang điểm",
    "áo", "quần", "giày", "dép", "túi xách",
    "nail", "beauty", "tranh", "decor", "trang trí"
]

def filter_products(input_file, output_file, limit=25):
    """Filter products to keep only real stationery"""
    
    print("[LOADING] Reading raw products...")
    with open(input_file, 'r', encoding='utf-8') as f:
        all_products = json.load(f)
    
    print(f"[INPUT] {len(all_products)} products loaded\n")
    
    cleaned = []
    filtered = 0
    
    for product in all_products:
        if len(cleaned) >= limit:
            break
        
        name = product.get('name', '').lower()
        
        # Block out of stock
        if any(kw in name for kw in OUT_OF_STOCK_KEYWORDS):
            filtered += 1
            continue
        
        # Block non-stationery
        if any(kw in name for kw in BLACKLIST):
            filtered += 1
            continue
        
        # Must have at least one stationery keyword
        if not any(kw in name for kw in STRICT_VPP_KEYWORDS):
            filtered += 1
            continue
        
        cleaned.append(product)
        print(f"[OK] {len(cleaned):2}. {product.get('name', 'Unknown')[:60]:<60} | {product.get('price', 'Contact'):>12}")
    
    # Save cleaned products
    print(f"\n[SAVING] {len(cleaned)} valid products to {output_file}")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(cleaned, f, ensure_ascii=False, indent=2)
    
    # Also format for build.py
    build_format = [
        {
            "name": p['name'],
            "price": p['price'],
            "image": p['image'],
            "link": p['affiliate_link']
        }
        for p in cleaned
    ]
    
    print(f"[UPDATE] Updating products.json for build.py...")
    with open('products.json', 'w', encoding='utf-8') as f:
        json.dump(build_format, f, ensure_ascii=False, indent=2)
    
    print(f"\n[SUMMARY]")
    print(f"  Cleaned: {len(cleaned)} products")
    print(f"  Filtered: {filtered} products")
    print(f"  Success rate: {len(cleaned) * 100 // (len(cleaned) + filtered)}%")

if __name__ == "__main__":
    filter_products('shopee_products.json', 'shopee_products_cleaned.json', limit=30)
