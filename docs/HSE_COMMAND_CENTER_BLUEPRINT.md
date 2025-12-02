# SmartAPD: HSE 4.0 Command Center Blueprint

Dokumen ini menerjemahkan konsep "SmartAPD: HSE 4.0 Command Center" ke dalam rancangan teknis dan langkah implementasi berdasarkan kode yang sudah ada. Gunakan blueprint ini sebagai pegangan untuk demo lomba maupun pengembangan industri.

---

## 1. Pilar Arsitektur & Peran Pengguna

| Pilar | Peran Utama | Fokus | Modul Utama |
|-------|-------------|-------|-------------|
| Situational Awareness | Executive, HSE Manager | Monitoring 5-detik | "The Pulse" (Halaman Utama) |
| Incident Management | Supervisor Lapangan, HSE Manager | Penanganan insiden end-to-end | Alert & Investigasi |
| Risk Intelligence | HSE Manager, Data Analyst | Prediksi & analitik mendalam | Analitik Risiko & Prediksi |
| Compliance & System | Administrator, HR | Pengaturan, laporan, integrasi | Admin & Integrasi |

Peran tambahan:
- **Executive (Pimpinan):** Akses read-only ke ringkasan KPI & risk map.
- **Supervisor Lapangan:** Mengelola alert di area masing-masing, upload bukti, lakukan spot-check.
- **HSE Manager:** Mengawasi keseluruhan operasi, menjalankan investigasi, melihat analitik prediktif.
- **Admin Sistem:** Mengatur user, kamera, sensor, notifikasi multikanal.

---

## 2. Modul 1 — Situational Awareness (“The Pulse”)

### Tujuan
Memberikan gambaran instan (<5 detik) terkait kondisi K3 di seluruh area.

### Fitur Kunci
1. **HSE Pulse Score**
   - Satu angka besar yang merepresentasikan kepatuhan real-time (0–100%).
   - Sumber data: `GET /api/discipline` (average compliance), `GET /api/stats` (violations vs detections).
   - Rumus awal (bisa dioptimalkan):
     ```ts
     pulse = 0.6 * complianceRate + 0.2 * (1 - activeViolations/target) + 0.2 * systemUpTime
     ```

2. **Live Interactive Risk Map**
   - Upgrade dari `RiskInsights` → gunakan floor map SVG / peta area.
   - Integrasi data: `risk_map`, `violations`, data sensor IoT (future endpoint `/api/sensors`).
   - Behaviour:
     - Warna area berubah (Hijau/Kuning/Merah) sesuai skor risiko.
     - Efek animasi “pulse” untuk area dengan alert aktif.
     - Klik area → popover berisi:
       - Kamera terkait (mini-player RTSP atau snapshot).
       - Ringkasan alert terakhir (3 pelanggaran terakhir, countdown eskalasi).
       - Tombol quick action: "Open Incident".

3. **Critical Alert Feed**
   - Ambil data `violations` status `unresolved` dengan severity `high`.
   - Tampilkan 3–5 alert terbaru dengan waktu, lokasi, dan tombol “View Workflow”.

4. **KPI Widget**
   - **Total Pelanggaran Hari Ini**: bandingkan dengan average 7 hari.
   - **Waktu Respons Rata-rata**: hitung dari `alert_actions` (pengurangan timestamp `resolve` pertama).
   - **LTI-Free Days**: counter hari tanpa pelanggaran severity “critical”.
   - **System Health**: status kamera (`/api/cameras`) dan sensor (`/api/sensors` backlog).

### Implementasi UI
- Buat halaman baru `app/dashboard/pulse/page.tsx` atau jadikan tab default di dashboard.
- Gunakan layout "card + map".
- Manfaatkan `ResponsiveContainer` (Recharts) atau peta kustom (SVG + `useEffect`).

---

## 3. Modul 2 — Incident Management (Alert & Investigasi)

### Tujuan
Mengelola insiden dari deteksi sampai investigasi selesai dengan akuntabilitas penuh.

