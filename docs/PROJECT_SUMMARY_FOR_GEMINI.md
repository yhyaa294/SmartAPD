# SmartAPD Project – Gemini Handoff Summary

Dokumentasi singkat ini merangkum struktur proyek, fitur utama, dan rencana kerja lanjutan agar mudah dilanjutkan dengan Gemini atau tim lain.

---

## 1. Arsitektur Tingkat Tinggi

| Layer | Stack | Keterangan |
|-------|-------|------------|
| **Edge / Vision** | Python, OpenCV, YOLOv8 (ultralytics) | `main.py` + modul di `src/` melakukan deteksi APD real-time, logging ke SQLite, dan mengirim alert. |
| **Backend API** | FastAPI, SQLite, APScheduler | Direktori `api/` menyajikan REST + WebSocket (`/api/*`, `/ws`), workflow alert, risk map, dan agregasi kedisiplinan. |
| **Frontend Dashboard** | Next.js 14 (App Router), React 18, Tailwind CSS, Recharts | Direktori `web-dashboard/` memuat dashboard desktop & mobile dengan tab Alerts/Reports/Settings, Risk Insights, serta komponen workflow baru. |
| **Automation & Docs** | Markdown playbooks | Folder dokumen (`IMPLEMENTATION_STATUS.md`, `PANDUAN_LENGKAP.md`, dll.) sebagai referensi implementasi & strategi. |

---

## 2. Struktur Folder Utama

```
.
├─ api/                      # FastAPI app (main.py, websocket.py, reports.py)
├─ web-dashboard/            # Next.js 14 app (app/, components/, services/)
├─ src/                      # Core vision pipeline (detector, database, utils)
├─ tests/                    # Pytest suites untuk sistem dan API
├─ training_data/, demo/     # Dataset & contoh input untuk pelatihan/demo
├─ notebooks/                # Eksperimen Jupyter (data exploration / prototyping)
├─ docs & playbooks          # *.md (master plan, panduan, pitch deck, branding)
├─ config.yaml               # Konfigurasi global (model, kamera, refresh interval)
├─ requirements.txt          # Dependensi Python (FastAPI, ultralytics, etc.)
└─ .env / .env.example       # Variabel lingkungan (API base URL, WebSocket URL)
```

---

## 3. Backend (FastAPI) – Fitur & Endpoint Penting

**File Kunci:** `api/main.py`

- **Monitoring & Statistik**
  - `GET /api/stats`, `GET /api/violations`, `GET /api/cameras`
  - `GET /api/risk-map` → agregasi risiko area & shift (dengan fallback demo)
  - `GET /api/discipline` → agregasi kedisiplinan per pekerja (baru)
- **Alert Workflow**
  - `POST /api/alerts/resolve` (mendukung catatan & evidence base64)
  - `POST /api/alerts/actions` (escalate manual/auto, menyimpan level, notes, evidence)
  - `GET /api/alerts/actions` (riwayat tindakan)
  - SQLite tabel `alert_actions` menyimpan catatan, actor, auto flag, evidence.
- **Real-time WebSocket**
  - Endpoint `/ws`, manager di `api/websocket.py` (dedup, severity routing, broadcast alert)
- **Auto Reports**
  - `api/reports.py` menghasilkan HTML laporan (PDF/email masih TODO)
- **Scheduler**
  - APScheduler terpasang (jadwal generate laporan otomatis)

**Cara Menjalankan Backend:**
```bash
uvicorn api.main:app --reload --port 8000
```
Pastikan `.env` berisi `BASE_URL`, `NEXT_PUBLIC_API_BASE_URL`, `NEXT_PUBLIC_WS_URL` sesuai lingkungan.

---

## 4. Frontend (Next.js) – Modul Utama

**Struktur:** `web-dashboard/`

- `app/dashboard/page.tsx` → halaman utama dengan sidebar + tab internal (Overview, Alerts, Reports, Settings). Terintegrasi WebSocket & Alert Center floating button.
- `components/dashboard/AlertsWorkflow.tsx`
  - Daftar alert + panel detail.
  - Filter severity/status, countdown auto-escalation (3 menit high, 5 menit medium).
  - Upload bukti (image/video/pdf) untuk resolve & escalate (tersimpan base64 di backend).
  - Riwayat tindakan menampilkan catatan, pelaku, evidence link, dan badge `AUTO` jika eskalasi otomatis.
- `components/RiskInsights.tsx` → heatmap & analitik risiko area.
- `components/dashboard/DisciplineLeaderboard.tsx`
  - Leaderboard top/low compliance, ringkasan pekerja, fallback demo.
  - Mode toggle & rentang hari (3/7/14/30).
- `components/dashboard/ReportsOverview.tsx` → ringkasan laporan mingguan/bulanan + fallback.
- `components/dashboard/SettingsPanel.tsx` → preferensi mobile, notifikasi, PWA.
- `services/api.ts` → klien API TS: metode `getDiscipline`, `resolveAlert`, `createAlertAction` (dengan evidence/auto flag) dll.
- `hooks/useWebSocket.ts` → manajemen koneksi, state text, auto-reconnect.

