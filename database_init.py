import sqlite3

conn = sqlite3.connect("database.db")
c = conn.cursor()

# =========================
# users 테이블
# =========================

c.execute("""
CREATE TABLE IF NOT EXISTS users (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    username TEXT UNIQUE,

    password TEXT,

    role TEXT

)
""")

# =========================
# 교내 대회
# =========================

c.execute("""
CREATE TABLE IF NOT EXISTS internal_contest (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    title TEXT,

    description TEXT,

    date TEXT

)
""")

# =========================
# 교외 대회
# =========================

c.execute("""
CREATE TABLE IF NOT EXISTS external_contest (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    title TEXT,

    description TEXT,

    date TEXT

)
""")

# =========================
# 장학금
# =========================

c.execute("""
CREATE TABLE IF NOT EXISTS scholarships (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    title TEXT,

    target TEXT,

    deadline TEXT

)
""")

# =========================
# 계획서
# =========================

c.execute("""
CREATE TABLE IF NOT EXISTS proposals (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    title TEXT,

    author TEXT,

    filename TEXT

)
""")

# =========================
# 보고서
# =========================

c.execute("""
CREATE TABLE IF NOT EXISTS reports (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    title TEXT,

    author TEXT,

    filename TEXT

)
""")

conn.commit()
conn.close()

print("DB 생성 완료")