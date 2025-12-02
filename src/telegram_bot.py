"""
Telegram Bot Module
Handles sending alerts and notifications via Telegram
"""

import os
import time
import logging
from datetime import datetime
from typing import Optional
import requests
from pathlib import Path

logger = logging.getLogger(__name__)


class TelegramBot:
    """Telegram bot for sending PPE violation alerts"""
    
    def __init__(self, token: str, chat_id: str, cooldown: int = 60):
        """
        Initialize Telegram bot
        
        Args:
            token: Telegram bot token
            chat_id: Telegram chat ID to send messages to
            cooldown: Minimum seconds between alerts (to prevent spam)
        """
        self.token = token
        self.chat_id = chat_id
        self.cooldown = cooldown
        self.last_alert_time = {}
        self.base_url = f"https://api.telegram.org/bot{token}"
        
        if not token or not chat_id:
            logger.warning("Telegram bot token or chat ID not configured")
            self.enabled = False
        else:
            self.enabled = True
            self._test_connection()
    
    def _test_connection(self) -> bool:
        """
        Test Telegram bot connection
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            url = f"{self.base_url}/getMe"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                bot_info = response.json()
                logger.info(f"Telegram bot connected: {bot_info['result']['username']}")
                return True
            else:
                logger.error(f"Telegram connection failed: {response.text}")
                self.enabled = False
                return False
        except Exception as e:
            logger.error(f"Telegram connection error: {e}")
            self.enabled = False
            return False
    
    def _can_send_alert(self, violation_type: str) -> bool:
        """
        Check if enough time has passed since last alert for this violation type
        
        Args:
            violation_type: Type of violation
            
        Returns:
            True if alert can be sent, False otherwise
        """
        current_time = time.time()
        last_time = self.last_alert_time.get(violation_type, 0)
        
        if current_time - last_time >= self.cooldown:
            self.last_alert_time[violation_type] = current_time
            return True
        
        return False
    
    def send_message(self, message: str, parse_mode: str = "HTML") -> bool:
        """
        Send text message via Telegram
        
        Args:
            message: Message text
            parse_mode: Message parse mode (HTML or Markdown)
            
        Returns:
            True if sent successfully, False otherwise
        """
        if not self.enabled:
            logger.warning("Telegram bot not enabled")
            return False
        
        try:
            url = f"{self.base_url}/sendMessage"
            payload = {
                "chat_id": self.chat_id,
                "text": message,
                "parse_mode": parse_mode
            }
            
            response = requests.post(url, json=payload, timeout=10)
            
            if response.status_code == 200:
                logger.info("Telegram message sent successfully")
                return True
            else:
                logger.error(f"Failed to send Telegram message: {response.text}")
                return False
        
        except Exception as e:
            logger.error(f"Error sending Telegram message: {e}")
            return False
    
    def send_photo(self, image_path: str, caption: str = "") -> bool:
        """
        Send photo via Telegram
        
        Args:
            image_path: Path to image file
            caption: Photo caption
            
        Returns:
            True if sent successfully, False otherwise
        """
        if not self.enabled:
            logger.warning("Telegram bot not enabled")
            return False
        
        if not os.path.exists(image_path):
            logger.error(f"Image file not found: {image_path}")
            return False
        
        try:
            url = f"{self.base_url}/sendPhoto"
            
            with open(image_path, 'rb') as photo:
                files = {'photo': photo}
                data = {
                    'chat_id': self.chat_id,
                    'caption': caption,
                    'parse_mode': 'HTML'
                }
                
                response = requests.post(url, files=files, data=data, timeout=30)
            
            if response.status_code == 200:
                logger.info(f"Telegram photo sent successfully: {image_path}")
                return True
            else:
                logger.error(f"Failed to send Telegram photo: {response.text}")
                return False
        
        except Exception as e:
            logger.error(f"Error sending Telegram photo: {e}")
            return False
    
    def send_violation_alert(self, violation_type: str, location: str = "Unknown",
                           confidence: float = 0.0, image_path: Optional[str] = None,
                           additional_info: str = "") -> bool:
        """
        Send PPE violation alert
        
        Args:
            violation_type: Type of violation (e.g., 'no_helmet')
            location: Location/camera identifier
            confidence: Detection confidence score
            image_path: Path to violation image (optional)
            additional_info: Additional information to include
            
        Returns:
            True if alert sent successfully, False otherwise
        """
        if not self.enabled:
            return False
        
        # Check cooldown
        if not self._can_send_alert(violation_type):
            logger.info(f"Alert cooldown active for {violation_type}")
            return False
        
        # Format violation type for display
        violation_display = violation_type.replace('_', ' ').title()
        
        # Create alert message
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        message = f"""
⚠️ <b>PPE VIOLATION DETECTED</b> ⚠️

