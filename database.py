import sqlite3

DB_NAME = "placement.db"

def get_conn():
    return sqlite3.connect(DB_NAME)

def init_db():
    """Initialize database with latest table structure"""
    conn = get_conn()
    c = conn.cursor()

    # Updated events table with package fields
    c.execute("""
    CREATE TABLE IF NOT EXISTS events(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        company TEXT,
        drive_date TEXT,
        drive_type TEXT,
        appeared INTEGER DEFAULT 0,
        placed INTEGER DEFAULT 0,
        package REAL DEFAULT 0.0,
        highest_package REAL DEFAULT 0.0,
        avg_package REAL DEFAULT 0.0,
        UNIQUE(company, drive_date)
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS students(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        branch TEXT,
        company TEXT,
        package REAL DEFAULT 0.0,
        drive_date TEXT
    )
    """)

    conn.commit()
    conn.close()
    print("✅ Database tables initialized/updated successfully")


def insert_event(data):
    conn = get_conn()
    c = conn.cursor()

    try:
        # Check for duplicate
        c.execute("""
            SELECT id FROM events 
            WHERE company = ? AND drive_date = ?
        """, (data.get("company"), data.get("date")))

        if c.fetchone():
            print(f"Skipped duplicate event: {data.get('company')} / {data.get('date')}")
            conn.close()
            return

        # Insert with all package fields
        c.execute("""
            INSERT INTO events 
            (company, drive_date, drive_type, appeared, placed, package, highest_package, avg_package)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data.get("company"),
            data.get("date"),
            data.get("type", "On-campus"),
            data.get("appeared", 0),
            data.get("placed", 0),
            data.get("package", 0.0),
            data.get("highest_package", 0.0),
            data.get("avg_package", 0.0)
        ))

        conn.commit()
        print(f"✅ Event inserted: {data.get('company')} - Placed: {data.get('placed')}")

    except Exception as e:
        print(f"❌ Error inserting event: {e}")
    finally:
        conn.close()


def insert_student(student):
    conn = get_conn()
    c = conn.cursor()

    try:
        c.execute("""
            SELECT id FROM students 
            WHERE name = ? AND company = ? AND drive_date = ?
        """, (
            student.get("name"),
            student.get("company"),
            student.get("date")
        ))

        if c.fetchone() is not None:
            conn.close()
            return

        c.execute("""
            INSERT INTO students (name, branch, company, package, drive_date)
            VALUES (?, ?, ?, ?, ?)
        """, (
            student.get("name"),
            student.get("branch", "N/A"),
            student.get("company"),
            student.get("package", 0.0),
            student.get("date")
        ))

        conn.commit()

    except Exception as e:
        print(f"Error inserting student: {e}")
    finally:
        conn.close()