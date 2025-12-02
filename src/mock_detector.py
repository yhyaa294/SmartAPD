import cv2
import time
import json
import requests
import logging
from datetime import datetime
from ultralytics import YOLO

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SmartAPDSystem:
    """
    SmartAPD System Mock Detector
    Simulates PPE detection (specifically helmets) using YOLOv8 for person detection
    and manual keyboard input to toggle violation states.
    """
    
    def __init__(self, camera_id=0, model_path='yolov8n.pt'):
        """
        Initialize the detector.
        
        Args:
            camera_id (int): ID of the webcam (usually 0).
            model_path (str): Path to YOLO weights.
        """
        self.camera_id = camera_id
        self.is_helmet_missing = False  # Default state: SAFE
        self.night_mode = False        # Default: Normal time
        self.intruder_mode = False     # Default: No intruder simulation
        self.last_log_time = time.time()
        
        # Initialize YOLO model
        try:
            logger.info(f"Loading YOLO model from {model_path}...")
            self.model = YOLO(model_path)
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise

        # Initialize Webcam
        logger.info(f"Opening camera {camera_id}...")
        self.cap = cv2.VideoCapture(camera_id)
        if not self.cap.isOpened():
            raise RuntimeError("Could not open webcam. Please verify camera connection.")

        # Define colors (BGR format)
        self.COLOR_SAFE = (0, 255, 0)      # Green
        self.COLOR_VIOLATION = (0, 0, 255) # Red

    def _send_alert(self, payload):
        """
        Placeholder for API integration.
        Sends violation data to backend.
        
        Args:
            payload (dict): Data to send.
        """
        # Placeholder for alert sending logic
        pass

    def process_frame(self):
        """
        Main processing loop:
        1. Capture frame
        2. Detect persons (Class 0)
        3. Apply mock logic
        4. Visualize
        5. Log data
        """
        while True:
            ret, frame = self.cap.read()
            if not ret:
                logger.error("Failed to capture frame")
                break

            # Run YOLO inference - Filter for 'person' class only (class 0)
            # verbose=False keeps the terminal clean
            results = self.model(frame, classes=[0], verbose=False)

            # Person count in current frame
            person_count = 0
            
            # Process detections
            for result in results:
                boxes = result.boxes
                for box in boxes:
                    person_count += 1
                    
                    # Get coordinates
                    x1, y1, x2, y2 = box.xyxy[0]
                    x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)

                    # Determine Visuals based on Mock State
                    if self.is_helmet_missing or self.intruder_mode:
                        color = self.COLOR_VIOLATION
                        label = "VIOLATION: NO HELMET" if not self.intruder_mode else "INTRUDER DETECTED"
                    else:
                        color = self.COLOR_SAFE
                        label = "SAFE"

                    # Draw Bounding Box
                    cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)

                    # Draw Label Background
                    (w, h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
                    cv2.rectangle(frame, (x1, y1 - 20), (x1 + w, y1), color, -1)
                    
                    # Draw Text
                    cv2.putText(frame, label, (x1, y1 - 5), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

            # Display Help Instructions
            cv2.putText(frame, "Controls: 'M' Violation | 'N' Night Mode | 'I' Intruder | 'S' Safe", 
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
            
            status_text = []
            if self.night_mode: status_text.append("NIGHT MODE (02:00)")
            if self.intruder_mode: status_text.append("INTRUDER SIMULATION")
            
            if status_text:
                cv2.putText(frame, " | ".join(status_text), (10, 60), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

            # Show Frame
            cv2.imshow('SmartAPD Simulation - Mock Detector', frame)

            # Periodic Logging (Every 1 second)
            current_time = time.time()
            if current_time - self.last_log_time >= 1.0:
                self.log_telemetry(person_count)
                self.last_log_time = current_time

            # Handle Keyboard Input
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                logger.info("Stopping system...")
                break
            elif key == ord('m'):
                self.is_helmet_missing = True
                logger.warning(">>> SIMULATION: VIOLATION TRIGGERED (Missing Helmet)")
            elif key == ord('s'):
                self.is_helmet_missing = False
                self.night_mode = False
                self.intruder_mode = False
                logger.info(">>> SIMULATION: SYSTEM RESET (Safe)")
            elif key == ord('n'):
                self.night_mode = not self.night_mode
                logger.info(f">>> SIMULATION: NIGHT MODE {'ON' if self.night_mode else 'OFF'}")
            elif key == ord('i'):
                self.intruder_mode = not self.intruder_mode
                logger.warning(f">>> SIMULATION: INTRUDER MODE {'ON' if self.intruder_mode else 'OFF'}")

        self.cleanup()

    def log_telemetry(self, person_count):
        """
        Constructs and prints JSON telemetry data.
        Triggers alert if violation is active.
        """
        # Logic simulasi intruder: jika mode intruder aktif, anggap ada orang meskipun tidak terdeteksi
        final_person_count = person_count
        if self.intruder_mode and person_count == 0:
            final_person_count = 1

        status = "VIOLATION" if (self.is_helmet_missing or self.intruder_mode) else "SAFE"
        
        # Logic timestamp simulasi
        if self.night_mode:
            # Set ke jam 02:00 pagi hari ini
            now = datetime.now()
            timestamp = now.replace(hour=2, minute=0, second=0, microsecond=0).isoformat()
        else:
            timestamp = datetime.now().isoformat()

        telemetry = {
            "timestamp": timestamp,
            "camera_id": self.camera_id,
            "person_count": final_person_count,
            "violation_status": status,
            "simulation_mode": {
                "night_mode": self.night_mode,
                "intruder_mode": self.intruder_mode
            }
        }

        # Print JSON to terminal
        print(json.dumps(telemetry))

        # If violation and person detected, simulate alert
        if (self.is_helmet_missing or self.intruder_mode) and final_person_count > 0:
            self._send_alert(telemetry)

    def cleanup(self):
        """Release resources."""
        self.cap.release()
        cv2.destroyAllWindows()
        logger.info("Resources released. Exiting.")

if __name__ == "__main__":
    try:
        app = SmartAPDSystem()
        app.process_frame()
    except KeyboardInterrupt:
        logger.info("Interrupted by user.")
    except Exception as e:
        logger.critical(f"Fatal error: {e}")
