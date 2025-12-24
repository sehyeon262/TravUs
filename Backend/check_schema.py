import MySQLdb

connection = MySQLdb.connect(
    host='127.0.0.1',
    user='root',
    password='1234',
    database='travus',
    port=3306,
    charset='utf8mb4'
)

cursor = connection.cursor()

# travel_spots 테이블 구조 확인
cursor.execute('DESCRIBE travel_spots')
columns = cursor.fetchall()

print("travel_spots 테이블 구조:")
print("=" * 80)
for col in columns:
    print(f"컬럼명: {col[0]}, 타입: {col[1]}, Null: {col[2]}, Key: {col[3]}")
print("=" * 80)

# reviews 테이블 구조 확인
cursor.execute('DESCRIBE reviews')
review_columns = cursor.fetchall()

print("\nreviews 테이블 구조:")
print("=" * 80)
for col in review_columns:
    print(f"컬럼명: {col[0]}, 타입: {col[1]}, Null: {col[2]}, Key: {col[3]}")
print("=" * 80)

cursor.close()
connection.close()
