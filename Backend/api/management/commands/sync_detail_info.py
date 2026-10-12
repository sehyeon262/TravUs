import time
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction
from api.accessibility import normalized_values
from api.models import TravelSpot, AccessibilityInfo
from api.services.tour_api import tour_api_service


class Command(BaseCommand):
    help = 'DB에 저장된 여행지의 상세 정보와 무장애 정보를 업데이트합니다.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--content-id',
            type=str,
            help='특정 여행지의 content_id만 업데이트',
        )
        parser.add_argument(
            '--area-code',
            type=str,
            help='특정 지역 코드만 업데이트 (예: 1=서울, 39=제주)',
        )
        parser.add_argument(
            '--limit',
            type=int,
            help='업데이트할 최대 개수',
        )
        parser.add_argument(
            '--skip-existing',
            action='store_true',
            help='이미 상세 정보가 있는 여행지는 건너뛰기',
        )

    def handle(self, *args, **options):
        content_id = options.get('content_id')
        area_code = options.get('area_code')
        limit = options.get('limit')
        skip_existing = options['skip_existing']

        # 쿼리셋 구성
        queryset = TravelSpot.objects.filter(is_active=True)

        if content_id:
            queryset = queryset.filter(content_id=content_id)

        if area_code:
            queryset = queryset.filter(area_code=area_code)

        if skip_existing:
            # description이나 overview가 비어있는 것만
            queryset = queryset.filter(description__isnull=True) | queryset.filter(description='')

        if limit:
            queryset = queryset[:limit]

        total_count = queryset.count()

        if total_count == 0:
            self.stdout.write(self.style.WARNING('업데이트할 여행지가 없습니다.'))
            return

        self.stdout.write(self.style.SUCCESS(f'총 {total_count}개의 여행지 상세 정보를 업데이트합니다.'))
        self.stdout.write(self.style.WARNING('API Rate Limit 방지를 위해 요청 사이 1.5초 대기'))

        updated_count = 0
        failed_count = 0
        skipped_count = 0
        not_found_count = 0

        for idx, travel_spot in enumerate(queryset, 1):
            self.stdout.write(f'\n[{idx}/{total_count}] {travel_spot.name} (ID: {travel_spot.content_id})')

            has_data = False

            try:
                # 1. 공통 상세 정보 (detailCommon1)
                self.stdout.write('  [상세] 상세 정보 가져오는 중...')
                detail_result = tour_api_service.get_detail_common(
                    content_id=travel_spot.content_id,
                    content_type_id=travel_spot.content_type_id
                )

                # 디버깅: API 응답 확인
                if not detail_result:
                    self.stdout.write(self.style.WARNING('  [경고] API 응답 없음 - 건너뜀'))
                    not_found_count += 1
                    continue

                # 404 체크
                if detail_result.get('status_code') == 404:
                    self.stdout.write(self.style.WARNING('  [경고] API에 상세 정보 없음 (404) - 건너뜀'))
                    not_found_count += 1
                    continue

                # 에러 응답 체크
                if 'response' in detail_result:
                    response_header = detail_result['response'].get('header', {})
                    result_code = response_header.get('resultCode')
                    result_msg = response_header.get('resultMsg')

                    if result_code != '0000':
                        self.stdout.write(self.style.WARNING(f'  [경고] API 에러: {result_code} - {result_msg}'))
                        not_found_count += 1
                        continue

                if detail_result and 'response' in detail_result:
                    detail_body = detail_result['response'].get('body', {})
                    detail_items = detail_body.get('items', {})

                    if isinstance(detail_items, dict) and 'item' in detail_items:
                        detail_list = detail_items['item']
                        if detail_list and len(detail_list) > 0:
                            detail = detail_list[0]

                            # 상세 정보 업데이트 - API 명세의 모든 필드
                            # 기본 정보
                            if detail.get('overview'):
                                travel_spot.overview = detail.get('overview', '')
                            if detail.get('homepage'):
                                travel_spot.homepage = detail.get('homepage', '')
                            if detail.get('tel'):
                                travel_spot.tel = detail.get('tel', '')
                            if detail.get('telname'):
                                travel_spot.tel_name = detail.get('telname', '')

                            # 주소 정보
                            if detail.get('addr1'):
                                travel_spot.addr1 = detail.get('addr1', '')
                                # 기존 address 필드도 업데이트
                                travel_spot.address = detail.get('addr1', '')
                            if detail.get('addr2'):
                                travel_spot.addr2 = detail.get('addr2', '')
                            if detail.get('zipcode'):
                                travel_spot.zipcode = detail.get('zipcode', '')

                            # 좌표 정보
                            if detail.get('mapx'):
                                travel_spot.longitude = detail.get('mapx', '')
                            if detail.get('mapy'):
                                travel_spot.latitude = detail.get('mapy', '')
                            if detail.get('mlevel'):
                                travel_spot.mlevel = detail.get('mlevel', '')

                            # 분류 정보
                            if detail.get('cat1'):
                                travel_spot.cat1 = detail.get('cat1', '')
                            if detail.get('cat2'):
                                travel_spot.cat2 = detail.get('cat2', '')
                            if detail.get('cat3'):
                                travel_spot.cat3 = detail.get('cat3', '')

                            # 이미지 정보
                            if detail.get('firstimage'):
                                travel_spot.image_url = detail.get('firstimage', '')
                            if detail.get('firstimage2'):
                                travel_spot.thumbnail_url = detail.get('firstimage2', '')

                            # 메타 정보
                            if detail.get('createdtime'):
                                travel_spot.created_time = detail.get('createdtime', '')
                            if detail.get('modifiedtime'):
                                travel_spot.modified_time = detail.get('modifiedtime', '')
                            if detail.get('cpyrhtDivCd'):
                                travel_spot.cpyrht_div_cd = detail.get('cpyrhtDivCd', '')

                            # 지역 정보 (이미 있는 필드들도 업데이트)
                            if detail.get('areacode'):
                                travel_spot.area_code = detail.get('areacode', '')
                            if detail.get('sigungucode'):
                                travel_spot.sigungu_code = detail.get('sigungucode', '')

                            has_data = True
                            self.stdout.write(self.style.SUCCESS('  [완료] 상세 정보 업데이트 완료'))

                time.sleep(3)  # Rate limit 방지

                # 2. 소개 정보 (detailIntro1)
                self.stdout.write('  [소개] 소개 정보 가져오는 중...')
                intro_result = tour_api_service.get_detail_intro(
                    content_id=travel_spot.content_id,
                    content_type_id=travel_spot.content_type_id
                )

                if intro_result and 'response' in intro_result:
                    intro_body = intro_result['response'].get('body', {})
                    intro_items = intro_body.get('items', {})

                    if isinstance(intro_items, dict) and 'item' in intro_items:
                        intro_list = intro_items['item']
                        if intro_list and len(intro_list) > 0:
                            intro = intro_list[0]

                            # 소개 정보를 description에 추가 (없을 경우)
                            if not travel_spot.description:
                                # contenttypeid별로 다른 필드 사용
                                if travel_spot.content_type_id == '12':  # 관광지
                                    travel_spot.description = intro.get('infocenter', '')
                                elif travel_spot.content_type_id == '39':  # 음식점
                                    travel_spot.description = intro.get('infocenterfood', '')
                                elif travel_spot.content_type_id == '32':  # 숙박
                                    travel_spot.description = intro.get('infocenterlodging', '')
                                has_data = True

                            self.stdout.write(self.style.SUCCESS('  [완료] 소개 정보 업데이트 완료'))

                time.sleep(3)  # Rate limit 방지

                # 3. 무장애 관광 정보 (detailWithTour2)
                self.stdout.write('  [무장애] 무장애 정보 가져오는 중...')
                with_tour_result = tour_api_service.get_detail_with_tour(travel_spot.content_id)

                if with_tour_result and 'response' in with_tour_result:
                    header = with_tour_result['response'].get('header', {})
                    if header.get('resultCode') != '0000':
                        raise ValueError('TourAPI accessibility response was not successful')
                    with_tour_body = with_tour_result['response'].get('body', {})
                    with_tour_items = with_tour_body.get('items', {})

                    if isinstance(with_tour_items, dict) and 'item' in with_tour_items:
                        with_tour_list = with_tour_items['item']
                        if isinstance(with_tour_list, dict):
                            with_tour_list = [with_tour_list]
                        if with_tour_list and len(with_tour_list) > 0:
                            with_tour = with_tour_list[0]

                            if str(with_tour.get('contentid', travel_spot.content_id)) != travel_spot.content_id:
                                raise ValueError('TourAPI accessibility content ID does not match the requested place')

                            # Parse every field before writing; malformed responses preserve existing data.
                            values = normalized_values(with_tour)
                            with transaction.atomic():
                                accessibility, created = AccessibilityInfo.objects.update_or_create(
                                    travel_spot=travel_spot, defaults=values
                                )

                            action = '생성' if created else '업데이트'
                            self.stdout.write(self.style.SUCCESS(f'  [완료] 무장애 정보 {action} 완료'))
                            has_data = True

                time.sleep(3)  # Rate limit 방지

                # 데이터가 있는 경우에만 저장
                if has_data:
                    travel_spot.last_synced_at = timezone.now()
                    travel_spot.save()
                    updated_count += 1
                    self.stdout.write(self.style.SUCCESS(f'  [성공] 완료 ({updated_count}/{total_count})'))
                else:
                    skipped_count += 1
                    self.stdout.write(self.style.WARNING(f'  [건너뜀] 업데이트할 데이터 없음'))

            except Exception as e:
                failed_count += 1
                self.stdout.write(self.style.ERROR(f'  [실패] 실패: {e}'))
                continue

        # 최종 결과 출력
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS(f'업데이트 완료!'))
        self.stdout.write(f'  - 성공: {updated_count}개')
        self.stdout.write(f'  - 실패: {failed_count}개')
        self.stdout.write(f'  - 건너뜀 (데이터 없음): {skipped_count}개')
        self.stdout.write(f'  - 404 (API에 없음): {not_found_count}개')
        self.stdout.write('='*60)
