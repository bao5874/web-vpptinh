#!/usr/bin/env python
# -*- coding: utf-8 -*-
import requests
import csv
import json
import io
import re
import base64
import time
import os

WOODEN_LOGO = "data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNTAiIGhlaWdodD0iNTAiIHZpZXdCb3g9IjAgMCA1MCA1MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48ZGVmcz48cmFkaWFsR3JhZGllbnQgaWQ9Indvb2RHcmFkIiBjeD0iNDAlIiBjeT0iNDAlIj48c3RvcCBvZmZzZXQ9IjAlIiBzdHlsZT0ic3RvcC1jb2xvcjojZDRhNTc0O3N0b3Atb3BhY2l0eToxIiAvPjxzdG9wIG9mZnNldD0iNTAlIiBzdHlsZT0ic3RvcC1jb2xvcjojYTg4MjVhO3N0b3Atb3BhY2l0eToxIiAvPjxzdG9wIG9mZnNldD0iMTAwJSIgc3R5bGU9InN0b3AtY29sb3I6IzdhNWU0MjtzdG9wLW9wYWNpdHk6MSIgLz48L3JhZGlhbEdyYWRpZW50PjwvZGVmcz48Y2lyY2xlIGN4PSIyNSIgY3k9IjI1IiByPSIyNCIgZmlsbD0idXJsKCN3b29kR3JhZCkiIHN0cm9rZT0iIzVjM2QxYSIgc3Ryb2tlLXdpZHRoPSIxIi8+PGxpbmUgeDE9IjEwIiB5MT0iMTUiIHgyPSI0MCIgeTI9IjE4IiBzdHJva2U9IiM2YjUzNDAiIHN0cm9rZS13aWR0aD0iMC41IiBvcGFjaXR5PSIwLjYiLz48bGluZSB4MT0iOCIgeTE9IjI1IiB4Mj0iNDIiIHkyPSIyNyIgc3Ryb2tlPSIjNmI1MzQwIiBzdHJva2Utd2lkdGg9IjAuNSIgb3BhY2l0eT0iMC42Ii8+PGxpbmUgeDE9IjEyIiB5MT0iMzUiIHgyPSIzOCIgeTI9IjMzIiBzdHJva2U9IiM2YjUzNDAiIHN0cm9rZS13aWR0aD0iMC41IiBvcGFjaXR5PSIwLjYiLz48ZyB0cmFuc2Zvcm09InRyYW5zbGF0ZSgxNSwgMTgpIj48cmVjdCB4PSIwIiB5PSIwIiB3aWR0aD0iMyIgaGVpZ2h0PSIxMiIgZmlsbD0ibm9uZSIgc3Ryb2tlPSIjZmZmIiBzdHJva2Utd2lkdGg9IjEuNSIgcng9IjEuNSIvPjxjaXJjbGUgY3g9IjEuNSIgY3k9IjEzIiByPSIxIiBmaWxsPSIjZmZmIi8+PC9nPjxnIHRyYW5zZm9ybT0idHJhbnNsYXRlKDIzLCAxOCkiPjxyZWN0IHg9IjAiIHk9IjAiIHdpZHRoPSI1IiBoZWlnaHQ9IjgiIGZpbGw9Im5vbmUiIHN0cm9rZT0iI2ZmZiIgc3Ryb2tlLXdpZHRoPSIxIiByeD0iMC41Ii8+PGxpbmUgeDE9IjEiIHkxPSIyIiB4Mj0iNCIgeTI9IjIiIHN0cm9rZT0iI2ZmZiIgc3Ryb2tlLXdpZHRoPSIwLjUiLz48bGluZSB4MT0iMSIgeTE9IjQiIHgyPSI0IiB5Mj0iNCIgc3Ryb2tlPSIjZmZmIiBzdHJva2Utd2lkdGg9IjAuNSIvPjwvZz48ZyB0cmFuc2Zvcm09InRyYW5zbGF0ZSgxMiwgMzIpIj48cmVjdCB4PSIwIiB5PSIwIiB3aWR0aD0iMTAiIGhlaWdodD0iMiIgZmlsbD0ibm9uZSIgc3Ryb2tlPSIjZmZmIiBzdHJva2Utd2lkdGg9IjEiIHJ4PSIwLjUiLz48bGluZSB4MT0iMiIgeTE9Ii0wLjUiIHgyPSIyIiB5Mj0iMi41IiBzdHJva2U9IiNmZmYiIHN0cm9rZS13aWR0aD0iMC41Ii8+PGxpbmUgeDE9IjUiIHkxPSItMC41IiB4Mj0iNSIgeTI9IjIuNSIgc3Ryb2tlPSIjZmZmIiBzdHJva2Utd2lkdGg9IjAuNSIvPjxsaW5lIHgxPSI4IiB5MT0iLTAuNSIgeDI9IjgiIHkyPSIyLjUiIHN0cm9rZT0iI2ZmZiIgc3Ryb2tlLXdpZHRoPSIwLjUiLz48L2c+PC9zdmc+"

BASE_AFF_URL = "https://go.isclix.com/deep_link/v6/6906519896943843292/4751584435713464237?sub4=oneatweb&utm_source=shopee&utm_campaign=vpp&url_enc="
LINK_CSV = "http://datafeed.accesstrade.me/shopee.vn.csv"

