import requests
import urllib.parse

# --- CẤU HÌNH ---
# Khi nào đăng ký Accesstrade xong, bạn dán Token vào đây
ACCESSTRADE_TOKEN = "DÁN_TOKEN_CỦA_BẠN_VÀO_ĐÂY" 
USE_REAL_API = False # Đổi thành True nếu đã điền Token ở trên

def make_money_link(original_url):
    """
    Hàm này biến link thường thành link affiliate.
    """
    if not original_url or "http" not in original_url:
        return "#"

    # CHẾ ĐỘ 1: CHẠY THẬT (Gọi API Accesstrade)
    if USE_REAL_API:
        try:
            api_endpoint = "https://api.accesstrade.vn/v1/datafeeds/deep_link"
            headers = {
                "Authorization": f"Token {ACCESSTRADE_TOKEN}",
                "Content-Type": "application/json"
            }
            params = {
                "url": original_url,
                "utm_source": "vpptinh_bot" # Để biết khách đến từ bot nào
            }
            
            response = requests.get(api_endpoint, headers=headers, params=params, timeout=5)
            data = response.json()
            
            if response.status_code == 200 and 'data' in data:
                return data['data']['short_link'] # Trả về link rút gọn (kol.com.vn/...)
            else:
                print(f"⚠️ Lỗi API: {data}")
        except Exception as e:
            print(f"❌ Lỗi kết nối API: {e}")

    # CHẾ ĐỘ 2: DEMO (Để bạn test code ngay bây giờ)
    # Chúng ta sẽ giả vờ gắn UTM code vào để nhìn cho "nguy hiểm"
    # Link sẽ trông như: shopee.vn/...?utm_source=AFFILIATE_TEST
    parsed = urllib.parse.urlparse(original_url)
    new_query = "utm_source=AFFILIATE_TEST&utm_medium=VPPTinh_Bot"
    if parsed.query:
        new_query = parsed.query + "&" + new_query
    
    fake_affiliate_link = parsed._replace(query=new_query).geturl()
    return fake_affiliate_link

# Test thử luôn khi chạy file này
if __name__ == "__main__":
    test_link = "https://shopee.vn/But-bi-thien-long-i.123.456"
    print("Link gốc:", test_link)
    print("Link tiền:", make_money_link(test_link))