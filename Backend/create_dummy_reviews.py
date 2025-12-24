import MySQLdb
from datetime import datetime, timedelta
import random

# 데이터베이스 연결 (UTF-8 인코딩)
connection = MySQLdb.connect(
    host='127.0.0.1',
    user='root',
    password='1234',
    database='travus',
    port=3306,
    charset='utf8mb4'
)

cursor = connection.cursor()

# 첫 10개 여행지 조회
cursor.execute('SELECT id, name, content_type_id, cat3 FROM travel_spots LIMIT 10')
travel_spots = cursor.fetchall()

print("처음 10개 여행지:")
print("=" * 80)
for spot in travel_spots:
    print(f"ID: {spot[0]}, 이름: {spot[1]}, 타입: {spot[2]}, 카테고리: {spot[3]}")
print("=" * 80)

# 사용자 ID 조회 (리뷰 작성자로 사용)
cursor.execute('SELECT id FROM users LIMIT 20')
user_ids = [user[0] for user in cursor.fetchall()]

print(f"\n사용 가능한 사용자 수: {len(user_ids)}")

# 각 여행지별 다양한 리뷰 템플릿
review_templates = {
    '관광지': [
        "정말 멋진 곳이에요! 사진으로만 보다가 직접 가보니 훨씬 더 아름답더라구요. 특히 {}이/가 인상 깊었어요. 주변 경관도 너무 좋고, 산책하기 딱 좋았습니다. 다만 주말에는 사람이 많아서 평일에 방문하시는 걸 추천드려요.",
        "가족들과 함께 다녀왔는데 모두 만족했어요. 볼거리가 많아서 시간 가는 줄 몰랐습니다. {}도 정말 인상적이었고, 주변에 맛집들도 많아서 좋았어요. 날씨 좋은 날 방문하시면 더욱 좋을 것 같아요!",
        "기대 이상이었어요! 특히 {}이/가 너무 마음에 들었습니다. 사진 찍기 좋은 포토존도 많고, 주변 환경도 깨끗하게 잘 정돈되어 있어요. 주차 공간도 넉넉해서 편하게 다녀왔습니다.",
        "여러 번 방문했지만 올 때마다 새로운 느낌이에요. {}의 아름다움은 계절마다 다르더라구요. 이번에는 날씨가 특히 좋아서 더 즐거웠습니다. 다음에 또 방문하고 싶어요!",
        "친구들과 추억 만들기 좋은 곳이에요. {}을/를 배경으로 사진도 많이 찍었어요. 입장료 대비 만족도가 높았고, 직원분들도 친절하셨습니다. 주변에 카페도 있어서 쉬어가기 좋았어요."
    ],
    '음식점': [
        "음식이 정말 맛있어요! 특히 {}이/가 일품이었습니다. 양도 푸짐하고 가격도 합리적이에요. 서비스도 친절하셔서 기분 좋게 식사했습니다. 재방문 의사 100%입니다!",
        "맛집 인정! {}을/를 주문했는데 정말 최고였어요. 신선한 재료 사용하시는 게 느껴지고, 음식이 깔끔하게 나왔어요. 웨이팅이 있을 수 있으니 시간 여유 갖고 가시는 걸 추천드려요.",
        "가족 외식으로 다녀왔는데 모두가 만족했어요. {}의 맛이 일품이고, 반찬도 정갈하게 잘 나왔습니다. 주차 공간도 있어서 편했어요. 다음에 또 방문할게요!",
        "SNS에서 보고 찾아갔는데 기대 이상이었어요! {}이/가 정말 맛있고 사장님도 친절하세요. 분위기도 좋아서 데이트 코스로도 추천드립니다. 사진도 예쁘게 나와요!",
        "단골 되었어요! {}을/를 먹으러 자주 찾게 되는 곳입니다. 맛도 맛이지만 서비스가 정말 좋아요. 음식도 빨리 나오고, 매번 만족스러운 식사를 하고 갑니다."
    ],
    '카페': [
        "분위기 너무 좋은 카페예요! {}을/를 주문했는데 맛도 훌륭했습니다. 인테리어가 감성적이어서 사진 찍기 좋고, 조용해서 작업하기에도 좋았어요. 다음에 친구들과 또 올게요!",
        "커피 맛집 찾았어요! {}의 맛이 정말 일품이고, 디저트도 맛있어요. 공간이 넓어서 여유롭게 시간 보내기 좋았습니다. 주차도 가능해서 편리했어요.",
        "힐링하기 좋은 곳이에요. {}을/를 마시며 창밖 풍경 구경하는 재미가 있어요. 직원분들도 친절하시고, 음료 퀄리티가 높아요. 가격대비 만족도 높습니다!",
        "데이트 장소로 완벽해요! {}도 맛있고 분위기도 로맨틱해요. 좌석 간격이 넓어서 프라이빗한 대화 나누기 좋았어요. 베이커리류도 다양해서 선택의 폭이 넓어요.",
        "작업하기 좋은 카페예요. {}을/를 시켜놓고 몇 시간 있었는데 와이파이도 빠르고 콘센트도 많아요. 조용한 분위기에서 집중하기 딱 좋았습니다."
    ],
    'default': [
        "기대했던 것보다 훨씬 좋았어요! 시설도 깨끗하고 관리가 잘 되어 있어요. 다음에 가족들과 함께 다시 방문하고 싶습니다. 주변 환경도 좋고 접근성도 괜찮아요.",
        "정말 만족스러운 방문이었어요! 직원분들도 친절하시고 전반적으로 관리가 잘 되어 있더라구요. 사진도 많이 찍었고 좋은 추억 만들었습니다. 강력 추천해요!",
        "여러 곳 다녀봤지만 여기가 가장 마음에 들어요. 시설이 현대적이고 깨끗해서 좋았습니다. 접근성도 좋고 주변에 볼거리도 많아요. 재방문 의사 있습니다!",
        "생각보다 훨씬 좋았어요! 분위기도 좋고 시설도 잘 갖춰져 있어요. 친구들한테 추천했더니 다들 만족했다고 하더라구요. 다음에 또 올게요!",
        "완전 만족했어요! 기대 이상의 경험이었고, 주변 경관도 아름다워요. 사진 찍기도 좋고 산책하기에도 좋은 곳입니다. 날씨 좋은 날 방문 추천드려요!"
    ]
}

