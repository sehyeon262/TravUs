import requests
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt

# 네이버 API 키
NAVER_CLIENT_ID = 'ehMeVNZQ4tPiZrqNxnzi'
NAVER_CLIENT_SECRET = 'k3HrwuBrmV'

# YouTube API 키
YOUTUBE_API_KEY = 'AIzaSyDe0FYArq5BSyYz5Hz9Q9sPterrMyHPK3w'


@csrf_exempt
@require_http_methods(["GET"])
def search_blog(request):
    """네이버 블로그 검색 API 프록시"""
    query = request.GET.get('query', '')
    display = request.GET.get('display', '10')

    if not query:
        return JsonResponse({'error': 'query parameter is required'}, status=400)

    url = 'https://openapi.naver.com/v1/search/blog.json'
    headers = {
        'X-Naver-Client-Id': NAVER_CLIENT_ID,
        'X-Naver-Client-Secret': NAVER_CLIENT_SECRET,
    }
    params = {
        'query': query,
        'display': display,
        'sort': 'sim'  # 정확도순
    }

    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        return JsonResponse(response.json(), safe=False)
    except requests.exceptions.RequestException as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def search_news(request):
    """네이버 뉴스 검색 API 프록시"""
    query = request.GET.get('query', '')
    display = request.GET.get('display', '10')

    if not query:
        return JsonResponse({'error': 'query parameter is required'}, status=400)

    url = 'https://openapi.naver.com/v1/search/news.json'
    headers = {
        'X-Naver-Client-Id': NAVER_CLIENT_ID,
        'X-Naver-Client-Secret': NAVER_CLIENT_SECRET,
    }
    params = {
        'query': query,
        'display': display,
        'sort': 'sim'  # 정확도순
    }

    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        return JsonResponse(response.json(), safe=False)
    except requests.exceptions.RequestException as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def search_youtube(request):
    """유튜브 검색 API 프록시"""
    query = request.GET.get('query', '')
    max_results = request.GET.get('maxResults', '12')

    if not query:
        return JsonResponse({'error': 'query parameter is required'}, status=400)

    url = 'https://www.googleapis.com/youtube/v3/search'
    params = {
        'key': YOUTUBE_API_KEY,
        'q': query,
        'part': 'snippet',
        'type': 'video',
        'maxResults': max_results,
        'order': 'relevance',
        'regionCode': 'KR',
        'relevanceLanguage': 'ko'
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return JsonResponse(response.json(), safe=False)
    except requests.exceptions.RequestException as e:
        return JsonResponse({'error': str(e)}, status=500)
