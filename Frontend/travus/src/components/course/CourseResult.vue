<template>
  <div class="course-result">
    <!-- 레퍼런스 그대로: 좌우 분할 레이아웃 (좌측 25~30%, 우측 70~75%) -->
    <div class="result-layout">

      <!-- 좌측 사이드바 - 레퍼런스 그대로 구현 -->
      <aside class="sidebar">
        <!-- 헤더 -->
        <div class="sidebar-header">
          <button class="btn-back" @click="emit('restart')">
            <i class="fa fa-arrow-left"></i>
          </button>
          <h1 class="planner-title">{{ courseData.title || 'AI코스 플래너' }}</h1>
          <div class="header-actions">
            <button
              class="btn-icon like-btn"
              :class="{ liked: isLiked }"
              @click="toggleLike"
              :disabled="!savedCourseId"
            >
              <i class="fa fa-thumbs-up"></i>
              <span class="like-count" v-if="likeCount > 0">{{ likeCount }}</span>
            </button>
            <button class="btn-icon" @click="showShareModal = true">
              <i class="fa fa-share-alt"></i>
            </button>
          </div>
        </div>

        <!-- 탭 메뉴 -->
        <div class="tab-menu">
          <button
            class="tab-item"
            :class="{ active: activeTab === 'schedule' }"
            @click="activeTab = 'schedule'"
          >
            여행 일정
          </button>
          <button
            class="tab-item"
            :class="{ active: activeTab === 'comments' }"
            @click="activeTab = 'comments'"
          >
            여행톡
          </button>
        </div>

        <!-- 여행 일정 탭 콘텐츠 -->
        <div v-if="activeTab === 'schedule'" class="tab-content">
          <!-- 여행 요약 카드 - AI 데이터 기반 -->
          <div class="trip-summary-card">
            <div class="summary-badge">
              <span class="badge-day">{{ courseData.duration?.name || '여행' }}</span>
            </div>
            <div class="summary-info">
              <div class="info-item">
                <span class="info-icon">📍</span>
                <span class="info-text">총 {{ itineraryDays.reduce((sum, day) => sum + day.places.length, 0) }}개 장소</span>
              </div>
              <div class="info-item">
                <span class="info-icon">🗺️</span>
                <span class="info-text">여행지역: {{ courseData.regions?.map(code => regionNameMap[code]).join(', ') }}</span>
              </div>
              <div class="info-item">
                <span class="info-icon">🏷️</span>
                <span class="info-text">{{ courseData.duration?.days || 1 }}일 일정</span>
              </div>
            </div>
            <div class="summary-tags">
              <span class="tag" v-for="theme in courseData.themes" :key="theme">#{{ theme }}</span>
            </div>
          </div>

          <!-- Day 헤더 -->
          <div class="day-header">
            <h3>{{ currentDay === -1 ? '전체 일정' : `Day ${currentDay}` }}</h3>
          </div>

          <!-- 장소 리스트 - 레퍼런스 그대로 (세로 스크롤) -->
          <div class="places-list">
          <div
            v-for="(place, index) in currentDayPlaces"
            :key="index"
            class="place-item"
            @click="focusOnMarker(place)"
          >
            <div class="place-number">{{ index + 1 }}</div>
            <div class="place-thumbnail">
              <img
                :src="getPlaceImage(place)"
                :alt="place.name"
                @error="handleImageError"
              />
            </div>
            <div class="place-content">
              <div class="place-category">{{ place.category || '여행지' }}</div>
              <div class="place-name">{{ place.name }}</div>
              <div class="place-address">{{ place.address || '주소 정보 없음' }}</div>
              <button class="btn-detail" @click.stop="showPlaceDetail(place)">더보기 <i class="fa fa-plus"></i></button>
            </div>
          </div>
        </div>
        </div>

        <!-- 여행톡 탭 콘텐츠 -->
        <div v-if="activeTab === 'comments'" class="tab-content comments-tab">
          <div class="comments-section">
            <h3 class="comments-title">여행톡</h3>
            <p class="comments-desc">이 코스에 대한 의견을 남겨주세요!</p>

            <!-- 댓글 입력 -->
            <div class="comment-input-wrapper">
              <textarea
                v-model="newComment"
                class="comment-input"
                placeholder="댓글을 입력하세요..."
                rows="3"
              ></textarea>
              <button class="btn-comment-submit" @click="submitComment" :disabled="!newComment.trim()">
                등록
              </button>
            </div>

            <!-- 댓글 목록 -->
            <div class="comments-list">
              <div v-if="comments.length === 0" class="no-comments">
                <p>아직 댓글이 없습니다. 첫 댓글을 남겨보세요!</p>
              </div>

              <template v-for="comment in comments" :key="comment?.id || Math.random()">
                <div v-if="comment" class="comment-item">
                  <div class="comment-header">
                    <span class="comment-author">{{ comment.username || '익명' }}</span>
                    <span class="comment-date">{{ comment.created_at ? formatDate(comment.created_at) : '' }}</span>
                  </div>
                  <div class="comment-content">{{ comment.content || '' }}</div>
                  <div class="comment-actions">
                    <button class="btn-comment-action" v-if="isMyComment(comment)" @click="deleteComment(comment.id)">
                      <i class="fa fa-trash"></i> 삭제
                    </button>
                  </div>
                </div>
              </template>
            </div>
          </div>
        </div>
      </aside>

      <!-- 우측 지도 영역 - 레퍼런스 그대로 -->
      <main class="map-area">
        <!-- 카카오맵 -->
        <div id="kakao-map" class="kakao-map"></div>

        <!-- 우측 상단: 날짜 토글 버튼 - 레퍼런스 그대로 위치 -->
        <div class="day-toggle">
          <button
            v-for="(_, index) in itineraryDays"
            :key="index"
            class="day-btn"
            :class="{ active: currentDay === index + 1 }"
            @click="switchDay(index + 1)"
          >
            <span class="day-circle" :class="`day${index + 1}`">{{ index + 1 }}</span>
            <span>{{ index + 1 }}일차</span>
          </button>
          <button
            class="day-btn"
            :class="{ active: currentDay === -1 }"
            @click="switchDay(-1)"
          >
            <span class="day-circle all">전체</span>
            <span>{{ itineraryDays.length }}일차</span>
          </button>
        </div>

        <!-- 우측 하단: 다시뽑기 버튼 - 레퍼런스 그대로 위치 -->
        <div class="map-footer">
          <button class="btn-regenerate" @click="emit('restart')">
            <i class="fa fa-refresh"></i>
            <span>추천코스가 마음에 들지 않나요?</span>
            <strong>다시뽑기</strong>
            <span class="badge-go">GO</span>
          </button>
        </div>
      </main>

      <!-- 네이버 지도 스타일: 상세 정보 패널 (사이드바 옆에 슬라이드) -->
      <div v-if="selectedPlace && showDetailPanel" class="detail-panel-overlay" @click="closeDetailPanel"></div>
      <aside v-if="selectedPlace" class="detail-panel" :class="{ active: showDetailPanel }">
        <div class="detail-panel-inner">
          <!-- 상단: 닫기 버튼 -->
          <div class="detail-header">
            <button class="btn-close-panel" @click="closeDetailPanel">
              <i class="fa fa-times"></i>
            </button>
          </div>

          <!-- 이미지 갤러리 (가로 스크롤) -->
          <div class="detail-image-gallery">
            <div class="gallery-container">
              <img
                :src="getPlaceImage(selectedPlace)"
                :alt="selectedPlace.name"
                class="gallery-image"
                @error="handleImageError"
              />
              <!-- 추가 이미지가 있다면 여기에 -->
            </div>
          </div>

          <!-- 장소 기본 정보 -->
          <div class="detail-content">
            <!-- 장소명 (클릭 시 상세 페이지로 이동) -->
            <h2 class="detail-title clickable" @click="goToSpotDetail(selectedPlace)">
              {{ selectedPlace.name }}
            </h2>

            <!-- 카테고리 / 태그 -->
            <div class="detail-category">
              <span class="category-badge">{{ selectedPlace.category || '여행지' }}</span>
            </div>

            <!-- 주소 -->
            <div class="detail-info-row" v-if="selectedPlace.address">
              <div class="info-label">
                <i class="fa fa-map-marker"></i>
                <span>주소</span>
              </div>
              <div class="info-value">{{ selectedPlace.address }}</div>
            </div>

            <!-- 전화번호 (있다면) -->
            <div class="detail-info-row" v-if="selectedPlace.phone">
              <div class="info-label">
                <i class="fa fa-phone"></i>
                <span>전화번호</span>
              </div>
              <div class="info-value">{{ selectedPlace.phone }}</div>
            </div>

            <!-- 구분선 -->
            <div class="divider"></div>

            <!-- 방문 후기 섹션 (향후 구현) -->
            <div class="detail-reviews">
              <h3 class="reviews-title">방문 후기</h3>
              <p class="no-reviews">아직 등록된 후기가 없습니다.</p>
            </div>
          </div>
        </div>
      </aside>

      <!-- 공유 모달 -->
      <div v-if="showShareModal" class="modal-overlay" @click="showShareModal = false">
        <div class="modal-content share-modal" @click.stop>
          <div class="modal-header">
            <h3>코스 공유하기</h3>
            <button class="btn-close-modal" @click="showShareModal = false">
              <i class="fa fa-times"></i>
            </button>
          </div>
          <div class="modal-body">
            <p class="share-desc">아래 링크를 복사하여 공유하세요</p>
            <div class="url-input-wrapper">
              <input
                ref="urlInput"
                type="text"
                :value="shareUrl"
                readonly
                class="url-input"
              />
              <button class="btn-copy" @click="copyUrl">
                <i class="fa" :class="urlCopied ? 'fa-check' : 'fa-copy'"></i>
                {{ urlCopied ? '복사됨' : '복사' }}
              </button>
            </div>
          </div>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/services/api'