# 각 여행지의 특징 키워드
feature_keywords = [
    "전망", "경치", "야경", "정원", "건축물", "역사", "문화", "체험",
    "시그니처 메뉴", "특선 요리", "시즌 메뉴", "인기 메뉴",
    "아메리카노", "라떼", "디저트", "베이커리",
    "전시", "공연", "이벤트", "프로그램"
]

# 평점 분포 (대부분 높은 평점)
rating_distribution = [5] * 50 + [4] * 30 + [3] * 15 + [2] * 4 + [1] * 1

# 각 여행지마다 3~7개의 리뷰 생성
total_reviews = 0
for spot in travel_spots:
    spot_id = spot[0]
    spot_name = spot[1]
    content_type = spot[2]  # content_type_id
    spot_category = spot[3] if spot[3] else 'default'  # cat3

    # 카테고리에 맞는 템플릿 선택
    if '음식' in spot_category or '식당' in spot_category or '레스토랑' in spot_category:
        templates = review_templates['음식점']
    elif '카페' in spot_category or '커피' in spot_category:
        templates = review_templates['카페']
    elif '관광' in spot_category or '명소' in spot_category or '공원' in spot_category:
        templates = review_templates['관광지']
    else:
        templates = review_templates['default']

    # 이 여행지에 생성할 리뷰 개수
    num_reviews = random.randint(3, 7)

    for i in range(num_reviews):
        # 랜덤 사용자 선택
        user_id = random.choice(user_ids)

        # 랜덤 평점 선택
        rating = random.choice(rating_distribution)

        # 리뷰 템플릿 선택 및 키워드 삽입
        template = random.choice(templates)
        keyword = random.choice(feature_keywords)
        content = template.format(keyword)

        # 랜덤 날짜 (최근 6개월 이내)
        days_ago = random.randint(1, 180)
        created_at = datetime.now() - timedelta(days=days_ago)

        # 리뷰 삽입
        insert_query = """
        INSERT INTO reviews (travel_spot_id, user_id, content, rating, images, like_count, created_at, updated_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """

        cursor.execute(insert_query, (
            spot_id,
            user_id,
            content,
            rating,
            '[]',  # 빈 JSON 배열
            0,  # like_count
            created_at,
            created_at
        ))

        total_reviews += 1

    print(f"[OK] {spot_name}: {num_reviews}개 리뷰 생성 완료")

# 커밋
connection.commit()

print("\n" + "=" * 80)
print(f"총 {total_reviews}개의 더미 리뷰가 생성되었습니다!")
print("=" * 80)

cursor.close()
connection.close()
