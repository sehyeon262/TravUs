import MySQLdb

# 데이터베이스 연결
connection = MySQLdb.connect(
    host='127.0.0.1',
    user='root',
    password='1234',
    database='travus',
    port=3306,
    charset='utf8mb4'
)

cursor = connection.cursor()

print("여행지별 리뷰 개수를 업데이트합니다...")
print("=" * 80)

# 각 여행지의 실제 리뷰 개수를 계산하여 업데이트
update_query = """
UPDATE travel_spots ts
SET review_count = (
    SELECT COUNT(*)
    FROM reviews r
    WHERE r.travel_spot_id = ts.id
)
"""

cursor.execute(update_query)
affected_rows = cursor.rowcount

print(f"[OK] {affected_rows}개 여행지의 리뷰 개수가 업데이트되었습니다.")

# 업데이트된 결과 확인 (처음 10개)
cursor.execute("""
    SELECT id, name, review_count
    FROM travel_spots
    WHERE review_count > 0
    ORDER BY id
    LIMIT 10
""")

results = cursor.fetchall()

print("\n업데이트된 여행지 (처음 10개):")
print("=" * 80)
for row in results:
    spot_id, spot_name, review_count = row
    print(f"ID {spot_id}: {spot_name} - 리뷰 {review_count}개")

# 커밋
connection.commit()

print("\n" + "=" * 80)
print("리뷰 개수 업데이트 완료!")

cursor.close()
connection.close()
