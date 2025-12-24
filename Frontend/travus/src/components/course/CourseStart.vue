<template>
  <div class="course-start">
    <!-- 커스텀 알림 모달 -->
    <CustomAlert
      v-model="showAlert"
      :title="alertConfig.title"
      :message="alertConfig.message"
      :type="alertConfig.type"
      :confirmText="alertConfig.confirmText"
      @confirm="handleAlertConfirm"
    />

    <!-- 히어로 섹션 -->
    <div class="hero-section">
      <div class="hero-content">
        <div class="text-section">
          <h1 class="hero-title">
            <span class="highlight-ai">AI</span><span class="highlight-text">코스</span> 플래너
          </h1>
          <p class="hero-subtitle">
            당신이 원하는 여행의 시작<br>
            1분이면 끝! 나만을 위한 여행 코스 추천
          </p>
          <div class="button-group">
            <button class="btn-primary" @click="handleCreateCourse">
              코스만들기
              <span class="arrow">→</span>
            </button>
          </div>
        </div>

        <div class="illustration-section">
          <img src="@/assets/course3.png" alt="AI 플래너 지도" class="map-image" />
        </div>
      </div>
    </div>

    <!-- 카테고리 탭 (히어로 위에 겹침) -->
    <div class="category-tabs-wrapper">
      <div class="category-tabs">
        <button
          v-for="category in categories"
          :key="category.id"
          class="tab-btn"
          :class="{ active: selectedCategory === category.id }"
          @click="selectCategory(category.id)"
        >
          {{ category.name }}
        </button>
      </div>
    </div>

    <!-- 지역 선택 (지역별 탭에서만 표시) -->
    <div v-if="selectedCategory === 'regional'" class="region-selector-wrapper">
      <div class="region-selector">
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
    </div>

    <!-- 코스 목록 섹션 -->
    <div class="courses-section">
      <div class="container">
        <!-- 섹션 제목 -->
        <div class="section-header">
          <h2 class="section-title">
            {{ selectedCategory === 'my-course' ? '나의 여행코스' : selectedCategory === 'best30' ? '월간 Best 30' : '지역별 사용자코스' }}
          </h2>
        </div>

        <!-- 로딩 -->
        <div v-if="loading" class="loading">
          <i class="fa fa-spinner fa-spin"></i>
          <p>코스를 불러오는 중...</p>
        </div>

        <!-- 코스 카드 그리드 -->
        <div v-else-if="courses.length > 0" class="cards-grid">
          <div
            v-for="course in courses"
            :key="course.id"
            class="course-card"
            @click="goToCourseDetail(course.id)"
          >
            <div class="card-image">
              <img :src="getCourseThumbnail(course)" :alt="course.title" @error="handleImageError" />
              <div class="course-overlay">
                <span class="spot-count">{{ course.course_spots ? course.course_spots.length : 0 }}개 장소</span>
              </div>
            </div>
            <div class="card-content">
              <h3 class="card-title">{{ course.title }}</h3>
              <p class="card-description">{{ course.description }}</p>

              <!-- 작성자 정보 -->
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
          <p v-if="selectedCategory === 'my-course'">아직 생성한 코스가 없습니다.</p>
          <p v-else-if="selectedCategory === 'best30'">아직 등록된 코스가 없습니다.</p>
          <p v-else>이 지역에 등록된 코스가 없습니다.</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/services/api'
import { useAuthStore } from '@/stores/auth'
import CustomAlert from '@/components/common/CustomAlert.vue'

const emit = defineEmits(['next', 'select-course'])

const router = useRouter()
const authStore = useAuthStore()

const selectedCategory = ref('best30')
const selectedRegion = ref('1')
const courses = ref([])
const loading = ref(false)

// 커스텀 알림 상태
const showAlert = ref(false)
const alertConfig = ref({
  title: '알림',
  message: '',
  type: 'info',
  confirmText: '확인'
})
const alertCallback = ref(null)

const categories = [
  { id: 'my-course', name: '나의 여행코스' },
  { id: 'best30', name: '월간Best30' },
  { id: 'regional', name: '지역별 사용자코스' }
]

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

// 커스텀 알림 표시 함수
const showCustomAlert = (config, callback = null) => {
  alertConfig.value = {
    title: config.title || '알림',
    message: config.message,
    type: config.type || 'info',
    confirmText: config.confirmText || '확인'
  }
  alertCallback.value = callback
  showAlert.value = true
}

