# AI Agent Instructions for web-banhang

## Project Overview
This is an **e-commerce scraping & affiliate marketing project** that:
1. Scrapes product data from Shopee (Vietnamese e-commerce platform) using Selenium
2. Converts direct links to affiliate links (monetization layer via Accesstrade)
3. Generates a static HTML product catalog for selling

## Architecture & Data Flow

### Core Components

**Spiders** (`spider*.py`, `spider_attach.py`, `spider_final.py`):
- Use Selenium to extract product data from Shopee listings
- Two connection modes: attach to running Chrome (port 9222) or launch new instance
- Extract: product name, price (₫ Vietnamese Dong), image URL, direct link
- Output: structured product data ready for monetization
- Key pattern: fallback CSS selectors (primary class + data attributes) for robustness against Shopee layout changes

**Affiliate Link Conversion** (`converter.py`, `converter2.py`):
- `converter.py`: Uses Base64 encoding + Accesstrade V6 deep link API (production mode)
- `converter2.py`: UTM parameter appending for demo/testing mode (when API token unavailable)
- Critical function: `make_money_link(shopee_link)` → returns monetized link
- Import pattern: `import converter` in spider_attach.py to convert links during extraction

**Static HTML Generator** (`build.py`):
- Loads product data from `data/products.json`
- Generates single-page HTML with CSS Grid product layout
- Outputs to both `index.html` (root) and `dist/index.html` for deployment
- Includes floating contact buttons (Zalo + phone) for Vietnamese market
- Responsive design: 2-column grid on mobile, auto-fill on desktop

**Data Store**:
- `data/products.json`: JSON array of product objects
- Schema: `{id, name, price, image_url, shopee_link, lazada_link}`
- Used by build.py as single source of truth

## Developer Workflows

### Extract Products
```bash
# Requires Chrome running on port 9222 (chrome.exe --remote-debugging-port=9222)
python spider_attach.py  # Attaches to running Chrome, extracts ~20 products
# Output: products.json with affiliate links already converted
```

### Generate Website
```bash
# After products.json exists
python build.py
# Creates/overwrites: index.html + dist/index.html with product grid
```

### Full Pipeline
1. Open Shopee search page in Chrome
2. Launch Chrome debug port: `chrome.exe --remote-debugging-port=9222`
3. Run `python spider_attach.py` → generates products.json with affiliate links
4. Run `python build.py` → generates index.html
5. Open `index.html` in browser to verify

## Key Patterns & Conventions

### Selector Fallback Pattern
All spiders use double-check for robustness:
```python
items = driver.find_elements(By.CSS_SELECTOR, ".shopee-search-item-result__item")
if len(items) == 0:
    items = driver.find_elements(By.CSS_SELECTOR, "[data-sqe='item']")
```
**Reason**: Shopee frequently changes class names; fallback to stable data attributes.

### Price Extraction
Always use digit filtering to extract numeric price:
```python
if '₫' in line or ('đ' in line and any(c.isdigit() for c in line)):
    price = int(''.join(filter(str.isdigit, line)))
```
Handles Vietnamese formatting variations.

### Affiliate Link Integration
Links are converted during scraping (spider_attach.py line 68), not at build time:
- Scraped link → `converter.make_money_link()` → stored in products.json
- Build.py reads pre-converted links; no double-conversion

### Chrome Debug Port
Required for attaching to running browser instead of launching headless:
```python
chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
```
Enables manual inspection of products before extraction.

## Configuration Points

- `converter.py` line 3: `ACCESSTRADE_BASE` → replace with your affiliate campaign URL
- `converter2.py` line 7: `ACCESSTRADE_TOKEN` → populate when API integration ready
- `build.py` line 77-78: Contact buttons (Zalo/phone) → update for your shop
- `data/products.json`: Primary data source (manually edit for quick testing)

## Common Issues & Solutions

| Issue | Root Cause | Fix |
|-------|-----------|-----|
| "Không kết nối được Chrome" | Debug port not running | `chrome.exe --remote-debugging-port=9222` |
| Selector returns 0 items | Shopee updated HTML structure | Add fallback selector in spider file |
| Price extraction fails | Non-standard formatting | Adjust filter logic for new Vietnamese format |
| products.json not found | build.py looks in 3 locations | Place file in data/, project root, or specify path |

## File Organization Purpose

```
spider_attach.py      → Main production scraper (attach mode)
spider_final.py       → Alternative scraper implementation  
spider_*.py           → Experimental/versioned scrapers
converter.py          → Production affiliate link conversion
converter2.py         → Demo/testing mode affiliate conversion
build.py              → HTML generation from products.json
data/products.json    → Product inventory (JSON array)
templates/            → HTML templates (unused in current build.py)
static/               → CSS/images assets (reference only, inlined in build.py)
dist/                 → Deployment output directory
```

## Dependencies & Environment
- **Selenium**: Web scraping & browser automation
- **Chrome**: Must support remote debugging (version 90+)
- **Python 3.6+**: For modern f-strings and json handling
- Vietnamese character encoding: UTF-8 required throughout