VPP_WHITELIST = [
    "bút bi", "bút chì", "bút gel", "bút nước", "bút dạ", "bút xóa", "bút nhớ", "bút lông", "ngòi bút", "bút dạ quang",
    "giấy a4", "giấy in", "giấy note", "giấy than", "giấy bìa", "giấy vẽ", "giấy in ảnh", "giấy kraft",
    "vở học sinh", "vở kẻ ngang", "vở ô ly", "sổ tay", "sổ lò xo", "sổ da", "sổ ghi chép",
    "kẹp giấy", "kẹp bướm", "kẹp tài liệu", "ghim bấm", "dập ghim", "ghim cài", "kẹp sắt",
    "bìa hồ sơ", "bìa còng", "bìa lá", "file lá", "túi clear bag", "cặp tài liệu", "file nhựa",
    "băng dính", "băng keo", "hồ dán", "keo dán", "băng trong suốt", "keo cơ khí",
    "thước kẻ", "ê ke", "compa", "hộp bút", "dao rọc giấy", "lưỡi dao", "kéo cắt",
    "khay đựng bút", "khay tài liệu", "kệ đựng hồ sơ", "khay để bàn", "hộp đựng", "tủ tài liệu"
]

JUNK_BLACKLIST = [
    "honda", "yamaha", "suzuki", "xe máy", "ô tô", "phụ tùng", "lốp", "nhớt", "pô", "gác chân", "bánh xe",
    "mực khô", "ăn vặt", "bánh", "kẹo", "thực phẩm", "mắm", "muối", "cơm", "mì", "tương", "rượu", "bia",
    "kẻ mắt", "kẻ mày", "trang điểm", "son môi", "phấn", "kem dưỡng", "serum", "mụn", "makeup", "mỹ phẩm",
    "áo sơ mi", "áo thun", "áo khoác", "quần jeans", "quần tây", "váy", "giày thể thao", "dép", "túi xách", "thời trang",
    "đồ chơi", "siêu nhân", "lắp ráp", "robot", "máy chơi game",
    "hết hàng", "bỏ mẫu", "liên hệ", "out of stock"
]

def tao_link_aff(url_goc):
    if not url_goc: return "#"
    try:
        encoded = base64.b64encode(url_goc.strip().encode("utf-8")).decode("utf-8")
        return f"{BASE_AFF_URL}{encoded}"
    except:
        return url_goc

def xuly_gia(gia_raw):
    try:
        gia_str = str(gia_raw).replace('.', '').replace(',', '')
        numbers = re.findall(r'\d+', gia_str)
        if not numbers: return "Lien he"
        gia_val = float(numbers[0])
        if gia_val > 5000000: gia_val /= 10
        if gia_val < 1000: return "Lien he"
        return "{:,.0f}VND".format(gia_val).replace(",", ".")
    except:
        return "Lien he"

print("[LOADING] Dang tai du lieu...")
r = requests.get(LINK_CSV, timeout=60)

if r.status_code == 200:
    reader = csv.DictReader(io.StringIO(r.text))
    clean_products = []
    excluded_count = 0
    
    print("[FILTER] Dang loc...")
    for row in reader:
        ten = row.get('name', '').lower()
        
        out_of_stock_keywords = [
            'hết hàng', 'không còn', 'bỏ mẫu', 'liên hệ', 'sold out', 'off stock', 
            'ngừng bán', 'kết thúc', 'hết lô', 'tạm hết', 'tạm dừng', 'không bán',
            'ngừng kinh doanh', 'order trước', 'đặt hàng', 'liên hệ shop',
            'không available', 'unavailable', 'hết', 'out', 'contact', 'inquire',
            'cũ', 'used', 'vintage', 'thanh lý', 'xả kho'
        ]
        
        if any(x in ten for x in out_of_stock_keywords): 
            excluded_count += 1
            continue
        
        if 'combo' in ten or 'set' in ten:
            if not any(x in ten for x in ['bút', 'giấy', 'vở']):
                excluded_count += 1
                continue
        
        is_real_vpp = (
            any(x in ten for x in ['bút', 'giấy', 'vở', 'sổ', 'kẹp', 'ghim', 'băng', 'keo', 'thước', 'compa', 'kéo']) or
            any(x in ten for x in ['hộp bút', 'kệ', 'hồ sơ', 'bìa', 'file', 'tài liệu', 'văn phòng'])
        )
        
        if not is_real_vpp: 
            excluded_count += 1
            continue
        
        if not any(good in ten for good in VPP_WHITELIST): 
            excluded_count += 1
            continue
        
        if "hộp đựng" in ten or "khay đựng" in ten:
            if not any(x in ten for x in ["bút", "tài liệu", "hồ sơ", "văn phòng"]):
                excluded_count += 1
                continue
        
        if any(bad in ten for bad in JUNK_BLACKLIST): 
            excluded_count += 1
            continue
        
        non_vpp_keywords = [
            'xe đạp', 'xe máy', 'kéo răng cưa', 'cắt viền', 'handmade',
            'decor', 'trang trí', 'tranh', 'nail', 'beauty', 'cơ khí chuyên dùng',
            'đục lỗ', 'tag tem', 'túi giấy trang trí', 'montessori'
        ]
        
        if any(x in ten for x in non_vpp_keywords): 
            excluded_count += 1
            continue
        
        gia_hien_thi = xuly_gia(row.get('price'))
        if gia_hien_thi == "Lien he": 
            excluded_count += 1
            continue
        
        clean_products.append({
            "name": row.get('name'),
            "price": gia_hien_thi,
            "image": row.get('image', '').split(',')[0].strip(' []"'),
            "link": tao_link_aff(row.get('url'))
        })
    
    final_list = clean_products[:15]
    print(f"[SUCCESS] Tim thay {len(final_list)} san pham (loai bo {excluded_count} san pham)")
    
    # Save products
    with open("products.json", "w", encoding="utf-8") as f:
        json.dump(final_list, f, ensure_ascii=False, indent=4)
    
    print("[SAVED] products.json updated")
else:
    print(f"[ERROR] CSV download failed: {r.status_code}")
