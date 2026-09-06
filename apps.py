from flask import Flask, render_template, request, redirect, session
import sqlite3
import pickle
import pandas as pd
from openpyxl import Workbook
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors

app = Flask(__name__)
model = pickle.load(open("student_model.pkl", "rb"))
app.secret_key = "your_secret_key_123"

@app.route("/")
def home():
    return render_template("index.html")
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        if username == "admin" and password == "admin123":
            session["admin"] = True
            return redirect("/admin_dashboard")

        return "Invalid Username or Password"

    return render_template("login.html")
@app.route("/student_registration", methods=["GET", "POST"])
def student_registration():

    if request.method == "POST":

        name = request.form["name"]
        usn = request.form["usn"]
        email = request.form["email"]
        phone = request.form["phone"]
        department = request.form["department"]
        semester = request.form["semester"]

        conn = sqlite3.connect("student.db")
        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO students(name, usn, email, phone, department, semester)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (name, usn, email, phone, department, semester))

        conn.commit()
        conn.close()

        return "Student Registered Successfully!"

    return render_template("student_registration.html")
@app.route("/view_students")
def view_students():

    conn = sqlite3.connect("student.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM students")
    students = cursor.fetchall()

    conn.close()

    return render_template("view_students.html", students=students)
@app.route("/edit_student/<int:id>")
def edit_student(id):

    conn = sqlite3.connect("student.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM students WHERE id=?", (id,))
    student = cursor.fetchone()

    conn.close()

    return render_template("edit_student.html", student=student)
@app.route("/update_student/<int:id>", methods=["POST"])
def update_student(id):

    name = request.form["student_name"]
    usn = request.form["usn"]
    email = request.form["email"]
    phone = request.form["phone"]
    department = request.form["department"]
    semester = request.form["semester"]

    conn = sqlite3.connect("student.db")
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE students
        SET name=?, usn=?, email=?, phone=?, department=?, semester=?
        WHERE id=?
    """, (name, usn, email, phone, department, semester, id))

    conn.commit()
    conn.close()

    return redirect("/view_students")
@app.route("/delete_student/<int:id>")
def delete_student(id):

    conn = sqlite3.connect("student.db")
    cursor = conn.cursor()

    cursor.execute("DELETE FROM students WHERE id=?", (id,))

    conn.commit()
    conn.close()

    return redirect("/view_students")

@app.route("/admin_dashboard")
def admin_dashboard():
    if "admin" not in session:
        return redirect("/login")

    conn = sqlite3.connect("student.db")
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM students")
    total_students = cursor.fetchone()[0]

    conn.close()

    return render_template(
        "admin_dashboard.html",
        total_students=total_students
    )
@app.route("/search_student")
def search_student():

    keyword = request.args.get("keyword")

    conn = sqlite3.connect("student.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM students WHERE name LIKE ? OR usn LIKE ?",
        ('%' + keyword + '%', '%' + keyword + '%')
    )

    students = cursor.fetchall()

    conn.close()

    return render_template(
        "view_students.html",
        students=students
    )
@app.route("/ai_prediction")
def ai_prediction():
    return render_template("ai_prediction.html")


@app.route("/predict", methods=["GET", "POST"])
def predict():

    prediction = None

    if request.method == "POST":
        attendance = int(request.form["attendance"])
        marks = int(request.form["marks"])

        prediction = model.predict([[attendance, marks]])[0]

    return render_template(
        "ai_prediction.html",
        prediction=prediction
    )
@app.route("/attendance", methods=["GET", "POST"])
def attendance():

    conn = sqlite3.connect("student.db")
    cursor = conn.cursor()

    cursor.execute("SELECT id, name, usn FROM students")
    students = cursor.fetchall()

    if request.method == "POST":

        student_id = request.form["student_id"]
        attendance_date = request.form["attendance_date"]
        status = request.form["status"]

        cursor.execute("""
        INSERT INTO attendance
        (student_id, attendance_date, status)
        VALUES (?, ?, ?)
        """, (student_id, attendance_date, status))

        conn.commit()
        conn.close()

        return "Attendance Saved Successfully!"

    conn.close()

    return render_template(
        "attendance.html",
        students=students
    )
@app.route("/view_attendance")
def view_attendance():

    conn = sqlite3.connect("student.db")
    cursor = conn.cursor()

    cursor.execute("""
SELECT
students.name,
students.usn,
attendance.attendance_date,
attendance.status
FROM attendance
JOIN students
ON attendance.student_id = students.id
""")
    attendance = cursor.fetchall()

    conn.close()

    return render_template(
        "view_attendance.html",
        attendance=attendance
    )
@app.route("/marks", methods=["GET", "POST"])
def marks():

    conn = sqlite3.connect("student.db")
    cursor = conn.cursor()

    # Get all students for the dropdown
    cursor.execute("SELECT id, name, usn FROM students")
    students = cursor.fetchall()

    if request.method == "POST":

        student_id = request.form["student_id"]
        ia1 = request.form["ia1"]
        ia2 = request.form["ia2"]
        ia3 = request.form["ia3"]

        cursor.execute("""
        INSERT INTO marks
        (student_id, ia1, ia2, ia3)
        VALUES (?, ?, ?, ?)
        """, (student_id, ia1, ia2, ia3))

        conn.commit()
        conn.close()

        return "Marks Saved Successfully!"

    conn.close()

    return render_template("marks.html", students=students)





@app.route("/student_report")
def student_report():

    conn = sqlite3.connect("student.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM students")
    students = cursor.fetchall()

    conn.close()

    return render_template(
        "student_report.html",
        students=students
    )
@app.route("/export_excel")
def export_excel():

    conn = sqlite3.connect("student.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM students")
    students = cursor.fetchall()

    conn.close()

    wb = Workbook()
    ws = wb.active
    ws.title = "Students"

    ws.append([
        "ID",
        "Name",
        "USN",
        "Email",
        "Phone",
        "Department",
        "Semester"
    ])

    for student in students:
        ws.append(student)

    wb.save("Student_Report.xlsx")

    return "Student_Report.xlsx created successfully!"
@app.route("/export_pdf")
def export_pdf():

    conn = sqlite3.connect("student.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM students")
    students = cursor.fetchall()

    conn.close()

    data = [
        ["ID", "Name", "USN", "Email", "Phone", "Department", "Semester"]
    ]

    for student in students:
        data.append(list(student))

    pdf = SimpleDocTemplate("Student_Report.pdf")

    table = Table(data)

    table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.grey),
        ("TEXTCOLOR", (0,0), (-1,0), colors.whitesmoke),
        ("GRID", (0,0), (-1,-1), 1, colors.black),
        ("BACKGROUND", (0,1), (-1,-1), colors.beige),
    ]))

    pdf.build([table])

    return "Student_Report.pdf created successfully!"
@app.route("/logout")
def logout():
    session.pop("admin", None)
    return redirect("/login")
@app.route("/view_marks")
def view_marks():

    conn = sqlite3.connect("student.db")
    cursor = conn.cursor()

    cursor.execute("""
    SELECT students.name,
           students.usn,
           marks.ia1,
           marks.ia2,
           marks.ia3
    FROM marks
    JOIN students
    ON marks.student_id = students.id
    """)

    marks = cursor.fetchall()

    conn.close()

    return render_template(
        "view_marks.html",
        marks=marks
    )



    

if __name__ == "__main__":
    app.run(debug=True, port=5001)
