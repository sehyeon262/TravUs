from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator


class TravelSpotCategory(models.Model):
    """여행지 카테고리"""
    name = models.CharField(max_length=50, unique=True, verbose_name='카테고리명')
    description = models.TextField(blank=True, null=True, verbose_name='설명')
    icon = models.CharField(max_length=50, blank=True, null=True, verbose_name='아이콘')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일')

    class Meta:
        db_table = 'travel_spot_categories'
        verbose_name = '여행지 카테고리'
        verbose_name_plural = '여행지 카테고리'

    def __str__(self):
        return self.name


class TravelSpot(models.Model):
    id = models.BigAutoField(primary_key=True)

    content_id = models.CharField(max_length=50, unique=True)
    content_type_id = models.CharField(max_length=20)

    name = models.CharField(max_length=200)
    address = models.CharField(max_length=300)

    area_code = models.CharField(max_length=10, null=True)
    sigungu_code = models.CharField(max_length=10, null=True)

    latitude = models.DecimalField(max_digits=10, decimal_places=7, null=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=7, null=True)

    description = models.TextField(null=True)
    overview = models.TextField(null=True)

    tel = models.TextField(null=True)
    homepage = models.CharField(max_length=200, null=True)
    image_url = models.CharField(max_length=200, null=True)
    thumbnail_url = models.CharField(max_length=200, null=True)

    rating = models.DecimalField(max_digits=3, decimal_places=2)
    review_count = models.IntegerField()
    view_count = models.IntegerField()
    bookmark_count = models.IntegerField()

    is_active = models.BooleanField()

    created_at = models.DateTimeField(null=True)
    updated_at = models.DateTimeField(null=True)
    last_synced_at = models.DateTimeField(null=True)

    category_id = models.BigIntegerField(null=True)

    class Meta:
        db_table = 'travel_spots'
        managed = False   # ⭐⭐⭐ 이게 핵심

