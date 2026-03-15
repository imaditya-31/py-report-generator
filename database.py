import sqlite3

DB_NAME = "placement.db"

def get_conn():
    return sqlite3.connect(DB_NAME)

def init_db():
    conn = get_conn()
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS events(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        company TEXT,
        drive_date TEXT,
        drive_type TEXT,
        appeared INTEGER,
        placed INTEGER,
        package REAL
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS students(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        branch TEXT,
        company TEXT,
        package REAL,
        drive_date TEXT
    )
    """)

    conn.commit()
    conn.close()

def insert_event(data):
    conn = get_conn()
    c = conn.cursor()
    
    c.execute("SELECT id FROM events WHERE company = ? AND drive_date = ?",
              (data["company"], data["date"]))
    
    if c.fetchone():
        print(f"Skipped duplicate event: {data['company']} / {data['date']}")
        conn.close()
        return
    
    # insert only if not exists
    c.execute("""
        INSERT INTO events (company, drive_date, drive_type, appeared, placed, package)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (data["company"], data["date"], data["type"], data["appeared"], data["placed"], data["package"]))
    
    conn.commit()
    conn.close()

def insert_student(student):
    conn = get_conn()
    c = conn.cursor()

    c.execute("""
        SELECT id FROM students 
        WHERE name = ? AND company = ? AND drive_date = ?
    """, (
        student["name"],
        student["company"],
        student["date"]
    ))

    if c.fetchone() is not None:
        # Optional: print("Skipped duplicate student →", student["name"])
        conn.close()
        return

    c.execute("""
        INSERT INTO students (name, branch, company, package, drive_date)
        VALUES (?, ?, ?, ?, ?)
    """, (
        student["name"],
        student["branch"],
        student["company"],
        student["package"],
        student["date"]
    ))

    conn.commit()
    conn.close()