// 알림 확인 버튼 클릭
const handleAlertConfirm = () => {
  if (alertCallback.value) {
    alertCallback.value()
    alertCallback.value = null
  }
}

// 코스 만들기 버튼 클릭
const handleCreateCourse = () => {
  if (!authStore.isLoggedIn) {
    showCustomAlert(
      {
        title: '로그인 필요',
        message: '코스 만들기는 로그인이 필요합니다.',
        type: 'info',
        confirmText: '로그인하기'
      },
      () => router.push('/login')
    )
    return
  }
  emit('next')
}

// 카테고리 변경 시 코스 로드
const selectCategory = async (categoryId) => {
  if (categoryId === 'my-course' && !authStore.isLoggedIn) {
    showCustomAlert(
      {
        title: '로그인 필요',
        message: '나의 여행코스를 보려면 로그인이 필요합니다.',
        type: 'info',
        confirmText: '로그인하기'
      },
      () => router.push('/login')
    )
    return
  }

  selectedCategory.value = categoryId
  await loadCourses()
}

// 지역 선택
const selectRegion = async (regionCode) => {
  selectedRegion.value = regionCode
  await loadCourses()
}

// 코스 로드
const loadCourses = async () => {
  loading.value = true
  courses.value = []

  try {
    let response

    if (selectedCategory.value === 'my-course') {
      response = await api.getMyCourses()
    } else if (selectedCategory.value === 'best30') {
      response = await api.getMonthlyBestCourses()
    } else if (selectedCategory.value === 'regional') {
      response = await api.getCoursesByRegion(selectedRegion.value)
    }

    courses.value = response.data.results || response.data
  } catch (error) {
    console.error('코스 불러오기 실패:', error)
    if (error.response?.status === 401 && selectedCategory.value === 'my-course') {
      // 나의 여행코스만 401 에러 시 로그인 페이지로 이동
      showCustomAlert(
        {
          title: '로그인 필요',
          message: '로그인이 필요합니다.',
          type: 'warning',
          confirmText: '로그인하기'
        },
        () => router.push('/login')
      )
    } else if (error.response?.status !== 401) {
      // 401이 아닌 다른 에러만 알림
      showCustomAlert(
        {
          title: '오류',
          message: '코스를 불러오는데 실패했습니다.',
          type: 'error',
          confirmText: '확인'
        }
      )
    }
    // 다른 탭에서 401이 나면 그냥 빈 배열로 처리
  } finally {
    loading.value = false
  }
}

// 코스 썸네일 가져오기
const getCourseThumbnail = (course) => {
  if (course.course_spots && course.course_spots.length > 0) {
    const firstSpot = course.course_spots[0].travel_spot
    if (firstSpot && firstSpot.image_url) return firstSpot.image_url
    if (firstSpot && firstSpot.thumbnail_url) return firstSpot.thumbnail_url
  }
  return 'https://via.placeholder.com/400x300?text=No+Image'
}

// 이미지 에러 처리
const handleImageError = (e) => {
  e.target.src = 'https://via.placeholder.com/400x300?text=No+Image'
}

// 코스 상세로 이동
const goToCourseDetail = (courseId) => {
  emit('select-course', courseId)
}

// 날짜 포맷
const formatDate = (dateString) => {
  const date = new Date(dateString)
  const now = new Date()
  const diffMs = now - date
  const diffDays = diffMs / 86400000

  if (diffDays < 1) return '오늘'
  if (diffDays < 2) return '어제'
  if (diffDays < 7) return diffDays.toFixed(0) + '일 전'
  if (diffDays < 30) return (diffDays / 7).toFixed(0) + '주 전'

  return date.toLocaleDateString('ko-KR')
}

// 초기 로드
onMounted(async () => {
  await loadCourses()
})
</script>

<style scoped>
.course-start {
  width: 100%;
  /* background: #5b6fc7; */
}

/* 히어로 섹션 */
.hero-section {
  background: url('@/assets/background.gif') center center / cover no-repeat;
  padding: 140px 2rem 100px;
  min-height: calc(100vh - 100px);
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
}

.hero-section::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  /* background: rgba(91, 111, 199, 0.7); */
  pointer-events: none;
}

