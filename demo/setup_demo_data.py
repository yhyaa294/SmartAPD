"""
Setup Demo Data - Buat data dummy untuk testing dashboard
Tanpa perlu model training dulu!
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta
import random

# Add src to path
sys.path.insert(0, 'src')

from database import Database

print("=" * 60)
print("  🎲 SETUP DEMO DATA - UNTUK TESTING DASHBOARD")
print("=" * 60)
print()

# Initialize database
print("📦 Initializing database...")
db = Database()
print("✅ Database ready!")
print()

# Generate demo data
print("🎲 Generating demo data...")
print()

# Simulate 7 days of data
for day in range(7):
    date = datetime.now() - timedelta(days=6-day)
    
    # Random detections per day (10-30)
    num_detections = random.randint(10, 30)
    
    for i in range(num_detections):
        # Random time during the day
        hour = random.randint(8, 17)  # Work hours
        minute = random.randint(0, 59)
        
        detection_time = date.replace(hour=hour, minute=minute, second=0)
        
        # Random number of persons (1-5)
        total_persons = random.randint(1, 5)
        
        # Random compliance (70-90% compliant)
        compliance_rate = random.uniform(0.7, 0.9)
        compliant_persons = int(total_persons * compliance_rate)
        violations = total_persons - compliant_persons
        
        # Log detection
        detection_id = db.log_detection(
            camera_source=f"Camera_{random.randint(1, 3)}",
            total_persons=total_persons,
            compliant_persons=compliant_persons,
            violations=violations,
            detection_data={
                "timestamp": detection_time.isoformat(),
                "demo": True
            }
        )
        
        # Log violations if any
        if violations > 0:
            for v in range(violations):
                violation_types = ['no_helmet', 'no_vest', 'no_gloves']
                violation_type = random.choice(violation_types)
                
                db.log_violation(
                    camera_source=f"Camera_{random.randint(1, 3)}",
                    violation_type=violation_type,
                    person_id=random.randint(1, 100),
                    confidence=random.uniform(0.75, 0.95),
                    bbox=[
                        random.randint(100, 300),
                        random.randint(100, 300),
                        random.randint(400, 600),
                        random.randint(400, 600)
                    ],
                    notes=f"Demo violation - Day {day+1}"
                )
    
    print(f"  Day {day+1}/7: {num_detections} detections generated ✅")

print()
print("=" * 60)
print("  📊 DEMO DATA SUMMARY")
print("=" * 60)

# Get statistics
stats = db.get_statistics(days=7)
violations = db.get_violations(limit=100)
violation_types = db.get_violation_types_count(days=7)

print()
print(f"Total Detections: {stats['total_detections']}")
print(f"Total Violations: {stats['total_violations']}")
print(f"Compliance Rate: {stats['compliance_rate']:.1f}%")
print()

print("Violation Types:")
for vtype in violation_types:
    print(f"  - {vtype['violation_type']}: {vtype['count']}")

print()
print("=" * 60)
print("  ✅ DEMO DATA READY!")
print("=" * 60)
print()
print("🌐 Sekarang buka dashboard:")
print("   python -m streamlit run dashboard/app.py")
print()
print("📊 Dashboard akan menampilkan:")
print("   - Statistics 7 hari terakhir")
print("   - Violation history")
print("   - Charts & analytics")
print("   - Export data (CSV)")
print()
print("=" * 60)

db.close()
