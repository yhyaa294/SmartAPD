from fastapi import BackgroundTasks, FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
import sqlite3
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import threading
from collections import defaultdict, Counter
from pydantic import BaseModel

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from api.websocket import manager
from api.reports import ReportGenerator

DB_PATH = os.getenv("DB_PATH", os.path.join("logs", "detections.db"))
API_TITLE = "SmartAPD API"

app = FastAPI(title=API_TITLE)

scheduler_lock = threading.Lock()
scheduler: AsyncIOScheduler | None = None
HR_SEEDED = False

REPORT_SCHEDULE_CRON = os.getenv("REPORT_SCHEDULE_CRON", "0 6 * * MON")  # Default every Monday 06:00
REPORT_RECIPIENTS = [email.strip() for email in os.getenv("REPORT_RECIPIENTS", "").split(",") if email.strip()]
REPORT_TIMEZONE = os.getenv("REPORT_TIMEZONE", "Asia/Jakarta")
ENABLE_REPORT_SCHEDULER = os.getenv("ENABLE_REPORT_SCHEDULER", "true").lower() in {"1", "true", "yes"}

FALLBACK_RISK_MAP = {
    "generated_at": datetime.now().isoformat(),
    "summary": {
        "total_areas": 3,
        "highest_risk": {
            "location": "Workshop A",
            "riskScore": 88,
            "trend": "+12%"
        },
        "average_risk": 62
    },
    "areas": [
        {
            "location": "Workshop A",
            "camera": "Camera_1",
            "coordinates": {"lat": -6.2005, "lng": 106.8169},
            "totalViolations": 28,
            "recentViolations": 9,
            "riskScore": 88,
            "trend": "+12%",
            "topViolations": ["Tidak Pakai Helm", "Tidak Pakai Rompi"],
            "shiftRisks": [
                {"shift": "Pagi", "riskScore": 70},
                {"shift": "Siang", "riskScore": 85},
                {"shift": "Malam", "riskScore": 92}
            ]
        },
        {
            "location": "Gudang Bahan",
            "camera": "Camera_3",
            "coordinates": {"lat": -6.201, "lng": 106.818},
            "totalViolations": 16,
            "recentViolations": 5,
            "riskScore": 68,
            "trend": "+4%",
            "topViolations": ["Tidak Pakai Sarung Tangan"],
            "shiftRisks": [
                {"shift": "Pagi", "riskScore": 55},
                {"shift": "Siang", "riskScore": 64},
                {"shift": "Malam", "riskScore": 78}
            ]
        },
        {
            "location": "Area Loading",
            "camera": "Camera_4",
            "coordinates": {"lat": -6.1995, "lng": 106.8175},
            "totalViolations": 10,
            "recentViolations": 3,
            "riskScore": 52,
            "trend": "-6%",
            "topViolations": ["Tidak Pakai Helm"],
            "shiftRisks": [
                {"shift": "Pagi", "riskScore": 40},
                {"shift": "Siang", "riskScore": 58},
                {"shift": "Malam", "riskScore": 48}
            ]
        }
    ]
}

# CORS for local dev
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_conn():
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        ensure_hr_seed(conn)
        ensure_alert_tables(conn)
        return conn
    except Exception:
        return None


def ensure_hr_seed(conn: sqlite3.Connection):
    global HR_SEEDED
    if HR_SEEDED:
        return

    with scheduler_lock:
        if HR_SEEDED:
            return

        cursor = conn.cursor()

        # Teams and members
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS teams (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                supervisor TEXT,
                shift_lead TEXT,
                contact TEXT,
                current_shift TEXT,
                last_updated TEXT
            )
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS team_members (
                id INTEGER PRIMARY KEY,
                team_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                role TEXT,
                shift TEXT,
                phone TEXT,
                FOREIGN KEY(team_id) REFERENCES teams(id)
            )
            """
        )

        # Checklists tables
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS checklists (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                category TEXT,
                frequency TEXT,
                owner TEXT,
                last_updated TEXT,
                instructions TEXT
            )
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS checklist_items (
                id INTEGER PRIMARY KEY,
                checklist_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                mandatory INTEGER DEFAULT 1,
                order_index INTEGER DEFAULT 0,
                FOREIGN KEY(checklist_id) REFERENCES checklists(id)
            )
            """
        )

        # Seed default data if tables empty
        cursor.execute("SELECT COUNT(*) as c FROM teams")
        if cursor.fetchone()["c"] == 0:
            seed_teams(cursor)

        cursor.execute("SELECT COUNT(*) as c FROM checklists")
        if cursor.fetchone()["c"] == 0:
            seed_checklists(cursor)

        conn.commit()
        HR_SEEDED = True