const router = useRouter()

const props = defineProps({
  courseData: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['restart'])

// 지역 코드 → 이름 매핑
const regionNameMap = {
  '1': '서울',
  '2': '인천',
  '3': '대전',
  '4': '대구',
  '5': '광주',
  '6': '부산',
  '7': '울산',
  '8': '세종',
  '31': '경기',
  '32': '강원',
  '33': '충북',
  '34': '충남',
  '35': '경북',
  '36': '경남',
  '37': '전북',
  '38': '전남',
  '39': '제주'
}

// 상태 관리
const itineraryDays = ref([])
const currentDay = ref(1) // 현재 보고 있는 날짜 (1: Day1, 2: Day2, -1: 전체)
const kakaoMap = ref(null)
const markers = ref([])
const polylines = ref([])
const isLoading = ref(true)
const selectedPlace = ref(null) // 상세보기 선택된 장소
const showDetailPanel = ref(false) // 상세보기 패널 표시 여부

// 탭 및 댓글 관리
const activeTab = ref('schedule') // 'schedule' or 'comments'
const comments = ref([])
const newComment = ref('')
const currentUser = ref(null)

// 자동 저장 관리
const savedCourseId = ref(null) // 저장된 코스 ID
const isAutoSaving = ref(false)

// 좋아요 관리
const isLiked = ref(false)
const likeCount = ref(0)

// 공유 모달 관리
const showShareModal = ref(false)
const urlCopied = ref(false)
const urlInput = ref(null)

// 공유 URL 계산
const shareUrl = computed(() => {
  if (!savedCourseId.value) return window.location.href
  return `${window.location.origin}/course/${savedCourseId.value}`
})

// 현재 날짜의 장소들
const currentDayPlaces = computed(() => {
  let places = []

  if (currentDay.value === -1) {
    // 전체 보기
    places = itineraryDays.value.flatMap(day => day.places)
  } else {
    // 특정 날짜 보기 (1-based index로 변경)
    const dayIndex = currentDay.value - 1
    places = itineraryDays.value[dayIndex]?.places || []
  }

  // 숙박 필터링: 각 day의 첫 번째 장소가 숙박이면 제거
  // (숙박은 전날 마지막 코스로만 표시되어야 함)
  if (currentDay.value !== -1) {
    // 개별 day 보기일 때만 필터링
    const filtered = places.filter((place, index) => {
      // 첫 번째 항목이고 type이 'accommodation'이면 제외
      if (index === 0 && place.type === 'accommodation') {
        return false
      }
      return true
    })
    return filtered
  }

  return places
})

// 이미지 에러 핸들링
const handleImageError = (e) => {
  e.target.src = 'https://via.placeholder.com/80x80?text=No+Image'
}

// 장소 이미지 가져오기
const getPlaceImage = (place) => {
  if (place.image_url) return place.image_url
  if (place.first_image) return place.first_image
  return 'https://via.placeholder.com/80x80?text=No+Image'
}

// 날짜 전환
const switchDay = (dayIndex) => {
  currentDay.value = dayIndex
  updateMapMarkers()
}

// 카카오맵 SDK 로드
const loadKakaoMapScript = () => {
  return new Promise((resolve, reject) => {
    // 이미 로드되어 있으면 바로 리턴
    if (window.kakao && window.kakao.maps) {
      resolve()
      return
    }

    const apiKey = import.meta.env.VITE_KAKAO_MAP_API_KEY

    // 기존 스크립트 확인
    const existingScript = document.querySelector('script[src*="dapi.kakao.com"]')
    if (existingScript) {
      existingScript.remove()
    }

    const script = document.createElement('script')
    script.type = 'text/javascript'
    script.src = `//dapi.kakao.com/v2/maps/sdk.js?appkey=${apiKey}&autoload=false`

    script.onload = () => {
      if (window.kakao && window.kakao.maps) {
        window.kakao.maps.load(() => {
          resolve()
        })
      } else {
        console.error('❌ window.kakao.maps가 없음')
        reject(new Error('Kakao maps API not available'))
      }
    }

    script.onerror = (error) => {
      console.error('❌ 카카오맵 스크립트 로드 실패:', error)
      reject(error)
    }

    document.head.appendChild(script)
  })
}

// 카카오맵 초기화
const initializeKakaoMap = () => {
  const container = document.getElementById('kakao-map')
  if (!container) {
    console.error('❌ 카카오맵 컨테이너를 찾을 수 없습니다')
    return
  }


  const options = {
    center: new window.kakao.maps.LatLng(37.5665, 126.9780), // 서울시청
    level: 3 // 확대 레벨 (숫자가 작을수록 확대)
  }

  kakaoMap.value = new window.kakao.maps.Map(container, options)

  // 기본 마커 하나 추가 (테스트용)
  const markerPosition = new window.kakao.maps.LatLng(37.5665, 126.9780)
  const marker = new window.kakao.maps.Marker({
    position: markerPosition
  })
  marker.setMap(kakaoMap.value)
}

// 마커 색상 매핑
const getMarkerColor = (dayIndex) => {
  const colors = ['#4A90E2', '#34C759', '#FF9500']
  return colors[dayIndex] || '#4A90E2'
}

// 지도에 마커 및 경로 추가
const updateMapMarkers = () => {

  if (!kakaoMap.value || !itineraryDays.value.length) {
    console.warn('⚠️ 지도 또는 itineraryDays가 없음')
    return
  }

  // 기존 마커 및 폴리라인 제거
  markers.value.forEach(marker => marker.setMap(null))
  polylines.value.forEach(line => line.setMap(null))
  markers.value = []
  polylines.value = []

  const bounds = new window.kakao.maps.LatLngBounds()
  const linePath = []

  // 보여줄 날짜 결정 (1-based index로 변경)
  const daysToShow = currentDay.value === -1
    ? itineraryDays.value
    : [itineraryDays.value[currentDay.value - 1]]


  let globalIndex = 0

  daysToShow.forEach((day, dayIndex) => {
    const actualDayIndex = currentDay.value === -1 ? dayIndex : (currentDay.value - 1)


    day.places.forEach((place, placeIndex) => {

      if (!place.latitude || !place.longitude) {
        console.warn(`  ⚠️ ${place.name}: 좌표 없음`)
        return
      }

      const position = new window.kakao.maps.LatLng(
        parseFloat(place.latitude),
        parseFloat(place.longitude)
      )

      // 마커 번호 (전체 보기일 때는 연속 번호, 개별 보기일 때는 1부터)
      const markerNumber = currentDay.value === -1 ? globalIndex + 1 : placeIndex + 1
      globalIndex++

      // 커스텀 마커 생성 - 레퍼런스 스타일 그대로
      const markerContent = `
        <div style="
          width: 40px;
          height: 40px;
          background: ${getMarkerColor(actualDayIndex)};
          border: 3px solid white;
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          color: white;
          font-weight: 700;
          font-size: 16px;
          box-shadow: 0 2px 6px rgba(0,0,0,0.3);
          cursor: pointer;
        ">
          ${markerNumber}
        </div>
      `

      const customOverlay = new window.kakao.maps.CustomOverlay({
        position: position,
        content: markerContent,
        yAnchor: 0.5
      })

      customOverlay.setMap(kakaoMap.value)
      markers.value.push(customOverlay)
      bounds.extend(position)
      linePath.push(position)

      // 장소 객체에 위치 정보 저장
      place._position = position
    })

    // 경로선 그리기 (각 날짜별로 다른 색상)
    if (linePath.length > 1) {
      const polyline = new window.kakao.maps.Polyline({
        path: linePath,
        strokeWeight: 4,
        strokeColor: getMarkerColor(actualDayIndex),
        strokeOpacity: 0.7,
        strokeStyle: 'solid'
      })

      polyline.setMap(kakaoMap.value)
      polylines.value.push(polyline)
    }
  })

  // 모든 마커가 보이도록 지도 범위 조정
  if (markers.value.length > 0) {
    kakaoMap.value.setBounds(bounds)
  }
}

// 특정 마커에 포커스
const focusOnMarker = (place) => {
  if (!kakaoMap.value || !place._position) return

  kakaoMap.value.setCenter(place._position)
  kakaoMap.value.setLevel(3)
}

// 장소 상세보기 패널 열기
const showPlaceDetail = (place) => {
  selectedPlace.value = place
  showDetailPanel.value = true
}

// 장소 상세보기 패널 닫기
const closeDetailPanel = () => {
  showDetailPanel.value = false
  selectedPlace.value = null
}

// 장소 상세 페이지로 이동
const goToSpotDetail = (place) => {
  if (!place.id) return

  // TravelDetail 페이지로 이동 (spot ID + contentTypeId 쿼리 파라미터 전달)
  router.push({
    name: 'travel-detail',
    params: { id: place.id },
    query: { contentTypeId: place.content_type_id }
  })
}

// 댓글 관련 함수
const loadComments = async () => {
  try {
    // savedCourseId 사용 (자동 저장된 코스 ID)
    if (!savedCourseId.value) {
      return
    }

    const response = await api.getCourseComments(savedCourseId.value)

    // 응답이 배열인지 확인
    if (Array.isArray(response.data)) {
      comments.value = response.data
    } else if (response.data.results && Array.isArray(response.data.results)) {
      // 페이지네이션된 응답인 경우
      comments.value = response.data.results
    } else {
      console.warn('⚠️ 예상치 못한 댓글 응답 형식:', response.data)
      comments.value = []
    }

  } catch (error) {
    console.error('❌ 댓글 로드 실패:', error)
    comments.value = []
  }
}

const submitComment = async () => {
  if (!newComment.value.trim()) return

  // 코스가 저장되지 않았으면 저장 먼저 수행
  if (!savedCourseId.value) {
    alert('코스를 먼저 저장하고 있습니다. 잠시만 기다려주세요.')
    return
  }

  try {
    await api.createCourseComment(savedCourseId.value, {
      content: newComment.value
    })

    newComment.value = ''
    await loadComments()
  } catch (error) {
    console.error('댓글 작성 실패:', error)
    if (error.response?.status === 401) {
      alert('로그인이 필요합니다.')
    } else {
      alert('댓글 작성에 실패했습니다.')
    }
  }
}

const deleteComment = async (commentId) => {
  if (!confirm('댓글을 삭제하시겠습니까?')) return

  try {
    await api.deleteCourseComment(commentId)
    await loadComments()
  } catch (error) {
    console.error('댓글 삭제 실패:', error)
    alert('댓글 삭제에 실패했습니다.')
  }
}

const isMyComment = (comment) => {
  return currentUser.value && comment && comment.user === currentUser.value.id
}

const formatDate = (dateString) => {
  const date = new Date(dateString)
  const now = new Date()
  const diffMs = now - date
  const diffMins = Math.floor(diffMs / 60000)
  const diffHours = Math.floor(diffMs / 3600000)
  const diffDays = Math.floor(diffMs / 86400000)

  if (diffMins < 1) return '방금 전'
  if (diffMins < 60) return `${diffMins}분 전`
  if (diffHours < 24) return `${diffHours}시간 전`
  if (diffDays < 7) return `${diffDays}일 전`

  return date.toLocaleDateString('ko-KR')
}

// 자동 저장 함수
const autoSaveCourse = async () => {
  // 이미 저장된 코스 조회인 경우 (courseData.id가 있으면 조회 모드)
  if (props.courseData.id) {
    savedCourseId.value = props.courseData.id
    // 기존 코스의 좋아요 상태만 로드
    await loadLikeStatus()
    return
  }

  // 이미 저장 중이거나 저장된 경우
  if (isAutoSaving.value || savedCourseId.value) return

  try {
    isAutoSaving.value = true

    // 저장할 데이터 준비 - spots 데이터 포함
    const spots = []

    // rawItinerary에서 spots 데이터 추출
    if (props.courseData.rawItinerary) {
      props.courseData.rawItinerary.forEach((item, index) => {
        spots.push({
          travel_spot_id: item.id,
          order: item.order || index + 1,
          day: item.day || 1,
          type: item.type || 'travel',
          memo: '',
          stay_duration: null
        })
      })
    }

    const courseData = {
      title: props.courseData.title,
      description: props.courseData.description || '',
      is_public: false, // 기본값: 비공개
      spots: spots
    }


    // Course 저장
    const courseResponse = await api.saveCourse(courseData)
    const savedCourse = courseResponse.data

    savedCourseId.value = savedCourse.id

    // 저장 후 좋아요 상태 로드
    await loadLikeStatus()

  } catch (error) {
    console.error('코스 자동 저장 실패:', error)
    console.error('에러 상세:', error.response?.data)

    if (error.response?.status === 401) {
    }
  } finally {
    isAutoSaving.value = false
  }
}

// 좋아요 토글
const toggleLike = async () => {
  if (!savedCourseId.value) {
    alert('코스를 먼저 저장해주세요.')
    return
  }

  try {
    const response = await api.toggleCourseLike(savedCourseId.value)
    isLiked.value = response.data.is_liked
    likeCount.value = response.data.like_count
  } catch (error) {
    console.error('좋아요 토글 실패:', error)
    if (error.response?.status === 401) {
      alert('로그인이 필요합니다.')
    } else {
      alert('좋아요 처리에 실패했습니다.')
    }
  }
}

// 좋아요 상태 로드
const loadLikeStatus = async () => {
  if (!savedCourseId.value) return

  try {
    const response = await api.getCourseLikeStatus(savedCourseId.value)
    isLiked.value = response.data.liked
    likeCount.value = response.data.like_count
  } catch (error) {
    console.error('좋아요 상태 로드 실패:', error)
  }
}

// URL 복사
const copyUrl = async () => {
  try {
    await navigator.clipboard.writeText(shareUrl.value)
    urlCopied.value = true
    setTimeout(() => {
      urlCopied.value = false
    }, 2000)
  } catch (error) {
    console.error('URL 복사 실패:', error)
    // 폴백: input 선택 후 복사
    if (urlInput.value) {
      urlInput.value.select()
      document.execCommand('copy')
      urlCopied.value = true
      setTimeout(() => {
        urlCopied.value = false
      }, 2000)
    }
  }
}

// AI 생성 데이터를 itineraryDays 형식으로 변환
const loadAIGeneratedData = () => {
  try {
    isLoading.value = true


    // props.courseData.days 사용 (AI가 생성한 데이터 또는 조회한 데이터)
    if (props.courseData.days && props.courseData.days.length > 0) {
      itineraryDays.value = props.courseData.days.map(dayData => ({
        date: `Day ${dayData.day}`,
        places: dayData.spots.map(spot => {
          // spot.spot 또는 spot 자체가 여행지 데이터
          const spotData = spot.spot || spot

          // 디버깅: 실제 spotData 구조 확인

          // 좌표 필드명 확인 (latitude/longitude 또는 mapy/mapx)
          const lat = spotData.latitude || spotData.mapy
          const lng = spotData.longitude || spotData.mapx


          return {
            id: spotData.id, // TravelSpot의 실제 DB ID
            content_type_id: spotData.content_type_id, // 콘텐츠 타입 ID 추가
            name: spotData.name,
            address: spotData.address,
            latitude: parseFloat(lat),
            longitude: parseFloat(lng),
            image_url: spotData.image_url,
            category: getCategoryName(spotData.content_type_id),
            type: spot.type,
            phone: spotData.tel || spotData.phone || null // 전화번호 추가
          }
        })
      }))

    } else {
      console.warn('⚠️ 생성 데이터가 없습니다')
      useSampleData()
    }

  } catch (error) {
    console.error('❌ AI 데이터 로드 실패:', error)
    useSampleData()
  } finally {
    isLoading.value = false
  }
}

// 카테고리 이름 변환
const getCategoryName = (contentTypeId) => {
  const categoryMap = {
    12: '여행지',
    14: '문화시설',
    15: '축제',
    25: '여행코스',
    28: '레포츠',
    32: '숙박',
    38: '쇼핑',
    39: '음식점'
  }
  return categoryMap[contentTypeId] || '여행지'
}

// 샘플 데이터
const useSampleData = () => {
  const days = props.courseData.duration?.days || 1
  const tempDays = []

  for (let i = 0; i < days; i++) {
    tempDays.push({
      date: `Day ${i + 1}`,
      places: [
        {
          id: i * 10 + 1,
          name: '아르떼뮤지엄',
          address: '대구광역시 수성구 무학로 42',
          latitude: 35.8714 + (i * 0.01),
          longitude: 128.6014 + (i * 0.01),
          category: '여행지',
          image_url: null
        },
        {
          id: i * 10 + 2,
          name: '라벨라쿠치나',
          address: '대구광역시 수성구 무학로 151',
          latitude: 35.8714 + (i * 0.01) + 0.005,
          longitude: 128.6014 + (i * 0.01) + 0.005,
          category: '음식점',
          image_url: null
        }
      ]
    })
  }

  itineraryDays.value = tempDays
}

// 초기화
onMounted(async () => {
  try {

    await loadKakaoMapScript()

    initializeKakaoMap()

    loadAIGeneratedData()

    updateMapMarkers()

    // 사용자 정보 로드
    try {
      const userResponse = await api.getCurrentUser()
      currentUser.value = userResponse.data
    } catch (error) {
    }

    // 자동 저장 (코스 생성 시 자동으로 저장)
    await autoSaveCourse()

    // 댓글 로드 (autoSaveCourse 이후에 실행해야 savedCourseId가 설정됨)
    await loadComments()

  } catch (error) {
    console.error('❌ 초기화 실패:', error)
    console.error('❌ 에러 상세:', error.message, error.stack)
  }
})

// 날짜 변경 감지
watch(currentDay, () => {
  updateMapMarkers()
})
</script>

<style scoped>
/* 레퍼런스 그대로: 전체 레이아웃 */
.course-result {
  width: 100%;
  height: 100vh;
  overflow: hidden;
  background: #f5f5f5;
}

.result-layout {
  display: flex;
  height: 100%;
}

/* 레퍼런스 그대로: 좌측 사이드바 (25~30%) */
.sidebar {
  width: 380px;
  height: 100%;
  background: white;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  border-right: 1px solid #e0e0e0;
}

/* 사이드바 헤더 */
.sidebar-header {
  display: flex;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid #e0e0e0;
  gap: 12px;
}

.btn-back {
  background: none;
  border: none;
  font-size: 18px;
  color: #333;
  cursor: pointer;
  padding: 4px;
}

.planner-title {
  font-size: 18px;
  font-weight: 700;
  color: #000;
  margin: 0;
  flex: 1;
}

.header-actions {
  display: flex;
  gap: 8px;
}

.btn-icon {
  background: none;
  border: none;
  font-size: 16px;
  color: #666;
  cursor: pointer;
  padding: 4px 8px;
  transition: all 0.2s;
  position: relative;
}

.btn-icon:hover {
  color: #00C73C;
}

.btn-icon:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* 좋아요 버튼 */
.like-btn {
  display: flex;
  align-items: center;
  gap: 4px;
}

.like-btn.liked {
  color: #00C73C;
}

.like-btn.liked i {
  animation: likeAnimation 0.3s ease;
}

@keyframes likeAnimation {
  0% { transform: scale(1); }
  50% { transform: scale(1.3); }
  100% { transform: scale(1); }
}

.like-count {
  font-size: 12px;
  font-weight: 600;
  color: inherit;
}

/* 탭 메뉴 - 레퍼런스 그대로 */
.tab-menu {
  display: flex;
  border-bottom: 1px solid #e0e0e0;
}

.tab-item {
  flex: 1;
  padding: 12px 8px;
  background: none;
  border: none;
  font-size: 14px;
  color: #666;
  cursor: pointer;
  border-bottom: 2px solid transparent;
  transition: all 0.2s;
}

.tab-item.active {
  color: #00C73C;
  border-bottom-color: #00C73C;
  font-weight: 600;
}

/* 여행 요약 카드 - 레퍼런스 그대로 */
.trip-summary-card {
  margin: 16px;
  padding: 16px;
  background: #E8F5F1;
  border-radius: 8px;
}

.summary-badge {
  margin-bottom: 12px;
}

.badge-day {
  display: inline-block;
  padding: 4px 12px;
  background: #00C73C;
  color: white;
  border-radius: 12px;
  font-size: 13px;
  font-weight: 600;
}

.summary-info {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 12px;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: #333;
}

.info-icon {
  font-size: 14px;
}

.summary-tags {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.tag {
  padding: 4px 10px;
  background: white;
  border-radius: 12px;
  font-size: 12px;
  color: #00C73C;
}

/* 평점 섹션 */
.rating-section {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  border-bottom: 1px solid #f0f0f0;
}

.rating-label {
  font-size: 13px;
  color: #666;
}

.stars {
  display: flex;
  gap: 4px;
}

.stars i {
  font-size: 16px;
  color: #ddd;
  cursor: pointer;
}

/* Day 헤더 */
.day-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px;
  background: white;
}

.day-header h3 {
  font-size: 16px;
  font-weight: 700;
  color: #000;
  margin: 0;
}

.btn-expand {
  display: flex;
  align-items: center;
  gap: 6px;
  background: none;
  border: none;
  font-size: 13px;
  color: #666;
  cursor: pointer;
}

/* 장소 리스트 - 레퍼런스 그대로 (세로 스크롤) */
.places-list {
  flex: 1;
  overflow-y: auto;
  padding: 0 16px 16px;
}

.places-list::-webkit-scrollbar {
  width: 6px;
}

.places-list::-webkit-scrollbar-thumb {
  background: #ddd;
  border-radius: 3px;
}

.place-item {
  display: flex;
  gap: 12px;
  padding: 16px 0;
  border-bottom: 1px solid #f0f0f0;
  cursor: pointer;
  transition: background 0.2s;
}

.place-item:hover {
  background: #f9f9f9;
}

.place-number {
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #4A90E2;
  color: white;
  border-radius: 50%;
  font-size: 14px;
  font-weight: 700;
  flex-shrink: 0;
}

.place-thumbnail {
  width: 80px;
  height: 80px;
  flex-shrink: 0;
  border-radius: 8px;
  overflow: hidden;
  background: #f0f0f0;
}

.place-thumbnail img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.place-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.place-category {
  display: inline-block;
  padding: 2px 8px;
  background: #00C73C;
  color: white;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 600;
  align-self: flex-start;
}

.place-name {
  font-size: 15px;
  font-weight: 600;
  color: #000;
  margin-top: 4px;
}

.place-address {
  font-size: 12px;
  color: #888;
  line-height: 1.4;
}

.btn-detail {
  align-self: flex-start;
  margin-top: 4px;
  padding: 4px 8px;
  background: none;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 11px;
  color: #666;
  cursor: pointer;
}

/* 레퍼런스 그대로: 우측 지도 영역 (70~75%) */
.map-area {
  flex: 1;
  position: relative;
  height: 100%;
}

.kakao-map {
  width: 100%;
  height: 100%;
}

/* 우측 상단: 날짜 토글 - 레퍼런스 그대로 위치 */
.day-toggle {
  position: absolute;
  top: 20px;
  right: 20px;
  display: flex;
  gap: 8px;
  z-index: 10;
}

.day-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  background: white;
  border: 2px solid #e0e0e0;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 600;
  color: #666;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: 0 2px 6px rgba(0,0,0,0.1);
}