.hero-content {
  max-width: 1400px;
  width: 100%;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 6rem;
  align-items: center;
  position: relative;
  z-index: 1;
}

.text-section {
  color: white;
  padding-left: 4rem;
}

.hero-title {
  font-size: 4rem;
  font-weight: 700;
  line-height: 1.2;
  margin: 0 0 2rem 0;
  letter-spacing: -2px;
}

.highlight-ai {
  color: #00ff88;
  font-style: italic;
}

.highlight-text {
  color: white;
}

.hero-subtitle {
  font-size: 1.5rem;
  line-height: 1.8;
  margin: 0 0 3rem 0;
  opacity: 0.95;
  font-weight: 300;
  color: rgba(255, 255, 255, 0.95);
}

.button-group {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
  margin-bottom: 4rem;
}

.btn-primary {
  padding: 1.25rem 3rem;
  font-size: 1.25rem;
  font-weight: 600;
  border-radius: 50px;
  border: none;
  cursor: pointer;
  transition: all 0.3s ease;
  display: inline-flex;
  align-items: center;
  gap: 0.75rem;
  background: #4158D0;
  color: white;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
}

.btn-primary:hover {
  transform: translateY(-3px);
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.3);
  background: #3549b8;
}

.arrow {
  font-size: 1.5rem;
  transition: transform 0.3s ease;
}

.btn-primary:hover .arrow {
  transform: translateX(4px);
}

.partner-logos {
  display: flex;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;
  opacity: 0.9;
}

.partner-text {
  font-size: 0.875rem;
  color: white;
  font-weight: 400;
}

.separator {
  color: rgba(255, 255, 255, 0.5);
  font-size: 0.875rem;
}

.illustration-section {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  perspective: 1200px;
}

.map-image {
  width: 100%;
  max-width: 800px;
  height: auto;
  display: block;
  filter: drop-shadow(0 20px 60px rgba(0, 0, 0, 0.3));
  margin-top: -150px;
}

@keyframes float {
  0%, 100% {
    transform: translateY(0) rotateY(-5deg);
  }
  50% {
    transform: translateY(-20px) rotateY(5deg);
  }
}

/* 반응형 */
@media (max-width: 1200px) {
  .hero-content {
    grid-template-columns: 1fr;
    text-align: center;
    gap: 4rem;
  }

  .illustration-section {
    justify-content: center;
    order: -1;
  }

  .button-group {
    justify-content: center;
  }

  .partner-logos {
    justify-content: center;
  }
}

@media (max-width: 768px) {
  .hero-section {
    padding: 120px 1.5rem 80px;
    min-height: auto;
  }

  .hero-title {
    font-size: 2.5rem;
  }

  .hero-subtitle {
    font-size: 1.125rem;
  }

  .btn-primary {
    width: 100%;
    justify-content: center;
    padding: 1rem 2rem;
    font-size: 1.125rem;
  }

  .map-image {
    max-width: 100%;
  }

  .partner-logos {
    font-size: 0.75rem;
  }

  .partner-text {
    font-size: 0.75rem;
  }
}

/* 카테고리 탭 래퍼 (겹침 효과) */
.category-tabs-wrapper {
  position: relative;
  margin-top: -60px;
  z-index: 10;
  padding: 0 2rem;
}

/* 카테고리 탭 */
.category-tabs {
  display: flex;
  justify-content: center;
  gap: 0;
  background: #2c3e7a;
  border-radius: 3px;
  padding: 0.5rem;
  max-width: 1200px;
  margin: 0 auto;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
}

/* Best 30 섹션 */
.best30-section {
  background: #f8f9fa;
  padding: 5rem 0 4rem;
}

.container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 2rem;
}

.tab-btn {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 1rem 1.5rem;
  background: transparent;
  color: rgba(255, 255, 255, 0.7);
  border: none;
  border-radius: 3px;
  font-size: 1.1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.tab-btn:hover {
  color: white;
  background: rgba(255, 255, 255, 0.1);
}

.tab-btn.active {
  background: white;
  color: #2c3e7a;
}

.tab-icon {
  font-size: 1.25rem;
}

/* 섹션 헤더 */
.section-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 2rem;
}

.section-title {
  font-size: 1.75rem;
  font-weight: 700;
  color: #1a202c;
  margin: 0;
}