🚨 <b>Violation:</b> {violation_display}
📍 <b>Location:</b> {location}
🕐 <b>Time:</b> {timestamp}
📊 <b>Confidence:</b> {confidence:.1%}
"""
        
        if additional_info:
            message += f"\n📝 <b>Details:</b> {additional_info}"
        
        message += "\n\n⚡ Please take immediate action to ensure worker safety!"
        
        # Send photo if available
        if image_path and os.path.exists(image_path):
            return self.send_photo(image_path, caption=message)
        else:
            return self.send_message(message)
    
    def send_daily_summary(self, total_detections: int, total_violations: int,
                          compliance_rate: float, violation_breakdown: dict) -> bool:
        """
        Send daily summary report
        
        Args:
            total_detections: Total number of detections
            total_violations: Total number of violations
            compliance_rate: Compliance rate percentage
            violation_breakdown: Dictionary of violation types and counts
            
        Returns:
            True if sent successfully, False otherwise
        """
        if not self.enabled:
            return False
        
        date = datetime.now().strftime("%Y-%m-%d")
        
        message = f"""
📊 <b>DAILY SAFETY REPORT</b> 📊
📅 Date: {date}

📈 <b>Summary:</b>
• Total Detections: {total_detections}
• Total Violations: {total_violations}
• Compliance Rate: {compliance_rate:.1f}%

"""
        
        if violation_breakdown:
            message += "🚨 <b>Violation Breakdown:</b>\n"
            for violation_type, count in violation_breakdown.items():
                violation_display = violation_type.replace('_', ' ').title()
                message += f"  • {violation_display}: {count}\n"
        
        # Add compliance status emoji
        if compliance_rate >= 95:
            message += "\n✅ <b>Excellent safety compliance!</b>"
        elif compliance_rate >= 80:
            message += "\n⚠️ <b>Good compliance, but room for improvement</b>"
        else:
            message += "\n🚨 <b>Safety compliance needs attention!</b>"
        
        return self.send_message(message)
    
    def send_system_status(self, status: str, message: str = "") -> bool:
        """
        Send system status notification
        
        Args:
            status: Status type (e.g., 'started', 'stopped', 'error')
            message: Additional message
            
        Returns:
            True if sent successfully, False otherwise
        """
        if not self.enabled:
            return False
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        status_emojis = {
            'started': '🟢',
            'stopped': '🔴',
            'error': '❌',
            'warning': '⚠️',
            'info': 'ℹ️'
        }
        
        emoji = status_emojis.get(status.lower(), '📢')
        
        alert_message = f"""
{emoji} <b>SYSTEM STATUS</b>

<b>Status:</b> {status.upper()}
<b>Time:</b> {timestamp}
"""
        
        if message:
            alert_message += f"\n<b>Message:</b> {message}"
        
        return self.send_message(alert_message)


def test_telegram_bot():
    """Test Telegram bot functionality"""
    from dotenv import load_dotenv
    load_dotenv()
    
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    
    if not token or not chat_id:
        print("❌ Telegram credentials not found in .env file")
        print("Please set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID")
        return
    
    print("🤖 Testing Telegram Bot...")
    
    bot = TelegramBot(token, chat_id)
    
    if not bot.enabled:
        print("❌ Bot initialization failed")
        return
    
    # Test simple message
    print("\n1. Testing simple message...")
    success = bot.send_message("✅ Test message from Smart Safety Vision!")
    print(f"   {'✅ Success' if success else '❌ Failed'}")
    
    # Test violation alert
    print("\n2. Testing violation alert...")
    success = bot.send_violation_alert(
        violation_type="no_helmet",
        location="Workshop Area 1",
        confidence=0.87,
        additional_info="Worker detected near machinery"
    )
    print(f"   {'✅ Success' if success else '❌ Failed'}")
    
    # Test system status
    print("\n3. Testing system status...")
    success = bot.send_system_status("started", "PPE detection system is now active")
    print(f"   {'✅ Success' if success else '❌ Failed'}")
    
    print("\n✅ Telegram bot test completed!")


if __name__ == "__main__":
    import sys
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    if '--test' in sys.argv:
        test_telegram_bot()
    else:
        print("Usage: python telegram_bot.py --test")