### Fitur Kunci
1. **Smart Triage Panel (Trello-like)**
   - Representasi kolom: `New`, `Investigating`, `Waiting Evidence`, `Resolved`.
   - Data sumber: `violations` + status tambahan (`stage`) tersimpan di DB.
   - Interaksi drag-and-drop (library: `@dnd-kit` atau `react-beautiful-dnd`).

2. **Digital Workflow Actions**
   - Tombol per kartu alert:
     - `Resolve` (dengan catatan & bukti – sudah ada di backend).
     - `Escalate` (level HSE Manager, auto countdown – sudah ada).
     - `Assign To…` (butuh kolom baru `assigned_to` pada `alert_actions` atau `violations`).
     - `Request Spot-Check` → memicu form dan notifikasi mobile.

3. **Evidence Locker**
   - Sidebar detail (sudah ada di `AlertsWorkflow`) → perindah supaya menampilkan timeline + preview bukti.
   - Simpan file sebagai base64 atau ke object storage (if available), simpan URL di `alert_actions`.

4. **AI Spot-Check Assistant**
   - Alur: supervisor upload foto → endpoint `/api/spot-check/analyze` (model vision) → hasil (aman/teguran) disimpan sebagai `alert_action` baru.
   - UI menampilkan balasan AI + rekomendasi ("Rekomendasi: Pasang signage tambahan").

### Backend Perluasan
- Tambah kolom `stage`, `assigned_to`, `due_at` pada `violations`.
- Endpoint baru: `POST /api/alerts/assign`, `POST /api/spot-check`.
- Notifikasi ke WA/email via backlog modul multikanal.

---

## 4. Modul 3 — Risk Intelligence (Analitik & Prediksi)

### Tujuan
Memungkinkan manajer mengambil keputusan proaktif berbasis data historis dan prediksi AI.

### Fitur Kunci
1. **Predictive Risk Forecasting**
   - Model: Analisis time-series (Prophet) atau ML ringan (XGBoost) menggunakan log `violations` + metadata.
   - Output: API `/api/risk-forecast?area=A&horizon=7d` → probabilitas per slot waktu.
   - UI: kartu insight ("Gudang B → 75% lebih tinggi pada Jumat 14–16") + chart garis.

2. **Deep Dive Analytics**
   - Gunakan `Recharts` + filter state untuk drill-down by tipe/area/shift/jam.
   - Perlu endpoint agregasi baru, contoh: `/api/analytics/violations?group_by=shift&type=helmet`.
   - Sertakan export CSV.

3. **Compliance Leaderboard**
   - Pakai `DisciplineLeaderboard.tsx` (sudah ada) sebagai blok + extend untuk poin/gamifikasi.
   - Tambah tab "Reward" & "Coaching" → integrasi ke modul gamifikasi.

### Data Pipeline
- ETL: jadwalkan job malam (APScheduler) untuk agregasi ke tabel `analytics_summary`.
- Simpan hasil prediksi agar halaman cepat.

---

## 5. Modul 4 — Compliance & System (Admin & HR)

### Tujuan
Mengatur konfigurasi sistem, laporan, notifikasi, user role, dan integrasi perangkat.

### Fitur Kunci
1. **Automated Report Generator**
   - Selesaikan backlog (`pdfkit/wkhtmltopdf`, scheduler).
   - UI: form pilih periode + channel (download/email).
   - Template investigasi: autogenerate doc dari `alert_actions` + bukti (download PDF/Word).

2. **Multi-Channel Notification Manager**
   - UI di `SettingsPanel`: tabel penerima, kanal (Email/WA/Telegram), trigger (severity/area/time).
   - Backend: simpan aturan (table `notification_rules`), endpoint `POST /api/notifications/test`.

3. **Role-Based Access Control (RBAC)**
   - Tambah tabel `users`, `roles`, `user_roles`.
   - Middleware FastAPI untuk cek permission (menentukan data scope per endpoint).
   - Frontend: guard route (Next.js middleware) + context user role.

4. **Asset Management (Kamera & IoT)**
   - Halaman list kamera (status online/offline, edit RTSP, drag ke area map).
   - Sensor center: register sensor, lihat status, threshold.
   - Endpoint: `/api/assets/cameras`, `/api/assets/sensors`.

