from flask import Flask, render_template, request, redirect
import os
from database import init_db, insert_event, insert_student
from extractor import extract_data
from report_service import (
    get_summary,
    get_chart_data,
    get_students,
    company_analysis
)

import plotly.graph_objs as go
import plotly.offline as opy

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

init_db()


@app.route("/")
def home():
    return render_template("upload.html")


@app.route("/upload", methods=["POST"])
def upload():
    files = request.files.getlist("files")
    print(f"Number of files received: {len(files)}")
    print(f"FILES RECEIVED: {[f.filename for f in files if f.filename]}")
    
    processed = 0
    
    for file in files:
        if file.filename == "":
            continue
            
        print(f"Processing file: {file.filename}")
        
        path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(path)
        
        print("  → Calling extract_data...")
        data, students = extract_data(path)
        
        # ← Put it HERE, after extraction
        print(f"  → Extracted students ({len(students)}):")
        if students:
            print("     " + "\n     ".join(s['name'] for s in students))
        else:
            print("     (no students extracted)")
        
        print(f"  → Extracted: company={data['company']}, placed={data['placed']}, students count={len(students)}")
        
        print("  → Inserting event...")
        insert_event(data)
        
        print(f"  → Inserting {len(students)} students...")
        for s in students:
            insert_student(s)
        
        processed += 1
    
    print(f"Upload complete. Processed {processed} files.")
    return redirect("/report")


@app.route("/report")
def report():

    summary = get_summary()
    companies, appeared, placed = get_chart_data()

    # Chart 1
    fig = go.Figure()
    fig.add_bar(x=companies, y=appeared, name="Appeared")
    fig.add_bar(x=companies, y=placed, name="Placed")
    chart = opy.plot(fig, output_type="div")

    # Chart 2
    c_names, c_counts = company_analysis()
    fig2 = go.Figure()
    fig2.add_bar(x=c_names, y=c_counts)
    company_chart = opy.plot(fig2, output_type="div")

    students = get_students()

    return render_template(
        "report.html",
        summary=summary,
        chart=chart,
        company_chart=company_chart,
        students=students
    )


if __name__ == "__main__":
    app.run(debug=True)