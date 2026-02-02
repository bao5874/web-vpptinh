import base64

# Link gốc chiến dịch của bạn
ACCESSTRADE_BASE = "https://go.isclix.com/deep_link/v6/6906519896943843292/4751584435713464237"

def make_money_link(shopee_link):
    """
    Hàm tạo link kiếm tiền chuẩn V6 (Dùng mã hóa Base64)
    """
    try:
        # BƯỚC 1: Mã hóa link Shopee sang dạng "Mật mã" (Base64)
        # Accesstrade V6 yêu cầu bước này để bảo mật link
        link_bytes = shopee_link.encode('utf-8')
        base64_bytes = base64.b64encode(link_bytes)
        base64_str = base64_bytes.decode('utf-8')
        
        # BƯỚC 2: Ghép vào link gốc
        # Lưu ý: Dùng tham số 'url_enc' (Link đã mã hóa) thay vì 'url' thường
        final_link = f"{ACCESSTRADE_BASE}?url_enc={base64_str}&utm_source=vpptinh_web"
        
        return final_link
        
    except Exception as e:
        print(f"Lỗi tạo link: {e}")
        return shopee_link

# Test thử xem nó có ra một chuỗi ký tự loằng ngoằng không (Nếu có là đúng!)
if __name__ == "__main__":
    link_thu = "https://shopee.vn/but-bi-thien-long"
    print("Link mã hóa của bạn:")
    print(make_money_link(link_thu))