**Cara Menjalankan Frontend:**
```bash
cd web-dashboard
pnpm install    # atau npm install
pnpm dev        # localhost:3000
```

---

## 5. Edge / Vision Pipeline

- `main.py` → loop utama pengolahan video (ultralytics YOLOv8), logging ke SQLite, kirim notifikasi Telegram.
- `src/`
  - `detector.py` → wrapper YOLO, logika threshold.
  - `database.py` → ORM ringan SQLite (detections, violations, statistics, alerts).
  - `notifier.py` (bila ada) → integrasi Telegram/WhatsApp (cek folder).
  - `utils/`, `config_loader.py` → utilitas.
- `config.yaml` → pengaturan kamera, jalur model, scheduler refresh.

---

## 6. Testing & Data

- `tests/test_system.py` → rangkaian Pytest untuk API & core logic.
- `demo/`, `training_data/` → file contoh & dataset pelatihan (cek README terkait sebelum commit besar).
- `.gitignore` mengabaikan gambar pelanggaran besar (`logs/violations/*.jpg`).

---

## 7. Dokumentasi Internal

- `IMPLEMENTATION_STATUS.md` → status fase, backlog, progress metrics.
- `PANDUAN_LENGKAP.md`, `MASTER_PLAN_INDUSTRIAL.md`, `RINGKASAN_PROJECT.md` → panduan penggunaan, strategi industri, ringkasan eksekutif.
- `MOBILE_ADMIN_FEATURES.md` → blueprint dashboard mobile & admin.
- `ACCESSIBILITY_FIXES.md`, `GITHUB_SETUP.md`, `SMARTAPD_BRANDING_GUIDE.md` → referensi tambahan.

Semua dokumen ini sudah siap dijadikan referensi prompt untuk tim Gemini.

---

## 8. Fitur yang Sudah Stabil (Nov 2025)

- Dashboard terpadu dengan tab Alerts/Reports/Settings + Risk Insights & Discipline Leaderboard.
- Workflow alert lengkap (resolve, escalate, evidence, auto-escalation, riwayat).
- Real-time alert badge + WebSocket hook.
- Backend agregasi risiko (risk map) & kedisiplinan.
- Push notification manager dipindah ke Settings.
- Fallback data & error handling bawaan untuk demo offline.

---

## 9. Backlog & Prioritas Berikutnya

1. **Spot-check AI Assistant**
   - Form manual check (foto/upload) dengan rekomendasi AI.
   - Integrasi ke workflow & log investigasi.

2. **Integrasi Sensor / IoT**
   - Endpoint ingest data (CO₂, suhu, getar).
   - Widget monitoring di dashboard + alert rules.

3. **Notifikasi Multikanal**
   - WhatsApp, Email, Telegram disatukan (with template manager).
   - Pengaturan kanal di Settings + toggling per severity.

4. **Gamifikasi & Reward**
   - Extend Discipline Leaderboard → badge, poin, leaderboard mingguan.
   - Panel histori reward untuk HR.

5. **Laporan Investigasi Otomatis**
   - Template investigasi + pengisian otomatis dari riwayat alert.
   - Workflow approval (HSE → Manager → HR).

6. **Teknis lainnya**
   - PDF conversion + email scheduler (`api/reports.py`).
   - Kamera health monitoring (RTSP ping), PWA offline mode.
   - Markdown lint (README) sebelum release.

---

## 10. Perintah Penting

```bash
# Backend
uvicorn api.main:app --reload --port 8000

# Frontend
cd web-dashboard
pnpm dev

# Jalankan test
pytest -q
```

Pastikan environment variable:
- `NEXT_PUBLIC_API_BASE_URL` (contoh: `http://localhost:8000`)
- `NEXT_PUBLIC_WS_URL` (contoh: `ws://localhost:8000/ws`)
- Token Telegram, SMTP, dsb. di `.env` backend.

---

## 11. Tips untuk Gemini

- Gunakan dokumentasi di folder root sebagai prompt awal untuk memahami konteks pengguna.
- Mulai dengan mengecek `IMPLEMENTATION_STATUS.md` untuk status harian.
- Untuk pengembangan UI baru, rujuk `web-dashboard/components/` agar konsisten styling (Tailwind).
- Untuk menambah endpoint, extend `api/main.py` dan update `web-dashboard/services/api.ts` agar typing konsisten.
- Saat menambah data real-time, manfaatkan `useWebSocket.ts` atau extend WebSocket backend.
- Tambahkan catatan di `PROJECT_SUMMARY_FOR_GEMINI.md` ini bila ada perubahan besar, agar knowledge tetap sinkron.

---

**Disusun:** 09 Nov 2025 – Cascaded Assistant

Silakan lanjutkan pengerjaan sesuai roadmap di atas menggunakan Gemini.
