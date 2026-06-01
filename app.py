# app.py

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    session,
    send_from_directory
)

import sqlite3
import os
import re

from werkzeug.utils import secure_filename

# =========================
# Flask 설정
# =========================

app = Flask(__name__)

app.secret_key = "supernova_secret_key"

DATABASE = "database.db"

# =========================
# 업로드 폴더 생성
# =========================

os.makedirs("uploads/proposals", exist_ok=True)
os.makedirs("uploads/reports", exist_ok=True)

# =========================
# DB 연결 함수
# =========================

def get_db():

    conn = sqlite3.connect(DATABASE)

    conn.row_factory = sqlite3.Row

    return conn

# =========================
# 메인 페이지
# =========================

@app.route("/")
def index():

    return render_template("index.html")

# =========================
# 회원가입
# =========================

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("database.db")
        c = conn.cursor()

        # 중복 확인
        c.execute("""
            SELECT * FROM users
            WHERE username=?
        """, (username,))

        existing_user = c.fetchone()

        if existing_user:

            conn.close()

            return """
            <script>
                alert('이미 존재하는 아이디입니다.');
                history.back();
            </script>
            """

        c.execute("""
            INSERT INTO users (username, password, role)
            VALUES (?, ?, ?)
        """, (username, password, "user"))

        conn.commit()
        conn.close()

        return redirect("/login")

    return render_template("register.html")
# =========================
# 로그인
# =========================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("database.db")
        conn.row_factory = sqlite3.Row

        c = conn.cursor()

        c.execute("""
            SELECT * FROM users
            WHERE username=? AND password=?
        """, (username, password))

        user = c.fetchone()

        conn.close()

        if user:

            session["user_id"] = user["id"]
            session["username"] = user["username"]
            session["role"] = user["role"]

            return redirect("/")

    return render_template("login.html")

# =========================
# 로그아웃
# =========================

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/")

# =========================
# 관리자 페이지
# =========================

# =========================
# 관리자 페이지
# =========================

@app.route("/admin")
def admin():

    if session.get("role") != "admin":
        return redirect("/")

    conn = get_db()
    c = conn.cursor()

    c.execute("""
        SELECT * FROM users
        ORDER BY id DESC
    """)
    users = c.fetchall()

    c.execute("""
        SELECT * FROM proposals
        ORDER BY id DESC
    """)
    proposals = c.fetchall()

    c.execute("""
        SELECT * FROM reports
        ORDER BY id DESC
    """)
    reports = c.fetchall()

    c.execute("""
        SELECT * FROM internal_contest
        ORDER BY id DESC
    """)
    internal_contests = c.fetchall()

    c.execute("""
        SELECT * FROM external_contest
        ORDER BY id DESC
    """)
    external_contests = c.fetchall()

    c.execute("""
        SELECT * FROM scholarships
        ORDER BY id DESC
    """)
    scholarships = c.fetchall()

    conn.close()

    return render_template(
        "admin.html",
        users=users,
        proposals=proposals,
        reports=reports,
        internal_contests=internal_contests,
        external_contests=external_contests,
        scholarships=scholarships
    )

# =========================
# 회원 삭제
# =========================

@app.route("/delete_user/<int:user_id>")
def delete_user(user_id):

    # 관리자만 가능

    if session.get("role") != "admin":

        return redirect("/")

    conn = get_db()
    c = conn.cursor()

    # admin 계정 삭제 방지

    c.execute("""
        SELECT * FROM users
        WHERE id=?
    """, (user_id,))

    user = c.fetchone()

    if user and user["role"] == "admin":

        conn.close()

        return """
        <script>
            alert('관리자 계정은 삭제할 수 없습니다.');
            history.back();
        </script>
        """

    # 삭제 실행

    c.execute("""
        DELETE FROM users
        WHERE id=?
    """, (user_id,))

    conn.commit()
    conn.close()

    return redirect("/admin")

# =========================
# 교내 대회 페이지
# =========================

@app.route("/contest/internal")
def internal_contest():

    conn = get_db()
    c = conn.cursor()

    c.execute("""

        SELECT * FROM internal_contest
        ORDER BY id DESC

    """)

    contests = c.fetchall()

    conn.close()

    return render_template(

        "internal_contest.html",

        contests=contests

    )

# =========================
# 교외 대회 페이지
# =========================

@app.route("/contest/external")
def external_contest():

    conn = get_db()
    c = conn.cursor()

    c.execute("""

        SELECT * FROM external_contest
        ORDER BY id DESC

    """)

    contests = c.fetchall()

    conn.close()

    return render_template(

        "external_contest.html",

        contests=contests

    )

# =========================
# 장학금 페이지
# =========================

@app.route("/scholarship")
def scholarship():

    conn = get_db()
    c = conn.cursor()

    c.execute("""

        SELECT * FROM scholarships
        ORDER BY id DESC

    """)

    scholarships = c.fetchall()

    conn.close()

    return render_template(

        "scholarship.html",

        scholarships=scholarships

    )

# =========================
# 계획서 페이지
# =========================

@app.route("/proposal")
def proposal():

    conn = get_db()
    c = conn.cursor()

    c.execute("""

        SELECT * FROM proposals
        ORDER BY id DESC

    """)

    proposals = c.fetchall()

    conn.close()

    return render_template(

        "proposal.html",

        proposals=proposals

    )

