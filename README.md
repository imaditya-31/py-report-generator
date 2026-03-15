# Python Report Generator

A simple web tool made for college placement cells.  
You can upload placement drive reports (in Word .docx or PDF format), the app automatically reads important information like company name, date, number of students appeared, number of students placed, and list of selected students — then shows you beautiful charts and summary.

## Features

- Upload one or many placement reports at once (.docx or .pdf)
- Automatically reads company, date, appeared/placed counts and student names
- Saves everything in a simple database (no complicated setup)
- Shows nice summary cards, bar charts and full list of placed students
- Modern and easy drag-and-drop upload page

## Technologies Used

- Backend: Flask (Python)
- Document reading: python-docx + PyPDF2
- Database: SQLite (automatic – no installation needed)
- Charts: Plotly
- Frontend: HTML + CSS + little JavaScript

## How to Run This Project (Very Simple Steps)

### Step 1: Get the project on your computer

Open Command Prompt (Windows) or Terminal (Mac/Linux) and run these two commands one by one:

```bash
git clone https://github.com/imaditya-31/py-report-generator.git
cd py-report-generator
```

After this, you are inside the project folder.

### Step 2: Create a safe space for Python packages (virtual environment)

This step is important — it keeps this project separate from other Python projects on your computer.

#### On Windows:

```bash
Bashpython -m venv venv
venv\Scripts\activate
```

#### On Mac / Linux:

```bash
Bashpython3 -m venv venv
source venv/bin/activate
```

After running one of these, you should see (venv) appear at the start of your command line — that means it's working.

### Step 3: Install all required packages

Just run this one command:

```bash
Bashpip install -r requirements.txt
```

Wait for it to finish (it will download Flask, Plotly, etc.).

### Step 4: Start the application

Run this command:

##### Windows:

```bash
Bashpython app.py
```

#### Mac / Linux:

```bash
Bashpython3 app.py
```

You will see messages like:

```bash
Running on http://127.0.0.1:5000
```

### Step 5: Open in browser

Open any web browser (Chrome, Edge, Firefox) and type this address: http://localhost:5000 or http://127.0.0.1:5000
Press Enter — you should see the upload page!
How to Use It

Click "Click to browse" or drag your placement report files (.docx or .pdf)

Click Generate Report
Wait a few seconds — you will see summary numbers, charts and list of placed students

To stop the app: go back to the command window and press

```bash
Ctrl + C
```

## 👨‍💻 Developer

**Made with ❤️ by Aditya Vishwakarma**
