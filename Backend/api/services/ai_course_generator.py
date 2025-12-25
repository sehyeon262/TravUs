"""
AI 여행 코스 생성 서비스
GMS API를 통해 OpenAI GPT를 호출하여 여행 코스를 생성합니다.
"""

import requests
import json
from django.conf import settings


class AICourseGenerator:
    """AI 여행 코스 생성기"""

    def __init__(self):
        self.gms_api_key = getattr(settings, 'GMS_API_KEY', 'S14P02EA02-e78f608f-87c7-4534-a076-6916104b3bdc')
        self.gms_api_url = 'https://gms.ssafy.io/gmsapi/api.openai.com/v1/chat/completions'
        self.model = 'gpt-4o-mini'

    def generate_course(self, region, duration, themes, travel_spots):
        """
        여행 코스 생성

        Args:
            region (str): 지역명 (예: "서울")
            duration (str): 여행 기간 ("당일치기", "1박 2일", "2박 3일")
            themes (list): 여행 테마 리스트 (예: ["역사·문화", "자연"])
            travel_spots (list): DB에서 조회한 여행지 목록

        Returns:
            dict: AI가 생성한 여행 코스
        """
        # 1. 시스템 프롬프트 생성
        system_prompt = self._generate_system_prompt(duration)

        # 2. 사용자 프롬프트 생성
        user_prompt = self._generate_user_prompt(region, themes, travel_spots)

        # 3. GMS API 호출
        try:
            response = requests.post(
                self.gms_api_url,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.gms_api_key}"
                },
                json={
                    "model": self.model,
                    "messages": [
                        {
                            "role": "system",
                            "content": system_prompt
                        },
                        {
                            "role": "user",
                            "content": user_prompt
                        }
                    ],
                    "temperature": 0.7,
                    "response_format": {"type": "json_object"}
                },
                timeout=30
            )

            if response.status_code == 200:
                ai_result = response.json()
                recommendation = json.loads(ai_result['choices'][0]['message']['content'])

                # 4. 응답 검증
                self._validate_response(recommendation, duration, travel_spots)

                return recommendation
            else:
                raise Exception(f"GMS API 호출 실패: {response.status_code} - {response.text}")

        except requests.exceptions.Timeout:
            raise Exception("AI 응답 시간 초과")
        except requests.exceptions.RequestException as e:
            raise Exception(f"AI API 호출 중 오류: {str(e)}")
        except json.JSONDecodeError as e:
            raise Exception(f"AI 응답 파싱 오류: {str(e)}")

    def _generate_system_prompt(self, duration):
        """시스템 프롬프트 생성"""

        patterns = {
            "당일치기": {
                "description": "travel → travel → restaurant → travel → travel → restaurant",
                "structure": [
                    {"order": 1, "type": "travel"},
                    {"order": 2, "type": "travel"},
                    {"order": 3, "type": "restaurant"},
                    {"order": 4, "type": "travel"},
                    {"order": 5, "type": "travel"},
                    {"order": 6, "type": "restaurant"}
                ]
            },
            "1박 2일": {
                "description": """
Day 1: travel → travel → restaurant → travel → travel → restaurant → accommodation
Day 2: travel → travel → restaurant → travel → travel → restaurant
                """,
                "structure": [
                    {"day": 1, "order": 1, "type": "travel"},
                    {"day": 1, "order": 2, "type": "travel"},
                    {"day": 1, "order": 3, "type": "restaurant"},
                    {"day": 1, "order": 4, "type": "travel"},
                    {"day": 1, "order": 5, "type": "travel"},
                    {"day": 1, "order": 6, "type": "restaurant"},
                    {"day": 1, "order": 7, "type": "accommodation"},
                    {"day": 2, "order": 1, "type": "travel"},
                    {"day": 2, "order": 2, "type": "travel"},
                    {"day": 2, "order": 3, "type": "restaurant"},
                    {"day": 2, "order": 4, "type": "travel"},
                    {"day": 2, "order": 5, "type": "travel"},
                    {"day": 2, "order": 6, "type": "restaurant"}
                ]
            },
            "2박 3일": {
                "description": """
Day 1: travel → travel → restaurant → travel → travel → restaurant → accommodation
Day 2: travel → travel → restaurant → travel → travel → restaurant → accommodation
Day 3: travel → travel → restaurant → travel → travel → restaurant
                """,
                "structure": [
                    {"day": 1, "order": 1, "type": "travel"},
                    {"day": 1, "order": 2, "type": "travel"},
                    {"day": 1, "order": 3, "type": "restaurant"},
                    {"day": 1, "order": 4, "type": "travel"},
                    {"day": 1, "order": 5, "type": "travel"},
                    {"day": 1, "order": 6, "type": "restaurant"},
                    {"day": 1, "order": 7, "type": "accommodation"},
                    {"day": 2, "order": 1, "type": "travel"},
                    {"day": 2, "order": 2, "type": "travel"},
                    {"day": 2, "order": 3, "type": "restaurant"},
                    {"day": 2, "order": 4, "type": "travel"},
                    {"day": 2, "order": 5, "type": "travel"},
                    {"day": 2, "order": 6, "type": "restaurant"},
                    {"day": 2, "order": 7, "type": "accommodation"},
                    {"day": 3, "order": 1, "type": "travel"},
                    {"day": 3, "order": 2, "type": "travel"},
                    {"day": 3, "order": 3, "type": "restaurant"},
                    {"day": 3, "order": 4, "type": "travel"},
                    {"day": 3, "order": 5, "type": "travel"},
                    {"day": 3, "order": 6, "type": "restaurant"}
                ]
            }
        }

        pattern_info = patterns.get(duration)
        if not pattern_info:
            raise ValueError(f"지원하지 않는 여행 기간: {duration}")

        return f"""당신은 여행 코스 추천 전문가입니다.

**중요 규칙:**
1. 절대로 새로운 장소를 만들지 마세요
2. 반드시 제공된 여행지 목록의 ID만 사용하세요
3. 아래 순서 패턴을 정확히 따라야 합니다
4. 장소 타입을 정확히 구분하여 선택하세요
   - content_type_id가 39인 것은 음식점(restaurant)입니다
   - content_type_id가 32인 것은 숙박(accommodation)입니다
   - 그 외는 모두 여행지(travel)입니다

**여행 순서 패턴 ({duration}):**
{pattern_info['description']}

**응답 형식:**
- 반드시 JSON 형식으로만 응답하세요
- 각 항목은 day(해당되는 경우), order, type, id만 포함
- id는 반드시 제공된 후보 목록에 있는 실제 ID여야 합니다
- type은 "travel", "restaurant", "accommodation" 중 하나입니다

**🎯 동선 최적화 (매우 중요!):**
- **같은 날짜 내에서는 반드시 가까운 장소들끼리 선택하세요**
- 위도(latitude)와 경도(longitude)를 기준으로 거리 계산하세요
- 각 여행지 간 이동 거리가 5km 이내가 되도록 선택하세요
- 점심 식사는 오전 여행지 근처(1-2km 이내), 저녁 식사는 오후 여행지 근처로 선택하세요
- 숙박 시설은 마지막 여행지나 식당에서 가까운 곳(3km 이내)으로 선택하세요
- 다음 날 첫 여행지는 숙박 시설에서 가까운 곳부터 시작하세요

**JSON 구조 예시:**
{{
  "title": "생성된 코스 제목",
  "description": "코스에 대한 간단한 설명",
  "itinerary": [
    {{"day": 1, "order": 1, "type": "travel", "id": 123}},
    {{"day": 1, "order": 2, "type": "travel", "id": 456}},
    {{"day": 1, "order": 3, "type": "restaurant", "id": 789}},
    {{"day": 1, "order": 7, "type": "accommodation", "id": 321}},
    ...
  ]
}}

사용자가 선택한 테마와 각 장소의 특성을 고려하되, **동선 최적화를 최우선**으로 하세요.
"""

    def _generate_user_prompt(self, region, themes, travel_spots):
        """사용자 프롬프트 생성"""

        # 여행지, 음식점, 숙박 분리
        restaurants = [spot for spot in travel_spots if spot.get('content_type_id') == '39']
        accommodations = [spot for spot in travel_spots if spot.get('content_type_id') == '32']
        attractions = [spot for spot in travel_spots if spot.get('content_type_id') not in ['39', '32']]

        # 간결한 정보만 포함 (ID, 이름, 위치, 타입)
        def simplify_spot(spot):
            return {
                'id': spot.get('id'),
                'name': spot.get('name'),
                'latitude': float(spot.get('latitude')) if spot.get('latitude') else None,
                'longitude': float(spot.get('longitude')) if spot.get('longitude') else None,
                'content_type_id': spot.get('content_type_id'),
                'description': spot.get('description', '')[:80]
            }

        simplified_attractions = [simplify_spot(spot) for spot in attractions[:50]]
        simplified_restaurants = [simplify_spot(spot) for spot in restaurants[:30]]
        simplified_accommodations = [simplify_spot(spot) for spot in accommodations[:20]]

        themes_str = ", ".join(themes) if themes else "일반 관광"

        return f"""
지역: {region}
사용자가 선택한 테마: {themes_str}

**선택 가능한 여행지 목록 ({len(simplified_attractions)}개):**
{json.dumps(simplified_attractions, ensure_ascii=False, indent=2)}

**선택 가능한 음식점 목록 ({len(simplified_restaurants)}개):**
{json.dumps(simplified_restaurants, ensure_ascii=False, indent=2)}

**선택 가능한 숙박 목록 ({len(simplified_accommodations)}개):**
{json.dumps(simplified_accommodations, ensure_ascii=False, indent=2)}

**중요한 규칙:**
1. **반드시** 위 목록에 있는 장소들의 id만 사용해주세요. 목록에 없는 id를 사용하면 안 됩니다.
2. 각 장소의 id 값을 정확히 복사하여 사용하세요.
3. 순서 패턴을 정확히 따라주세요.
4. 위도(latitude)/경도(longitude)를 고려하여 가까운 장소들끼리 선택해주세요.
5. 같은 지역({region}) 내의 장소들만 선택해주세요.
"""

    def _validate_response(self, response, duration, travel_spots):
        """AI 응답 검증"""

        if 'itinerary' not in response:
            raise ValueError("AI 응답에 'itinerary' 필드가 없습니다")

        itinerary = response['itinerary']

        if not isinstance(itinerary, list):
            raise ValueError("itinerary는 리스트여야 합니다")

        # 여행지 ID 목록 추출
        spot_ids = {spot['id'] for spot in travel_spots}

        # 각 항목 검증 (필수 필드와 type만 확인, ID는 views.py에서 필터링)
        for item in itinerary:
            # 필수 필드 확인
            if 'id' not in item or 'type' not in item or 'order' not in item:
                raise ValueError(f"필수 필드 누락: {item}")

            # ID 존재 여부는 경고만 출력 (에러 발생하지 않음)
            if item['id'] not in spot_ids:
                print(f"[WARNING] AI가 존재하지 않는 ID를 반환했습니다: {item['id']} (views.py에서 필터링됨)")

            # type 값 확인
            if item['type'] not in ['travel', 'restaurant', 'accommodation']:
                raise ValueError(f"잘못된 type 값: {item['type']}")

        # 기간별 최소 개수 확인은 제거 (필터링 후 개수가 줄어들 수 있음)
        # views.py에서 필터링 후 최종 검증

        return True


# 싱글톤 인스턴스
ai_course_generator = AICourseGenerator()
