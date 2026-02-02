import schedule
import time
import os
import datetime

def cong_viec_buoi_sang():
    print(f"⏰ RENG RENG! Bây giờ là {datetime.datetime.now()}. Bắt đầu làm việc!")
    
    # 1. Chạy Bot đi săn hàng và tạo link tiền
    print("1️⃣  Đang đi săn hàng mới...")
    os.system("python spider_hunt.py")
    
    # 2. Xây lại giao diện web
    print("2️⃣  Đang xây lại Web...")
    os.system("python build.py")
    
    # 3. Đẩy lên mạng (Cloudflare)
    print("3️⃣  Đang đẩy lên mạng...")
    os.system("git add .")
    os.system('git commit -m "Tu dong cap nhat luc 5h sang"')
    os.system("git push")
    
    print("✅ HOÀN TẤT! Web đã mới toanh. Giờ tôi đi ngủ tiếp đây.")

# --- CẤU HÌNH THỜI GIAN ---
# Đặt giờ chạy là 05:00 sáng mỗi ngày
schedule.every().day.at("05:00").do(cong_viec_buoi_sang)

print("🤖 BOT ĐANG CHẠY NGẦM... (Đừng tắt cửa sổ này nhé)")
print("Hẹn gặp lại vào 5:00 sáng mai!")

# Vòng lặp vô tận để chờ đến giờ
while True:
    schedule.run_pending()
    time.sleep(60) # Cứ 1 phút kiểm tra đồng hồ 1 lần