def seed_teams(cursor: sqlite3.Cursor) -> None:
    now = datetime.now().isoformat()
    teams = [
        (1, "Tim Mandor A", "Budi Santoso", "Siti Rahma", "+62 812-3456-7890", "Shift Pagi", now),
        (2, "Tim Mandor B", "Andi Wijaya", "Rina Oktaviani", "+62 813-9876-5432", "Shift Malam", now),
    ]
    cursor.executemany(
        "INSERT INTO teams (id, name, supervisor, shift_lead, contact, current_shift, last_updated) VALUES (?, ?, ?, ?, ?, ?, ?)",
        teams,
    )

    members = [
        (1, 1, "Agus Salim", "Operator Crane", "Shift Pagi", "+62 811-2233-4455"),
        (2, 1, "Dewi Lestari", "Safety Officer", "Shift Pagi", "+62 819-9988-7766"),
        (3, 1, "Rahmat Hidayat", "Welder", "Shift Pagi", "+62 812-1234-5678"),
        (4, 2, "Wulan Sari", "Safety Officer", "Shift Malam", "+62 817-4455-6677"),
        (5, 2, "Irwan Pratama", "Operator Forklift", "Shift Malam", "+62 815-5544-3322"),
        (6, 2, "Yusuf Mahendra", "Supervisor Lapangan", "Shift Malam", "+62 812-6677-8899"),
    ]
    cursor.executemany(
        "INSERT INTO team_members (id, team_id, name, role, shift, phone) VALUES (?, ?, ?, ?, ?, ?)",
        members,
    )


