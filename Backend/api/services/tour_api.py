import requests
import logging
from django.conf import settings
from typing import Dict, List, Optional
from urllib.parse import quote

# 로깅 설정 (print 대신 사용 권장)
logger = logging.getLogger(__name__)


class TourAPIService:
    """한국관광공사 무장애 여행 API 서비스 (TourAPI 4.0 기준)"""

    def __init__(self):
        self.base_url = settings.TOUR_API_BASE_URL
        self.api_key = settings.TOUR_API_KEY
        self.mobile_os = settings.TOUR_API_MOBILE_OS
        self.mobile_app = settings.TOUR_API_MOBILE_APP

        # Service1과 Service2 fallback을 위한 URL 리스트
        self.fallback_urls = [
            'http://apis.data.go.kr/B551011/KorWithService1',
            'http://apis.data.go.kr/B551011/KorWithService2'
        ]

    def _make_request(self, endpoint: str, params: Dict) -> Optional[Dict]:
        """
        API 요청 공통 메서드

        공공데이터 포털 API의 특성상 serviceKey를 URL에 직접 포함시키고,
        나머지 파라미터는 requests의 params로 전달하여 이중 인코딩 방지
        """
        # ServiceKey 처리: 이미 인코딩되어 있는지 확인 후 처리
        if '%' in self.api_key:
            # 이미 인코딩된 키라면 그대로 사용
            service_key = self.api_key
        else:
            # 디코딩된 키라면 인코딩 수행
            service_key = quote(self.api_key, safe='')

        # URL에 serviceKey 직접 포함 (이중 인코딩 방지)
        url = f"{self.base_url}/{endpoint}?serviceKey={service_key}"

        # 기본 파라미터 설정 (공통)
        base_params = {
            'MobileOS': self.mobile_os,
            'MobileApp': self.mobile_app,
            '_type': 'json',
        }

        # ⚠️ 중요: pagination 파라미터는 목록 API에서만 사용
        # detailCommon, detailIntro, detailInfo 등에서는 numOfRows/pageNo가 오류 유발
        if endpoint.endswith('List2') or endpoint.endswith('Keyword2'):
            base_params.update({
                'numOfRows': 20,
                'pageNo': 1
            })

        # 파라미터 병합 (사용자 파라미터가 우선)
        request_params = {**base_params, **params}

        try:
            logger.info(f"=== Making TourAPI request ===")
            logger.info(f"Endpoint: {endpoint}")
            logger.info(f"Parameters: {request_params}")

            response = requests.get(url, params=request_params, timeout=10)

            # 인증키가 포함된 전체 요청 URL은 기록하지 않는다.
            logger.info("TourAPI request completed: endpoint=%s", endpoint)
            logger.info(f"Response Status: {response.status_code}")

            # 404는 별도 처리 (raise하지 않고 None 반환)
            if response.status_code == 404:
                logger.warning(f"TourAPI returned 404 - Resource not found")
                return {'status_code': 404, 'error': 'NOT_FOUND'}

            response.raise_for_status()
            json_response = response.json()

            # 응답 구조 간단히 로깅
            if 'response' in json_response:
                body = json_response.get('response', {}).get('body', {})
                total_count = body.get('totalCount', 'N/A')
                logger.info(f"Response totalCount: {total_count}")

            return json_response

        except requests.exceptions.RequestException as e:
            logger.error("TourAPI request failed: endpoint=%s error_type=%s", endpoint, type(e).__name__)
            return None
        except ValueError as e:  # JSON Decode Error
            logger.error(f"TourAPI JSON Decode Failed: {e}")
            return None

    def _normalize_response(self, response: Optional[Dict]) -> List[Dict]:
        """
        응답 데이터를 항상 List 형태로 반환하도록 정규화하는 헬퍼 메서드.
        TourAPI는 결과가 1개면 Dict, 2개 이상이면 List로 반환하는데,
        이를 항상 List로 통일하여 프론트엔드의 Array.isArray 체크를 줄임.
        """
        if not response:
            return []

        try:
            body = response.get('response', {}).get('body', {})
            items = body.get('items', {})

            # 데이터가 아예 없는 경우 (items가 빈 문자열로 올 때가 있음)
            if not items:
                return []

            item_list = items.get('item', [])

            # 결과가 1개일 경우 dict로 오고, 여러개일 경우 list로 옴 -> 무조건 list로 변환
            if isinstance(item_list, dict):
                return [item_list]
            return item_list if isinstance(item_list, list) else []

        except (AttributeError, TypeError):
            return []

    def get_area_based_list(
        self,
        area_code: Optional[str] = None,
        sigungu_code: Optional[str] = None,
        content_type_id: Optional[str] = None,
        page_no: int = 1,
        num_of_rows: int = 20
    ) -> Optional[Dict]:
        """
        지역 기반 관광정보 조회

        원본 응답이 필요한 경우(totalCount 등)가 있으므로 정규화 선택적 적용
        """
        params = {
            'pageNo': page_no,
            'numOfRows': num_of_rows,
            'arrange': 'A',  # A=제목순, C=수정일순, D=생성일순
        }

        if area_code:
            params['areaCode'] = area_code
        if sigungu_code:
            params['sigunguCode'] = sigungu_code
        if content_type_id:
            params['contentTypeId'] = content_type_id

        return self._make_request('areaBasedList2', params)

    def get_detail_common(self, content_id: str, content_type_id: Optional[str] = None) -> Optional[Dict]:
        """
        공통정보 상세 조회 (Service1/Service2 자동 fallback 지원)

        기본 정보와 contenttypeid를 가져오는 핵심 메서드
        404 발생 시 다른 서비스 버전으로 재시도

        Args:
            content_id: 콘텐츠 ID (필수)
            content_type_id: 콘텐츠 타입 ID (권장)
                - 12: 관광지
                - 14: 문화시설
                - 15: 축제공연행사
                - 25: 여행코스
                - 28: 레포츠
                - 32: 숙박
                - 38: 쇼핑
                - 39: 음식점
        """
        logger.info(f"=== get_detail_common called with content_id: {content_id}, content_type_id: {content_type_id} ===")

        # detailCommon2는 필수 파라미터만 사용 (매뉴얼 기준)
        params = {
            'contentId': content_id
        }

        # contentTypeId는 옵션이지만 있으면 추가
        if content_type_id:
            params['contentTypeId'] = content_type_id
            logger.info(f"✅ contentTypeId provided: {content_type_id}")

        # 먼저 detailCommon2 시도 (무장애 여행 API 권장)
        result = self._make_request('detailCommon2', params)

        # 404가 아니고 정상 응답이면 바로 반환
        if result and result.get('status_code') != 404 and 'response' in result:
            logger.info(f"✅ Success with base_url: {self.base_url}")
            items = result.get('response', {}).get('body', {}).get('items', {}).get('item', [])
            if isinstance(items, dict):
                logger.info(f"API returned title: {items.get('title', 'NO TITLE')}, contentid: {items.get('contentid', 'NO ID')}")
            elif isinstance(items, list) and len(items) > 0:
                logger.info(f"API returned title: {items[0].get('title', 'NO TITLE')}, contentid: {items[0].get('contentid', 'NO ID')}")
            return result

        # 404인 경우, 다른 서비스 URL들로 fallback 시도
        if result and result.get('status_code') == 404:
            logger.warning(f"⚠️ Got 404 from {self.base_url}, trying fallback URLs...")

            for fallback_url in self.fallback_urls:
                if fallback_url == self.base_url:
                    continue  # 이미 시도한 URL은 건너뛰기

                logger.info(f"🔄 Trying fallback URL: {fallback_url}")

                # 임시로 base_url 변경
                original_url = self.base_url
                self.base_url = fallback_url

                fallback_result = self._make_request('detailCommon2', params)

                # base_url 복원
                self.base_url = original_url

                # 성공하면 반환
                if fallback_result and fallback_result.get('status_code') != 404 and 'response' in fallback_result:
                    logger.info(f"✅ Success with fallback URL: {fallback_url}")
                    items = fallback_result.get('response', {}).get('body', {}).get('items', {}).get('item', [])
                    if isinstance(items, dict):
                        logger.info(f"API returned title: {items.get('title', 'NO TITLE')}")
                    elif isinstance(items, list) and len(items) > 0:
                        logger.info(f"API returned title: {items[0].get('title', 'NO TITLE')}")
                    return fallback_result

            # 모든 fallback URL 실패
            logger.error(f"❌ All service URLs failed for content_id: {content_id}")
            return {'status_code': 404, 'error': 'NOT_FOUND_IN_ALL_SERVICES'}

        return result

    def get_detail_intro(self, content_id: str, content_type_id: str) -> Optional[Dict]:
        """
        소개 정보 조회 (detailIntro2)

        주의: content_type_id는 필수 파라미터입니다.
        기본값을 제거하여 호출하는 쪽에서 반드시 올바른 타입을 전달하도록 강제합니다.
        - 12: 관광지
        - 32: 숙박
        - 39: 음식점
        - 15: 행사/공연/축제
        """
        params = {
            'contentId': content_id,
            'contentTypeId': content_type_id,
        }

        return self._make_request('detailIntro2', params)

    def get_detail_info(self, content_id: str, content_type_id: str) -> Optional[Dict]:
        """
        반복 정보 조회 (detailInfo2)

        주의: content_type_id는 필수 파라미터입니다.
        각 타입별로 다른 구조의 데이터를 반환하므로 정확한 타입 전달이 중요합니다.
        """
        params = {
            'contentId': content_id,
            'contentTypeId': content_type_id,
        }

        return self._make_request('detailInfo2', params)

    def get_detail_image(self, content_id: str) -> Optional[Dict]:
        """이미지 정보 조회 (detailImage2)"""
        params = {
            'contentId': content_id,
            'imageYN': 'Y',
            'subImageYN': 'Y',  # 서브 이미지 포함
            'numOfRows': 100,
        }

        return self._make_request('detailImage2', params)

    def get_detail_with_tour(self, content_id: str) -> Optional[Dict]:
        """
        무장애 관광정보 상세 조회

        KorWithService2는 detailWithTour2를 사용합니다.
        응답 형식: Y/N이 아닌 텍스트 설명 반환
        """
        params = {
            'contentId': content_id,
        }

        # detailWithTour2로 변경 (KorWithService2 표준)
        return self._make_request('detailWithTour2', params)

    def search_keyword(
        self,
        keyword: str,
        area_code: Optional[str] = None,
        content_type_id: Optional[str] = None,
        page_no: int = 1,
        num_of_rows: int = 20
    ) -> Optional[Dict]:
        """키워드 검색"""
        params = {
            'keyword': keyword,
            'pageNo': page_no,
            'numOfRows': num_of_rows,
            'arrange': 'A',
        }

        if area_code:
            params['areaCode'] = area_code
        if content_type_id:
            params['contentTypeId'] = content_type_id

        return self._make_request('searchKeyword2', params)

    def get_area_code(self, area_code: Optional[str] = None) -> Optional[Dict]:
        """
        지역코드 조회 (areaCode2)

        시·군·구 지역 코드 목록을 조회
        """
        params = {
            'numOfRows': 100,
        }

        if area_code:
            params['areaCode'] = area_code

        return self._make_request('areaCode2', params)

    def get_category_code(
        self,
        content_type_id: Optional[str] = None,
        cat1: Optional[str] = None,
        cat2: Optional[str] = None,
        cat3: Optional[str] = None
    ) -> Optional[Dict]:
        """
        서비스분류코드 조회 (categoryCode2)

        관광지의 대·중·소분류 코드를 조회
        - cat1: 대분류 (12: 관광지, 14: 문화시설, 15: 축제공연행사, 28: 레포츠, 32: 숙박, 38: 쇼핑, 39: 음식점)
        - cat2: 중분류
        - cat3: 소분류
        """
        params = {
            'numOfRows': 100,
        }

        if content_type_id:
            params['contentTypeId'] = content_type_id
        if cat1:
            params['cat1'] = cat1
        if cat2:
            params['cat2'] = cat2
        if cat3:
            params['cat3'] = cat3

        return self._make_request('categoryCode2', params)

    def get_location_based_list(
        self,
        mapx: str,
        mapy: str,
        radius: int = 1000,
        content_type_id: Optional[str] = None,
        page_no: int = 1,
        num_of_rows: int = 20
    ) -> Optional[Dict]:
        """
        위치기반 관광정보 조회 (locationBasedList2)

        GPS 좌표 기반으로 주변 여행지 검색
        - mapx: GPS X좌표 (WGS84)
        - mapy: GPS Y좌표 (WGS84)
        - radius: 거리 반지름 (단위: m, 최대 20000m)
        """
        params = {
            'mapX': mapx,
            'mapY': mapy,
            'radius': radius,
            'pageNo': page_no,
            'numOfRows': num_of_rows,
            'arrange': 'A',
        }

        if content_type_id:
            params['contentTypeId'] = content_type_id

        return self._make_request('locationBasedList2', params)


# 싱글톤 인스턴스
tour_api_service = TourAPIService()
