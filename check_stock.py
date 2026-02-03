#!/usr/bin/env python
# -*- coding: utf-8 -*-
import requests
import csv
import io

LINK_CSV = "http://datafeed.accesstrade.me/shopee.vn.csv"

try:
    r = requests.get(LINK_CSV, timeout=30)
    reader = csv.DictReader(io.StringIO(r.text))
    
    print("Stock field examples from CSV:")
    print("=" * 80)
    
    count = 0
    for row in reader:
        if 'stock' in row:
            stock_val = row.get('stock', 'N/A')
            name = row.get('name', '')[:60]
            print(f"Stock: '{stock_val}' | Name: {name}")
            count += 1
            if count >= 20:
                break
    
    print("\n" + "=" * 80)
    print("Check above for actual stock values (watch for blank, 0, or negative numbers)")
    
except Exception as e:
    print(f"Error: {e}")
