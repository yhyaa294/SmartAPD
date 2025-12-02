import requests
import os
from datetime import datetime

# --- KONFIGURASI TELEGRAM ---
BOT_TOKEN = "8302407915:AAG2JSTTiJdVnrKM8jElv-6ZTIawNMtJsgM"
CHAT_ID = "6134497614"

def send_alert(message, image_path=None):
    """
    Mengirim pesan alert ke Telegram.
    
    Args:
        message (str): Pesan teks (bisa menggunakan format Markdown).
        image_path (str, optional): Path ke file gambar yang akan dikirim.
    """
    try:
        if image_path and os.path.exists(image_path):
            # Endpoint untuk mengirim gambar
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
            with open(image_path, 'rb') as img_file:
                files = {'photo': img_file}
                data = {
                    'chat_id': CHAT_ID,
                    'caption': message,
                    'parse_mode': 'Markdown'
                }
                response = requests.post(url, files=files, data=data)
        else:
            # Endpoint untuk pesan teks biasa
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
            data = {
                'chat_id': CHAT_ID,
                'text': message,
                'parse_mode': 'Markdown'
            }
            response = requests.post(url, data=data)

        # Cek status respon
        if response.status_code == 200:
            print(f"[Telegram] Pesan terkirim: {message[:30]}...")
            return True
        else:
            print(f"[Telegram] Gagal mengirim: {response.text}")
            return False

    except Exception as e:
        print(f"[Telegram] Error: {e}")
        return False

# --- BLOCK PENGUJIAN (Jalankan file ini untuk test) ---
if __name__ == "__main__":
    print("--- MENGUJI KONEKSI TELEGRAM ---")
    
    # 1. Contoh Format Pesan Professional
    current_time = datetime.now().strftime("%H:%M:%S")
    test_message = (
        "🚨 **TEST PELANGGARAN TERDETEKSI!**\n\n"
        "📍 *Lokasi:* Zona A - Assembly Line\n"
        f"⏰ *Waktu:* {current_time}\n"
        "⚠️ *Jenis:* Tidak Menggunakan Helm\n\n"
        "🔍 *Status:* Perlu Tinjauan"
    )

    # 2. Kirim Test (Tanpa Gambar)
    print("Mengirim pesan test...")
    success = send_alert(test_message)
    
    if success:
        print("✅ Test Berhasil! Cek Telegram Anda.")
    else:
        print("❌ Test Gagal.")