.day-btn.active {
  background: #4A90E2;
  color: white;
  border-color: #4A90E2;
}

.day-circle {
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #4A90E2;
  color: white;
  border-radius: 50%;
  font-size: 12px;
  font-weight: 700;
}

.day-circle.day2 {
  background: #34C759;
}

.day-circle.day3 {
  background: #FF9500;
}

.day-circle.all {
  background: #666;
}

.day-btn.active .day-circle {
  background: white;
  color: #4A90E2;
}

/* 우측 하단: 다시뽑기 버튼 - 레퍼런스 그대로 위치 */
.map-footer {
  position: absolute;
  bottom: 20px;
  right: 20px;
  z-index: 10;
}

.btn-regenerate {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 20px;
  background: white;
  border: 2px solid #00C73C;
  border-radius: 24px;
  font-size: 13px;
  color: #333;
  cursor: pointer;
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
  transition: all 0.2s;
}

.btn-regenerate:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(0,0,0,0.2);
}

.btn-regenerate i {
  color: #00C73C;
}

.btn-regenerate strong {
  color: #00C73C;
  font-weight: 700;
}

.badge-go {
  padding: 2px 8px;
  background: #00C73C;
  color: white;
  border-radius: 8px;
  font-size: 11px;
  font-weight: 700;
}

