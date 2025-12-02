"""
Migration: Add Incident Management Columns

Adds stage, assigned_to, due_at, and related fields to the violations table.
"""

def upgrade(conn):
    cursor = conn.cursor()
    
    # Get the current table structure
    cursor.execute("PRAGMA table_info(violations)")
    columns = [row[1] for row in cursor.fetchall()]
    
    # Add new columns if they don't exist
    if 'stage' not in columns:
        cursor.execute("ALTER TABLE violations ADD COLUMN stage TEXT DEFAULT 'new'")
    if 'assigned_to' not in columns:
        cursor.execute("ALTER TABLE violations ADD COLUMN assigned_to TEXT")
    if 'due_at' not in columns:
        cursor.execute("ALTER TABLE violations ADD COLUMN due_at TEXT")
    if 'last_updated_at' not in columns:
        # SQLite doesn't support datetime('now') in ALTER TABLE, so we'll set the default value after adding the column
        cursor.execute("ALTER TABLE violations ADD COLUMN last_updated_at TEXT")
        cursor.execute("UPDATE violations SET last_updated_at = datetime('now') WHERE last_updated_at IS NULL")
    
    # Add check constraint for stage (SQLite doesn't support adding CHECK constraints with ALTER TABLE)
    # We'll handle this in the application layer instead
    
    # Set default values for existing records
    cursor.execute("UPDATE violations SET stage = 'new' WHERE stage IS NULL")
    cursor.execute("UPDATE violations SET last_updated_at = datetime('now') WHERE last_updated_at IS NULL")
    
    # Create indexes for better performance
    cursor.execute("""
    CREATE INDEX IF NOT EXISTS idx_violations_stage 
    ON violations(stage, assigned_to);
    """)
    
    # Add trigger to update last_updated_at on any change
    cursor.execute("DROP TRIGGER IF EXISTS update_violations_timestamp")
    cursor.execute("""
    CREATE TRIGGER IF NOT EXISTS update_violations_timestamp
    AFTER UPDATE ON violations
    FOR EACH ROW
    BEGIN
        UPDATE violations 
        SET last_updated_at = datetime('now')
        WHERE id = OLD.id;
    END;
    """)
    
    conn.commit()

def downgrade(conn):
    cursor = conn.cursor()
    
    # Remove trigger
    cursor.execute("DROP TRIGGER IF EXISTS update_violations_timestamp;")
    
    # Remove index
    cursor.execute("DROP INDEX IF EXISTS idx_violations_stage;")
    
    # SQLite doesn't support DROP COLUMN in all versions, so we'll create a new table
    cursor.execute("""
    CREATE TABLE violations_backup (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        worker TEXT NOT NULL,
        location TEXT NOT NULL,
        violation TEXT NOT NULL,
        status TEXT NOT NULL,
        resolved BOOLEAN NOT NULL DEFAULT 0,
        evidence TEXT,
        camera_id INTEGER,
        confidence REAL,
        violation_type TEXT,
        notes TEXT
    )
    """)
    
    # Copy data to backup
    cursor.execute("""
    INSERT INTO violations_backup 
    SELECT id, timestamp, worker, location, violation, status, resolved, 
           evidence, camera_id, confidence, violation_type, notes
    FROM violations
    """)
    
    # Drop and recreate the original table
    cursor.execute("DROP TABLE violations;")
    cursor.execute("ALTER TABLE violations_backup RENAME TO violations;")
    
    conn.commit()

if __name__ == "__main__":
    import sqlite3
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python 20241109_add_incident_management_columns.py <db_path> [--downgrade]")
        sys.exit(1)
        
    db_path = sys.argv[1]
    should_downgrade = len(sys.argv) > 2 and sys.argv[2] == "--downgrade"
    
    conn = sqlite3.connect(db_path)
    
    try:
        if should_downgrade:
            print("Downgrading database...")
            downgrade(conn)
            print("Downgrade completed successfully.")
        else:
            print("Upgrading database...")
            upgrade(conn)
            print("Upgrade completed successfully.")
    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()
    finally:
        conn.close()
