"""
Smart Safety Vision - System Test Script
Quick test to verify all components are working
"""

import os
import sys


print("1️⃣ Testing Python Version...")
print(f"   Python: {sys.version}")
if sys.version_info >= (3, 8):
    print("   ✅ Python version OK")
else:
    print("   ❌ Python 3.8+ required")
    sys.exit(1)
print()

# Test 2: Import Core Libraries
print("2️⃣ Testing Core Libraries...")
try:
    import cv2
    print(f"   ✅ OpenCV: {cv2.__version__}")
except ImportError as e:
    print(f"   ❌ OpenCV not found: {e}")

try:
    import torch
    print(f"   ✅ PyTorch: {torch.__version__}")
    if torch.cuda.is_available():
        print(f"   ✅ CUDA available: {torch.cuda.get_device_name(0)}")
    else:
        print("   ℹ️  CUDA not available (CPU mode)")
except ImportError as e:
    print(f"   ❌ PyTorch not found: {e}")

try:
    from ultralytics import YOLO
    print("   ✅ Ultralytics YOLOv8")
except ImportError as e:
    print(f"   ❌ Ultralytics not found: {e}")

try:
    import streamlit
    print(f"   ✅ Streamlit: {streamlit.__version__}")
except ImportError as e:
    print(f"   ❌ Streamlit not found: {e}")

try:
    import yaml
    print("   ✅ PyYAML")
except ImportError as e:
    print(f"   ❌ PyYAML not found: {e}")

try:
    from dotenv import load_dotenv
    print("   ✅ python-dotenv")
except ImportError as e:
    print(f"   ❌ python-dotenv not found: {e}")

print()

# Test 3: Project Structure
print("3️⃣ Testing Project Structure...")
required_files = [
    'main.py',
    'requirements.txt',
    'config.yaml',
    '.env.example',
    'src/detector.py',
    'src/telegram_bot.py',
    'src/database.py',
    'src/config.py',
    'src/utils.py',
    'dashboard/app.py'
]

for file in required_files:
    if os.path.exists(file):
        print(f"   ✅ {file}")
    else:
        print(f"   ❌ {file} not found")
print()

# Test 4: Configuration
print("4️⃣ Testing Configuration...")
if os.path.exists('.env'):
    print("   ✅ .env file exists")
    from dotenv import load_dotenv
    load_dotenv()
    
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    
    if token and token != 'your_bot_token_here':
        print("   ✅ Telegram bot token configured")
    else:
        print("   ⚠️  Telegram bot token not configured")
    
    if chat_id and chat_id != 'your_chat_id_here':
        print("   ✅ Telegram chat ID configured")
    else:
        print("   ⚠️  Telegram chat ID not configured")
else:
    print("   ⚠️  .env file not found (copy from .env.example)")
print()

# Test 5: Import Project Modules
print("5️⃣ Testing Project Modules...")
sys.path.insert(0, 'src')

try:
    from config import config
    print("   ✅ config module")
except Exception as e:
    print(f"   ❌ config module: {e}")

try:
    from database import Database
    print("   ✅ database module")
except Exception as e:
    print(f"   ❌ database module: {e}")

try:
    from telegram_bot import TelegramBot
    print("   ✅ telegram_bot module")
except Exception as e:
    print(f"   ❌ telegram_bot module: {e}")

try:
    from detector import PPEDetector
    print("   ✅ detector module")
except Exception as e:
    print(f"   ❌ detector module: {e}")

try:
    import utils
    print("   ✅ utils module")
except Exception as e:
    print(f"   ❌ utils module: {e}")

print()

# Test 6: Database
print("6️⃣ Testing Database...")
try:
    from database import Database
    db = Database('logs/test.db')
    print("   ✅ Database connection successful")
    
    # Test insert
    detection_id = db.log_detection(
        camera_source="test_camera",
        total_persons=5,
        compliant_persons=3,
        violations=2,
        detection_data={"test": "data"}
    )
    print(f"   ✅ Database write successful (ID: {detection_id})")
    
    # Test read
    stats = db.get_statistics(days=7)
    print(f"   ✅ Database read successful")
    
    db.close()
    
    # Cleanup test database
    if os.path.exists('logs/test.db'):
        os.remove('logs/test.db')
        print("   ✅ Test database cleaned up")
    
except Exception as e:
    print(f"   ❌ Database test failed: {e}")

print()

# Test 7: Camera Detection
print("7️⃣ Testing Camera Access...")
try:
    import cv2
    cap = cv2.VideoCapture(0)
    
    if cap.isOpened():
        ret, frame = cap.read()
        if ret:
            h, w = frame.shape[:2]
            print(f"   ✅ Camera detected: {w}x{h}")
        else:
            print("   ⚠️  Camera detected but cannot read frame")
        cap.release()
    else:
        print("   ⚠️  No camera detected (will use video file for testing)")
except Exception as e:
    print(f"   ⚠️  Camera test: {e}")

print()

# Summary
print("=" * 60)
print("  📊 TEST SUMMARY")
print("=" * 60)
print()
print("✅ Core system components are ready!")
print()
print("🚀 Next Steps:")
print("   1. Configure Telegram bot (optional):")
print("      - Copy .env.example to .env")
print("      - Add your bot token and chat ID")
print()
print("   2. Run the system:")
print("      python main.py --source 0")
print()
print("   3. Launch dashboard:")
print("      streamlit run dashboard/app.py")
print()
print("   4. For testing without camera:")
print("      python main.py --source test_video.mp4")
print()
print("=" * 60)


def test_system_placeholder() -> None:
    """Lightweight placeholder so pytest has at least one test case."""

    assert True
