import re
from docx import Document
import PyPDF2


# ---------------- FILE READ ----------------

def read_docx(path):
    doc = Document(path)
    return "\n".join(p.text for p in doc.paragraphs)


def read_pdf(path):
    text = ""
    with open(path, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        for page in reader.pages:
            t = page.extract_text()
            if t:
                text += t
    return text


# ---------------- GENERIC FINDER ----------------

def try_patterns(text, patterns, default=""):
    for p in patterns:
        m = re.search(p, text, re.I)
        if m:
            return m.group(1).strip()
    return default


# ---------------- COMPANY ----------------

def find_company(text):
    patterns = [
        r"Name of the Company\s*[:\-]?\s*(.+?)(?:\n|\s{2,}|$)",
        r"Company Name\s*[:\-]?\s*(.+?)(?:\n|\s{2,}|$)",
        r"On\s+\d{1,2}.*?\s+([A-Za-z\s\.\&]+?)\s+(?:was| Pvt\.? Ltd|Private Limited)",
        r"for\s+([A-Za-z0-9\s\.\&\-]+?)\s+(?:was organized|Pvt|on\s+\d{1,2})",
    ]
    val = try_patterns(text, patterns, "Unknown")
    return val.strip().replace("\n", " ")


# ---------------- DATE ----------------

def find_date(text):
    patterns = [
        r"(?:Date|on)\s*[-–:]\s*(\d{1,2}[a-z]{0,3}\s+[A-Za-z]+\s+\d{4})",
        r"(\d{1,2}(?:st|nd|rd|th)?\s+[A-Za-z]+\s*,?\s*\d{4})",
        r"(\d{2,4}[-/]\d{2}[-/]\d{2,4})"
    ]
    return try_patterns(text, patterns, "")


# ---------------- APPEARED ----------------

def find_appeared(text):
    # Prioritize explicit "registered" numbers
    patterns = [
        r"Number of the students registered\s*(\d+)\s*\(Online\)\s*&\s*(\d+)\s*\(Offline\)",  # 65 & 23
        r"(\d+)\s*students?\s*registered",
        r"out of\s*(\d+)\s*students",
        r"Total\s*(\d+)\s*participants|students",
    ]

    for pat in patterns:
        m = re.search(pat, text, re.I)
        if m:
            if len(m.groups()) == 2:  # online + offline
                return int(m.group(1)) + int(m.group(2))
            else:
                return int(m.group(1))

    # Very last fallback: count lines that look like student names
    student_count = len(extract_students(text, "temp", "temp"))  # rough estimate
    if student_count > 5:
        return student_count * 5  # rough multiplier if only placed list available

    return 0


# ---------------- PLACED ----------------

def find_placed(text):
    patterns_high_priority = [
        r"Finally Placed Students:\s*(\d+)",               # exact label
        r"Total number of students placed\s*(\d+)",
        r"(\d+)\s*students?\s*(?:were|got|finally)?\s*(?:selected|placed)",
        r"out of .*?,\s*(\d+)\s+placed",
    ]

    for pat in patterns_high_priority:
        m = re.search(pat, text, re.I)
        if m:
            return int(m.group(1))

    # Strong fallback: if we extracted many students → trust the list count
    student_list = extract_students(text, "temp", "temp")
    if len(student_list) >= 5:  # reasonable threshold to trust
        return len(student_list)

    return 0

# ---------------- STUDENT LIST ----------------

def extract_students(text, company, date):
    students = []

    section = re.search(
        r"(?:Name of the Students|Name of the Students\s*Gender\s*Email ID\s*Phone Number|Finally Placed Students?:?)(.*?)(NOTICE|Feedback|Glimpses|HR Feedback|Student Feedback|$)",
        text, re.S | re.I
    )

    if not section:
        return students

    block = section.group(1).strip()
    lines = [line.strip() for line in block.split("\n") if line.strip()]

    for line in lines:
        # Skip obvious non-name lines
        if any(keyword in line.lower() for keyword in [
            "number of", "total", "registered", "placed students", "finally", "eligibility",
            "notice", "feedback", "glimpses", "registration", "hr", "date", "company"
        ]):
            continue

        # Must look like a real name: at least two words, no numbers (except maybe initials), no @ or phone-like patterns
        words = line.split()
        if len(words) < 2:
            continue

        # Avoid lines with numbers, emails, headers
        if any(char.isdigit() for char in line) and not any(c.isalpha() for c in words[0]):
            continue

        if "@" in line or len(line) > 60 or " " * 3 in line:  # rough tab/email check
            continue

        # Very basic name-like check: first word starts with capital, contains letters
        if not (words[0][0].isupper() and any(c.isalpha() for c in words[0])):
            continue

        students.append({
            "name": line,
            "branch": "N/A",
            "company": company,
            "package": 0.0,
            "date": date
        })

    return students

# ----------------COMPLEX STUDENT LIST EXTRACTION----------------

def extract_students_from_tables(doc, company, date):
    students = []
    
    for table in doc.tables:
        if len(table.rows) < 2:
            continue  # skip tiny tables
            
        # Try to detect header row
        header_texts = []
        for cell in table.rows[0].cells:
            txt = cell.text.strip().lower()
            header_texts.append(txt)
        
        # Common header patterns
        has_name = any("name" in h for h in header_texts)
        has_gender = any("gender" in h for h in header_texts)
        has_email = any("email" in h for h in header_texts)
        has_phone = any(("phone" in h or "mobile" in h) for h in header_texts)
        
        if not has_name:
            continue  # probably not a student list table
            
        # Guess column indices
        name_col = next((i for i, h in enumerate(header_texts) if "name" in h), 0)
        
        for row in table.rows[1:]:  # skip header
            if len(row.cells) <= name_col:
                continue
                
            name_cell = row.cells[name_col].text.strip()
            if not name_cell or len(name_cell.split()) < 2:
                continue  # skip empty / invalid
                
            student = {
                "name": name_cell,
                "branch": "N/A",
                "company": company,
                "package": 0.0,
                "date": date
            }
            
            # Optional: try to get gender/email/phone if columns exist
            if has_gender and len(row.cells) > name_col + 1:
                gender_col = next((i for i, h in enumerate(header_texts) if "gender" in h), name_col + 1)
                if gender_col < len(row.cells):
                    student["gender"] = row.cells[gender_col].text.strip()  # you can add this field later if needed
            
            students.append(student)
    
    return students


# ---------------- MAIN ----------------

def extract_data(filepath):
    doc = None
    text = ""

    if filepath.lower().endswith(".docx"):
        doc = Document(filepath)
        full_text = "\n".join(para.text.strip() for para in doc.paragraphs if para.text.strip())
        tables_text = "\n".join(
            cell.text.strip() for table in doc.tables 
            for row in table.rows for cell in row.cells if cell.text.strip()
        )
        text = full_text + "\n\n" + tables_text
    else:
        text = read_pdf(filepath)

    company = find_company(text).strip() or "Unknown"
    date_str = find_date(text).strip()

    # ── Extract students first ── (most reliable source for placed count)
    students = []

    if doc is not None:
        students = extract_students_from_tables(doc, company, date_str)

    if not students:
        students = extract_students(text, company, date_str)

    # Clean junk entries
    cleaned_students = []
    for s in students:
        name = s["name"].strip()
        if len(name.split()) < 2:
            continue
        if any(kw in name.lower() for kw in ["number of", "finally", "registered", "placed students", "eligibility"]):
            continue
        cleaned_students.append(s)

    # Trust the number of extracted student names as placed count
    placed_count = len(cleaned_students)

    # Try to parse appeared (registered) from text
    appeared_count = find_appeared(text)

    # If parsed appeared looks unrealistic (smaller than placed), correct it
    if appeared_count < placed_count:
        appeared_count = max(placed_count, placed_count * 3)   # at least placed, preferably more

    # Optional: if still low and we have many students, assume higher ratio
    if appeared_count < 30 and placed_count >= 10:
        appeared_count = placed_count * 5

    data = {
        "company": company,
        "date": date_str,
        "type": "On-campus",
        "appeared": appeared_count,
        "placed": placed_count,           # ← use the real count!
        "package": 0.0
    }

    return data, cleaned_students