.info-btn {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #e2e8f0;
  border: none;
  border-radius: 50%;
  cursor: pointer;
  color: #4a5568;
  transition: all 0.2s ease;
}

.info-btn:hover {
  background: #cbd5e0;
}

/* 카드 그리드 */
.cards-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1.5rem;
}

.destination-card {
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  cursor: pointer;
}

.destination-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.15);
}

.card-image {
  position: relative;
  width: 100%;
  height: 220px;
  overflow: hidden;
}

.card-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
}

.destination-card:hover .card-image img {
  transform: scale(1.1);
}

.accessibility-badge {
  position: absolute;
  bottom: 12px;
  right: 12px;
  width: 40px;
  height: 40px;
  background: rgba(0, 0, 0, 0.6);
  border: none;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s ease;
  backdrop-filter: blur(4px);
}

.accessibility-badge:hover {
  background: rgba(0, 0, 0, 0.8);
  transform: scale(1.1);
}

.card-content {
  padding: 1.25rem;
}

.card-title {
  font-size: 1.125rem;
  font-weight: 700;
  color: #1a202c;
  margin: 0 0 0.5rem 0;
}

.card-location {
  font-size: 0.875rem;
  color: #718096;
  margin: 0;
}

/* Best 30 반응형 */
@media (max-width: 1200px) {
  .cards-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (max-width: 768px) {
  .category-tabs-wrapper {
    margin-top: -40px;
  }

  .best30-section {
    padding: 4rem 0 3rem;
  }

  .category-tabs {
    flex-direction: column;
    max-width: 100%;
  }

  .tab-btn {
    padding: 0.875rem;
  }

  .cards-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 1rem;
  }

  .section-title {
    font-size: 1.5rem;
  }
}

@media (max-width: 480px) {
  .cards-grid {
    grid-template-columns: 1fr;
  }
}

/* 지역 선택 */
.region-selector-wrapper {
  background: #f8f9fa;
  padding: 1.5rem 2rem 0;
}

.region-selector {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
  max-width: 1400px;
  margin: 0 auto;
  justify-content: center;
}

.region-btn {
  padding: 0.5rem 1rem;
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 20px;
  font-size: 0.875rem;
  color: #4a5568;
  cursor: pointer;
  transition: all 0.2s;
}

.region-btn:hover {
  border-color: #2c3e7a;
  color: #2c3e7a;
}

.region-btn.active {
  background: #2c3e7a;
  border-color: #2c3e7a;
  color: white;
}

/* 코스 섹션 */
.courses-section {
  background: #f8f9fa;
  padding: 3rem 0 4rem;
}

/* 로딩 */
.loading {
  text-align: center;
  padding: 4rem 2rem;
  color: #718096;
}

.loading i {
  font-size: 3rem;
  margin-bottom: 1rem;
  color: #2c3e7a;
}

.loading p {
  font-size: 1rem;
  margin: 0;
}

/* 코스 카드 */
.course-card {
  background: white;
  border-radius: 12px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.course-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.15);
}

.course-card .card-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
}

.course-card:hover .card-image img {
  transform: scale(1.1);
}

.course-overlay {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 0.75rem;
  background: linear-gradient(to top, rgba(0, 0, 0, 0.7), transparent);
}

.spot-count {
  color: white;
  font-size: 0.8rem;
  font-weight: 600;
}

.card-description {
  font-size: 0.875rem;
  color: #718096;
  margin: 0 0 0.75rem 0;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  line-height: 1.5;
}

.course-meta {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 0.75rem;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid #f0f0f0;
  font-size: 0.8rem;
}

.author {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  color: #718096;
}

.author i {
  color: #2c3e7a;
}

.date {
  font-size: 0.75rem;
  color: #a0aec0;
}

.course-stats {
  display: flex;
  gap: 1rem;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  font-size: 0.8rem;
  color: #718096;
}

.stat-item i {
  color: #2c3e7a;
}

/* 빈 상태 */
.empty-state {
  text-align: center;
  padding: 4rem 2rem;
}

.empty-state i {
  font-size: 4rem;
  color: #cbd5e0;
  margin-bottom: 1rem;
}

.empty-state p {
  font-size: 1rem;
  color: #a0aec0;
  margin: 0;
}
</style>
