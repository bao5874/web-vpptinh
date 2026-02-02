import urllib.parse

# ĐÂY LÀ LINK KIẾM TIỀN RIÊNG CỦA BẠN (Đừng để lộ cho người khác nhé)
# Tôi đã cắt phần đuôi thừa, chỉ giữ lại phần khung sườn quan trọng nhất.
ACCESSTRADE_BASE = "https://go.isclix.com/deep_link/v6/6906519896943843292/4751584435713464237"

def make_money_link(shopee_link):
    """
    Hàm này biến link Shopee thường -> Link Kiếm Tiền (Affiliate)
    """
    try:
        # 1. Mã hóa link Shopee (Để máy tính hiểu được các ký tự đặc biệt)
        encoded_url = urllib.parse.quote(shopee_link, safe='')
        
        # 2. Ghép vào link của bạn
        # Cấu trúc: [LINK_CỦA_BẠN] + ?url=[LINK_SHOPEE] + [NGUỒN_KHÁCH]
        final_link = f"{ACCESSTRADE_BASE}?url={encoded_url}&utm_source=vpptinh_web"
        
        return final_link
        
    except Exception as e:
        # Nếu lỗi thì trả về link gốc (Khách vẫn mua được, chỉ là mình không có tiền thôi)
        print(f"Lỗi tạo link: {e}")
        return shopee_link

# Test thử luôn xem máy in tiền có chạy không
if __name__ == "__main__":
    link_thu = "https://shopee.vn/but-bi-thien-long"
    print("Link kiếm tiền của bạn là:")
    print(make_money_link(link_thu))