def seed_checklists(cursor: sqlite3.Cursor) -> None:
    now = datetime.now().isoformat()
    checklists = [
        (
            1,
            "Inspeksi APD Harian",
            "APD",
            "Harian",
            "Safety Officer",
            now,
            "Pastikan seluruh pekerja menggunakan APD sesuai standar sebelum mulai bekerja.",
        ),
        (
            2,
            "Audit Area Kerja",
            "Operasional",
            "Mingguan",
            "Mandor",
            now,
            "Periksa kondisi area kerja, signage, dan potensi bahaya setiap awal minggu.",
        ),
    ]
    cursor.executemany(
        "INSERT INTO checklists (id, name, category, frequency, owner, last_updated, instructions) VALUES (?, ?, ?, ?, ?, ?, ?)",
        checklists,
    )

    items = [
        (1, 1, "Helm keselamatan terpasang", "Cek kondisi helm bebas retak dan sesuai ukuran.", 1, 1),
        (2, 1, "Rompi reflektif digunakan", "Pastikan rompi bersih dan reflektif.", 1, 2),
        (3, 1, "Sepatu kerja sesuai standar", "Sol anti slip dan tidak rusak.", 1, 3),
        (4, 2, "Area kerja bebas hambatan", "Singkirkan material yang mengganggu jalur.", 1, 1),
        (5, 2, "Rambu peringatan terlihat jelas", "Ganti rambu yang pudar atau rusak.", 1, 2),
        (6, 2, "Pencahayaan memadai", "Catat area yang masih gelap.", 0, 3),
    ]
    cursor.executemany(
        """
        INSERT INTO checklist_items (id, checklist_id, title, description, mandatory, order_index)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        items,
    )


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/stats")
def get_stats():
    conn = get_conn()
    if conn is None:
        # fallback demo numbers
        return {
            "totalDetections": 45,
            "violations": 12,
            "complianceRate": 73.3,
            "compliantWorkers": 33,
        }
    try:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) AS c FROM detections")
        total = cur.fetchone()[0] if cur.fetchone is not None else 0
        cur.execute("SELECT COUNT(*) AS c FROM detections WHERE violation = 1")
        vio = cur.fetchone()[0] if cur.fetchone is not None else 0
        comp_rate = round(((total - vio) / total * 100.0), 1) if total > 0 else 0.0
        # demo estimate
        compliant_workers = max(total - vio, 0)
        return {
            "totalDetections": total if total else 45,
            "violations": vio if total else 12,
            "complianceRate": comp_rate if total else 73.3,
            "compliantWorkers": compliant_workers if total else 33,
        }
    finally:
        try:
            conn.close()
        except Exception:
            pass


@app.get("/api/pulse")
def get_pulse(days: int = 7) -> Dict[str, Any]:
    """Return HSE Pulse score and key KPIs for the Pulse page.
    Metrics:
    - pulse_score: 0-100 composite
    - total_today: violations today; avg_7d: average per day over lookback
    - avg_response_time_sec: average time from violation to first resolve action
    - lti_free_days: days since last critical (derived from violation_type containing 'helm' as example proxy)
    - system_health: cameras_online/total, sensors placeholder
    - unresolved_high: count unresolved high/critical
    """
    conn = get_conn()
    if conn is None:
        raise HTTPException(status_code=500, detail="Database unavailable")

    try:
        cursor = conn.cursor()

        now = datetime.now()
        start_today = datetime(now.year, now.month, now.day)
        lookback_start = now - timedelta(days=max(days, 1))

        # Violations today
        cursor.execute(
            """
            SELECT COUNT(*) as cnt
            FROM violations
            WHERE timestamp >= ?
            """,
            (start_today.isoformat(),),
        )
        row = cursor.fetchone()
        total_today = int(row["cnt"]) if row else 0

        # Violations in lookback (for average per day)
        cursor.execute(
            """
            SELECT COUNT(*) as cnt
            FROM violations
            WHERE timestamp >= ?
            """,
            (lookback_start.isoformat(),),
        )
        row = cursor.fetchone()
        violations_lookback = int(row["cnt"]) if row else 0
        avg_7d = round(violations_lookback / float(days), 2) if days else violations_lookback

        # Average response time: first resolve action per violation
        cursor.execute(
            """
            SELECT v.id as vid, v.timestamp as vts,
                   MIN(CASE WHEN aa.action='resolve' THEN aa.created_at END) as rts
            FROM violations v
            LEFT JOIN alert_actions aa ON aa.violation_id = v.id
            WHERE v.timestamp >= ?
            GROUP BY v.id
            """,
            (lookback_start.isoformat(),),
        )
        times = []
        for r in cursor.fetchall():
            if r["vts"] and r["rts"]:
                try:
                    dt_v = datetime.fromisoformat(r["vts"])  # type: ignore
                    dt_r = datetime.fromisoformat(r["rts"])  # type: ignore
                    diff = (dt_r - dt_v).total_seconds()
                    if diff >= 0:
                        times.append(diff)
                except Exception:
                    continue
        avg_response_time_sec = int(sum(times) / len(times)) if times else 0

        # LTI-free days proxy: days since last critical (e.g., violation_type contains 'helm')
        cursor.execute(
            """
            SELECT MAX(timestamp) as last_crit
            FROM violations
            WHERE LOWER(violation_type) LIKE '%helm%' OR LOWER(violation_type) LIKE '%helmet%'
            """
        )
        row = cursor.fetchone()
        lti_free_days = 0
        if row and row["last_crit"]:
            try:
                last_crit = datetime.fromisoformat(row["last_crit"])  # type: ignore
                lti_free_days = max(0, (now - last_crit).days)
            except Exception:
                lti_free_days = 0

        # System health: cameras
        cursor.execute("SELECT COUNT(*) as total FROM cameras")
        total_cameras = int((cursor.fetchone() or {"total": 0})["total"])  # type: ignore
        cursor.execute("SELECT COUNT(*) as online FROM cameras WHERE status='online'")
        online_cameras = int((cursor.fetchone() or {"online": 0})["online"])  # type: ignore

        # Unresolved high: unresolved and likely high severity
        cursor.execute(
            """
            SELECT COUNT(*) as cnt
            FROM violations
            WHERE (status='unresolved' OR resolved=0)
              AND (
                LOWER(violation_type) LIKE '%helm%' OR LOWER(violation_type) LIKE '%helmet%'
              )
            """
        )
        unresolved_high = int((cursor.fetchone() or {"cnt": 0})["cnt"])  # type: ignore

        # Composite pulse (heuristic):
        # Base on average compliance from discipline endpoint fallback if needed
        # compliance ~ 100 - 100*(violations/detections). Use discipline if available.
        # Here approximate from last 7d: fewer violations -> higher score.
        # Normalize violation rate against (avg_7d + 1) and online cameras ratio.
        camera_ratio = (online_cameras / total_cameras) if total_cameras else 1.0
        violation_factor = 1.0 / (1.0 + (avg_7d / 10.0))  # more avg violations -> lower factor
        response_factor = 1.0 / (1.0 + (avg_response_time_sec / 300.0))  # 5min baseline
        pulse_score = max(0.0, min(1.0, 0.5 * violation_factor + 0.3 * response_factor + 0.2 * camera_ratio)) * 100.0

        return {
            "generated_at": now.isoformat(),
            "pulse_score": round(pulse_score, 1),
            "violations": {
                "total_today": total_today,
                "avg_per_day": avg_7d,
            },
            "avg_response_time_sec": avg_response_time_sec,
            "lti_free_days": lti_free_days,
            "system_health": {
                "cameras_online": online_cameras,
                "cameras_total": total_cameras,
                "sensors": {
                    "online": 0,
                    "total": 0,
                },
            },
            "unresolved_high": unresolved_high,
        }
    finally:
        try:
            conn.close()
        except Exception:
            pass
@app.get("/api/violations")
def get_violations(limit: int = 10) -> List[Dict[str, Any]]:
    conn = get_conn()
    if conn is None:
        return [
            {"id": 1, "worker": "Worker #A001", "location": "Workshop A", "violation": "No Helmet", "time": "14:23", "status": "unresolved"},
            {"id": 2, "worker": "Worker #B002", "location": "Test Zone", "violation": "No Vest", "time": "13:45", "status": "unresolved"},
            {"id": 3, "worker": "Worker #C003", "location": "Demo Site", "violation": "No Gloves", "time": "12:18", "status": "resolved"},
        ]
    try:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT id, worker_id as worker, location, violation_type as violation,
                   strftime('%H:%M', timestamp) as time,
                   CASE WHEN violation = 1 THEN 'unresolved' ELSE 'resolved' END as status
            FROM detections
            ORDER BY timestamp DESC
            LIMIT ?
            """,
            (limit,),
        )
        rows = cur.fetchall()
        results = [dict(r) for r in rows]
        return results
    finally:
        try:
            conn.close()
        except Exception:
            pass


