# 📘 SmartAPD - Panduan Lengkap

## 🎯 Apa itu SmartAPD?

**SmartAPD™** adalah sistem monitoring Alat Pelindung Diri (APD) berbasis AI yang mendeteksi pelanggaran keselamatan kerja secara real-time menggunakan CCTV.

**Tagline:** "AI That Sees Safety"

---

## 🔧 Cara Kerja Sistem

### **1. Deteksi (AI Vision)**
```
CCTV → YOLOv8 AI → Deteksi APD
```
- Kamera CCTV merekam area kerja
- AI YOLOv8 menganalisis setiap frame
- Mendeteksi: Helmet, Vest, Gloves, Goggles
- Hasil: ✅ Lengkap atau ⚠️ Violation

### **2. Penyimpanan Data**
```
Detection → SQLite Database → Log History
```
- Setiap deteksi disimpan ke database
- Data: Waktu, Lokasi, Status APD, Camera ID
- Bisa di-export ke CSV

### **3. Alert Otomatis**
```
Violation → Telegram Bot → Notifikasi Real-time
```
- Jika ada pelanggaran → kirim alert
- Notifikasi ke Telegram supervisor
- Include: Foto, Lokasi, Waktu

### **4. Dashboard Analytics**
```
Database → Web Dashboard → Visualisasi
```
- Dashboard menampilkan statistik
- Charts: Trend violations, Compliance rate
- Table: Recent violations

---

## 🚀 Cara Install & Run

### **A. Backend (Python AI)**

#### **1. Install Dependencies**
```bash
# Install Python packages
pip install -r requirements.txt
```

**requirements.txt:**
```
ultralytics>=8.0.0
opencv-python>=4.8.0
numpy>=1.24.0
python-telegram-bot>=20.0
pyyaml>=6.0
```

#### **2. Setup Config**
Edit `config.yaml`:
```yaml
model:
  path: "models/best.pt"
  confidence: 0.5

camera:
  source: 0  # 0 = webcam, atau "rtsp://..."
  
telegram:
  bot_token: "YOUR_BOT_TOKEN"
  chat_id: "YOUR_CHAT_ID"

database:
  path: "detections.db"
```

#### **3. Run Detection**
```bash
# Webcam
python main.py --source 0

# Video file
python main.py --source demo_video.mp4

# RTSP stream
python main.py --source rtsp://192.168.1.100:554/stream
```

---

### **B. Frontend (Web Dashboard)**

#### **1. Install Dependencies**
```bash
cd web-dashboard
npm install
```

#### **2. Run Dev Server**
```bash
npm run dev
```

#### **3. Open Browser**
```
http://localhost:3000
```

#### **4. Login**
Gunakan salah satu access code:
- `ADMIN2024`
- `SAFETY001`
- `SUPERVISOR`

---

## 🔗 Cara Koneksi Backend ↔ Frontend

### **Opsi 1: Mock Data (Demo)**
**Status:** ✅ Sudah jalan (current)

Dashboard menggunakan mock data untuk demo:
```typescript
// web-dashboard/app/dashboard/page.tsx
const mockStats = {
  totalDetections: 45,
  violations: 12,
  complianceRate: 73.3
}
```

### **Opsi 2: Real API (Production)**

#### **Step 1: Buat API Backend**
Buat file `api.py`:
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sqlite3

app = FastAPI()

# Allow CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/stats")
def get_stats():
    conn = sqlite3.connect('detections.db')
    cursor = conn.cursor()
    
    # Query statistics
    cursor.execute("SELECT COUNT(*) FROM detections")
    total = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM detections WHERE status='violation'")
    violations = cursor.fetchone()[0]
    
    conn.close()
    
    return {
        "totalDetections": total,
        "violations": violations,
        "complianceRate": ((total - violations) / total * 100) if total > 0 else 0
    }

