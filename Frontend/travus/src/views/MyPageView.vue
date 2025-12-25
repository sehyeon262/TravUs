<template>
  <div class="mypage-view">
    <NavigationBar
      :is-t-t-s-enabled="isTTSEnabled"
      @toggle-tts="toggleTTS"
      @focus="handleFocus"
    />

    <div class="mypage-container">
      <!-- 왼쪽 사이드바 - 개인정보 -->
      <aside class="sidebar">
        <div class="profile-section">
          <div class="profile-avatar">
            <img src="@/assets/topbtn.png" alt="프로필" />
          </div>
          <h2 class="profile-name">{{ displayName }}</h2>
          <p class="profile-username">@{{ user?.username }}</p>
        </div>

        <div class="info-section">
          <div class="info-item">
            <span class="info-label">이메일</span>
            <span class="info-value">{{ user?.email || '미등록' }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">전화번호</span>
            <span class="info-value">{{ user?.phone || '미등록' }}</span>
          </div>
        </div>

        <div class="sidebar-footer">
          <button class="withdraw-link" @click="handleWithdraw" @focus="handleFocus">
            회원 탈퇴
          </button>
        </div>
      </aside>

      <!-- 오른쪽 컨텐츠 영역 -->
      <main class="content-area">
        <!-- 탭 메뉴 -->
        <div class="tabs-section">
          <button
            v-for="tab in tabs"
            :key="tab.key"
            class="tab-btn"
            :class="{ active: activeTab === tab.key }"
            @click="activeTab = tab.key"
            @focus="handleFocus"
          >
            {{ tab.label }}
          </button>
        </div>

        <!-- 탭 컨텐츠 -->
        <div class="tab-content">
          <!-- 1. 북마크한 장소 -->
          <div v-if="activeTab === 'bookmarks'" class="content-wrapper">
            <div class="filter-chips">
              <button
                v-for="region in regions"
                :key="region.key"
                class="filter-chip"
                :class="{ active: activeRegion === region.key }"
                @click="activeRegion = region.key"
                @focus="handleFocus"
              >
                {{ region.label }}
              </button>
            </div>

            <div v-if="filteredBookmarks.length === 0" class="empty-state">
              <img src="@/assets/mypage1.png" alt="북마크 없음" class="empty-icon" />
              <p>북마크한 장소가 없습니다</p>
            </div>
            <div v-else class="items-list">
              <div
                v-for="bookmark in filteredBookmarks"
                :key="bookmark.id"
                class="list-item"
                @click="goToTravelSpot(bookmark.travel_spot_id)"
              >
                <img :src="bookmark.image || 'https://via.placeholder.com/100x100'" :alt="bookmark.name" class="item-image" />
                <div class="item-info">
                  <h3 class="item-title">{{ bookmark.name }}</h3>
                  <p class="item-description">{{ bookmark.address }}</p>
                  <span class="item-date">{{ formatDate(bookmark.created_at) }}</span>
                </div>
                <button class="item-action-btn">
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <path d="M5 12h14M12 5l7 7-7 7" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  </svg>
                </button>
              </div>
            </div>
          </div>

          <!-- 2. 여행지 댓글 -->
          <div v-if="activeTab === 'travel-reviews'" class="content-wrapper">
            <div v-if="travelReviews.length === 0" class="empty-state">
              <img src="@/assets/mypage2.png" alt="댓글 없음" class="empty-icon" />
              <p>작성한 댓글이 없습니다</p>
            </div>
            <div v-else class="items-list">
              <div
                v-for="review in travelReviews"
                :key="review.id"
                class="list-item"
                @click="goToTravelSpotFromReview(review)"
              >
                <div class="item-icon"><img src="@/assets/mypage2.png" alt="댓글 없음" class="empty-icon" /></div>
                <div class="item-info">
                  <h3 class="item-title">{{ review.spot_name || '여행지' }}</h3>
                  <p class="item-description">{{ review.content }}</p>
                  <span class="item-date">{{ formatDate(review.created_at) }}</span>
                </div>
                <button class="item-action-btn">
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <path d="M5 12h14M12 5l7 7-7 7" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  </svg>
                </button>
              </div>
            </div>
          </div>

          <!-- 3. 생성한 코스 -->
          <div v-if="activeTab === 'my-courses'" class="content-wrapper">
            <div v-if="myCourses.length === 0" class="empty-state">
              <img src="@/assets/mypage3.png" alt="코스 없음" class="empty-icon" />
              <p>생성한 코스가 없습니다</p>
            </div>
            <div v-else class="items-list">
              <div
                v-for="course in myCourses"
                :key="course.id"
                class="list-item"
                @click="goToCourse(course.id)"
              >
                <img :src="course.image || 'https://via.placeholder.com/100x100'" :alt="course.title" class="item-image" />
                <div class="item-info">
                  <h3 class="item-title">{{ course.title }}</h3>
                  <p class="item-description">{{ course.spots_count }}개 장소</p>
                  <span class="item-date">{{ formatDate(course.created_at) }}</span>
                </div>
                <button class="item-action-btn">
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <path d="M5 12h14M12 5l7 7-7 7" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  </svg>
                </button>
              </div>
            </div>
          </div>

          <!-- 4. 좋아요한 코스 -->
          <div v-if="activeTab === 'liked-courses'" class="content-wrapper">
            <div v-if="likedCourses.length === 0" class="empty-state">
              <img src="@/assets/mypage4.png" alt="좋아요 없음" class="empty-icon" />
              <p>좋아요한 코스가 없습니다</p>
            </div>
            <div v-else class="items-list">
              <div
                v-for="course in likedCourses"
                :key="course.id"
                class="list-item"
                @click="goToCourse(course.course_id || course.id)"
              >
                <img :src="course.image || 'https://via.placeholder.com/100x100'" :alt="course.title" class="item-image" />
                <div class="item-info">
                  <h3 class="item-title">{{ course.title }}</h3>
                  <p class="item-description">{{ course.spots_count }}개 장소</p>
                  <span class="item-date">{{ formatDate(course.created_at) }}</span>
                </div>
                <button class="item-action-btn">
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <path d="M5 12h14M12 5l7 7-7 7" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  </svg>
                </button>
              </div>
            </div>
          </div>

          <!-- 5. 코스 댓글 -->
          <div v-if="activeTab === 'course-comments'" class="content-wrapper">
            <div v-if="courseComments.length === 0" class="empty-state">
              <img src="@/assets/mypage5.png" alt="댓글 없음" class="empty-icon" />
              <p>작성한 댓글이 없습니다</p>
            </div>
            <div v-else class="items-list">
              <div
                v-for="comment in courseComments"
                :key="comment.id"
                class="list-item"
                @click="goToCourse(comment.course || comment.course_id)"
              >
                <div class="item-icon">💭</div>
                <div class="item-info">
                  <h3 class="item-title">{{ comment.course_title || '코스' }}</h3>
                  <p class="item-description">{{ comment.content }}</p>
                  <span class="item-date">{{ formatDate(comment.created_at) }}</span>
                </div>
                <button class="item-action-btn">
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <path d="M5 12h14M12 5l7 7-7 7" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  </svg>
                </button>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import NavigationBar from '@/components/common/NavigationBar.vue'
import { useAuthStore } from '@/stores/auth'
import { useTTS } from '@/composables/useTTS'
import api from '@/services/api'
import { alert, confirm } from '@/utils/alert'

const authStore = useAuthStore()
const router = useRouter()
const { isTTSEnabled, speak, toggleTTS } = useTTS()

const user = computed(() => authStore.currentUser)
const displayName = computed(() => {
  if (!user.value) return '여행자'
  const lastName = user.value.last_name || ''
  const firstName = user.value.first_name || ''
  return lastName + firstName || user.value.name || user.value.username || '여행자'
})

// 탭 정의
const tabs = [
  { key: 'bookmarks', label: '북마크한 장소' },
  { key: 'travel-reviews', label: '여행지 댓글' },
  { key: 'my-courses', label: '나만의 코스' },
  { key: 'liked-courses', label: '좋아요한 코스' },
  { key: 'course-comments', label: '코스 댓글' }
]

const activeTab = ref('bookmarks')

// 지역 필터
const regions = [
  { key: 'all', label: '전체' },
  { key: '1', label: '서울' },
  { key: '2', label: '인천' },
  { key: '3', label: '대전' },
  { key: '4', label: '대구' },
  { key: '5', label: '광주' },
  { key: '6', label: '부산' },
  { key: '7', label: '울산' },
  { key: '8', label: '세종' },
  { key: '31', label: '경기' },
  { key: '32', label: '강원' },
  { key: '33', label: '충북' },
  { key: '34', label: '충남' },
  { key: '35', label: '경북' },
  { key: '36', label: '경남' },
  { key: '37', label: '전북' },
  { key: '38', label: '전남' },
  { key: '39', label: '제주' }
]

const activeRegion = ref('all')

// 데이터
const bookmarks = ref([])
const travelReviews = ref([])
const myCourses = ref([])
const likedCourses = ref([])
const courseComments = ref([])

// 필터링된 북마크
const filteredBookmarks = computed(() => {
  if (activeRegion.value === 'all') {
    return bookmarks.value
  }
  return bookmarks.value.filter(b => String(b.area_code) === activeRegion.value)
})

// 로그인 확인
onMounted(async () => {
  // 토큰이 없거나 로그인 상태가 아니면 로그인 페이지로
  const token = localStorage.getItem('access_token')
  if (!authStore.isLoggedIn || !token) {
    await alert('로그인이 필요한 서비스입니다.')
    authStore.logout() // 상태 정리
    router.push('/login')
    return
  }

  await loadUserData()
})

// 사용자 데이터 로드
const loadUserData = async () => {
  try {
    // 북마크 로드
    const bookmarksResponse = await api.getBookmarks()
    console.log('북마크 데이터:', bookmarksResponse.data)
    bookmarks.value = (bookmarksResponse.data.results || bookmarksResponse.data || []).map(b => ({
      id: b.id,
      travel_spot_id: b.travel_spot?.id || b.travel_spot,
      name: b.travel_spot?.name || b.travel_spot_name || '여행지',
      address: b.travel_spot?.address || b.address || '',
      image: b.travel_spot?.image_url || b.image_url,
      area_code: b.travel_spot?.area_code || b.area_code,
      created_at: b.created_at
    }))

    // 여행지 댓글 로드
    const reviewsResponse = await api.getReviews({ user: user.value.id })
    console.log('여행지 댓글 데이터:', reviewsResponse.data)
    travelReviews.value = (reviewsResponse.data.results || reviewsResponse.data || []).map(r => ({
      id: r.id,
      travel_spot: r.travel_spot,
      spot_name: r.travel_spot_name || '여행지',
      content: r.content,
      created_at: r.created_at
    }))

    // 내 코스 로드
    const coursesResponse = await api.getCourses({ user: user.value.id })
    console.log('내 코스 데이터:', coursesResponse.data)
    myCourses.value = (coursesResponse.data.results || coursesResponse.data || []).map(c => ({
      id: c.id,
      title: c.title,
      spots_count: c.spots?.length || c.spots_count || 0,
      image: c.image_url,
      created_at: c.created_at
    }))

    // 좋아요한 코스 로드
    const likedCoursesResponse = await api.getLikedCourses()
    console.log('좋아요한 코스 데이터:', likedCoursesResponse.data)
    likedCourses.value = (likedCoursesResponse.data.results || likedCoursesResponse.data || []).map(l => ({
      id: l.id,
      course_id: l.course?.id || l.course,
      title: l.course?.title || l.course_title || '코스',
      spots_count: l.course?.spots?.length || l.course_spots_count || 0,
      image: l.course?.image_url,
      created_at: l.created_at
    }))

    // 코스 댓글 로드
    const courseCommentsResponse = await api.getCourseComments({ user: user.value.id })
    console.log('코스 댓글 데이터:', courseCommentsResponse.data)
    courseComments.value = (courseCommentsResponse.data.results || courseCommentsResponse.data || []).map(c => ({
      id: c.id,
      course: c.course?.id || c.course,
      course_title: c.course?.title || c.course_title || '코스',
      content: c.content,
      created_at: c.created_at
    }))
  } catch (error) {
    console.error('데이터 로드 실패:', error)
    console.error('에러 상세:', error.response?.data)

    // 401 에러(인증 실패) 시 로그아웃 처리
    if (error.response?.status === 401) {
      await alert('로그인이 만료되었습니다. 다시 로그인해주세요.')
      authStore.logout()
      router.push('/login')
    }
  }
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  const now = new Date()
  const diff = now - date
  const diffDays = Math.floor(diff / (1000 * 60 * 60 * 24))

  if (diffDays === 0) return '오늘'
  if (diffDays === 1) return '어제'
  if (diffDays < 7) return `${diffDays}일 전`
  return date.toLocaleDateString('ko-KR')
}

const goToTravelSpot = async (travelSpotId) => {
  if (!travelSpotId) {
    await alert('여행지 정보를 찾을 수 없습니다.')
    return
  }
  router.push(`/travel/${travelSpotId}`)
}

const goToTravelSpotFromReview = async (review) => {
  const spotId = review.travel_spot || review.travel_spot_id
  if (!spotId) {
    await alert('여행지 정보를 찾을 수 없습니다.')
    return
  }
  router.push(`/travel/${spotId}`)
}

const goToCourse = async (courseId) => {
  if (!courseId) {
    await alert('코스 정보를 찾을 수 없습니다.')
    return
  }
  router.push(`/course/${courseId}`)
}

const handleWithdraw = async () => {
  const result = await confirm('정말 회원 탈퇴하시겠습니까?\n모든 데이터가 삭제되며 복구할 수 없습니다.')
  if (result) {
    // TODO: 회원 탈퇴 API 구현
    await alert('회원 탈퇴 기능은 준비 중입니다.')
  }
}

const handleFocus = (payload) => {
  const text =
    typeof payload === 'string'
      ? payload
      : payload?.target?.innerText ||
        payload?.target?.getAttribute('aria-label') ||
        payload?.target?.getAttribute('placeholder') ||
        ''

  if (text && isTTSEnabled.value) {
    speak(text)
  }
}
</script>

<style scoped>
.mypage-view {
  min-height: 100vh;
  background: #f3f4f6;
  padding-top: 80px;
}

.mypage-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 2rem 1.5rem;
  display: grid;
  grid-template-columns: 320px 1fr;
  gap: 2rem;
  align-items: start;
}

