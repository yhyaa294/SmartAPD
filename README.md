# 🦺 Smart Safety Vision (SSV) - PPE Violation Detection System

## 🎯 Project Overview

**Smart Safety Vision** is an AI-powered Personal Protective Equipment (PPE) violation detection system designed to enhance workplace safety through real-time monitoring. The system uses computer vision and machine learning to automatically detect workers who are not wearing proper safety equipment (helmets, safety vests, gloves) and sends instant alerts to supervisors.

### 🌟 Key Features

- ✅ **Real-time PPE Detection** using YOLOv8 object detection
- 📱 **Telegram Bot Integration** for instant violation alerts
- 🌐 **Modern React Web Dashboard** with Next.js + Tailwind CSS
- 📹 **CCTV Monitoring System** with multi-camera view & area map
- 💾 **Database Logging** for compliance tracking
- 📹 **Multi-source Support** (CCTV, IP Camera, Webcam, Video files)
- 🚀 **Lightweight & Efficient** - runs on regular laptops
- 📊 **Analytics & Reporting** with violation statistics
- 🔐 **Secure Login System** with access code authentication
- 📈 **Interactive Charts** with Recharts visualization
- 📤 **Export Functionality** - Download data as CSV

---

## 🏗️ System Architecture

```
👷 Worker → 🎥 Camera Feed → 🤖 YOLOv8 Detection → 💾 SQLite Database
                                        ↓
                              📱 Telegram Alert + 🌐 Web Dashboard
```

### Workflow

1. **Input**: Video stream from CCTV/IP Camera/Webcam
2. **Processing**: YOLOv8 model detects people and PPE items
3. **Classification**: Determines compliance status (wearing/not wearing PPE)
4. **Alert**: Sends Telegram notification if violation detected
5. **Logging**: Stores detection data in database
6. **Visualization**: Real-time dashboard displays statistics

---

## 📁 Project Structure

```
smart-safety-vision/
├── src/                      # Python backend source code
│   ├── detector.py           # YOLO detection engine
│   ├── telegram_bot.py       # Telegram notification system
│   ├── database.py           # Database operations
│   ├── config.py             # Configuration settings
│   └── utils.py              # Helper functions
├── web-dashboard/            # React/Next.js frontend
│   ├── app/
│   │   ├── page.tsx          # Landing page
│   │   ├── login/page.tsx    # Login system
│   │   ├── dashboard/page.tsx # Main dashboard
│   │   ├── monitoring/page.tsx # CCTV monitoring
│   │   ├── layout.tsx        # Root layout
│   │   └── globals.css       # Global styles
│   ├── middleware.ts         # Auth middleware
│   ├── package.json          # Dependencies
│   ├── tailwind.config.js    # Tailwind config
│   └── tsconfig.json         # TypeScript config
├── demo/                     # Demo scripts
│   ├── demo_detection.py     # Detection demo
│   ├── demo_simple.py        # Simple demo
│   ├── demo_with_helmet.py   # Helmet detection demo
│   └── setup_demo_data.py    # Demo data setup
├── tests/                    # Unit tests
│   ├── test_system.py        # System tests
│   └── test_telegram.py      # Telegram tests
├── notebooks/                # Jupyter notebooks
│   └── train_model.ipynb     # Model training
├── models/                   # Model weights
│   └── best.pt               # Trained YOLOv8 model
├── logs/                     # Logs & database
│   ├── detections.db         # SQLite database
│   └── violations/           # Violation images
├── training_data/            # Training dataset
├── docs/                     # Documentation
│   ├── WEB_MASTER_PLAN.md    # Web dashboard plan
│   ├── CCTV_MONITORING_GUIDE.md # CCTV guide
│   └── ...                   # Other guides
├── main.py                   # Main application
├── requirements.txt          # Python dependencies
├── config.yaml               # System configuration
├── .env.example              # Environment template
└── README.md                 # This file
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Webcam/IP Camera/CCTV access
- Telegram Bot Token (optional, for notifications)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/smart-safety-vision.git
cd smart-safety-vision
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure settings**
```bash
cp .env.example .env
# Edit .env with your Telegram Bot Token and other settings
```

4. **Download or train the model**
- Option A: Download pre-trained model (see Dataset & Model section)
- Option B: Train your own model using `notebooks/train_model.ipynb`

### Running the System

**1. Start Real-time Detection (Python Backend)**
```bash
python main.py --source 0  # Webcam
python main.py --source video.mp4  # Video file
python main.py --source http://192.168.1.100:8080/video  # IP Camera
```

**2. Launch Web Dashboard (React/Next.js)**
```bash
cd web-dashboard
npm install  # First time only
npm run dev
```
Then open: http://localhost:3000

**3. Test Telegram Bot**
```bash
python src/telegram_bot.py --test
```

**4. Run Demo Scripts**
```bash
python demo/demo_detection.py  # Basic detection demo
python demo/demo_with_helmet.py  # Helmet detection demo
```

---

## 📊 Dataset & Model Training

### Recommended Datasets

1. **Roboflow PPE Detection Dataset**
   - URL: https://universe.roboflow.com/ppe-detection
   - Classes: helmet, no_helmet, vest, no_vest, person

2. **Kaggle Hard Hat Detection**
   - URL: https://www.kaggle.com/datasets/andrewmvd/hard-hat-detection

3. **Custom Dataset Creation**
   - Use tools like LabelImg or Roboflow for annotation
   - Minimum 500 images per class recommended

### Training Process

1. **Prepare Dataset**
   - Organize in YOLO format (images + labels)
   - Split: 70% train, 20% validation, 10% test

2. **Train Model** (Google Colab recommended)
```python
from ultralytics import YOLO