/* 네이버 지도 스타일: 상세 정보 패널 오버레이 */
.detail-panel-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: transparent;
  z-index: 14;
  cursor: default;
}

/* 네이버 지도 스타일: 상세 정보 패널 */
.detail-panel {
  position: absolute;
  top: 20px; /* 상단 여백 */
  left: 400px; /* 사이드바 + 여백 */
  width: 420px;
  height: calc(100% - 40px); /* 상하 여백 */
  background: white;
  box-shadow: 0 2px 12px rgba(0,0,0,0.15);
  border-radius: 16px;
  transform: translateX(-100%);
  transition: transform 0.3s ease-in-out;
  z-index: 15;
  overflow: hidden;
}

.detail-panel.active {
  transform: translateX(0);
}

.detail-panel-inner {
  height: 100%;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
}

/* 상단 헤더 */
.detail-header {
  position: absolute;
  top: 16px;
  right: 16px;
  z-index: 20;
}

.btn-close-panel {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.9);
  border: none;
  border-radius: 50%;
  font-size: 18px;
  color: #333;
  cursor: pointer;
  box-shadow: 0 2px 8px rgba(0,0,0,0.15);
  transition: all 0.2s;
}

.btn-close-panel:hover {
  background: white;
  color: #000;
}

/* 이미지 갤러리 */
.detail-image-gallery {
  width: 100%;
  background: #f5f5f5;
  position: relative;
}