/* 왼쪽 사이드바 */
.sidebar {
  background: white;
  border-radius: 16px;
  padding: 2rem;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  position: sticky;
  top: 100px;
}

.profile-section {
  text-align: center;
  padding-bottom: 2rem;
  border-bottom: 2px solid #e5e7eb;
}

.profile-avatar {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  background: #f3f4f6;
  padding: 15px;
  margin: 0 auto 1.5rem;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.profile-avatar img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.profile-name {
  font-size: 1.5rem;
  font-weight: 800;
  margin: 0 0 0.5rem 0;
  color: #111827;
}

.profile-username {
  font-size: 1rem;
  color: #6b7280;
  margin: 0;
}

/* 정보 섹션 */
.info-section {
  padding: 2rem 0;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.info-label {
  font-size: 0.875rem;
  font-weight: 600;
  color: #6b7280;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.info-value {
  font-size: 1rem;
  color: #111827;
  font-weight: 500;
}

/* 사이드바 푸터 */
.sidebar-footer {
  padding-top: 2rem;
  border-top: 2px solid #e5e7eb;
}

.withdraw-link {
  background: none;
  border: none;
  color: #dc2626;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  padding: 0;
  text-decoration: underline;
  transition: color 0.2s ease;
}

.withdraw-link:hover {
  color: #b91c1c;
}

/* 오른쪽 컨텐츠 영역 */
.content-area {
  background: white;
  border-radius: 16px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  overflow: hidden;
}

/* 탭 메뉴 */
.tabs-section {
  display: flex;
  gap: 0.5rem;
  padding: 1.5rem 2rem 0;
  border-bottom: 2px solid #e5e7eb;
  overflow-x: auto;
}

.tab-btn {
  padding: 1rem 1.5rem;
  background: transparent;
  border: none;
  border-bottom: 3px solid transparent;
  font-size: 1rem;
  font-weight: 600;
  color: #6b7280;
  cursor: pointer;
  white-space: nowrap;
  transition: all 0.2s ease;
}

.tab-btn:hover {
  color: #111827;
}

.tab-btn.active {
  color: #667eea;
  border-bottom-color: #667eea;
}

/* 탭 컨텐츠 */
.tab-content {
  min-height: 500px;
}

.content-wrapper {
  padding: 2rem;
}

/* 필터 칩 */
.filter-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  margin-bottom: 2rem;
}

.filter-chip {
  padding: 0.5rem 1rem;
  background: #f3f4f6;
  border: 2px solid transparent;
  border-radius: 20px;
  font-size: 0.875rem;
  font-weight: 600;
  color: #6b7280;
  cursor: pointer;
  transition: all 0.2s ease;
}

.filter-chip:hover {
  background: #e5e7eb;
}

.filter-chip.active {
  background: #ede9fe;
  border-color: #667eea;
  color: #667eea;
}

/* 빈 상태 */
.empty-state {
  text-align: center;
  padding: 4rem 1rem;
  color: #9ca3af;
}

.empty-icon {
  width: 200px;
  height: 200px;
  object-fit: contain;
  margin-bottom: 1rem;
}

.empty-state p {
  font-size: 1.1rem;
  margin: 0;
}

/* 아이템 리스트 */
.items-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.list-item {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  padding: 1.5rem;
  background: #f9fafb;
  border-radius: 12px;
  border: 1px solid #e5e7eb;
  cursor: pointer;
  transition: all 0.2s ease;
}

.list-item:hover {
  background: #f3f4f6;
  border-color: #d1d5db;
  transform: translateX(4px);
}

.item-image {
  width: 80px;
  height: 80px;
  border-radius: 8px;
  object-fit: cover;
  flex-shrink: 0;
}

.item-icon {
  width: 80px;
  height: 80px;
  border-radius: 8px;
  background: #b8c4e0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2.5rem;
  flex-shrink: 0;
}

.item-icon img{
  padding-top: 20px;
  width: 85px;
}

.item-info {
  flex: 1;
  min-width: 0;
}

.item-title {
  font-size: 1.1rem;
  font-weight: 700;
  margin: 0 0 0.5rem 0;
  color: #111827;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.item-description {
  font-size: 0.95rem;
  color: #6b7280;
  margin: 0 0 0.5rem 0;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  white-space: normal;
}

.item-date {
  font-size: 0.875rem;
  color: #9ca3af;
}

.item-action-btn {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  border: none;
  background: #111827;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  flex-shrink: 0;
  transition: all 0.2s ease;
}

.item-action-btn:hover {
  background: #374151;
  transform: translateX(4px);
}

/* 반응형 */
@media (max-width: 1024px) {
  .mypage-container {
    grid-template-columns: 1fr;
    gap: 1.5rem;
  }

  .sidebar {
    position: static;
  }

  .tabs-section {
    padding: 1rem 1.5rem 0;
  }

  .tab-btn {
    padding: 0.875rem 1rem;
    font-size: 0.9rem;
  }

  .content-wrapper {
    padding: 1.5rem;
  }
}

@media (max-width: 768px) {
  .mypage-container {
    padding: 1rem;
  }

  .sidebar {
    padding: 1.5rem;
  }

  .profile-avatar {
    width: 100px;
    height: 100px;
  }

  .profile-name {
    font-size: 1.25rem;
  }

  .list-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }

  .item-image,
  .item-icon {
    width: 100%;
    height: 200px;
  }

  .item-action-btn {
    align-self: flex-end;
  }
}
</style>
