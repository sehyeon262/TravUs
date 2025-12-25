<template>
  <div class="course-list-view">
    <NavigationBar />

    <div class="container">
      <!-- 헤더 -->
      <div class="page-header">
        <h1 class="page-title">여행 코스</h1>
        <p class="page-subtitle">다양한 여행 코스를 둘러보고 나만의 코스를 만들어보세요</p>
      </div>

      <!-- 탭 메뉴 -->
      <div class="tab-menu">
        <button
          class="tab-btn"
          :class="{ active: activeTab === 'my' }"
          @click="switchTab('my')"
        >
          <i class="fa fa-user"></i>
          나의 여행코스
        </button>
        <button
          class="tab-btn"
          :class="{ active: activeTab === 'best' }"
          @click="switchTab('best')"
        >
          <i class="fa fa-trophy"></i>
          월간 Best 30
        </button>
        <button
          class="tab-btn"
          :class="{ active: activeTab === 'region' }"
          @click="switchTab('region')"
        >
          <i class="fa fa-map-marker"></i>
          지역별 사용자코스
        </button>
      </div>

      <!-- 지역 선택 (지역별 탭에서만 표시) -->
      <div v-if="activeTab === 'region'" class="filters-section">
        <div class="region-filter">
          <button
            v-for="region in regions"
            :key="region.code"
            class="region-btn"
            :class="{ active: selectedRegion === region.code }"
            @click="selectRegion(region.code)"
          >
            {{ region.name }}
          </button>
        </div>

        <!-- 정렬 필터 -->
        <div class="sort-filter">
          <button
            class="sort-btn"
            :class="{ active: sortOrder === 'likes' }"
            @click="changeSortOrder('likes')"
          >
            <i class="fa fa-thumbs-up"></i>
            추천순
          </button>
          <button
            class="sort-btn"
            :class="{ active: sortOrder === 'latest' }"
            @click="changeSortOrder('latest')"
          >
            <i class="fa fa-clock-o"></i>
            최신순
          </button>
        </div>
      </div>

      <!-- 로딩 -->
      <div v-if="loading" class="loading">
        <i class="fa fa-spinner fa-spin"></i>
        <p>코스를 불러오는 중...</p>
      </div>

      <!-- 코스 목록 -->
      <div v-else-if="courses.length > 0" class="course-grid">
        <div
          v-for="course in courses"
          :key="course.id"
          class="course-card"
          @click="goToCourseDetail(course.id)"
        >
          <!-- 썸네일 -->
          <div class="course-thumbnail">
            <img :src="getCourseThumbnail(course)" :alt="course.title" @error="handleImageError" />
            <div class="course-overlay">
              <span class="spot-count">{{ course.course_spots ? course.course_spots.length : 0 }}개 장소</span>
            </div>
          </div>

          <!-- 정보 -->
          <div class="course-info">
            <h3 class="course-title">{{ course.title }}</h3>
            <p class="course-description">{{ course.description }}</p>

            <!-- 작성자 -->
            <div class="course-meta">
              <span class="author">
                <i class="fa fa-user"></i>
                {{ course.user_name || course.username }}
              </span>
              <span class="date">{{ formatDate(course.created_at) }}</span>
            </div>

            <!-- 통계 -->
            <div class="course-stats">
              <span class="stat-item">
                <i class="fa fa-thumbs-up"></i>
                {{ course.like_count }}
              </span>
              <span class="stat-item">
                <i class="fa fa-eye"></i>
                {{ course.view_count }}
              </span>
              <span class="stat-item">
                <i class="fa fa-comment"></i>
                {{ course.comments_count || 0 }}
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- 빈 상태 -->
      <div v-else class="empty-state">
        <i class="fa fa-map-o"></i>
        <p v-if="activeTab === 'my'">아직 생성한 코스가 없습니다.</p>
        <p v-else-if="activeTab === 'best'">아직 등록된 코스가 없습니다.</p>
        <p v-else>이 지역에 등록된 코스가 없습니다.</p>
        <button class="btn-create-course" @click="goToCreateCourse">
          <i class="fa fa-plus"></i>
          코스 만들기
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import NavigationBar from '@/components/common/NavigationBar.vue'
import api from '@/services/api'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const activeTab = ref('best') // 기본: 월간 Best 30
const courses = ref([])
const loading = ref(false)
const selectedRegion = ref('1') // 기본: 서울
const sortOrder = ref('likes') // 기본: 추천순

