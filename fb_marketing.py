import json
import random
import os
import requests
import webbrowser
import pyperclip # Thư viện copy vào clipboard
import time

# --- CẤU HÌNH ---
FILE_JSON = "products.json"
FILE_LOG = "data/da_dang_fb.txt" # Lưu lại những món đã đăng để không trùng
LINK_FACEBOOK = "https://www.facebook.com/" # Hoặc link Fanpage/Group của bạn

# Những câu mở đầu "mồi chài" khách
LOI_CHAO = [
    "🔥 HÀNG MỚI VỀ! Kèo thơm cho cả nhà ơi!",
    "🌿 Góc văn phòng phẩm cute lạc lối, nhìn là mê!",
    "✨ Deal hời giá hủy diệt, chỉ có tại VPP Tịnh!",
    "📢 Xả kho giá gốc, văn phòng phẩm xịn xò đây ạ!",
    "🎁 Món này đang Hot rần rần, em về được ít hàng thôi ạ!"
]

# Những câu kêu gọi hành động (CTA)
KEU_GOI = [
    "👉 Mua ngay kẻo hết:",
    "👉 Chốt đơn tại đây:",
    "👉 Link chính hãng Shopee:",
    "🛒 Bấm vào đây rinh ngay:",
    "🚀 Ship hỏa tốc tại:"
]

HASHTAGS = "#VPPTinh #VanPhongPham #DecorBanHoc #Shopee #GiaRe"

def tai_anh(url_anh):
    """Tải ảnh sản phẩm về để chuẩn bị đăng"""
    try:
        response = requests.get(url_anh)
        if response.status_code == 200:
            with open("anh_dang_fb.jpg", "wb") as f:
                f.write(response.content)
            return True
    except:
        pass
    return False

def lay_san_pham_chua_dang():
    # 1. Đọc danh sách đã đăng
    da_dang = []
    if os.path.exists(FILE_LOG):
        with open(FILE_LOG, "r", encoding="utf-8") as f:
            da_dang = f.read().splitlines()

    # 2. Đọc kho hàng
    try:
        with open(FILE_JSON, "r", encoding="utf-8") as f:
            products = json.load(f)
    except:
        print("❌ Chưa có file products.json. Hãy chạy final_boss.py trước!")
        return None

    # 3. Lọc ra món chưa đăng
    mon_moi = [p for p in products if p['link'] not in da_dang]
    
    if not mon_moi:
        print("✅ Bạn đã đăng hết hàng trong kho rồi! Hãy cập nhật thêm hàng mới.")
        return None
        
    # 4. Chọn ngẫu nhiên 1 món
    return random.choice(mon_moi)

def luu_lich_su(link_sp):
    """Lưu lại để lần sau không chọn trúng món này nữa"""
    if not os.path.exists("data"):
        os.makedirs("data")
    with open(FILE_LOG, "a", encoding="utf-8") as f:
        f.write(link_sp + "\n")

def viet_content_quang_cao():
    print("🤖 TRỢ LÝ MARKETING ĐANG LÀM VIỆC...")
    
    sp = lay_san_pham_chua_dang()
    if not sp: return

    print(f"💎 Đã chọn được món: {sp['name']}")
    
    # 1. Tải ảnh
    print("⬇️  Đang tải ảnh về máy...")
    if not tai_anh(sp['image']):
        print("❌ Lỗi tải ảnh. Bỏ qua món này.")
        return

    # 2. Soạn nội dung (Copywriting)
    intro = random.choice(LOI_CHAO)
    cta = random.choice(KEU_GOI)
    
    # Mẫu bài đăng Facebook chuẩn SEO
    content = f"""{intro}

✏️ {sp['name']}
💰 Giá chỉ: {sp['price']}

✅ Hàng chuẩn xịn, ảnh thật shop chụp.
✅ Phù hợp cho học sinh, sinh viên, dân văn phòng.
✅ Đổi trả thoải mái nếu lỗi.

{cta} {sp['link']}

------------------
{HASHTAGS}"""

    # 3. Copy vào Clipboard
    pyperclip.copy(content)
    print("✅ Đã soạn xong nội dung và COPY sẵn vào bộ nhớ tạm!")

    # 4. Mở Facebook
    print("🌐 Đang mở Facebook...")
    webbrowser.open(LINK_FACEBOOK)
    
    # 5. Lưu lịch sử
    luu_lich_su(sp['link'])
    
    print("\n" + "="*40)
    print("👉 HƯỚNG DẪN ĐĂNG BÀI (Chỉ mất 2 giây):")
    print("1. Bấm vào ô 'Bạn đang nghĩ gì?' trên Facebook.")
    print("2. Bấm Ctrl + V để dán nội dung đã soạn sẵn.")
    print("3. Kéo file 'anh_dang_fb.jpg' (vừa tải về) vào bài đăng.")
    print("4. Bấm ĐĂNG!")
    print("="*40 + "\n")

if __name__ == "__main__":
    viet_content_quang_cao()