@app.get("/api/cameras")
def get_cameras() -> List[Dict[str, Any]]:
    # Return demo cameras for now. Can be backed by DB table "cameras" later.
    return [
        {"id": 1, "name": "Demo Camera 1", "location": "Test Area", "status": "online", "violations": 2, "workers": 5},
        {"id": 2, "name": "Demo Camera 2", "location": "Workshop", "status": "online", "violations": 1, "workers": 3},
        {"id": 3, "name": "Demo Camera 3", "location": "Assembly", "status": "online", "violations": 0, "workers": 4},
        {"id": 4, "name": "Demo Camera 4", "location": "Storage", "status": "offline", "violations": 0, "workers": 0},
    ]


@app.get("/api/teams")
def get_teams(include_members: bool = True) -> List[Dict[str, Any]]:
    conn = get_conn()
    if conn is None:
        # Fallback to seeded sample data if DB unreachable
        sample = [
            {
                "id": 1,
                "name": "Tim Mandor A",
                "supervisor": "Budi Santoso",
                "shift_lead": "Siti Rahma",
                "contact": "+62 812-3456-7890",
                "current_shift": "Shift Pagi",
                "members": [
                    {"name": "Agus Salim", "role": "Operator Crane", "shift": "Shift Pagi", "phone": "+62 811-2233-4455"},
                    {"name": "Dewi Lestari", "role": "Safety Officer", "shift": "Shift Pagi", "phone": "+62 819-9988-7766"},
                ],
            }
        ]
        return sample

    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, name, supervisor, shift_lead, contact, current_shift, last_updated FROM teams ORDER BY name"
        )
        teams = [dict(row) for row in cursor.fetchall()]

        if include_members and teams:
            team_ids = tuple(team["id"] for team in teams)
            placeholders = ",".join("?" for _ in team_ids)
            cursor.execute(
                f"SELECT team_id, name, role, shift, phone FROM team_members WHERE team_id IN ({placeholders}) ORDER BY order_index"  # type: ignore[str-format]
                if False
                else "SELECT team_id, name, role, shift, phone FROM team_members ORDER BY team_id, name",
                team_ids if team_ids else (0,),
            )

            members_by_team: Dict[int, List[Dict[str, Any]]] = {}
            for row in cursor.fetchall():
                members_by_team.setdefault(row["team_id"], []).append(dict(row))

            for team in teams:
                team["members"] = members_by_team.get(team["id"], [])

        return teams
    finally:
        conn.close()


