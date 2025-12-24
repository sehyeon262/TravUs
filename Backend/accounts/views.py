from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate, get_user_model
from .serializers import UserSignupSerializer, UserSerializer, UserLoginSerializer

User = get_user_model()


@api_view(['POST'])
@permission_classes([AllowAny])
def signup(request):
    """
    회원가입 API
    - 회원가입 후 자동으로 JWT 토큰을 발급하여 로그인 처리
    """
    serializer = UserSignupSerializer(data=request.data)

    if serializer.is_valid():
        try:
            # 사용자 생성
            user = serializer.save()

            # JWT 토큰 생성 (회원가입 후 자동 로그인)
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)

            # 사용자 정보 직렬화
            user_data = UserSerializer(user).data

            return Response({
                'message': '회원가입이 완료되었습니다.',
                'user': user_data,
                'tokens': {
                    'access': access_token,
                    'refresh': refresh_token
                }
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({
                'error': f'회원가입 중 오류가 발생했습니다: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # 에러 메시지 추출
    error_messages = []
    for field, errors in serializer.errors.items():
        if isinstance(errors, list):
            error_messages.extend(errors)
        else:
            error_messages.append(str(errors))

    return Response({
        'error': error_messages[0] if error_messages else '회원가입에 실패했습니다.',
        'details': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([AllowAny])
def check_username(request):
    """
    아이디 중복 확인 API
    """
    username = request.query_params.get('username', '').strip()

    if not username:
        return Response({
            'available': False,
            'message': '아이디를 입력해주세요.'
        }, status=status.HTTP_400_BAD_REQUEST)

    # 아이디 길이 검증
    if len(username) < 4 or len(username) > 20:
        return Response({
            'available': False,
            'message': '아이디는 4-20자로 입력해주세요.'
        }, status=status.HTTP_400_BAD_REQUEST)

    # 아이디 형식 검증 (영문+숫자만)
    if not username.isalnum():
        return Response({
            'available': False,
            'message': '아이디는 영문과 숫자만 사용 가능합니다.'
        }, status=status.HTTP_400_BAD_REQUEST)

    # 중복 확인
    exists = User.objects.filter(username=username).exists()

    return Response({
        'available': not exists,
        'message': '사용 가능한 아이디입니다.' if not exists else '이미 사용중인 아이디입니다.'
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    """
    로그인 API
    - JWT 토큰을 발급하여 인증 처리
    """
    serializer = UserLoginSerializer(data=request.data)

    if not serializer.is_valid():
        return Response({
            'error': '아이디와 비밀번호를 입력해주세요.'
        }, status=status.HTTP_400_BAD_REQUEST)

    username = serializer.validated_data['username']
    password = serializer.validated_data['password']

    # 사용자 인증
    user = authenticate(username=username, password=password)

    if user is None:
        return Response({
            'error': '아이디 또는 비밀번호가 올바르지 않습니다.'
        }, status=status.HTTP_401_UNAUTHORIZED)

    # JWT 토큰 생성
    refresh = RefreshToken.for_user(user)
    access_token = str(refresh.access_token)
    refresh_token = str(refresh)

    # 사용자 정보 직렬화
    user_data = UserSerializer(user).data

    return Response({
        'message': '로그인되었습니다.',
        'user': user_data,
        'tokens': {
            'access': access_token,
            'refresh': refresh_token
        }
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    """
    로그아웃 API
    - Refresh 토큰을 블랙리스트에 추가
    """
    try:
        refresh_token = request.data.get('refresh')
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()

        return Response({
            'message': '로그아웃되었습니다.'
        })
    except Exception as e:
        return Response({
            'error': '로그아웃에 실패했습니다.'
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_info(request):
    """
    현재 로그인한 사용자 정보 조회 API
    """
    serializer = UserSerializer(request.user)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([AllowAny])
def password_reset_request(request):
    """
    비밀번호 재설정 요청 API
    - 이메일로 비밀번호 재설정 링크 전송 (실제 이메일 전송은 구현하지 않음)
    """
    email = request.data.get('email', '').strip()

    if not email:
        return Response({
            'error': '이메일을 입력해주세요.'
        }, status=status.HTTP_400_BAD_REQUEST)

    # 이메일로 사용자 검색
    try:
        user = User.objects.get(email=email)

        # 실제 프로덕션 환경에서는 여기서 이메일 전송
        # 지금은 임시 비밀번호를 생성하고 직접 변경
        import random
        import string
        temp_password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))

        user.set_password(temp_password)
        user.save()

        # 실제로는 이메일로 전송하지만, 개발 환경에서는 응답으로 반환
        return Response({
            'message': '임시 비밀번호가 이메일로 전송되었습니다.',
            'temp_password': temp_password  # 실제 프로덕션에서는 삭제
        })
    except User.DoesNotExist:
        # 보안상 이메일이 존재하지 않아도 성공 메시지 반환
        return Response({
            'message': '해당 이메일로 비밀번호 재설정 링크가 전송되었습니다.'
        })