const regions = [
  { code: '1', name: '서울' },
  { code: '2', name: '인천' },
  { code: '3', name: '대전' },
  { code: '4', name: '대구' },
  { code: '5', name: '광주' },
  { code: '6', name: '부산' },
  { code: '7', name: '울산' },
  { code: '8', name: '세종' },
  { code: '31', name: '경기' },
  { code: '32', name: '강원' },
  { code: '33', name: '충북' },
  { code: '34', name: '충남' },
  { code: '35', name: '경북' },
  { code: '36', name: '경남' },
  { code: '37', name: '전북' },
  { code: '38', name: '전남' },
  { code: '39', name: '제주' }
]

// 탭 전환
const switchTab = async (tab) => {
  if (tab === 'my' && !authStore.isLoggedIn) {
    alert('로그인이 필요합니다.')
    router.push('/login')
    return
  }

  activeTab.value = tab
  await loadCourses()
}

// 지역 선택
const selectRegion = async (regionCode) => {
  selectedRegion.value = regionCode
  await loadCourses()
}

// 정렬 방식 변경
const changeSortOrder = async (order) => {
  sortOrder.value = order
  await loadCourses()
}

// 코스 불러오기
const loadCourses = async () => {
  loading.value = true
  courses.value = []

  try {
    let response

    if (activeTab.value === 'my') {
      response = await api.getMyCourses()
    } else if (activeTab.value === 'best') {
      response = await api.getMonthlyBestCourses()
    } else if (activeTab.value === 'region') {
      response = await api.getCoursesByRegion(selectedRegion.value, sortOrder.value)
    }

    courses.value = response.data.results || response.data
  } catch (error) {
    console.error('코스 불러오기 실패:', error)
    if (error.response?.status === 401) {
      alert('로그인이 필요합니다.')
      router.push('/login')
    } else {
      alert('코스를 불러오는데 실패했습니다.')
    }
  } finally {
    loading.value = false
  }
}

// 코스 썸네일
const getCourseThumbnail = (course) => {
  if (course.course_spots && course.course_spots.length > 0) {
    const firstSpot = course.course_spots[0].travel_spot
    if (firstSpot && firstSpot.image_url) return firstSpot.image_url
    if (firstSpot && firstSpot.thumbnail_url) return firstSpot.thumbnail_url
  }
  return 'https://via.placeholder.com/300x200?text=No+Image'
}

// 이미지 에러
const handleImageError = (e) => {
  e.target.src = 'https://via.placeholder.com/300x200?text=No+Image'
}

// 날짜 포맷
const formatDate = (dateString) => {
  if (!dateString) return '-'

  const date = new Date(dateString)
  if (isNaN(date.getTime())) return '-'

  const now = new Date()
  const diffMs = now - date
  const diffDays = Math.floor(diffMs / 86400000)

  // 미래 날짜는 그대로 표시
  if (diffDays < 0) return date.toLocaleDateString('ko-KR')

  if (diffDays === 0) return '오늘'
  if (diffDays === 1) return '어제'
  if (diffDays < 7) return diffDays + '일 전'
  if (diffDays < 30) return Math.floor(diffDays / 7) + '주 전'

  return date.toLocaleDateString('ko-KR')
}

// 코스 상세로 이동
const goToCourseDetail = (courseId) => {
  router.push(`/course-detail/${courseId}`)
}

// 코스 만들기로 이동
const goToCreateCourse = () => {
  router.push('/course')
}

// 초기 로드
onMounted(async () => {
  await loadCourses()
})
</script>

<style scoped>
.course-list-view {
  min-height: 100vh;
  background: #f5f5f5;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 80px 20px 40px;
}

/* 페이지 헤더 */
.page-header {
  text-align: center;
  margin-bottom: 40px;
}

.page-title {
  font-size: 32px;
  font-weight: 700;
  color: #000;
  margin: 0 0 12px 0;
}

