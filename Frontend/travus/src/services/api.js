import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api'
const API_ROOT_URL = API_BASE_URL.replace(/\/api\/?$/, '')
const AI_BASE_URL = import.meta.env.VITE_AI_BASE_URL || `${API_ROOT_URL}/ai`

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Attach JWT token when available
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

const aiClient = axios.create({
  baseURL: AI_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error)
    return Promise.reject(error)
  }
)

aiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('AI API Error:', error)
    return Promise.reject(error)
  }
)

export default {
  // Travel spots (DB-backed)
  getTravelSpots(params = {}) {
    return apiClient.get('/travel-spots/', { params })
  },

  getTravelSpotDetail(id) {
    return apiClient.get(`/travel-spots/${id}/`)
  },

  getTravelSpotByContentId(contentId) {
    return apiClient.get('/travel-spots/by_content_id/', {
      params: { content_id: contentId }
    })
  },

  // Public data API proxies
  getTravelSpotsFromAPI(params = {}) {
    return apiClient.get('/travel-spots/from_api/', { params })
  },

  searchTravelSpotsAPI(keyword, params = {}) {
    return apiClient.get('/travel-spots/search_api/', {
      params: { keyword, ...params }
    })
  },

  getTravelSpotDetailCommon(contentId, contentTypeId = null) {
    const params = { content_id: contentId }
    if (contentTypeId) {
      params.content_type_id = contentTypeId
    }
    return apiClient.get('/travel-spots/detail_common/', { params })
  },

  getTravelSpotDetailIntro(contentId, contentTypeId = 12) {
    return apiClient.get('/travel-spots/detail_intro/', {
      params: {
        content_id: contentId,
        content_type_id: contentTypeId
      }
    })
  },

  getTravelSpotDetailInfo(contentId, contentTypeId = 12) {
    return apiClient.get('/travel-spots/detail_info/', {
      params: {
        content_id: contentId,
        content_type_id: contentTypeId
      }
    })
  },

  getTravelSpotDetailImages(contentId) {
    return apiClient.get('/travel-spots/detail_image/', {
      params: { content_id: contentId }
    })
  },

  getTravelSpotDetailWithTour(contentId) {
    return apiClient.get('/travel-spots/detail_with_tour/', {
      params: { content_id: contentId }
    })
  },

  getAreaCodes(areaCode = null) {
    const params = {}
    if (areaCode) params.area_code = areaCode
    return apiClient.get('/travel-spots/area_code/', { params })
  },

  getCategoryCodes(params = {}) {
    return apiClient.get('/travel-spots/category_code/', { params })
  },

  getTravelSpotsByLocation(mapx, mapy, params = {}) {
    return apiClient.get('/travel-spots/location_based/', {
      params: { mapx, mapy, ...params }
    })
  },

  // User features
  getCategories() {
    return apiClient.get('/categories/')
  },

  getBookmarks() {
    return apiClient.get('/bookmarks/')
  },

  createBookmark(data) {
    return apiClient.post('/bookmarks/', data)
  },

  deleteBookmark(id) {
    return apiClient.delete(`/bookmarks/${id}/`)
  },

  // 북마크 토글
  toggleBookmark(travelSpotId) {
    return apiClient.post('/bookmarks/toggle/', {
      travel_spot_id: travelSpotId
    })
  },

  // 북마크 상태 확인
  checkBookmark(travelSpotId) {
    return apiClient.get('/bookmarks/check/', {
      params: { travel_spot_id: travelSpotId }
    })
  },

  // 코스 목록
  getCourses(params = {}) {
    return apiClient.get('/courses/', { params })
  },

  getCourseDetail(id) {
    return apiClient.get(`/courses/${id}/`)
  },

  generateAICourse(data) {
    return apiClient.post('/courses/generate_ai_course/', data, {
      timeout: 60000
    })
  },

  saveCourse(data) {
    return apiClient.post('/courses/', data)
  },

  // 나의 여행코스 조회
  getMyCourses() {
    return apiClient.get('/courses/my_courses/')
  },

  // 월간 Best 30 코스
  getMonthlyBestCourses() {
    return apiClient.get('/courses/monthly_best/')
  },

  // 지역별 사용자 코스
  getCoursesByRegion(areaCode, ordering = 'likes') {
    return apiClient.get('/courses/by_region/', {
      params: {
        area_code: areaCode,
        ordering: ordering
      }
    })
  },

  // 코스 상세 조회
  getCourseDetail(courseId) {
    return apiClient.get(`/courses/${courseId}/`)
  },

  // 코스 좋아요 토글
  toggleCourseLike(courseId) {
    return apiClient.post(`/courses/${courseId}/like/`)
  },

  getCourseLikeStatus(courseId) {
    return apiClient.get(`/courses/${courseId}/like_status/`)
  },

  getReviews(travelSpotId) {
    return apiClient.get('/reviews/', {
      params: { travel_spot: travelSpotId }
    })
  },

  createReview(data) {
    return apiClient.post('/reviews/', data)
  },

  // 리뷰 수정
  updateReview(reviewId, data) {
    return apiClient.patch(`/reviews/${reviewId}/`, data)
  },

  // 리뷰 삭제
  deleteReview(reviewId) {
    return apiClient.delete(`/reviews/${reviewId}/`)
  },

  // AI 리뷰 요약
  getReviewSummary(travelSpotId) {
    return apiClient.get('/reviews/summary/', {
      params: { travel_spot: travelSpotId }
    })
  },

  // 코스 댓글 관련
  getCourseComments(courseId) {
    return apiClient.get(`/courses/${courseId}/comments/`)
  },

  createCourseComment(courseId, data) {
    return apiClient.post(`/courses/${courseId}/comments/`, data)
  },

  deleteCourseComment(commentId) {
    return apiClient.delete(`/comments/${commentId}/`)
  },

  getCurrentUser() {
    return apiClient.get('/auth/me/')
  },

  // AI endpoints
  analyzeImage(formData) {
    return aiClient.post('/image/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },

  chatAI(data) {
    return aiClient.post('/chat/', data)
  },

  transcribeAudio(formData) {
    return aiClient.post('/speech/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  }
}
