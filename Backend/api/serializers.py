from rest_framework import serializers
from .models import (
    TravelSpotCategory, TravelSpot, AccessibilityInfo,
    Bookmark, Course, CourseSpot, Review, CourseComment, CourseLike
)
from django.contrib.auth import authenticate, get_user_model

User = get_user_model()


class TravelSpotCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = TravelSpotCategory
        fields = ['id', 'name', 'description', 'icon', 'created_at']


class AccessibilityInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccessibilityInfo
        fields = [
            'id', 'parking', 'route', 'public_transport', 'restroom',
            'wheelchair', 'exit', 'elevator', 'audio_guide',
            'parking_info', 'route_info', 'restroom_info',
            'wheelchair_info', 'exit_info', 'elevator_info',
            'braile_block', 'help_dog', 'guide_system',
            'stroller', 'lactation_room'
        ]


class TravelSpotListSerializer(serializers.ModelSerializer):
    """여행지 리스트용 Serializer (간단한 정보)"""
    category_name = serializers.CharField(source='category.name', read_only=True)
    is_bookmarked = serializers.SerializerMethodField()

    class Meta:
        model = TravelSpot
        fields = [
            'id', 'content_id', 'content_type_id', 'name', 'category_name',
            'address', 'area_code', 'latitude', 'longitude',
            'image_url', 'thumbnail_url', 'tel',
            'rating', 'review_count', 'view_count', 'bookmark_count',
            'is_bookmarked'
        ]

    def get_is_bookmarked(self, obj):
        """현재 사용자가 이 여행지를 북마크했는지 여부"""
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False

        # prefetched bookmarks가 있으면 사용 (N+1 쿼리 방지)
        if hasattr(obj, '_user_bookmarked'):
            return obj._user_bookmarked

        # 없으면 직접 조회
        return Bookmark.objects.filter(
            user=request.user,
            travel_spot=obj
        ).exists()


class TravelSpotDetailSerializer(serializers.ModelSerializer):
    """여행지 상세 정보용 Serializer"""
    category = TravelSpotCategorySerializer(read_only=True)
    accessibility = AccessibilityInfoSerializer(read_only=True)

    class Meta:
        model = TravelSpot
        fields = [
            'id', 'content_id', 'content_type_id', 'name', 'category',
            'address', 'area_code', 'sigungu_code', 'latitude', 'longitude',
            'description', 'tel', 'homepage',
            'image_url', 'thumbnail_url',
            'rating', 'review_count', 'view_count', 'bookmark_count',
            'accessibility', 'is_active', 'created_at', 'updated_at'
        ]


class BookmarkSerializer(serializers.ModelSerializer):
    travel_spot = TravelSpotListSerializer(read_only=True)

    class Meta:
        model = Bookmark
        fields = ['id', 'travel_spot', 'memo', 'created_at']


