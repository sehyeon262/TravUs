from django.db import models
from django.conf import settings
from rest_framework import viewsets, status, generics, permissions
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.views import APIView
from .models import TravelSpot, TravelSpotCategory, Bookmark, Course, CourseSpot, Review, CourseComment, CourseLike
from .serializers import (
    TravelSpotListSerializer, TravelSpotDetailSerializer,
    TravelSpotCategorySerializer, BookmarkSerializer,
    CourseSerializer, CourseCreateSerializer, ReviewSerializer,
    CourseCommentSerializer, CourseLikeSerializer
)
from .services.tour_api import tour_api_service
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from .serializers import SignupSerializer, LoginSerializer



User = get_user_model()



class TravelSpotViewSet(viewsets.ReadOnlyModelViewSet):
    """
    여행지 ViewSet (DB 기반)

    list: 여행지 목록 조회 (페이지네이션, 필터링, 검색 지원)
    retrieve: 여행지 상세 조회
    """
    queryset = TravelSpot.objects.filter(is_active=True)
    permission_classes = [permissions.AllowAny]

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return TravelSpotDetailSerializer
        return TravelSpotListSerializer

    def get_queryset(self):
        queryset = super().get_queryset()

        # 이미지가 있는 여행지만 (목록 조회시)
        if self.action == 'list':
            queryset = queryset.exclude(image_url__isnull=True).exclude(image_url='')

        # 필터링
        area_code = self.request.query_params.get('area_code')
        sigungu_code = self.request.query_params.get('sigungu_code')
        content_type_id = self.request.query_params.get('content_type_id')
        # category = self.request.query_params.get('category')
        search = self.request.query_params.get('search')

        if area_code:
            queryset = queryset.filter(area_code=area_code)
        if sigungu_code:
            queryset = queryset.filter(sigungu_code=sigungu_code)
        if content_type_id:
            queryset = queryset.filter(content_type_id=content_type_id)
        # if category:
        #     queryset = queryset.filter(category__name=category)
        if search:
            queryset = queryset.filter(
                models.Q(name__icontains=search) |
                models.Q(address__icontains=search) |
                models.Q(description__icontains=search)
            )

        # 무장애 시설 필터링
        facilities = self.request.query_params.get('facilities')
        if facilities:
            # 쉼표로 구분된 시설 목록을 파싱
            facility_list = [f.strip() for f in facilities.split(',') if f.strip()]

            # 각 시설에 대해 필터링 (AND 조건)
            for facility in facility_list:
                # accessibility__ 프리픽스를 사용하여 관련 AccessibilityInfo 필드 필터링
                filter_kwargs = {f'accessibility__{facility}': True}
                queryset = queryset.filter(**filter_kwargs)

        # 정렬 (기본: 최신순, 옵션: 인기순, 평점순)
        ordering = self.request.query_params.get('ordering', '-created_at')
        if ordering == 'popular':
            queryset = queryset.order_by('-view_count', '-bookmark_count')
        elif ordering == 'rating':
            queryset = queryset.order_by('-rating', '-review_count')
        else:
            queryset = queryset.order_by(ordering)

        # return queryset.select_related('category').prefetch_related('accessibility')
        return queryset.prefetch_related('accessibility')
    
    def retrieve(self, request, pk=None):
        """상세 조회 시 조회수 증가"""
        _ = pk  # URL parameter (사용하지 않지만 signature에 필요)
        instance = self.get_object()
        instance.view_count += 1
        instance.save(update_fields=['view_count'])
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def by_content_id(self, request):
        """
        content_id로 여행지 조회
        GET /api/travel-spots/by_content_id/?content_id=123456
        """
        content_id = request.query_params.get('content_id')

        if not content_id:
            return Response(
                {'error': 'content_id가 필요합니다'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            travel_spot = TravelSpot.objects.prefetch_related('accessibility').get(
                content_id=content_id,
                is_active=True
            )
            serializer = TravelSpotDetailSerializer(travel_spot)
            return Response(serializer.data)
        except TravelSpot.DoesNotExist:
            return Response(
                {'error': f'content_id({content_id})에 해당하는 여행지를 찾을 수 없습니다'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=False, methods=['get'])
    def recommendations(self, request):
        """
        같은 지역 추천 여행지
        GET /api/travel-spots/recommendations/?content_id=123456&limit=6
        """
        content_id = request.query_params.get('content_id')
        limit = int(request.query_params.get('limit', 6))

        if not content_id:
            return Response(
                {'error': 'content_id가 필요합니다'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # 현재 여행지 조회
            current_spot = TravelSpot.objects.get(content_id=content_id, is_active=True)

            # 같은 지역의 관광지 (content_type_id=12) 추천
            recommendations = TravelSpot.objects.filter(
                area_code=current_spot.area_code,
                content_type_id='12',  # 관광지만
                is_active=True
            ).exclude(
                id=current_spot.id  # 현재 여행지 제외
            ).order_by('-view_count')[:limit]  # 조회수 높은 순

            serializer = TravelSpotListSerializer(recommendations, many=True)
            return Response(serializer.data)

        except TravelSpot.DoesNotExist:
            return Response(
                {'error': f'content_id({content_id})에 해당하는 여행지를 찾을 수 없습니다'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=False, methods=['get'])
    def from_api(self, request):
        # 1. content_id 확인
        content_id = request.query_params.get('content_id')
        content_type_id = request.query_params.get('content_type_id')

        # [수정] ID가 있으면 상세 조회 로직만 수행하고 종료
        if content_id:
            # contentTypeId 포함하여 조회 (안정성 향상)
            result = tour_api_service.get_detail_common(content_id, content_type_id)

            # 404 처리
            if result and result.get('status_code') == 404:
                return Response(
                    {'error': f'해당 ID({content_id})의 여행지 정보를 찾을 수 없습니다.'},
                    status=status.HTTP_404_NOT_FOUND
                )

            # 데이터를 성공적으로 가져온 경우
            if result and 'response' in result:
                response_body = result['response'].get('body', {})
                items = response_body.get('items', {})

                if isinstance(items, dict) and 'item' in items:
                    item_list = items['item']
                    # 리스트가 아니면 리스트로 감싸기 (Normalize)
                    if not isinstance(item_list, list):
                        item_list = [item_list]
                elif isinstance(items, list):
                        # items 자체가 리스트인 경우 (가끔 발생)
                        item_list = items
                else:
                    item_list = []

                # 검색 결과가 있으면 반환
                if item_list:
                    return Response({
                        'count': len(item_list),
                        'results': item_list
                    })

            # [핵심] 조회 실패 시 500 에러 반환
            return Response(
                {'error': 'Tour API 요청 실패 - 네트워크 오류 또는 서버 문제'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        area_code = request.query_params.get('area_code')
        sigungu_code = request.query_params.get('sigungu_code')
        content_type_id = request.query_params.get('content_type_id')
        page_no = int(request.query_params.get('page', 1))
        num_of_rows = int(request.query_params.get('size', 20))

        result = tour_api_service.get_area_based_list(
            area_code=area_code,
            sigungu_code=sigungu_code,
            content_type_id=content_type_id,
            page_no=page_no,
            num_of_rows=num_of_rows
        )

        if result and 'response' in result:
            response_body = result['response'].get('body', {})
            items = response_body.get('items', {})

            # items 구조 처리 강화
            item_list = []
            if items:
                if isinstance(items, dict) and 'item' in items:
                    data = items['item']
                    item_list = data if isinstance(data, list) else [data]
                elif isinstance(items, list):
                    item_list = items
            
            return Response({
                'count': response_body.get('totalCount', 0),
                'results': item_list
            })

        return Response(
            {'error': 'API 요청 실패'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    @action(detail=False, methods=['get'])
    def search_api(self, request):

        keyword = request.query_params.get('keyword', '')
        area_code = request.query_params.get('area_code')
        page_no = int(request.query_params.get('page', 1))
        num_of_rows = int(request.query_params.get('size', 20))

        if not keyword:
            return Response(
                {'error': '검색어를 입력해주세요'},
                status=status.HTTP_400_BAD_REQUEST
            )

        result = tour_api_service.search_keyword(
            keyword=keyword,
            area_code=area_code,
            page_no=page_no,
            num_of_rows=num_of_rows
        )

        if result and 'response' in result:
            response_body = result['response'].get('body', {})
            items = response_body.get('items', {})

            # items가 딕셔너리이고 'item' 키가 있으면 그것을 사용
            if isinstance(items, dict) and 'item' in items:
                item_list = items['item']
            else:
                item_list = []

            return Response({
                'count': response_body.get('totalCount', 0),
                'results': item_list
            })

        return Response(
            {'error': 'API 요청 실패'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    @action(detail=False, methods=['get'])
    def detail_common(self, request):
        """
        공통 정보 상세 조회 (detailCommon1 - Service1/Service2 fallback 지원)

        Query Parameters:
            - content_id (필수): 콘텐츠 ID
            - content_type_id (선택): 콘텐츠 타입 ID (12:관광지, 14:문화시설, 15:축제, 32:숙박, 39:음식점 등)
                                      제공 시 조회 안정성이 크게 향상됩니다.
        """
        content_id = request.query_params.get('content_id')
        content_type_id = request.query_params.get('content_type_id')

        if not content_id:
            return Response(
                {'error': 'content_id가 필요합니다'},
                status=status.HTTP_400_BAD_REQUEST
            )

        result = tour_api_service.get_detail_common(content_id, content_type_id)

        # 404 처리 (데이터가 존재하지 않음)
        if result and result.get('status_code') == 404:
            return Response(
                {'error': f'해당 content_id({content_id})의 상세 정보를 찾을 수 없습니다.'},
                status=status.HTTP_404_NOT_FOUND
            )

        # 정상 응답
        if result and 'response' in result:
            return Response(result)

        # 기타 오류 (네트워크 오류 등)
        return Response(
            {'error': 'Tour API 요청 실패 - 네트워크 오류 또는 서버 문제'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    @action(detail=False, methods=['get'])
    def detail_intro(self, request):
        """소개 정보 조회 (detailIntro2)"""
        content_id = request.query_params.get('content_id')
        content_type_id = request.query_params.get('content_type_id')

        if not content_id:
            return Response(
                {'error': 'content_id가 필요합니다'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not content_type_id:
            return Response(
                {'error': 'content_type_id가 필요합니다'},
                status=status.HTTP_400_BAD_REQUEST
            )

        result = tour_api_service.get_detail_intro(content_id, content_type_id)

        if result:
            return Response(result)

        return Response(
            {'error': 'API 요청 실패'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    @action(detail=False, methods=['get'])
    def detail_info(self, request):
        """반복 정보 조회 (detailInfo2)"""
        content_id = request.query_params.get('content_id')
        content_type_id = request.query_params.get('content_type_id')

        if not content_id:
            return Response(
                {'error': 'content_id가 필요합니다'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not content_type_id:
            return Response(
                {'error': 'content_type_id가 필요합니다'},
                status=status.HTTP_400_BAD_REQUEST
            )

        result = tour_api_service.get_detail_info(content_id, content_type_id)

        if result:
            return Response(result)

        return Response(
            {'error': 'API 요청 실패'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    @action(detail=False, methods=['get'])
    def detail_image(self, request):
        """이미지 정보 조회 (detailImage2)"""
        content_id = request.query_params.get('content_id')

        if not content_id:
            return Response(
                {'error': 'content_id가 필요합니다'},
                status=status.HTTP_400_BAD_REQUEST
            )

        result = tour_api_service.get_detail_image(content_id)

        if result:
            return Response(result)

        return Response(
            {'error': 'API 요청 실패'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    @action(detail=False, methods=['get'])
    def detail_with_tour(self, request):
        """무장애 여행정보 조회 (detailWithTour1)"""
        content_id = request.query_params.get('content_id')

        if not content_id:
            return Response(
                {'error': 'content_id가 필요합니다'},
                status=status.HTTP_400_BAD_REQUEST
            )

        result = tour_api_service.get_detail_with_tour(content_id)

        if result:
            return Response(result)

        return Response(
            {'error': 'API 요청 실패'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    @action(detail=False, methods=['get'])
    def area_code(self, request):
        """지역코드 조회 (areaCode2)"""
        area_code = request.query_params.get('area_code')

        result = tour_api_service.get_area_code(area_code)

        if result:
            return Response(result)

        return Response(
            {'error': 'API 요청 실패'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    @action(detail=False, methods=['get'])
    def category_code(self, request):
        """서비스분류코드 조회 (categoryCode2)"""
        content_type_id = request.query_params.get('content_type_id')
        cat1 = request.query_params.get('cat1')
        cat2 = request.query_params.get('cat2')
        cat3 = request.query_params.get('cat3')

        result = tour_api_service.get_category_code(
            content_type_id=content_type_id,
            cat1=cat1,
            cat2=cat2,
            cat3=cat3
        )

        if result:
            return Response(result)

        return Response(
            {'error': 'API 요청 실패'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    @action(detail=False, methods=['get'])
    def location_based(self, request):
        """위치기반 관광정보 조회 (locationBasedList2)"""
        mapx = request.query_params.get('mapx')
        mapy = request.query_params.get('mapy')
        radius = int(request.query_params.get('radius', 1000))
        content_type_id = request.query_params.get('content_type_id')
        page_no = int(request.query_params.get('page', 1))
        num_of_rows = int(request.query_params.get('size', 20))

        if not mapx or not mapy:
            return Response(
                {'error': 'mapx와 mapy가 필요합니다'},
                status=status.HTTP_400_BAD_REQUEST
            )

        result = tour_api_service.get_location_based_list(
            mapx=mapx,
            mapy=mapy,
            radius=radius,
            content_type_id=content_type_id,
            page_no=page_no,
            num_of_rows=num_of_rows
        )

        if result and 'response' in result:
            response_body = result['response'].get('body', {})
            items = response_body.get('items', {})

            item_list = []
            if items:
                if isinstance(items, dict) and 'item' in items:
                    data = items['item']
                    item_list = data if isinstance(data, list) else [data]
                elif isinstance(items, list):
                    item_list = items

            return Response({
                'count': response_body.get('totalCount', 0),
                'results': item_list
            })

        return Response(
            {'error': 'API 요청 실패'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


class TravelSpotCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """여행지 카테고리 ViewSet"""
    queryset = TravelSpotCategory.objects.all()
    serializer_class = TravelSpotCategorySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class BookmarkViewSet(viewsets.ModelViewSet):
    """북마크 ViewSet"""
    serializer_class = BookmarkSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return Bookmark.objects.filter(user=self.request.user).select_related('travel_spot')
        return Bookmark.objects.none()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def toggle(self, request):
        """북마크 토글 (추가/삭제)"""
        travel_spot_id = request.data.get('travel_spot_id')

        if not travel_spot_id:
            return Response(
                {'error': 'travel_spot_id가 필요합니다.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            travel_spot = TravelSpot.objects.get(id=travel_spot_id)
        except TravelSpot.DoesNotExist:
            return Response(
                {'error': '여행지를 찾을 수 없습니다.'},
                status=status.HTTP_404_NOT_FOUND
            )

        # 이미 북마크가 있는지 확인
        bookmark = Bookmark.objects.filter(
            user=request.user,
            travel_spot=travel_spot
        ).first()

        if bookmark:
            # 북마크 삭제
            bookmark.delete()
            return Response({
                'bookmarked': False,
                'message': '북마크가 삭제되었습니다.'
            })
        else:
            # 북마크 추가
            Bookmark.objects.create(
                user=request.user,
                travel_spot=travel_spot
            )
            return Response({
                'bookmarked': True,
                'message': '북마크가 추가되었습니다.'
            })

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def check(self, request):
        """북마크 상태 확인"""
        travel_spot_id = request.query_params.get('travel_spot_id')

        if not travel_spot_id:
            return Response(
                {'error': 'travel_spot_id가 필요합니다.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        bookmarked = Bookmark.objects.filter(
            user=request.user,
            travel_spot_id=travel_spot_id
        ).exists()

        return Response({'bookmarked': bookmarked})


class CourseViewSet(viewsets.ModelViewSet):
    """여행 코스 ViewSet"""
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return CourseCreateSerializer
        return CourseSerializer

    def get_serializer_context(self):
        """Serializer에 request 전달"""
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def get_queryset(self):
        queryset = Course.objects.all()
        if self.request.user.is_authenticated:
            # 본인 코스 + 공개 코스
            queryset = queryset.filter(
                models.Q(user=self.request.user) | models.Q(is_public=True)
            )
        else:
            # 공개 코스만
            queryset = queryset.filter(is_public=True)

        return queryset.select_related('user').prefetch_related('course_spots__travel_spot')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        """코스 조회 시 조회수 증가"""
        instance = self.get_object()
        instance.view_count += 1
        instance.save(update_fields=['view_count'])
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def like(self, request, pk=None):
        """코스 좋아요 토글"""
        course = self.get_object()
        user = request.user

        # 좋아요 여부 확인
        like_instance = CourseLike.objects.filter(user=user, course=course).first()

        if like_instance:
            # 이미 좋아요 -> 취소
            like_instance.delete()
            course.like_count = models.F('like_count') - 1
            course.save(update_fields=['like_count'])
            course.refresh_from_db()
            return Response({
                'message': '좋아요를 취소했습니다.',
                'is_liked': False,
                'like_count': course.like_count
            })
        else:
            # 좋아요 추가
            CourseLike.objects.create(user=user, course=course)
            course.like_count = models.F('like_count') + 1
            course.save(update_fields=['like_count'])
            course.refresh_from_db()
            return Response({
                'message': '좋아요를 눌렀습니다.',
                'is_liked': True,
                'like_count': course.like_count
            })

    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def generate_ai_course(self, request):
        """
        AI를 이용한 여행 코스 생성

        Request Body:
            - region (str): 지역명 (예: "서울")
            - area_code (str): 지역 코드 (예: "1")
            - duration (str): 여행 기간 ("당일치기", "1박 2일", "2박 3일")
            - themes (list): 여행 테마 리스트 (선택사항)

        Response:
            - title: 코스 제목
            - description: 코스 설명
            - itinerary: 일정 배열 [{ day, order, type, id, spot_detail }]
        """
        from .services.ai_course_generator import ai_course_generator

        # 요청 데이터 검증
        region = request.data.get('region')
        area_code = request.data.get('area_code')
        duration = request.data.get('duration')
        themes = request.data.get('themes', [])

        print(f"[DEBUG] AI 코스 생성 요청: region={region}, area_code={area_code}, duration={duration}, themes={themes}")

        if not region or not area_code or not duration:
            print(f"[ERROR] 필수 파라미터 누락: region={region}, area_code={area_code}, duration={duration}")
            return Response(
                {'error': '지역, 지역코드, 여행 기간은 필수입니다'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if duration not in ["당일치기", "1박 2일", "2박 3일"]:
            return Response(
                {'error': '여행 기간은 "당일치기", "1박 2일", "2박 3일" 중 하나여야 합니다'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # DB에서 해당 지역의 여행지 조회
            travel_spots = TravelSpot.objects.filter(
                area_code=area_code,
                is_active=True
            ).exclude(
                image_url__isnull=True
            ).exclude(
                image_url=''
            ).exclude(
                latitude__isnull=True
            ).exclude(
                longitude__isnull=True
            ).values(
                'id', 'name', 'content_type_id', 'description',
                'latitude', 'longitude', 'address', 'image_url', 'area_code'
            )

            print(f"[DEBUG] DB 조회 결과: {len(travel_spots)}개 장소")
            if len(travel_spots) > 0:
                print(f"[DEBUG] 첫 번째 장소: name={travel_spots[0].get('name')}, area_code={travel_spots[0].get('area_code')}, address={travel_spots[0].get('address')}")
                # 지역 코드 분포 확인
                area_codes = {}
                for spot in travel_spots:
                    code = spot.get('area_code')
                    area_codes[code] = area_codes.get(code, 0) + 1
                print(f"[DEBUG] 지역 코드 분포: {area_codes}")

            # 여행지, 음식점, 숙박 분리
            attractions = [spot for spot in travel_spots if spot['content_type_id'] not in ['39', '32']]
            restaurants = [spot for spot in travel_spots if spot['content_type_id'] == '39']
            accommodations = [spot for spot in travel_spots if spot['content_type_id'] == '32']

            # 충분한 데이터가 있는지 확인
            required_counts = {
                "당일치기": {"travel": 4, "restaurant": 2, "accommodation": 0},
                "1박 2일": {"travel": 8, "restaurant": 4, "accommodation": 1},
                "2박 3일": {"travel": 12, "restaurant": 6, "accommodation": 2}
            }

            required = required_counts[duration]
            if len(attractions) < required["travel"]:
                return Response(
                    {'error': f'해당 지역의 여행지가 부족합니다 (필요: {required["travel"]}개, 현재: {len(attractions)}개)'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if len(restaurants) < required["restaurant"]:
                return Response(
                    {'error': f'해당 지역의 음식점이 부족합니다 (필요: {required["restaurant"]}개, 현재: {len(restaurants)}개)'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if len(accommodations) < required["accommodation"]:
                return Response(
                    {'error': f'해당 지역의 숙박시설이 부족합니다 (필요: {required["accommodation"]}개, 현재: {len(accommodations)}개)'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # AI 코스 생성
            all_spots = list(travel_spots)
            ai_result = ai_course_generator.generate_course(
                region=region,
                duration=duration,
                themes=themes,
                travel_spots=all_spots
            )

            # 생성된 ID 목록으로 상세 정보 조회
            spot_ids = [item['id'] for item in ai_result['itinerary']]
            spot_details = TravelSpot.objects.filter(id__in=spot_ids).values(
                'id', 'name', 'content_type_id', 'description', 'address',
                'latitude', 'longitude', 'image_url', 'tel', 'homepage'
            )

            # ID를 키로 하는 딕셔너리 생성
            spot_dict = {spot['id']: spot for spot in spot_details}

            # AI 응답에 상세 정보 추가 및 검증
            valid_itinerary = []
            for item in ai_result['itinerary']:
                spot_detail = spot_dict.get(item['id'])
                if spot_detail:
                    item['spot_detail'] = spot_detail
                    valid_itinerary.append(item)
                else:
                    # ID가 없는 경우 로그 남기고 스킵
                    print(f"[WARNING] ID {item['id']}에 해당하는 장소를 찾을 수 없습니다")

            # 유효한 일정으로 교체
            ai_result['itinerary'] = valid_itinerary

            # 최소 장소 수 확인 (기간별 최소 요구사항)
            min_required = {
                "당일치기": 6,
                "1박 2일": 10,  # 최소한의 일정 (숙박 포함하면 충분)
                "2박 3일": 15   # 최소한의 일정 (숙박 포함하면 충분)
            }

            min_count = min_required.get(duration, 6)
            if len(valid_itinerary) < min_count:
                invalid_count = len(ai_result['itinerary']) - len(valid_itinerary) if 'itinerary' in ai_result else 0
                return Response(
                    {
                        'error': f'AI가 생성한 일정 중 일부 장소를 찾을 수 없습니다. (유효: {len(valid_itinerary)}개, 필요: {min_count}개 이상)\n다시 시도해주세요.'
                    },
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            return Response(ai_result, status=status.HTTP_200_OK)

        except ValueError as e:
            return Response(
                {'error': f'입력 값 오류: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': f'AI 코스 생성 실패: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def toggle_like(self, request, pk=None):
        """
        코스 좋아요 토글

        이미 좋아요한 경우: 좋아요 취소
        좋아요하지 않은 경우: 좋아요 추가

        Response:
            - liked: 현재 좋아요 상태 (boolean)
            - like_count: 현재 총 좋아요 수
        """
        course = self.get_object()
        user = request.user

        like_obj, created = CourseLike.objects.get_or_create(
            user=user,
            course=course
        )

        if created:
            # 좋아요 추가
            course.like_count = models.F('like_count') + 1
            course.save(update_fields=['like_count'])
            course.refresh_from_db()
            liked = True
        else:
            # 좋아요 취소
            like_obj.delete()
            course.like_count = models.F('like_count') - 1
            course.save(update_fields=['like_count'])
            course.refresh_from_db()
            liked = False

        return Response({
            'liked': liked,
            'like_count': course.like_count
        })

    @action(detail=True, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def like_status(self, request, pk=None):
        """
        현재 사용자의 코스 좋아요 상태 조회

        Response:
            - liked: 좋아요 여부 (boolean)
            - like_count: 총 좋아요 수
        """
        course = self.get_object()
        user = request.user

        liked = CourseLike.objects.filter(user=user, course=course).exists()

        return Response({
            'liked': liked,
            'like_count': course.like_count
        })

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def my_courses(self, request):
        """
        나의 여행코스 조회
        - 현재 로그인한 사용자가 작성한 모든 코스 반환
        """
        user = request.user
        queryset = Course.objects.filter(user=user).select_related('user').prefetch_related('course_spots__travel_spot')
        queryset = queryset.order_by('-created_at')

        # 페이지네이션
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], permission_classes=[permissions.AllowAny])
    def monthly_best(self, request):
        """
        월간 Best 30 코스 조회
        - 좋아요 수 기준 상위 30개 공개 코스 반환
        - 최근 30일 이내 생성된 코스 중에서 선택
        """
        from datetime import datetime, timedelta

        # 최근 30일
        thirty_days_ago = datetime.now() - timedelta(days=30)

        queryset = Course.objects.filter(
            is_public=True,
            created_at__gte=thirty_days_ago
        ).select_related('user').prefetch_related('course_spots__travel_spot')

        queryset = queryset.order_by('-like_count', '-view_count')[:30]

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], permission_classes=[permissions.AllowAny])
    def by_region(self, request):
        """
        지역별 사용자 코스 조회
        - area_code 파라미터로 특정 지역의 공개 코스 반환

        Query Parameters:
            - area_code (str): 지역 코드 (필수)
            - ordering (str): 정렬 방식 (선택, 기본값: 'likes')
                - 'likes': 추천순 (좋아요 많은 순)
                - 'latest': 최신순 (최근 생성순)
        """
        area_code = request.query_params.get('area_code')
        ordering = request.query_params.get('ordering', 'likes')  # 기본값: 추천순

        if not area_code:
            return Response(
                {'error': 'area_code 파라미터가 필요합니다.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 해당 지역의 여행지를 포함하는 코스 찾기
        from django.db.models import Q, Exists, OuterRef

        # CourseSpot을 통해 해당 지역의 TravelSpot을 포함하는 코스 찾기
        course_spots_with_area = CourseSpot.objects.filter(
            course=OuterRef('pk'),
            travel_spot__area_code=area_code
        )

        queryset = Course.objects.filter(
            is_public=True
        ).annotate(
            has_area_spot=Exists(course_spots_with_area)
        ).filter(
            has_area_spot=True
        ).select_related('user').prefetch_related('course_spots__travel_spot')

        # 정렬 방식 적용
        if ordering == 'latest':
            queryset = queryset.order_by('-created_at', '-like_count')
        else:  # 기본값: likes (추천순)
            queryset = queryset.order_by('-like_count', '-created_at')

        # 페이지네이션
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class ReviewViewSet(viewsets.ModelViewSet):
    """리뷰 ViewSet"""
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        queryset = Review.objects.all()
        travel_spot_id = self.request.query_params.get('travel_spot')

        if travel_spot_id:
            queryset = queryset.filter(travel_spot_id=travel_spot_id)

        return queryset.select_related('user', 'travel_spot').order_by('-created_at')

    def perform_create(self, serializer):
        print(f"🔍 댓글 작성 요청 데이터: {self.request.data}")
        print(f"🔍 요청 사용자: {self.request.user}")
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'], permission_classes=[permissions.AllowAny])
    def summary(self, request):
        """AI 댓글 요약 기능"""
        travel_spot_id = request.query_params.get('travel_spot')

        if not travel_spot_id:
            return Response(
                {'error': 'travel_spot 파라미터가 필요합니다.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 해당 여행지의 모든 댓글 가져오기
        reviews = Review.objects.filter(travel_spot_id=travel_spot_id).select_related('user')

        if reviews.count() == 0:
            return Response({
                'summary': '아직 작성된 댓글이 없습니다.',
                'review_count': 0
            })

        # 댓글 내용 수집
        review_texts = [f"평점 {review.rating}점: {review.content}" for review in reviews]
        combined_text = "\n".join(review_texts)

        try:
            import requests
            import json

            gms_api_key = getattr(settings, 'GMS_API_KEY', 'S14P02EA02-e78f608f-87c7-4534-a076-6916104b3bdc')
            gms_api_url = 'https://gms.ssafy.io/gmsapi/api.openai.com/v1/chat/completions'

            response = requests.post(
                gms_api_url,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {gms_api_key}"
                },
                json={
                    "model": "gpt-4o-mini",
                    "messages": [
                        {
                            "role": "developer",
                            "content": "당신은 여행지 리뷰 분석 전문가입니다. 사용자들의 댓글을 분석하여 핵심 내용을 4줄로 간결하게 요약해주세요."
                        },
                        {
                            "role": "user",
                            "content": f"""다음은 여행지에 대한 사용자 댓글들입니다. 이 댓글들을 분석하여 4줄로 요약해주세요.

댓글 내용:
{combined_text}

요약 형식:
1. 전반적인 평가 (긍정적/부정적)
2. 주요 장점
3. 주요 단점 또는 개선점
4. 방문 추천 여부

4줄로 간결하게 작성해주세요."""
                        }
                    ],
                    "temperature": 0.7
                },
                timeout=30
            )

            if response.status_code == 200:
                ai_result = response.json()
                summary_text = ai_result['choices'][0]['message']['content']

                return Response({
                    'summary': summary_text,
                    'review_count': reviews.count()
                })
            else:
                raise Exception(f"GMS API 호출 실패: {response.status_code}")

        except Exception as e:
            print(f"AI 요약 생성 실패: {str(e)}")
            return Response({
                'summary': '댓글 요약을 생성하는 중 오류가 발생했습니다.',
                'review_count': reviews.count(),
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CheckUsernameView(APIView):
    """아이디 중복 체크"""
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        username = request.query_params.get('username', '').strip()

        if not username:
            return Response({
                'available': False,
                'message': '아이디를 입력해주세요.'
            }, status=status.HTTP_400_BAD_REQUEST)

        # 아이디 길이 및 형식 검증
        if len(username) < 4 or len(username) > 20:
            return Response({
                'available': False,
                'message': '아이디는 4-20자여야 합니다.'
            }, status=status.HTTP_400_BAD_REQUEST)

        # 아이디 사용 가능 여부 확인
        exists = User.objects.filter(username=username).exists()

        return Response({
            'available': not exists,
            'message': '사용 가능한 아이디입니다.' if not exists else '이미 사용중인 아이디입니다.'
        })


class SignupView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = SignupSerializer
    permission_classes = [permissions.AllowAny]

class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        refresh = RefreshToken.for_user(user)
        return Response({
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "phone": getattr(user, "phone", ""),
                "disability_type": getattr(user, "disability_type", "NONE"),
                "preferred_accessibility": getattr(user, "preferred_accessibility", {}),
            },
        })

class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response({'detail': 'refresh 토큰이 필요합니다.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except TokenError:
            return Response({'detail': '유효하지 않은 토큰입니다.'}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'detail': '로그아웃되었습니다.'}, status=status.HTTP_205_RESET_CONTENT)

class MeView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        return Response({
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "phone": getattr(user, "phone", ""),
            "disability_type": getattr(user, "disability_type", "NONE"),
            "preferred_accessibility": getattr(user, "preferred_accessibility", {}),
        })


# 코스 댓글 API
class CourseCommentListCreateView(generics.ListCreateAPIView):
    """코스 댓글 목록 조회 및 생성"""
    serializer_class = CourseCommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        course_id = self.kwargs['course_id']
        return CourseComment.objects.filter(course_id=course_id, parent=None).order_by('-created_at')

    def perform_create(self, serializer):
        course_id = self.kwargs['course_id']
        serializer.save(user=self.request.user, course_id=course_id)


class CourseCommentDetailView(generics.RetrieveUpdateDestroyAPIView):
    """코스 댓글 상세 조회, 수정, 삭제"""
    queryset = CourseComment.objects.all()
    serializer_class = CourseCommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return CourseComment.objects.filter(user=self.request.user)


class CourseCommentRepliesView(generics.ListAPIView):
    """댓글의 대댓글 목록 조회"""
    serializer_class = CourseCommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        comment_id = self.kwargs['comment_id']
        return CourseComment.objects.filter(parent_id=comment_id).order_by('created_at')
@api_view(['POST'])
def analyze_image(request):
    return Response({"message": "analyze_image OK"})

@api_view(['POST'])
def chat_ai(request):
    return Response({"message": "chat_ai OK"})