# =========================
# 보고서 페이지
# =========================

@app.route("/report")
def report():

    conn = get_db()
    c = conn.cursor()

    c.execute("""

        SELECT * FROM reports
        ORDER BY id DESC

    """)

    reports = c.fetchall()

    conn.close()

    return render_template(

        "report.html",

        reports=reports

    )

# =========================
# 계획서 업로드
# =========================

@app.route("/upload_proposal", methods=["GET", "POST"])
def upload_proposal():

    if request.method == "POST":

        title = request.form["title"]
        author = request.form["author"]

        file = request.files["file"]

        filename = secure_filename(file.filename)

        filepath = os.path.join(

            "uploads/proposals",
            filename

        )

        file.save(filepath)

        conn = get_db()
        c = conn.cursor()

        c.execute("""

            INSERT INTO proposals
            (title, author, filename)

            VALUES (?, ?, ?)

        """, (

            title,
            author,
            filename

        ))

        conn.commit()
        conn.close()

        return redirect("/proposal")

    return render_template("upload_proposal.html")

# =========================
# 보고서 업로드
# =========================

@app.route("/upload_report", methods=["GET", "POST"])
def upload_report():

    if request.method == "POST":

        title = request.form["title"]
        author = request.form["author"]

        file = request.files["file"]

        filename = secure_filename(file.filename)

        filepath = os.path.join(

            "uploads/reports",
            filename

        )

        file.save(filepath)

        conn = get_db()
        c = conn.cursor()

        c.execute("""

            INSERT INTO reports
            (title, author, filename)

            VALUES (?, ?, ?)

        """, (

            title,
            author,
            filename

        ))

        conn.commit()
        conn.close()

        return redirect("/report")

    return render_template("upload_report.html")

# =========================
# 교내 대회 생성
# =========================

@app.route("/create_internal_contest", methods=["POST"])
def create_internal_contest():

    if session.get("role") != "admin":

        return redirect("/")

    title = request.form["title"]
    description = request.form["description"]
    date = request.form["date"]

    conn = get_db()
    c = conn.cursor()

    c.execute("""

        INSERT INTO internal_contest
        (title, description, date)

        VALUES (?, ?, ?)

    """, (

        title,
        description,
        date

    ))

    conn.commit()
    conn.close()

    return redirect("/admin")

# =========================
# 교외 대회 생성
# =========================

@app.route("/create_external_contest", methods=["POST"])
def create_external_contest():

    if session.get("role") != "admin":

        return redirect("/")

    title = request.form["title"]
    description = request.form["description"]
    date = request.form["date"]

    conn = get_db()
    c = conn.cursor()

    c.execute("""

        INSERT INTO external_contest
        (title, description, date)

        VALUES (?, ?, ?)

    """, (

        title,
        description,
        date

    ))

    conn.commit()
    conn.close()

    return redirect("/admin")

# =========================
# 장학금 생성
# =========================

@app.route("/create_scholarship", methods=["POST"])
def create_scholarship():

    if session.get("role") != "admin":

        return redirect("/")

    title = request.form["title"]
    target = request.form["target"]
    deadline = request.form["deadline"]

    conn = get_db()
    c = conn.cursor()

    c.execute("""

        INSERT INTO scholarships
        (title, target, deadline)

        VALUES (?, ?, ?)

    """, (

        title,
        target,
        deadline

    ))

    conn.commit()
    conn.close()

    return redirect("/admin")

# =========================
# 계획서 다운로드
# =========================

@app.route("/download/proposal/<filename>")
def download_proposal(filename):

    return send_from_directory(

        "uploads/proposals",
        filename,
        as_attachment=True

    )

# =========================
# 보고서 다운로드
# =========================

@app.route("/download/report/<filename>")
def download_report(filename):

    return send_from_directory(

        "uploads/reports",
        filename,
        as_attachment=True

    )
# =========================
# 교내대회 삭제
# =========================

@app.route("/delete_internal_contest/<int:contest_id>")
def delete_internal_contest(contest_id):

    if session.get("role") != "admin":
        return redirect("/")

    conn = get_db()
    c = conn.cursor()

    c.execute("""
        DELETE FROM internal_contest
        WHERE id=?
    """, (contest_id,))

    conn.commit()
    conn.close()

    return redirect("/admin")


# =========================
# 교외대회 삭제
# =========================

@app.route("/delete_external_contest/<int:contest_id>")
def delete_external_contest(contest_id):

    if session.get("role") != "admin":
        return redirect("/")

    conn = get_db()
    c = conn.cursor()

    c.execute("""
        DELETE FROM external_contest
        WHERE id=?
    """, (contest_id,))

    conn.commit()
    conn.close()

    return redirect("/admin")


# =========================
# 장학금 삭제
# =========================

@app.route("/delete_scholarship/<int:scholarship_id>")
def delete_scholarship(scholarship_id):

    if session.get("role") != "admin":
        return redirect("/")

    conn = get_db()
    c = conn.cursor()

    c.execute("""
        DELETE FROM scholarships
        WHERE id=?
    """, (scholarship_id,))

    conn.commit()
    conn.close()

    return redirect("/admin")
# =========================
# 실행
# =========================

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)