class AccessibilityInfo(models.Model):
    """무장애 정보: True=가능, False=불가, None=판단할 정보 부족."""
    travel_spot = models.OneToOneField(
        TravelSpot, on_delete=models.CASCADE, related_name='accessibility', verbose_name='여행지'
    )
    parking = models.BooleanField(null=True, default=None, verbose_name='장애인 주차장')
    parking_info = models.TextField(blank=True, null=True, verbose_name='장애인 주차장 원문')
    public_transport = models.BooleanField(null=True, default=None, verbose_name='대중교통 접근')
    public_transport_info = models.TextField(blank=True, null=True, verbose_name='대중교통 접근 원문')
    route = models.BooleanField(null=True, default=None, verbose_name='접근로')
    route_info = models.TextField(blank=True, null=True, verbose_name='접근로 원문')
    ticket_office = models.BooleanField(null=True, default=None, verbose_name='매표소')
    ticket_office_info = models.TextField(blank=True, null=True, verbose_name='매표소 원문')
    promotion = models.BooleanField(null=True, default=None, verbose_name='홍보물')
    promotion_info = models.TextField(blank=True, null=True, verbose_name='홍보물 원문')
    wheelchair = models.BooleanField(null=True, default=None, verbose_name='휠체어 대여')
    wheelchair_info = models.TextField(blank=True, null=True, verbose_name='휠체어 대여 원문')
    exit = models.BooleanField(null=True, default=None, verbose_name='출입통로')
    exit_info = models.TextField(blank=True, null=True, verbose_name='출입통로 원문')
    elevator = models.BooleanField(null=True, default=None, verbose_name='승강기')
    elevator_info = models.TextField(blank=True, null=True, verbose_name='승강기 원문')
    restroom = models.BooleanField(null=True, default=None, verbose_name='장애인 화장실')
    restroom_info = models.TextField(blank=True, null=True, verbose_name='장애인 화장실 원문')
    auditorium = models.BooleanField(null=True, default=None, verbose_name='관람석')
    auditorium_info = models.TextField(blank=True, null=True, verbose_name='관람석 원문')
    room = models.BooleanField(null=True, default=None, verbose_name='장애인 객실')
    room_info = models.TextField(blank=True, null=True, verbose_name='장애인 객실 원문')
    braile_block = models.BooleanField(null=True, default=None, verbose_name='점자블록')
    braile_block_info = models.TextField(blank=True, null=True, verbose_name='점자블록 원문')
    help_dog = models.BooleanField(null=True, default=None, verbose_name='안내견 동반')
    help_dog_info = models.TextField(blank=True, null=True, verbose_name='안내견 동반 원문')
    guide_human = models.BooleanField(null=True, default=None, verbose_name='안내 인력')
    guide_human_info = models.TextField(blank=True, null=True, verbose_name='안내 인력 원문')
    audio_guide = models.BooleanField(null=True, default=None, verbose_name='음성안내')
    audio_guide_info = models.TextField(blank=True, null=True, verbose_name='음성안내 원문')
    big_print = models.BooleanField(null=True, default=None, verbose_name='큰 글자 안내')
    big_print_info = models.TextField(blank=True, null=True, verbose_name='큰 글자 안내 원문')
    braile_promotion = models.BooleanField(null=True, default=None, verbose_name='점자 홍보물')
    braile_promotion_info = models.TextField(blank=True, null=True, verbose_name='점자 홍보물 원문')
    guide_system = models.BooleanField(null=True, default=None, verbose_name='유도 안내 설비')
    guide_system_info = models.TextField(blank=True, null=True, verbose_name='유도 안내 설비 원문')
    sign_guide = models.BooleanField(null=True, default=None, verbose_name='수어 안내')
    sign_guide_info = models.TextField(blank=True, null=True, verbose_name='수어 안내 원문')
    video_guide = models.BooleanField(null=True, default=None, verbose_name='자막 영상 안내')
    video_guide_info = models.TextField(blank=True, null=True, verbose_name='자막 영상 안내 원문')
    hearing_room = models.BooleanField(null=True, default=None, verbose_name='청각장애 객실')
    hearing_room_info = models.TextField(blank=True, null=True, verbose_name='청각장애 객실 원문')
    stroller = models.BooleanField(null=True, default=None, verbose_name='유모차 대여')
    stroller_info = models.TextField(blank=True, null=True, verbose_name='유모차 대여 원문')
    lactation_room = models.BooleanField(null=True, default=None, verbose_name='수유실')
    lactation_room_info = models.TextField(blank=True, null=True, verbose_name='수유실 원문')
    baby_spare_chair = models.BooleanField(null=True, default=None, verbose_name='유아용 의자')
    baby_spare_chair_info = models.TextField(blank=True, null=True, verbose_name='유아용 의자 원문')
    handicap_etc = models.TextField(blank=True, null=True)
    blind_handicap_etc = models.TextField(blank=True, null=True)
    hearing_handicap_etc = models.TextField(blank=True, null=True)
    infants_family_etc = models.TextField(blank=True, null=True)
    source_payload = models.JSONField(default=dict, blank=True, verbose_name='마지막 무장애 원본 응답')
    legacy_flags = models.JSONField(default=dict, blank=True, editable=False, verbose_name='재판정 전 기존 값')
    normalization_version = models.CharField(max_length=32, default='', blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일')

    class Meta:
        db_table = 'accessibility_info'
        verbose_name = '무장애 정보'
        verbose_name_plural = '무장애 정보'

    def __str__(self):
        return f"{self.travel_spot.name} 접근성 정보"


class Bookmark(models.Model):
    """북마크"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='bookmarks',
        verbose_name='사용자'
    )
    travel_spot = models.ForeignKey(
        TravelSpot,
        on_delete=models.CASCADE,
        related_name='bookmarks',
        verbose_name='여행지'
    )
    memo = models.TextField(blank=True, null=True, verbose_name='메모')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일')

    class Meta:
        db_table = 'bookmarks'
        verbose_name = '북마크'
        verbose_name_plural = '북마크'
        unique_together = [['user', 'travel_spot']]
        indexes = [
            models.Index(fields=['user', '-created_at']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.travel_spot.name}"


class Course(models.Model):
    """여행 코스"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='courses',
        verbose_name='사용자'
    )
    title = models.CharField(max_length=200, verbose_name='코스 제목')
    description = models.TextField(blank=True, null=True, verbose_name='설명')

    # 코스 메타 정보
    total_distance = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='총 거리(km)'
    )
    estimated_duration = models.IntegerField(
        null=True,
        blank=True,
        verbose_name='예상 소요시간(분)'
    )

    # 공개 설정
    is_public = models.BooleanField(default=False, verbose_name='공개 여부')
    like_count = models.IntegerField(default=0, verbose_name='좋아요 수')
    view_count = models.IntegerField(default=0, verbose_name='조회수')

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일')

    class Meta:
        db_table = 'courses'
        verbose_name = '여행 코스'
        verbose_name_plural = '여행 코스'
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['-like_count']),
        ]

    def __str__(self):
        return self.title