@app.get("/api/violations")
def get_violations():
    conn = sqlite3.connect('detections.db')
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, worker_id, location, violation_type, 
               timestamp, severity, camera_id 
        FROM detections 
        WHERE status='violation'
        ORDER BY timestamp DESC 
        LIMIT 10
    """)
    
    violations = []
    for row in cursor.fetchall():
        violations.append({
            "id": row[0],
            "worker": row[1],
            "location": row[2],
            "violation": row[3],
            "time": row[4],
            "severity": row[5],
            "camera": row[6]
        })
    
    conn.close()
    return violations
```

#### **Step 2: Run API**
```bash
pip install fastapi uvicorn
uvicorn api:app --reload --port 8000
```

#### **Step 3: Update Frontend**
Edit `web-dashboard/app/dashboard/page.tsx`:
```typescript
// Ganti mock data dengan API call
useEffect(() => {
  const fetchData = async () => {
    // Fetch stats
    const statsRes = await fetch('http://localhost:8000/api/stats')
    const statsData = await statsRes.json()
    setStats(statsData)
    
    // Fetch violations
    const violationsRes = await fetch('http://localhost:8000/api/violations')
    const violationsData = await violationsRes.json()
    setViolations(violationsData)
  }
  
  fetchData()
  // Refresh every 5 seconds
  const interval = setInterval(fetchData, 5000)
  return () => clearInterval(interval)
}, [])
```

---

## 📊 Struktur Database

### **Table: detections**
```sql
CREATE TABLE detections (
    id INTEGER PRIMARY KEY,
    timestamp TEXT,
    camera_id TEXT,
    worker_id TEXT,
    location TEXT,
    helmet BOOLEAN,
    vest BOOLEAN,
    gloves BOOLEAN,
    goggles BOOLEAN,
    status TEXT,  -- 'compliant' or 'violation'
    violation_type TEXT,
    severity TEXT,  -- 'high', 'medium', 'low'
    image_path TEXT
);
```

### **Cara Akses Database**
```python
import sqlite3

# Connect
conn = sqlite3.connect('detections.db')
cursor = conn.cursor()

# Query
cursor.execute("SELECT * FROM detections WHERE status='violation'")
results = cursor.fetchall()

# Close
conn.close()
```

---

## 🎨 Struktur Website

### **1. Landing Page** (`/`)
- Hero section
- Features showcase
- Team & Technology
- CTA button

### **2. Login Page** (`/login`)
- Access code input
- Demo codes displayed
- Orange theme

### **3. Dashboard** (`/dashboard`)
- **Sidebar Navigation:**
  - Overview
  - CCTV
  - Alerts
  - Reports
  - Settings
- **Main Content:**
  - 4 KPI cards
  - Area chart (trend)
  - Pie chart (types)
  - Violations table
  - Export CSV

### **4. CCTV Monitoring** (`/monitoring`)
- Grid view (4 cameras)
- Single view (focus 1)
- Map view (location)

---

## 📁 Struktur File Project

```
SmartAPD/
├── main.py                 # Main detection script
├── config.yaml             # Configuration
├── requirements.txt        # Python dependencies
│
├── src/
│   ├── detector.py         # YOLOv8 detector class
│   ├── database.py         # SQLite operations
│   ├── telegram_bot.py     # Telegram notifications
│   └── utils.py            # Helper functions
│
├── models/
│   └── best.pt             # Trained YOLOv8 model
│
├── demo/
│   └── demo_video.mp4      # Demo video
│
└── web-dashboard/
    ├── app/
    │   ├── page.tsx        # Landing page
    │   ├── login/
    │   │   └── page.tsx    # Login page
    │   ├── dashboard/
    │   │   └── page.tsx    # Dashboard (sidebar + charts)
    │   └── monitoring/
    │       └── page.tsx    # CCTV monitoring
    ├── package.json
    └── tailwind.config.js
```

---

## 🎯 Flow Lengkap

### **1. Setup Awal**
```bash
# Backend
pip install -r requirements.txt
python main.py --source 0

# Frontend (terminal baru)
cd web-dashboard
npm install
npm run dev
```

### **2. Demo Flow**
```
1. Buka http://localhost:3000
2. Klik "Akses Dashboard"
3. Login dengan ADMIN2024
4. Lihat dashboard (mock data)
5. Klik CCTV → Monitoring page
6. Toggle sidebar, explore features
```

### **3. Production Flow**
```
1. Setup API backend (api.py)
2. Run: uvicorn api:app --port 8000
3. Update frontend untuk fetch dari API
4. Run detection: python main.py --source rtsp://...
5. Dashboard otomatis update setiap 5 detik
```

---

## 🔧 Troubleshooting

### **Problem: Model not found**
```bash
# Download YOLOv8 model
pip install ultralytics
python -c "from ultralytics import YOLO; YOLO('yolov8n.pt')"
```

### **Problem: Port already in use**
```bash
# Change port
npm run dev -- -p 3001  # Frontend
uvicorn api:app --port 8001  # Backend
```

### **Problem: CORS error**
Tambahkan di `api.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 📊 Data Flow Diagram

```
┌─────────────┐
│    CCTV     │
│   Camera    │
└──────┬──────┘
       │ Video Stream
       ▼
┌─────────────┐
│   YOLOv8    │
│  Detection  │
└──────┬──────┘
       │ Detection Results
       ▼
┌─────────────┐
│   SQLite    │
│  Database   │
└──────┬──────┘
       │
       ├─────────────┐
       │             │
       ▼             ▼
┌─────────────┐ ┌─────────────┐
│  Telegram   │ │  FastAPI    │
│    Bot      │ │   Server    │
└─────────────┘ └──────┬──────┘
                       │ JSON API
                       ▼
                ┌─────────────┐
                │    React    │
                │  Dashboard  │
                └─────────────┘
```

---

## 🎨 Design System

### **Colors:**
- 🔶 Orange `#FF7A00` - Alert, Warning
- 🟩 Green `#34C759` - Safety, Success
- ⚪ White `#FFFFFF` - Background
- ⚫ Dark Gray `#1F2937` - Text

### **Components:**
- Sidebar navigation
- KPI cards with icons
- Interactive charts (Recharts)
- Data tables
- Export buttons

---

## 📝 Checklist Demo

**Persiapan:**
- [ ] Install dependencies (Python + Node)
- [ ] Download demo video
- [ ] Test webcam
- [ ] Run backend
- [ ] Run frontend

**Demo:**
- [ ] Show landing page
- [ ] Login to dashboard
- [ ] Explain 4 KPI cards
- [ ] Show charts (trend + types)
- [ ] Show violations table
- [ ] Export CSV
- [ ] Go to CCTV monitoring
- [ ] Toggle views (Grid/Single/Map)
- [ ] Logout

---

## 🚀 Next Steps

### **For Demo:**
1. Use mock data (sudah jalan)
2. Prepare demo video
3. Practice 5-minute pitch

### **For Production:**
1. Setup FastAPI backend
2. Connect real database
3. Integrate Telegram bot
4. Deploy to server

---

## 📞 Support

**Documentation:**
- README.md - Project overview
- SMARTAPD_BRANDING_GUIDE.md - Design system
- CARA_DEMO_TANPA_CCTV.md - Demo without hardware

**Tech Stack:**
- Python 3.8+
- React 18
- Next.js 14
- YOLOv8
- FastAPI
- SQLite

---

**🔥 PANDUAN LENGKAP SELESAI! 🚀**

**© 2025 SmartAPD - AI That Sees Safety**
