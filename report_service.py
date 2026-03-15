from database import get_conn

def get_summary():
    conn = get_conn()
    c = conn.cursor()

    c.execute("SELECT COUNT(*), SUM(appeared), SUM(placed), MAX(package), AVG(package) FROM events")
    row = c.fetchone()

    total_drives = row[0] or 0
    appeared = row[1] or 0
    placed = row[2] or 0

    percentage = (placed / appeared * 100) if appeared else 0

    summary = {
        "total_drives": total_drives,
        "appeared": appeared,
        "placed": placed,
        "percentage": round(percentage, 2),
        "highest_package": row[3] or 0,
        "avg_package": round(row[4] or 0, 2)
    }

    conn.close()
    return summary


def get_chart_data():
    conn = get_conn()
    c = conn.cursor()

    c.execute("SELECT company, appeared, placed FROM events")
    data = c.fetchall()

    conn.close()

    companies = [d[0] for d in data]
    appeared = [d[1] for d in data]
    placed = [d[2] for d in data]

    return companies, appeared, placed

def get_students():
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT name, branch, company, package, drive_date FROM students")
    rows = c.fetchall()
    conn.close()
    return rows


def company_analysis():
    conn = get_conn()
    c = conn.cursor()

    c.execute("""
        SELECT company, COUNT(*) 
        FROM students 
        GROUP BY company
    """)

    data = c.fetchall()
    conn.close()

    companies = [d[0] for d in data]
    counts = [d[1] for d in data]

    return companies, counts