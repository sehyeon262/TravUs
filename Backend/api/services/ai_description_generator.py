"""
AI 여행지 상세 설명 생성 서비스
GMS API를 통해 OpenAI GPT를 호출하여 여행지 상세 설명을 생성합니다.
"""

import requests
from django.conf import settings


class AIDescriptionGenerator:
    """AI 여행지 상세 설명 생성기"""

    def __init__(self):
        self.gms_api_key = getattr(settings, 'GMS_API_KEY', 'S14P02EA02-e78f608f-87c7-4534-a076-6916104b3bdc')
        self.gms_api_url = 'https://gms.ssafy.io/gmsapi/api.openai.com/v1/chat/completions'
        self.model = 'gpt-4o-mini'

    def generate_description(self, spot_name, address, category=None):
        """
        여행지 상세 설명 생성

        Args:
            spot_name (str): 여행지 이름
            address (str): 여행지 주소
            category (str, optional): 여행지 카테고리

        Returns:
            str: AI가 생성한 4줄 정도의 상세 설명
        """
        # 시스템 프롬프트
        system_prompt = """당신은 전문적인 여행지 가이드입니다.
사용자에게 여행지에 대한 매력적이고 정확한 정보를 제공하는 것이 목표입니다.
여행지의 특징, 매력, 역사적/문화적 의미를 간결하고 흥미롭게 설명해주세요.
반드시 4줄 이내로 작성하되, 각 문장은 핵심적인 정보를 담아야 합니다."""

        # 사용자 프롬프트
        category_info = f", 카테고리: {category}" if category else ""
        user_prompt = f"""다음 여행지에 대한 상세 설명을 4줄 이내로 작성해주세요:

여행지 이름: {spot_name}
주소: {address}{category_info}

요구사항:
1. 4줄 이내로 간결하게 작성 (각 줄은 한 문장)
2. 여행지의 주요 특징과 매력을 포함
3. 방문객이 알아야 할 핵심 정보 포함
4. 친근하고 흥미로운 톤으로 작성
5. 불필요한 수식어는 제외하고 핵심만 전달

응답은 오직 설명 텍스트만 반환하세요. 다른 말은 하지 마세요."""

        # GMS API 호출
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
                    "max_tokens": 300
                },
                timeout=30
            )

            if response.status_code == 200:
                ai_result = response.json()
                description = ai_result['choices'][0]['message']['content'].strip()

                # 혹시 따옴표나 불필요한 문자가 있으면 제거
                description = description.strip('"').strip("'")

                return description
            else:
                raise Exception(f"GMS API 호출 실패: {response.status_code} - {response.text}")

        except requests.exceptions.Timeout:
            raise Exception("AI 응답 시간 초과 (30초)")
        except requests.exceptions.RequestException as e:
            raise Exception(f"AI API 호출 중 오류: {str(e)}")
        except Exception as e:
            raise Exception(f"AI 설명 생성 중 오류: {str(e)}")