class CourseSpotSerializer(serializers.ModelSerializer):
    travel_spot = TravelSpotListSerializer(read_only=True)
    day = serializers.SerializerMethodField()
    spot_type = serializers.SerializerMethodField()

    class Meta:
        model = CourseSpot
        fields = ['id', 'travel_spot', 'order', 'day', 'spot_type', 'memo', 'stay_duration']

    def get_day(self, obj):
        """order를 기반으로 day 계산 (하루에 3~5개 장소 가정)"""
        # 코스의 총 spot 수를 가져와서 day 계산
        # 간단하게 order를 5로 나눠서 계산 (하루 최대 5개 장소)
        return ((obj.order - 1) // 5) + 1

    def get_spot_type(self, obj):
        """여행지 타입 반환 (content_type_id 기반)"""
        if obj.travel_spot.content_type_id == 32:
            return 'accommodation'  # 숙박
        return 'attraction'  # 기본값: 여행지


class CourseSerializer(serializers.ModelSerializer):
    """코스 조회용 Serializer"""
    course_spots = CourseSpotSerializer(many=True, read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    user_name = serializers.CharField(source='user.first_name', read_only=True)
    is_liked = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = [
            'id', 'user', 'username', 'user_name', 'title', 'description',
            'total_distance', 'estimated_duration',
            'is_public', 'like_count', 'view_count', 'comments_count',
            'is_liked', 'course_spots', 'created_at', 'updated_at'
        ]
        read_only_fields = ['user', 'like_count', 'view_count', 'created_at', 'updated_at']

    def get_is_liked(self, obj):
        """현재 사용자가 좋아요를 눌렀는지 확인"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return CourseLike.objects.filter(user=request.user, course=obj).exists()
        return False

    def get_comments_count(self, obj):
        """댓글 수 반환 (대댓글 제외)"""
        return obj.comments.filter(parent__isnull=True).count()


class ReviewSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(source='user.id', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    user_name = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Review
        fields = [
            'id', 'user', 'user_id', 'username', 'user_name', 'travel_spot',
            'rating', 'content', 'accessibility_rating',
            'images', 'like_count', 'created_at', 'updated_at'
        ]
        extra_kwargs = {
            'user': {'read_only': True},
            'rating': {'required': False},
            'accessibility_rating': {'required': False},
            'images': {'required': False},
            'like_count': {'read_only': True}
        }


class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = [
            "id", "username", "email", "password",
            "first_name", "last_name", "phone",
            "disability_type", "preferred_accessibility",
        ]
        extra_kwargs = {
            "email": {"required": False, "allow_blank": True},
            "first_name": {"required": False, "allow_blank": True},
            "last_name": {"required": False, "allow_blank": True},
            "phone": {"required": False, "allow_blank": True},
        }

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(
            username=data.get("username"),
            password=data.get("password")
        )
        if not user:
            raise serializers.ValidationError("아이디 또는 비밀번호가 올바르지 않습니다.")
        data["user"] = user
        return data


class CourseCommentSerializer(serializers.ModelSerializer):
    """코스 댓글 Serializer"""
    username = serializers.CharField(source='user.username', read_only=True)
    replies_count = serializers.SerializerMethodField()

    class Meta:
        model = CourseComment
        fields = [
            'id', 'user', 'username', 'course', 'content',
            'parent', 'replies_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['user', 'course', 'created_at', 'updated_at']

    def get_replies_count(self, obj):
        return obj.replies.count()


class CourseCommentCreateSerializer(serializers.ModelSerializer):
    """코스 댓글 생성용 Serializer"""
    class Meta:
        model = CourseComment
        fields = ['content', 'parent']


class CourseCreateSerializer(serializers.ModelSerializer):
    """코스 생성/수정용 Serializer"""
    spots = serializers.ListField(
        child=serializers.DictField(),
        write_only=True,
        required=False
    )

    class Meta:
        model = Course
        fields = [
            'title', 'description', 'total_distance',
            'estimated_duration', 'is_public', 'spots'
        ]

    def create(self, validated_data):
        spots_data = validated_data.pop('spots', [])
        # user는 perform_create에서 이미 전달되므로 여기서는 제거
        # validated_data에 이미 user가 포함되어 있음

        # 코스 생성
        course = Course.objects.create(**validated_data)

        # 코스 여행지 추가
        for spot_data in spots_data:
            CourseSpot.objects.create(
                course=course,
                travel_spot_id=spot_data.get('travel_spot_id'),
                order=spot_data.get('order', 0),
                memo=spot_data.get('memo', ''),
                stay_duration=spot_data.get('stay_duration')
            )

        return course

    def update(self, instance, validated_data):
        spots_data = validated_data.pop('spots', None)

        # 코스 기본 정보 업데이트
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # 코스 여행지 업데이트 (기존 삭제 후 재생성)
        if spots_data is not None:
            instance.course_spots.all().delete()
            for spot_data in spots_data:
                CourseSpot.objects.create(
                    course=instance,
                    travel_spot_id=spot_data.get('travel_spot_id'),
                    order=spot_data.get('order', 0),
                    memo=spot_data.get('memo', ''),
                    stay_duration=spot_data.get('stay_duration')
                )

        return instance


class CourseLikeSerializer(serializers.ModelSerializer):
    """코스 좋아요 Serializer"""
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = CourseLike
        fields = ['id', 'user', 'username', 'course', 'created_at']
        read_only_fields = ['user', 'created_at']