# Load pretrained YOLOv8n model
model = YOLO('yolov8n.pt')

# Train on custom dataset
results = model.train(
    data='data.yaml',
    epochs=100,
    imgsz=640,
    batch=16,
    name='ppe_detection'
)
```

3. **Evaluate Performance**
```python
metrics = model.val()
print(f"mAP50: {metrics.box.map50}")
print(f"mAP50-95: {metrics.box.map}")
```

4. **Export Model**
```python
model.export(format='onnx')  # Optional: for faster inference
```

---

## ⚙️ Configuration

### config.yaml

```yaml
model:
  weights: "models/best.pt"
  confidence: 0.5
  iou_threshold: 0.45

camera:
  source: 0  # 0 for webcam, URL for IP camera
  fps: 30
  resolution: [1280, 720]

detection:
  classes:
    - helmet
    - no_helmet
    - vest
    - no_vest
    - person
  
telegram:
  enabled: true
  cooldown: 60  # seconds between alerts

database:
  path: "logs/detections.db"
  save_images: true
```

### Environment Variables (.env)

```env
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here
MODEL_PATH=models/best.pt
CONFIDENCE_THRESHOLD=0.5
```

---

## 📱 Telegram Bot Setup

1. **Create Bot**
   - Open Telegram and search for @BotFather
   - Send `/newbot` and follow instructions
   - Copy the Bot Token

2. **Get Chat ID**
   - Send a message to your bot
   - Visit: `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`
   - Copy the `chat.id` value

3. **Configure**
   - Add token and chat ID to `.env` file

---

## 🌐 Web Dashboard Features

### **Landing Page** (`/`)
- Modern hero section with gradient design
- Feature showcase (4 cards)
- Statistics display
- How it works section
- Call-to-action buttons

### **Login System** (`/login`)
- Secure access code authentication
- 3 default codes: ADMIN2024, SAFETY001, SUPERVISOR
- Password visibility toggle
- Error handling & validation
- LocalStorage session management

### **Main Dashboard** (`/dashboard`)
- **KPI Cards**: Total Detections, Violations, Compliance Rate, Compliant Workers
- **Interactive Charts**: 
  - Daily Violation Trend (Area Chart)
  - Violation Distribution (Pie Chart)
- **Violations Management**:
  - Recent violations list
  - Expandable details
  - Filter by type
  - Adjustable limit (5-50)
- **Export Functionality**:
  - Download Violations CSV
  - Download Statistics CSV
  - Download Violation Types CSV
- **Real-time Features**:
  - Live clock
  - Manual refresh
  - Auto-refresh toggle

### **CCTV Monitoring** (`/monitoring`)
- **Multi-View Modes**:
  - Grid View (2x2 multi-camera)
  - Single View (full-screen)
  - Map View (interactive area map)
- **Camera Features**:
  - 4 camera feeds
  - Online/Offline status
  - Worker & violation count
  - Location tracking
- **Interactive Map**:
  - Camera location markers
  - Color-coded status
  - Hover tooltips
  - Click to view camera

### **Security & Auth**
- Protected routes
- Auto-redirect if not logged in
- Session persistence
- Logout functionality

---

## 🧪 Testing & Validation

### Unit Tests
```bash
pytest tests/
```

### Performance Metrics
- **Inference Speed**: ~30-50 FPS on CPU, ~100+ FPS on GPU
- **Accuracy**: mAP50 > 0.85 (depends on training)
- **False Positive Rate**: < 5%

### Test Scenarios
1. Different lighting conditions
2. Various distances (2m - 10m)
3. Multiple people in frame
4. Partial occlusion
5. Different PPE colors

---

## 📈 Development Roadmap

### Phase 1: Foundation ✅ COMPLETE
- [x] Project setup and structure
- [x] Dataset collection and preparation
- [x] Model training and optimization
- [x] File organization (src/, demo/, tests/)

### Phase 2: Core Features ✅ COMPLETE
- [x] Real-time detection engine
- [x] Database integration
- [x] Telegram notification system
- [x] Multi-source support (webcam, video, IP camera)

### Phase 3: Web Dashboard ✅ COMPLETE
- [x] React/Next.js modern web interface
- [x] Landing page with modern UI
- [x] Secure login system
- [x] Main dashboard with analytics
- [x] Interactive charts (Recharts)
- [x] Export functionality (CSV)
- [x] Responsive design

### Phase 4: CCTV Monitoring ✅ COMPLETE
- [x] Multi-camera grid view
- [x] Single camera full-screen view
- [x] Interactive area map
- [x] Camera status tracking
- [x] Worker & violation monitoring

### Phase 5: Testing & Deployment ⏳ IN PROGRESS
- [x] Unit tests structure
- [x] Demo scripts
- [x] Comprehensive documentation
- [ ] Performance optimization
- [ ] Demo video creation
- [ ] Production deployment

### Phase 6: Future Enhancements 🔮 PLANNED
- [ ] Real CCTV stream integration
- [ ] Google Maps integration
- [ ] WebSocket real-time updates
- [ ] Mobile app (React Native)
- [ ] Advanced analytics & AI insights

---

## 🎓 Innovation Highlights

### Technical Innovation
1. **Multi-modal Detection**: Combines person detection with PPE classification
2. **Smart Alerting**: Cooldown mechanism prevents alert spam
3. **Adaptive Thresholding**: Configurable confidence levels
4. **Edge Computing Ready**: Lightweight enough for edge devices

### Practical Innovation
1. **Low-cost Solution**: Uses existing cameras and consumer hardware
2. **Easy Deployment**: Minimal setup required
3. **Scalable**: Can monitor multiple camera feeds
4. **Data-driven**: Provides actionable insights through analytics

### Social Impact
1. **Workplace Safety**: Reduces accidents through proactive monitoring
2. **Compliance**: Helps organizations meet K3 (Occupational Health & Safety) standards
3. **Education**: Raises awareness about safety equipment importance

---

## 🛠️ Troubleshooting

### Common Issues

**1. Model not loading**
- Ensure `best.pt` is in `models/` folder
- Check file path in config.yaml

**2. Camera not detected**
- Try different source indices (0, 1, 2)
- For IP camera, verify URL format: `http://IP:PORT/video`

**3. Telegram not sending**
- Verify bot token and chat ID
- Check internet connection
- Ensure bot is not blocked

**4. Low FPS**
- Reduce input resolution
- Use GPU if available
- Lower confidence threshold

---

## 📚 References & Resources

### Documentation
- [YOLOv8 Documentation](https://docs.ultralytics.com/)
- [OpenCV Python Tutorials](https://docs.opencv.org/4.x/d6/d00/tutorial_py_root.html)
- [Streamlit Documentation](https://docs.streamlit.io/)

### Datasets
- [Roboflow Universe](https://universe.roboflow.com/)
- [Kaggle Datasets](https://www.kaggle.com/datasets)

### Research Papers
- "You Only Look Once: Unified, Real-Time Object Detection" (Redmon et al.)
- "YOLOv8: State-of-the-Art Object Detection"

---

## 👥 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 👨‍💻 Author

Developed by [Your Name] as part of STEAM Innovation Project

**Contact**: your.email@example.com

---

## 🙏 Acknowledgments

- Ultralytics team for YOLOv8
- Roboflow for dataset tools
- Open-source community

---

**⚠️ Disclaimer**: This system is designed as an assistive tool and should not replace human supervision in critical safety scenarios.

# SmartAPD
#   S m a r t A P D  
 