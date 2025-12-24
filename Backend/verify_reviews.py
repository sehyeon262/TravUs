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

# 전체 리뷰 개수 확인
cursor.execute('SELECT COUNT(*) FROM reviews')
total_count = cursor.fetchone()[0]
print(f"전체 리뷰 개수: {total_count}개")
print("=" * 80)

# 여행지별 리뷰 개수 확인
cursor.execute('''
    SELECT ts.id, ts.name, COUNT(r.id) as review_count, AVG(r.rating) as avg_rating
    FROM travel_spots ts
    LEFT JOIN reviews r ON ts.id = r.travel_spot_id
    WHERE ts.id <= 10
    GROUP BY ts.id, ts.name
    ORDER BY ts.id
''')

results = cursor.fetchall()

print("\n여행지별 리뷰 현황 (처음 10개):")
print("=" * 80)
for row in results:
    spot_id, spot_name, review_count, avg_rating = row
    avg_rating_str = f"{avg_rating:.2f}" if avg_rating else "N/A"
    print(f"ID {spot_id}: {spot_name}")
    print(f"  - 리뷰 수: {review_count}개")
    print(f"  - 평균 평점: {avg_rating_str}")
    print()

# 최근 리뷰 3개 샘플 확인
print("=" * 80)
print("최근 리뷰 샘플 (3개):")
print("=" * 80)

cursor.execute('''
    SELECT r.id, ts.name, r.rating, r.content, r.created_at
    FROM reviews r
    JOIN travel_spots ts ON r.travel_spot_id = ts.id
    ORDER BY r.created_at DESC
    LIMIT 3
''')

samples = cursor.fetchall()
for review in samples:
    review_id, spot_name, rating, content, created_at = review
    print(f"\n리뷰 ID: {review_id}")
    print(f"여행지: {spot_name}")
    print(f"평점: {rating}점")
    print(f"작성일: {created_at}")
    print(f"내용: {content}")
    print("-" * 80)

cursor.close()
connection.close()