@app.get("/api/checklists")
def get_checklists() -> List[Dict[str, Any]]:
    conn = get_conn()
    if conn is None:
        return [
            {
                "id": 1,
                "name": "Inspeksi APD Harian",
                "category": "APD",
                "frequency": "Harian",
                "owner": "Safety Officer",
                "last_updated": datetime.now().isoformat(),
                "instructions": "Pastikan seluruh pekerja menggunakan APD sesuai standar sebelum mulai bekerja.",
                "items": [
                    {"title": "Helm keselamatan terpasang", "mandatory": True},
                    {"title": "Rompi reflektif digunakan", "mandatory": True},
                ],
            }
        ]

    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, name, category, frequency, owner, last_updated, instructions FROM checklists ORDER BY name"
        )
        checklists = [dict(row) for row in cursor.fetchall()]

        if not checklists:
            return []

        checklist_ids = tuple(item["id"] for item in checklists)
        placeholders = ",".join("?" for _ in checklist_ids)
        cursor.execute(
            f"""
            SELECT checklist_id, title, description, mandatory, order_index
            FROM checklist_items
            WHERE checklist_id IN ({placeholders})
            ORDER BY checklist_id, order_index
            """
            if checklist_ids
            else "SELECT checklist_id, title, description, mandatory, order_index FROM checklist_items ORDER BY checklist_id, order_index",
            checklist_ids if checklist_ids else (0,),
        )

        items_by_checklist: Dict[int, List[Dict[str, Any]]] = {}
        for row in cursor.fetchall():
            data = dict(row)
            data["mandatory"] = bool(data.get("mandatory", 0))
            items_by_checklist.setdefault(row["checklist_id"], []).append(data)

        for checklist in checklists:
            checklist["items"] = items_by_checklist.get(checklist["id"], [])

        return checklists
    finally:
        conn.close()


class ResolveAlertPayload(BaseModel):
    alert_id: int
    notes: Optional[str] = None
    actor: Optional[str] = None
    evidence: Optional[str] = None


class EscalateAlertPayload(BaseModel):
    alert_id: int
    level: Optional[str] = None
    notes: Optional[str] = None
    actor: Optional[str] = None
    severity: Optional[str] = None
    auto: Optional[bool] = False
    evidence: Optional[str] = None


