import os
import datetime
import time

def kich_hoat_he_thong():
    thoi_gian = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"🚀 [KÍCH HOẠT] Bắt đầu lúc: {thoi_gian}")
    
    # BƯỚC 1: GỌI FINAL BOSS (Làm tất cả: Tải CSV, Lọc, Gắn link tiền, Tạo HTML)
    # Lưu ý: Không cần gọi build.py nữa vì final_boss làm luôn rồi
    print("1️⃣  Đang khởi động 'Sếp Tổng' (Final Boss)...")
    
    # Lệnh os.system trả về 0 nếu thành công, khác 0 nếu lỗi
    ket_qua = os.system("python final_boss.py")
    
    if ket_qua != 0:
        print("❌ CẢNH BÁO: Final Boss gặp lỗi hoặc không tìm thấy file!")
        print("👉 Hãy kiểm tra xem file 'final_boss.py' có nằm cùng thư mục không.")
        # Dừng lại, không đẩy code lỗi lên mạng
        return 

    # BƯỚC 2: ĐẨY LÊN MẠNG (Chỉ chạy khi bước 1 thành công)
    print("2️⃣  Dữ liệu ngon lành. Đang đẩy lên Github...")
    try:
        os.system("git add .")
        # Ghi chú thời gian cập nhật vào commit để dễ theo dõi
        os.system(f'git commit -m "Auto Update: {thoi_gian}"')
        os.system("git push")
        print("✅ PUSH THÀNH CÔNG!")
    except Exception as e:
        print(f"⚠️ Lỗi khi Push: {e}")
    
    print("-" * 30)
    print(f"🎉 HOÀN TẤT TOÀN BỘ LÚC: {datetime.datetime.now()}")
    print("Web vpptinh.com đã được làm mới. Cửa sổ này sẽ tự đóng sau 5 giây.")
    
    # Chờ 5 giây cho bạn kịp đọc thông báo rồi mới thoát
    time.sleep(5)

# --- PHẦN CHÍNH ---
# Khi file này được gọi, nó chạy hàm trên ngay lập tức
if __name__ == "__main__":
    kich_hoat_he_thong()