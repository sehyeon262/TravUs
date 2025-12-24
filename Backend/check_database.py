import MySQLdb

# 데이터베이스 연결
connection = MySQLdb.connect(
    host='127.0.0.1',
    user='root',
    password='1234',
    database='travus',
    port=3306
)

cursor = connection.cursor()

# 테이블 목록 확인
cursor.execute("SHOW TABLES")
tables = cursor.fetchall()

print("travus 데이터베이스의 테이블 목록:")
print("=" * 50)
for table in tables:
    table_name = table[0]
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    count = cursor.fetchone()[0]
    print(f"- {table_name}: {count} rows")

cursor.close()
connection.close()

print("=" * 50)
print("Database import success!")