@app.get("/api/discipline")
def get_discipline_stats(days: int = 7) -> Dict[str, Any]:
    conn = get_conn()
    if conn is None:
        raise HTTPException(status_code=500, detail="Database unavailable")

    lookback = datetime.now() - timedelta(days=days)

    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT worker_id, violation_type, timestamp
            FROM violations
            WHERE timestamp >= ?
            """,
            (lookback.isoformat(),),
        )
        rows = cursor.fetchall()

        cursor.execute(
            """
            SELECT worker_id, COUNT(*) as detections, SUM(violations) as violation_events
            FROM detections
            WHERE timestamp >= ?
            GROUP BY worker_id
            """,
            (lookback.isoformat(),),
        )
        detection_rows = cursor.fetchall()

        worker_stats: Dict[str, Dict[str, Any]] = defaultdict(lambda: {
            "violations": 0,
            "detections": 0,
            "topViolations": Counter(),
        })

        for row in rows:
            worker = row["worker_id"] or "Unknown"
            violation_type = row["violation_type"] or "unknown_violation"
            worker_stats[worker]["violations"] += 1
            worker_stats[worker]["topViolations"][violation_type] += 1

        for row in detection_rows:
            worker = row["worker_id"] or "Unknown"
            detections = row["detections"] or 0
            violations = row["violation_events"] or 0
            worker_stats[worker]["detections"] += detections
            worker_stats[worker]["violations"] += violations

        leaderboard = []
        total_compliance = 0
        total_workers = 0

        for worker, stats in worker_stats.items():
            detections = stats["detections"]
            violations = stats["violations"]
            if detections == 0:
                continue
            total_workers += 1
            compliance_rate = max(0.0, 100 - (violations / max(detections, 1)) * 100)
            total_compliance += compliance_rate
            leaderboard.append({
                "worker": worker,
                "detections": detections,
                "violations": violations,
                "complianceRate": round(compliance_rate, 2),
                "topViolations": [v for v, _ in stats["topViolations"].most_common(3)],
            })

        leaderboard.sort(key=lambda item: item["complianceRate"], reverse=True)

        return {
            "generated_at": datetime.now().isoformat(),
            "summary": {
                "total_workers": total_workers,
                "average_compliance": round(total_compliance / max(total_workers, 1), 2),
            },
            "leaderboard": leaderboard,
        }
    except Exception as exc:
        print(f"Discipline aggregation failed: {exc}")
        raise HTTPException(status_code=500, detail="Gagal menghitung statistik kedisiplinan")
    finally:
        try:
            conn.close()
        except Exception:
            pass


@app.get("/api/alerts/actions")
def list_alert_actions(limit: int = 100) -> List[Dict[str, Any]]:
    conn = get_conn()
    if conn is None:
        raise HTTPException(status_code=500, detail="Database unavailable")

    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT aa.id, aa.violation_id as alert_id, aa.action, aa.notes, aa.level, aa.actor,
                   aa.auto_generated as auto, aa.evidence, aa.created_at as timestamp,
                   v.worker_id as worker, v.violation_type as violation
            FROM alert_actions aa
            LEFT JOIN violations v ON aa.violation_id = v.id
            ORDER BY aa.created_at DESC
            LIMIT ?
            """,
            (limit,),
        )
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


@app.post("/api/alerts/resolve")
def resolve_alert(payload: ResolveAlertPayload):
    conn = get_conn()
    if conn is None:
        raise HTTPException(status_code=500, detail="Database unavailable")

    try:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE violations SET resolved = 1 WHERE id = ?",
            (payload.alert_id,),
        )
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Alert tidak ditemukan")

        cursor.execute(
            """
            INSERT INTO alert_actions (violation_id, action, notes, actor, auto_generated, evidence)
            VALUES (?, ?, ?, ?, 0, ?)
            """,
            (
                payload.alert_id,
                'resolve',
                payload.notes,
                payload.actor,
                payload.evidence,
            ),
        )
        conn.commit()

        action = {
            "id": cursor.lastrowid,
            "alert_id": payload.alert_id,
            "action": "resolve",
            "notes": payload.notes,
            "actor": payload.actor,
            "evidence": payload.evidence,
            "timestamp": datetime.now().isoformat(),
            "auto": False,
        }
        return action
    finally:
        conn.close()


