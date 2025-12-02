"""
Test Telegram Bot - Kirim pesan test
"""

import os
import sys

import pytest
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src to path
sys.path.insert(0, 'src')

from telegram_bot import TelegramBot

print("=" * 60)
print("  📱 TELEGRAM BOT TEST")
print("=" * 60)
print()

# Get credentials
token = os.getenv('TELEGRAM_BOT_TOKEN')
chat_id = os.getenv('TELEGRAM_CHAT_ID')

if not token or token == 'your_bot_token_here':
    print("❌ TELEGRAM_BOT_TOKEN tidak ditemukan!")
    print()
    print("📝 Cara setup:")
    print("1. Buka Telegram, cari @BotFather")
    print("2. Kirim /newbot")
    print("3. Copy token yang dikasih")
    print("4. Edit file .env:")
    print("   TELEGRAM_BOT_TOKEN=token_lu_disini")
    print()
    print("Lihat TELEGRAM_SETUP.md untuk panduan lengkap!")
    pytest.skip("TELEGRAM_BOT_TOKEN tidak dikonfigurasi", allow_module_level=True)

if not chat_id or chat_id == 'your_chat_id_here':
    print("❌ TELEGRAM_CHAT_ID tidak ditemukan!")
    print()
    print("📝 Cara dapat Chat ID:")
    print("1. Kirim pesan ke bot lu")
    print("2. Buka: https://api.telegram.org/bot<TOKEN>/getUpdates")
    print("3. Cari 'chat':{'id':123456}")
    print("4. Edit file .env:")
    print("   TELEGRAM_CHAT_ID=123456")
    print()
    print("Lihat TELEGRAM_SETUP.md untuk panduan lengkap!")
    pytest.skip("TELEGRAM_CHAT_ID tidak dikonfigurasi", allow_module_level=True)

print("🔧 Initializing Telegram Bot...")
print(f"   Token: {token[:10]}...{token[-5:]}")
print(f"   Chat ID: {chat_id}")
print()

# Initialize bot
bot = TelegramBot(token=token, chat_id=chat_id, cooldown=0)

if not bot.enabled:
    print("❌ Bot gagal connect!")
    print("   Cek token dan chat ID lu!")
    sys.exit(1)

print("✅ Bot connected!")
print()

# Test 1: Simple Message
print("📨 Test 1: Kirim pesan sederhana...")
success = bot.send_message("✅ Test message dari Smart Safety Vision!")

if success:
    print("   ✅ Berhasil! Cek Telegram lu!")
else:
    print("   ❌ Gagal kirim pesan!")

print()

# Test 2: Violation Alert
print("🚨 Test 2: Kirim violation alert...")
success = bot.send_violation_alert(
    violation_type="no_helmet",
    location="Workshop Area 1",
    confidence=0.875,
    additional_info="Worker detected near machinery without helmet"
)

if success:
    print("   ✅ Berhasil! Cek Telegram lu!")
else:
    print("   ❌ Gagal kirim alert!")

print()

# Test 3: System Status
print("🟢 Test 3: Kirim system status...")
success = bot.send_system_status(
    status="started",
    message="PPE detection system is now active and monitoring"
)

if success:
    print("   ✅ Berhasil! Cek Telegram lu!")
else:
    print("   ❌ Gagal kirim status!")

print()

# Test 4: Daily Summary (Demo)
print("📊 Test 4: Kirim daily summary...")
success = bot.send_daily_summary(
    total_detections=45,
    total_violations=12,
    compliance_rate=73.3,
    violation_breakdown={
        'no_helmet': 7,
        'no_vest': 3,
        'no_gloves': 2
    }
)

if success:
    print("   ✅ Berhasil! Cek Telegram lu!")
else:
    print("   ❌ Gagal kirim summary!")

print()
print("=" * 60)
print("  ✅ TELEGRAM BOT TEST SELESAI!")
print("=" * 60)
print()
print("📱 Cek Telegram lu sekarang!")
print("   Harusnya ada 4 pesan:")
print("   1. Test message")
print("   2. Violation alert")
print("   3. System status")
print("   4. Daily summary")
print()
print("=" * 60)
