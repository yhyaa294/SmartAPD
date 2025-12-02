"""
Smart Safety Vision - Main Application
Real-time PPE violation detection system
"""

import cv2
import argparse
import logging
import sys
import time
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from config import config
from detector import PPEDetector
from database import Database
from telegram_bot import TelegramBot
from utils import save_frame, format_timestamp


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


class SmartSafetyVision:
    """Main application class for PPE detection system"""
    
    def __init__(self):
        """Initialize Smart Safety Vision system"""
        logger.info("Initializing Smart Safety Vision...")
        
        # Create necessary directories
        config.create_directories()
        
        # Initialize components
        self.detector = PPEDetector(
            model_path=config.model_path,
            confidence=config.confidence,
            iou_threshold=config.get('model.iou_threshold', 0.45),
            device=config.get('model.device', 'cpu')
        )
        
        self.database = Database(config.database_path)
        
        self.telegram_bot = None
        if config.get('alerts.telegram.enabled', True):
            self.telegram_bot = TelegramBot(
                bot_token=config.tg_bot_token,
                chat_id=config.telegram_chat_id,
                cooldown=config.get('alerts.telegram.cooldown_seconds', 60)
            )
        
        # Processing settings
        self.save_violations = config.get('database.save_violation_images', True)
        self.skip_frames = config.get('performance.skip_frames', 0)
        
        # Statistics
        self.frame_count = 0
        self.start_time = time.time()
        
        logger.info("Smart Safety Vision initialized successfully!")
    
    def process_frame(self, frame, camera_source: str = "Camera_1"):
        """
        Process a single frame
        
        Args:
            frame: Input frame
            camera_source: Camera identifier
            
        Returns:
            Annotated frame and detection results
        """
        # Perform detection
        annotated_frame, results = self.detector.detect(frame, visualize=True)
        
        # Log detection to database
        self.database.log_detection(
            camera_source=camera_source,
            total_persons=results['total_persons'],
            compliant_persons=results['compliant_persons'],
            violations=results['violation_count'],
            detection_data=results
        )
        
        # Handle violations
        if results['violations']:
            self._handle_violations(annotated_frame, results, camera_source)
        
        return annotated_frame, results
    
    def _handle_violations(self, frame, results, camera_source):
        """
        Handle detected violations
        
        Args:
            frame: Current frame
            results: Detection results
            camera_source: Camera identifier
        """
        for violation in results['violations']:
            violation_type = violation['type']
            confidence = violation['confidence']
            bbox = violation['person_bbox']
            
            # Save violation image
            image_path = None
            if self.save_violations:
                image_path = save_frame(frame, prefix=f"{violation_type}")
            
            # Log to database
            violation_id = self.database.log_violation(
                camera_source=camera_source,
                violation_type=violation_type,
                person_id=violation.get('id', 0),
                confidence=confidence,
                bbox=bbox,
                image_path=image_path
            )
            
            # Send Telegram alert
            if self.telegram_bot and self.telegram_bot.enabled:
                alert_sent = self.telegram_bot.send_violation_alert(
                    violation_type=violation_type,
                    location=camera_source,
                    confidence=confidence,
                    image_path=image_path
                )
                
                # Log alert
                if alert_sent:
                    self.database.log_alert(
                        violation_id=violation_id,
                        alert_type='telegram',
                        recipient=self.telegram_bot.chat_id,
                        status='sent',
                        message=f"{violation_type} detected"
                    )
    
    def run(self, source=None, show_preview: bool = True):
        """
        Run the detection system
        
        Args:
            source: Video source (camera index, file path, or URL)
            show_preview: Whether to show live preview window
        """
        # Use configured source if not provided
        if source is None:
            source = config.camera_source
        
        logger.info(f"Starting detection with source: {source}")
        
        # Send system start notification
        if self.telegram_bot and self.telegram_bot.enabled:
            self.telegram_bot.send_system_status(
                'started',
                f'PPE detection system started with source: {source}'
            )
        
        # Open video capture
        cap = cv2.VideoCapture(source)
        
        if not cap.isOpened():
            logger.error(f"Failed to open video source: {source}")
            return
        
        # Get video properties
        fps = int(cap.get(cv2.CAP_PROP_FPS)) or 30
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        logger.info(f"Video opened: {width}x{height} @ {fps} FPS")
        
        try:
            while True:
                ret, frame = cap.read()
                
                if not ret:
                    logger.warning("Failed to read frame")
                    break
                
                self.frame_count += 1
                
                # Skip frames if configured
                if self.skip_frames > 0 and self.frame_count % (self.skip_frames + 1) != 0:
                    continue
                
                # Process frame
                annotated_frame, results = self.process_frame(frame, f"Camera_{source}")
                
                # Calculate and display FPS
                elapsed_time = time.time() - self.start_time
                current_fps = self.frame_count / elapsed_time if elapsed_time > 0 else 0
                
                cv2.putText(
                    annotated_frame,
                    f"FPS: {current_fps:.1f}",
                    (width - 150, 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 255, 0),
                    2
                )
                
                # Show preview
                if show_preview:
                    cv2.imshow('Smart Safety Vision - PPE Detection', annotated_frame)
                    
                    key = cv2.waitKey(1) & 0xFF
                    if key == ord('q'):
                        logger.info("User requested quit")
                        break
                    elif key == ord('s'):
                        # Save screenshot
                        screenshot_path = save_frame(annotated_frame, prefix='screenshot')
                        logger.info(f"Screenshot saved: {screenshot_path}")
                
                # Log progress every 100 frames
                if self.frame_count % 100 == 0:
                    logger.info(f"Processed {self.frame_count} frames, "
                              f"FPS: {current_fps:.1f}")
        
        except KeyboardInterrupt:
            logger.info("Interrupted by user")
        
        except Exception as e:
            logger.error(f"Error during processing: {e}", exc_info=True)
            
            if self.telegram_bot and self.telegram_bot.enabled:
                self.telegram_bot.send_system_status('error', str(e))
        
        finally:
            # Cleanup
            cap.release()
            cv2.destroyAllWindows()
            
            # Send system stop notification
            if self.telegram_bot and self.telegram_bot.enabled:
                stats = self.detector.get_statistics()
                self.telegram_bot.send_system_status(
                    'stopped',
                    f"Processed {self.frame_count} frames. "
                    f"Violations: {stats['total_violations']}"
                )
            
            logger.info("Detection system stopped")
            logger.info(f"Final statistics: {self.detector.get_statistics()}")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Smart Safety Vision - PPE Violation Detection System'
    )
    
    parser.add_argument(
        '--source',
        type=str,
        default=None,
        help='Video source: camera index (0), video file path, or IP camera URL'
    )
    
    parser.add_argument(
        '--no-preview',
        action='store_true',
        help='Disable live preview window'
    )
    
    parser.add_argument(
        '--config',
        type=str,
        default='config.yaml',
        help='Path to configuration file'
    )
    
    args = parser.parse_args()
    
    # Parse source
    source = args.source
    if source is not None and source.isdigit():
        source = int(source)
    
    # Print banner
    print("=" * 60)
    print("  🦺 SMART SAFETY VISION - PPE DETECTION SYSTEM 🦺")
    print("=" * 60)
    print(f"  Start Time: {format_timestamp()}")
    print(f"  Video Source: {source or 'Default from config'}")
    print(f"  Model: {config.model_path}")
    print(f"  Confidence: {config.confidence}")
    print("=" * 60)
    print()
    
    # Initialize and run system
    try:
        app = SmartSafetyVision()
        app.run(source=source, show_preview=not args.no_preview)
    
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