.gallery-container {
  display: flex;
  overflow-x: auto;
  scroll-snap-type: x mandatory;
  -webkit-overflow-scrolling: touch;
}

.gallery-container::-webkit-scrollbar {
  height: 8px;
}

.gallery-container::-webkit-scrollbar-thumb {
  background: #ddd;
  border-radius: 4px;
}

.gallery-image {
  width: 100%;
  height: 280px;
  object-fit: cover;
  flex-shrink: 0;
  scroll-snap-align: start;
}

/* 상세 콘텐츠 */
.detail-content {
  padding: 24px;
  flex: 1;
}

/* 장소명 */
.detail-title {
  font-size: 24px;
  font-weight: 700;
  color: #000;
  margin: 0 0 12px 0;
  line-height: 1.4;
}

.detail-title.clickable {
  cursor: pointer;
  transition: color 0.2s;
}

.detail-title.clickable:hover {
  color: #00C73C;
}

/* 카테고리 */
.detail-category {
  margin-bottom: 20px;
}

.category-badge {
  display: inline-block;
  padding: 6px 14px;
  background: #00C73C;
  color: white;
  border-radius: 4px;
  font-size: 13px;
  font-weight: 600;
}

/* 정보 행 */
.detail-info-row {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 16px 0;
  border-bottom: 1px solid #f0f0f0;
}