.page-subtitle {
  font-size: 16px;
  color: #666;
  margin: 0;
}

/* 탭 메뉴 */
.tab-menu {
  display: flex;
  gap: 12px;
  margin-bottom: 24px;
  justify-content: center;
}

.tab-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  background: white;
  border: 2px solid #e0e0e0;
  border-radius: 24px;
  font-size: 14px;
  font-weight: 600;
  color: #666;
  cursor: pointer;
  transition: all 0.2s;
}

.tab-btn i {
  font-size: 16px;
}

.tab-btn:hover {
  border-color: #00C73C;
  color: #00C73C;
}

.tab-btn.active {
  background: #00C73C;
  border-color: #00C73C;
  color: white;
}

/* 필터 섹션 */
.filters-section {
  display: flex;
  flex-direction: column;
  gap: 16px;
  margin-bottom: 24px;
}

/* 지역 필터 */
.region-filter {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  justify-content: center;
}

.region-btn {
  padding: 8px 16px;
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 16px;
  font-size: 13px;
  color: #666;
  cursor: pointer;
  transition: all 0.2s;
}

.region-btn:hover {
  border-color: #00C73C;
  color: #00C73C;
}

.region-btn.active {
  background: #00C73C;
  border-color: #00C73C;
  color: white;
}

/* 정렬 필터 */
.sort-filter {
  display: flex;
  gap: 12px;
  justify-content: center;
}

.sort-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 10px 20px;
  background: white;
  border: 2px solid #e0e0e0;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 600;
  color: #666;
  cursor: pointer;
  transition: all 0.2s;
}

.sort-btn i {
  font-size: 14px;
}

.sort-btn:hover {
  border-color: #00C73C;
  color: #00C73C;
}

.sort-btn.active {
  background: #00C73C;
  border-color: #00C73C;
  color: white;
}

/* 로딩 */
.loading {
  text-align: center;
  padding: 80px 20px;
  color: #666;
}

.loading i {
  font-size: 40px;
  margin-bottom: 16px;
  color: #00C73C;
}

.loading p {
  font-size: 16px;
  margin: 0;
}

/* 코스 그리드 */
.course-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 24px;
}

.course-card {
  background: white;
  border-radius: 12px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.course-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 4px 16px rgba(0,0,0,0.15);
}

.course-thumbnail {
  position: relative;
  width: 100%;
  height: 200px;
  overflow: hidden;
  background: #f0f0f0;
}

.course-thumbnail img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.course-overlay {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 12px;
  background: linear-gradient(to top, rgba(0,0,0,0.7), transparent);
}

.spot-count {
  color: white;
  font-size: 13px;
  font-weight: 600;
}

.course-info {
  padding: 16px;
}

.course-title {
  font-size: 18px;
  font-weight: 700;
  color: #000;
  margin: 0 0 8px 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.course-description {
  font-size: 14px;
  color: #666;
  margin: 0 0 12px 0;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  line-height: 1.5;
  height: 42px;
}

.course-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
  padding-bottom: 12px;
  border-bottom: 1px solid #f0f0f0;
}

.author {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
  color: #666;
}

.author i {
  color: #00C73C;
}

.date {
  font-size: 12px;
  color: #999;
}

.course-stats {
  display: flex;
  gap: 16px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
  color: #666;
}

.stat-item i {
  color: #00C73C;
}

/* 빈 상태 */
.empty-state {
  text-align: center;
  padding: 80px 20px;
}

.empty-state i {
  font-size: 60px;
  color: #ddd;
  margin-bottom: 16px;
}

.empty-state p {
  font-size: 16px;
  color: #999;
  margin: 0 0 24px 0;
}

.btn-create-course {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  background: #00C73C;
  color: white;
  border: none;
  border-radius: 24px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-create-course:hover {
  background: #00b035;
  transform: translateY(-2px);
}

/* 반응형 */
@media (max-width: 768px) {
  .container {
    padding: 60px 16px 24px;
  }

  .page-title {
    font-size: 24px;
  }

  .tab-menu {
    flex-direction: column;
  }

  .tab-btn {
    width: 100%;
    justify-content: center;
  }

  .course-grid {
    grid-template-columns: 1fr;
  }
}
</style>