@app.post("/api/alerts/actions")
def escalate_alert(payload: EscalateAlertPayload):
    conn = get_conn()
    if conn is None:
        raise HTTPException(status_code=500, detail="Database unavailable")

    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id FROM violations WHERE id = ?",
            (payload.alert_id,),
        )
        if cursor.fetchone() is None:
            raise HTTPException(status_code=404, detail="Alert tidak ditemukan")

        cursor.execute(
            """
            INSERT INTO alert_actions (violation_id, action, notes, level, actor, auto_generated, evidence)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                payload.alert_id,
                'escalate',
                payload.notes,
                payload.level,
                payload.actor,
                1 if payload.auto else 0,
                payload.evidence,
            ),
        )
        conn.commit()

        action = {
            "id": cursor.lastrowid,
            "alert_id": payload.alert_id,
            "action": "escalate",
            "notes": payload.notes,
            "level": payload.level,
            "actor": payload.actor,
            "timestamp": datetime.now().isoformat(),
            "auto": bool(payload.auto),
            "evidence": payload.evidence,
        }
        return action
    finally:
        conn.close()


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive and listen for client messages
            data = await websocket.receive_text()
            # Echo back for testing
            await websocket.send_json({"type": "echo", "message": data})
    except WebSocketDisconnect:
        manager.disconnect(websocket)


@app.post("/api/trigger-alert")
async def trigger_alert(violation: Dict[str, Any]):
    """Manually trigger a violation alert (for testing)"""
    await manager.send_violation_alert(violation)
    return {"status": "alert_sent", "violation": violation}


def _handle_report_generation(report_type: str = "weekly") -> Dict[str, Any]:
    generator = ReportGenerator(db_path=DB_PATH)
    html = generator.generate_weekly_report() if report_type == "weekly" else generator.generate_weekly_report()
    filename = f"{report_type}_report_{datetime.now().strftime('%Y%m%d')}"
    pdf_path = generator.save_pdf(html, filename)

    primary_recipient = REPORT_RECIPIENTS[0] if REPORT_RECIPIENTS else None
    if primary_recipient:
        subject = f"SmartAPD {report_type.title()} Safety Report"
        generator.send_email(
            to_email=primary_recipient,
            subject=subject,
            html_body=html,
            pdf_path=pdf_path,
        )

    return {
        "status": "success",
        "report_type": report_type,
        "file_path": pdf_path,
        "generated_at": datetime.now().isoformat(),
        "email_sent": bool(primary_recipient),
    }


@app.get("/api/reports/generate")
def generate_report(report_type: str = "weekly", background: BackgroundTasks | None = None):
    """Generate safety report and optionally trigger email delivery"""
    if report_type not in {"weekly", "monthly"}:
        return {"status": "error", "message": "Invalid report type"}

    if background:
        background.add_task(_handle_report_generation, report_type)
        return {"status": "queued", "message": "Report generation scheduled"}

    return _handle_report_generation(report_type)


def schedule_report_jobs():
    global scheduler
    if not ENABLE_REPORT_SCHEDULER:
        return

    with scheduler_lock:
        if scheduler and scheduler.running:
            return

        scheduler = AsyncIOScheduler(timezone=REPORT_TIMEZONE)
        scheduler.add_job(
            _handle_report_generation,
            CronTrigger.from_crontab(REPORT_SCHEDULE_CRON, timezone=REPORT_TIMEZONE),
            kwargs={"report_type": "weekly"},
            id="weekly_report_job",
            replace_existing=True,
        )
        scheduler.start()


@app.on_event("startup")
async def startup_event():
    conn = get_conn()
    if conn:
        conn.close()
    schedule_report_jobs()


@app.on_event("shutdown")
async def shutdown_event():
    global scheduler
    if scheduler and scheduler.running:
        scheduler.shutdown()


# To run locally: uvicorn api.main:app --reload --port 8000