---

## 6. Integrasi dengan Kode Eksisting

| Fitur Baru | File/Komponen Referensi Saat Ini | Aksi |
|------------|----------------------------------|------|
| HSE Pulse Score | `web-dashboard/services/api.ts`, `RiskInsights.tsx` | Tambah service `getPulse`, card baru di `dashboard/page.tsx`. |
| Live Risk Map | `RiskInsights.tsx` | Refactor jadi komponen `RiskMapInteractive` dengan peta SVG. |
| Smart Triage | `AlertsWorkflow.tsx` | Pisahkan list → buat `AlertsKanban.tsx` + state stage. |
| Evidence Locker | `AlertsWorkflow.tsx` | Sudah ada, perindah UI & preview file. |
| Spot-Check AI | (baru) | Tambah endpoint + komponen modal upload.
| Predictive Forecast | (baru) | Scheduler + endpoint + UI chart.
| Deep Analytics | `DisciplineLeaderboard.tsx` (pattern) | Buat halaman `analytics/page.tsx`.
| RBAC | Auth di `app/login/page.tsx` | Extend login (JWT/in-memory), guard route.
| Notification Manager | `SettingsPanel.tsx`, `PushNotificationManager.tsx` | Expand UI + integrasi ke backend.
| Asset Management | `app/monitoring/page.tsx` (jika ada) | Buat halaman baru `assets/page.tsx`.

---

## 7. Roadmap Implementasi (Sprint-Level)

1. **Sprint 1 – Situational Awareness**
   - Bangun Pulse Score & KPI widget.
   - Refactor Risk Map menjadi interaktif.
   - Tambah Critical Alert feed.

2. **Sprint 2 – Incident Management**
   - Implementasi Kanban triage + assign.
   - Melengkapi evidence locker & spot-check request.
   - Siapkan endpoint spot-check + notifikasi.

3. **Sprint 3 – Risk Intelligence**
   - Develop pipeline prediksi risiko.
   - Halaman analytics filterable.
   - Integrasi leaderboard (reward/coaching tag).

4. **Sprint 4 – Compliance & System**
   - Finalisasi report generator + template investigasi.
   - Bangun notification manager & RBAC.
   - Halaman asset management kamera/sensor.

---

## 8. Highlight untuk Presentasi Lomba

- **Demo “Pulse Mode”**: tunjukkan risk map berdenyut + score besar.
- **Simulasi incident**: jalankan alert, lihat auto-escalation, upload bukti, spot-check AI.
- **Tampilkan insight prediktif**: sejarah pelanggaran vs prediksi, sebutkan langkah pencegahan.
- **Tekankan budaya K3**: leaderboard & coaching plan.
- **Skalabilitas**: jelaskan modul notifikasi & asset management siap diintegrasi IoT.

---

## 9. Pertanyaan Pengembangan Lanjutan

1. Sumber data sensor apa yang tersedia (temperatur, gas, vibrasi)?
2. Apakah perusahaan memiliki floor map resmi (CAD) untuk dijadikan basis risk map?
3. Kanal notifikasi mana yang prioritas: WhatsApp Business API, Email SMTP, atau Telegram Bot?
4. Schema user existing (LDAP/AD) → integrasi SSO untuk RBAC?
5. Apakah dibutuhkan audit trail PDF untuk pemeriksaan regulasi?

Jawaban atas pertanyaan ini menentukan prioritas teknis sprint berikutnya.

---

## 10. Next Action Checklist

- [ ] Konfirmasi kebutuhan data untuk Pulse Score & Risk Map.
- [ ] Desain UI baru (mockup) untuk Pulse dan Kanban Incident.
- [ ] Tentukan stack model prediksi (Prophet vs regresi custom).
- [ ] Rancang schema RBAC dan migrasi database.
- [ ] Siapkan pipeline notifikasi multikanal (library / vendor yang digunakan).

Blueprint ini siap digunakan sebagai konteks utama ketika berpindah ke Gemini atau kolaborator lain.
