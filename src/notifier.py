import os
import logging
from datetime import datetime
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def send_telegram_alert(chat_id, message, image_path):
    """
    Mengirim alert ke Telegram beserta foto bukti pelanggaran.
    
    Args:
        chat_id (str): ID Chat Telegram (jika None, mengambil dari env).
        message (str): Pesan teks alert.
        image_path (str): Path file gambar yang akan dikirim.
    
    Returns:
        bool: True jika berhasil, False jika gagal.
    """
    # 1. Ambil konfigurasi dari Environment Variables
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    target_chat_id = chat_id or os.getenv("TELEGRAM_CHAT_ID")

    if not bot_token:
        logger.error("TELEGRAM_BOT_TOKEN tidak ditemukan di environment variables.")
        return False
    
    if not target_chat_id:
        logger.error("TELEGRAM_CHAT_ID tidak ditemukan (parameter kosong dan env var tidak ada).")
        return False

    # 2. Endpoint Telegram API
    url = f"https://api.telegram.org/bot{bot_token}/sendPhoto"

    # 3. Kirim Request
    try:
        if not os.path.exists(image_path):
            logger.error(f"File gambar tidak ditemukan: {image_path}")
            return False

        with open(image_path, 'rb') as image_file:
            payload = {
                'chat_id': target_chat_id,
                'caption': message
            }
            files = {
                'photo': image_file
            }
            
            response = requests.post(url, data=payload, files=files, timeout=10)
            response.raise_for_status() # Raise error untuk status 4xx/5xx
            
            logger.info(f"Alert berhasil dikirim ke {target_chat_id}")
            return True

    except requests.exceptions.RequestException as e:
        logger.error(f"Gagal mengirim alert Telegram: {e}")
        return False
    except Exception as e:
        logger.error(f"Terjadi kesalahan tak terduga: {e}")
        return False

def create_alert_message(camera_name, violation="Tidak Memakai Helm", action="Segera periksa lokasi!"):
    """
    Membuat format pesan alert standar profesional.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    return (
        "⚠️ CRITICAL ALERT - SmartAPD\n"
        f"Lokasi: {camera_name}\n"
        f"Waktu: {timestamp}\n"
        f"Pelanggaran: {violation}\n"
        f"Tindakan: {action}"
    )

if __name__ == "__main__":
    # Contoh penggunaan (Testing)
    # Pastikan file 'test_image.jpg' ada jika ingin menjalankan test ini
    dummy_msg = create_alert_message("Kamera Pintu Utama")
    print("Preview Pesan:\n" + dummy_msg)
    
    # Uncomment baris di bawah untuk test kirim (perlu .env setting)
    # send_telegram_alert(None, dummy_msg, "path/to/image.jpg")
