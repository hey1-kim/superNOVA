import sqlite3

conn = sqlite3.connect("database.db")
c = conn.cursor()

# 기존 admin 계정 삭제
c.execute("""
DELETE FROM users
WHERE username='admin'
""")

# 새 관리자 계정 생성
c.execute("""
INSERT INTO users (username, password, role)
VALUES (?, ?, ?)
""", ("2206김혜원", "lisa0326!", "admin"))

conn.commit()
conn.close()

print("관리자 계정 생성 완료")