class CourseSpot(models.Model):
    """코스 내 여행지"""
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='course_spots',
        verbose_name='코스'
    )
    travel_spot = models.ForeignKey(
        TravelSpot,
        on_delete=models.CASCADE,
        related_name='course_spots',
        verbose_name='여행지'
    )
    order = models.IntegerField(verbose_name='순서')
    day = models.IntegerField(default=1, verbose_name='일차')
    spot_type = models.CharField(
        max_length=20,
        default='travel',
        choices=[
            ('travel', '여행지'),
            ('restaurant', '음식점'),
            ('accommodation', '숙박')
        ],
        verbose_name='장소 타입'
    )
    memo = models.TextField(blank=True, null=True, verbose_name='메모')
    stay_duration = models.IntegerField(
        null=True,
        blank=True,
        verbose_name='체류 시간(분)'
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일')

    class Meta:
        db_table = 'course_spots'
        verbose_name = '코스 여행지'
        verbose_name_plural = '코스 여행지'
        unique_together = [['course', 'travel_spot']]
        ordering = ['order']
        indexes = [
            models.Index(fields=['course', 'order']),
        ]

    def __str__(self):
        return f"{self.course.title} - {self.order}. {self.travel_spot.name}"


class Review(models.Model):
    """리뷰"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='사용자'
    )
    travel_spot = models.ForeignKey(
        TravelSpot,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='여행지'
    )

    rating = models.IntegerField(
        default=5,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name='평점'
    )
    content = models.TextField(verbose_name='내용')

    # 접근성 평가
    accessibility_rating = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name='접근성 평점'
    )

    # 이미지
    images = models.JSONField(default=list, blank=True, verbose_name='이미지 URL 목록')

    # 통계
    like_count = models.IntegerField(default=0, verbose_name='좋아요 수')

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일')

    class Meta:
        db_table = 'reviews'
        verbose_name = '리뷰'
        verbose_name_plural = '리뷰'
        indexes = [
            models.Index(fields=['travel_spot', '-created_at']),
            models.Index(fields=['user', '-created_at']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.travel_spot.name} ({self.rating}점)"


class CourseLike(models.Model):
    """코스 좋아요"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='course_likes',
        verbose_name='사용자'
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='likes',
        verbose_name='코스'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일')

    class Meta:
        db_table = 'course_likes'
        verbose_name = '코스 좋아요'
        verbose_name_plural = '코스 좋아요'
        unique_together = [['user', 'course']]
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['course', '-created_at']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.course.title} 좋아요"


class CourseComment(models.Model):
    """코스 댓글 (여행톡)"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='course_comments',
        verbose_name='사용자'
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='코스'
    )
    content = models.TextField(verbose_name='내용')

    # 대댓글 지원
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='replies',
        verbose_name='부모 댓글'
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일')

    class Meta:
        db_table = 'course_comments'
        verbose_name = '코스 댓글'
        verbose_name_plural = '코스 댓글'
        indexes = [
            models.Index(fields=['course', '-created_at']),
            models.Index(fields=['user', '-created_at']),
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.course.title} 댓글"
