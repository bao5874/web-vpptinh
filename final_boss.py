import requests
import json
import os
import base64

# --- CẤU HÌNH MỚI ---
# Đây là link bạn vừa đưa, đã có sẵn UTM và mã hóa cho ngành Văn Phòng Phẩm
DEEP_LINK_BASE = "https://go.isclix.com/deep_link/v6/6906519896943843292/4751584435713464237?sub4=oneatweb&utm_source=shopee&utm_campaign=v%C4%83n+ph%C3%B2ng+ph%E1%BA%A9m&url_enc="

# Danh sách từ khóa "Sạch" để hiển thị (Vì link trên là link trang chủ ngành, ta cần danh sách sản phẩm cụ thể)
# Tôi đề xuất bạn nên có một danh sách sản phẩm "Mồi" chuẩn VPP để web luôn đẹp
SAN_PHAM_MAU = [
    {"name": "Combo 10 Bút Bi Thiên Long Đẹp", "url": "https://shopee.vn/search?keyword=bút%20bi%20thiên%20long"},
    {"name": "Sổ Tay Lò Xo A5 Giấy Chống Lóa", "url": "https://shopee.vn/search?keyword=sổ%20tay%20lò%20xo"},
    {"name": "Giấy In A4 Double A 80gsm", "url": "https://shopee.vn/search?keyword=giấy%20in%20a4"},
    {"name": "Hộp Bút Chì Màu 24 Tiêu Chuẩn", "url": "https://shopee.vn/search?keyword=bút%20chì%20màu"}
]

def tao_link_chuan(url_goc):
    # Mã hóa link sản phẩm sang Base64 để gắn vào Deep Link của bạn
    url_bytes = url_goc.encode("utf-8")
    base64_url = base64.b64encode(url_bytes).decode("utf-8")
    return f"{DEEP_LINK_BASE}{base64_url}"

def cap_nhat_san_pham():
    print("🎯 Đang đồng bộ sản phẩm theo danh mục VPP...")
    
    products = []
    # Thay vì lấy CSV lỗi thời, ta dùng danh sách từ khóa chuẩn để tạo link
    for sp in SAN_PHAM_MAU:
        products.append({
            "name": sp['name'],
            "price": "Xem tại Shopee", # Shopee ẩn giá trong link tìm kiếm nên để vậy cho an toàn
            "image": "https://img.vietnamplus.vn/t620/uploaded/pcwvovt/2021_09_03/ttxvpp.jpg", # Ảnh đại diện chung cho VPP
            "link": tao_link_chuan(sp['url'])
        })

    # Ghi ra file JSON
    with open("products.json", "w", encoding="utf-8") as f:
        json.dump(products, f, ensure_ascii=False, indent=4)
    
    print(f"✅ Đã tạo xong {len(products)} link chuẩn VPP.")
    
    # Đẩy lên GitHub
    os.system("git add .")
    os.system('git commit -m "Update link vpp chuan"')
    os.system("git push")

if __name__ == "__main__":
    cap_nhat_san_pham()