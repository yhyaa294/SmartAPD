import requests
import datetime

# --- KONFIGURASI ---
TOKEN = "8302407915:AAG2JSTTiJdVnrKM8jElv-6ZTIawNMtJsgM"
CHAT_ID = "6134497614"
# -------------------

def send_test_message():
    waktu = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Format Pesan HTML/Markdown
    pesan = (
        f"✅ <b>SISTEM SMART-APD ONLINE</b>\n\n"
        f"🤖 <b>Status:</b> Bot Terhubung\n"
        f"⏰ <b>Waktu Server:</b> {waktu}\n"
        f"📡 <b>Koneksi:</b> Stabil\n\n"
        f"<i>Sistem siap melaporkan pelanggaran K3.</i>"
    )

    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": pesan,
        "parse_mode": "HTML"
    }

    try:
        print("Mengirim pesan ke Telegram...")
        response = requests.post(url, data=data)
        if response.status_code == 200:
            print("✅ SUKSES! Cek Telegram Anda sekarang.")
        else:
            print(f"❌ GAGAL! Error: {response.text}")
    except Exception as e:
        print(f"❌ ERROR KONEKSI: {e}")

if __name__ == "__main__":
    send_test_message()