.detail-info-row .info-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 600;
  color: #666;
}

.detail-info-row .info-label i {
  font-size: 16px;
  color: #00C73C;
  width: 20px;
}

.detail-info-row .info-value {
  font-size: 15px;
  color: #333;
  line-height: 1.6;
  padding-left: 28px;
}

/* 구분선 */
.divider {
  height: 8px;
  background: #f5f5f5;
  margin: 24px -24px;
}

/* 후기 섹션 */
.detail-reviews {
  padding-top: 24px;
}

.reviews-title {
  font-size: 18px;
  font-weight: 700;
  color: #000;
  margin: 0 0 16px 0;
}

.no-reviews {
  font-size: 14px;
  color: #999;
  text-align: center;
  padding: 40px 20px;
  margin: 0;
}

/* 탭 콘텐츠 */
.tab-content {
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
}

/* 여행톡 탭 */
.comments-tab {
  padding: 16px;
}

.comments-section {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.comments-title {
  font-size: 18px;
  font-weight: 700;
  color: #000;
  margin: 0;
}

.comments-desc {
  font-size: 14px;
  color: #666;
  margin: 0;
}

/* 댓글 입력 */
.comment-input-wrapper {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 16px;
  background: #f9f9f9;
  border-radius: 8px;
}

.comment-input {
  width: 100%;
  padding: 12px;
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  font-size: 14px;
  resize: vertical;
  font-family: inherit;
}

.comment-input:focus {
  outline: none;
  border-color: #00C73C;
}

.btn-comment-submit {
  align-self: flex-end;
  padding: 8px 24px;
  background: #00C73C;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s;
}

.btn-comment-submit:hover:not(:disabled) {
  background: #00b035;
}

.btn-comment-submit:disabled {
  background: #ccc;
  cursor: not-allowed;
}

/* 댓글 목록 */
.comments-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.no-comments {
  text-align: center;
  padding: 40px 20px;
  color: #999;
  font-size: 14px;
}

.no-comments p {
  margin: 0;
}

/* 댓글 아이템 */
.comment-item {
  padding: 16px;
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
}

.comment-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.comment-author {
  font-size: 14px;
  font-weight: 600;
  color: #333;
}

.comment-date {
  font-size: 12px;
  color: #999;
}

.comment-content {
  font-size: 14px;
  color: #333;
  line-height: 1.6;
  white-space: pre-wrap;
  margin-bottom: 8px;
}

.comment-actions {
  display: flex;
  gap: 8px;
}

.btn-comment-action {
  background: none;
  border: none;
  color: #999;
  font-size: 12px;
  cursor: pointer;
  padding: 4px 8px;
  transition: color 0.2s;
}

.btn-comment-action:hover {
  color: #ff4444;
}

/* 공유 모달 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  animation: fadeIn 0.2s ease;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.modal-content {
  background: white;
  border-radius: 16px;
  width: 90%;
  max-width: 500px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
  animation: slideUp 0.3s ease;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid #e0e0e0;
}

.modal-header h3 {
  font-size: 20px;
  font-weight: 700;
  color: #000;
  margin: 0;
}

.btn-close-modal {
  background: none;
  border: none;
  font-size: 20px;
  color: #666;
  cursor: pointer;
  padding: 4px;
  transition: color 0.2s;
}

.btn-close-modal:hover {
  color: #000;
}

.modal-body {
  padding: 24px;
}

.share-desc {
  font-size: 14px;
  color: #666;
  margin: 0 0 16px 0;
}

.url-input-wrapper {
  display: flex;
  gap: 8px;
}

.url-input {
  flex: 1;
  padding: 12px 16px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  font-size: 14px;
  color: #333;
  background: #f9f9f9;
}

.url-input:focus {
  outline: none;
  border-color: #00C73C;
  background: white;
}

.btn-copy {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 12px 20px;
  background: #00C73C;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
}

.btn-copy:hover {
  background: #00b035;
  transform: translateY(-1px);
}

.btn-copy i {
  font-size: 14px;
}

/* 반응형 - 레퍼런스는 데스크톱 기준이므로 모바일은 최소한만 */
@media (max-width: 768px) {
  .sidebar {
    width: 100%;
    position: absolute;
    z-index: 20;
    max-height: 50vh;
  }

  .map-area {
    width: 100%;
  }

  .detail-panel {
    left: 0;
    width: 100%;
  }

  .modal-content {
    width: 95%;
    margin: 20px;
  }

  .url-input-wrapper {
    flex-direction: column;
  }

  .btn-copy {
    width: 100%;
    justify-content: center;
  }
}
</style>
