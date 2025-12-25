<template>
  <section class="weekly-section">
    <div class="container">
      <div class="weekly-header">
        <h2 class="weekly-title"><span>지금</span> 떠나기 좋은 여행지 추천</h2>
        <div class="subtitle-container">
          <p class="weekly-subtitle">
            모두가 편안하게 다녀올 수 있는 여행지를 골라봤습니다.
          </p>
        </div>
      </div>

      <!-- 로딩 -->
      <div v-if="isLoading" class="loading-container">
        <div class="loading-spinner"></div>
        <p>데이터를 불러오는 중...</p>
      </div>

      <!-- 빈 데이터 -->
      <div v-else-if="destinations.length === 0" class="no-results">
        <p>추천 여행지를 불러올 수 없습니다.</p>
      </div>

      <!-- 슬라이드 캐러셀 -->
      <div v-else class="carousel-container">
        <div class="carousel-wrapper">
          <div class="carousel-track" :style="trackStyle">
            <div
              v-for="(destination, index) in destinations"
              :key="destination.id || destination.contentid || index"
              class="carousel-card"
              @click="handleCardClick(destination)"
            >
              <!-- 이미지 -->
              <div class="card-image">
                <img :src="formatDestination(destination).image" :alt="formatDestination(destination).name" />
                <button
                  class="bookmark-btn"
                  :class="{ bookmarked: destination.is_bookmarked }"
                  @click.stop="handleBookmark(destination)"
                >
                  <svg width="20" height="20" viewBox="0 0 24 24" :fill="destination.is_bookmarked ? 'currentColor' : 'none'" stroke="currentColor" stroke-width="2">
                    <path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z" stroke-linecap="round" stroke-linejoin="round"/>
                  </svg>
                </button>
              </div>

              <!-- 카드 정보 -->
              <div class="card-info">
                <span class="card-region">{{ formatDestination(destination).region }}</span>
                <h3 class="card-title">{{ formatDestination(destination).name }}</h3>
                <p class="card-description">{{ formatDestination(destination).description }}</p>
              </div>
            </div>
          </div>
        </div>

        <!-- 네비게이션 -->
        <div class="carousel-nav">
          <button class="nav-btn prev" @click="prevSlide" :disabled="currentIndex === 0">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path d="M15 18l-6-6 6-6" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </button>
          <button class="nav-btn next" @click="nextSlide" :disabled="currentIndex >= maxIndex">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path d="M9 18l6-6-6-6" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </button>
        </div>

        <!-- 인디케이터 -->
        <div class="carousel-indicators">
          <div class="indicator-bar">
            <div class="indicator-progress" :style="{ width: `${progress}%` }"></div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/services/api'

const emit = defineEmits(['focus'])
const router = useRouter()

const isLoading = ref(true)
const destinations = ref([])
const currentIndex = ref(0)
const visibleCards = 4

// 카드 클릭 핸들러
const handleCardClick = (destination) => {
  // 상세 페이지로 이동 (Vue Router 사용)
  // contentTypeId도 함께 전달하여 조회 안정성 향상
  router.push({
    path: `/travel/${destination.contentid}`,
    query: { contentTypeId: destination.contenttypeid || '12' }
  })
}

// 북마크 핸들러
const handleBookmark = async (destination) => {
  const token = localStorage.getItem('access_token')
  if (!token) {
    alert('로그인 후 이용 가능합니다.')
    router.push('/login')
    return
  }

  if (!destination.contentid) {
    alert('여행지 정보를 불러오는 중입니다.')
    return
  }

  try {
    // destination.contentid를 사용하여 DB의 TravelSpot을 찾아야 함
    // 하지만 현재 destination 객체에 DB의 id가 없는 상태
    // formatDestination에서 id를 매핑하도록 수정 필요
    const response = await api.toggleBookmark(destination.id)

    // 로컬 상태 업데이트
    const index = destinations.value.findIndex(d => d.contentid === destination.contentid)
    if (index !== -1) {
      destinations.value[index].is_bookmarked = response.data.bookmarked
    }

  } catch (error) {
    console.error('❌ 북마크 토글 실패:', error)
    alert('북마크 처리에 실패했습니다.')
  }
}

// 트랙 스타일
const trackStyle = computed(() => {
  // 각 이동 = 카드 너비(25%) + gap(2rem)
  const index = currentIndex.value

  if (index === 0) {
    return {
      transform: 'translateX(0)',
      transition: 'transform 0.5s ease'
    }
  }

  // calc를 사용하여 정확하게 계산
  return {
    transform: `translateX(calc(${-index} * (25% + 2rem)))`,
    transition: 'transform 0.5s ease'
  }
})

// 지역 코드 매핑
const regionMap = {
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

// 여행지 데이터를 카드 형식으로 변환
const formatDestination = (item) => {
  return {
    id: item.id || item.contentid || '',  // DB PK (id) 우선 사용
    contentid: item.contentid || item.content_id || '',
    name: item.title || item.name || '제목 없음',
    image: item.firstimage || item.image_url || 'https://via.placeholder.com/400x300',
    description: item.addr1 || item.address || '주소 정보 없음',
    region: regionMap[item.areacode || item.area_code] || '기타'
  }
}

// 최대 인덱스
const maxIndex = computed(() => {
  return Math.max(0, destinations.value.length - visibleCards)
})

// 진행률
const progress = computed(() => {
  if (destinations.value.length === 0 || maxIndex.value === 0) return 100
  return ((currentIndex.value / maxIndex.value) * 100)
})

// 이전 슬라이드
const prevSlide = () => {
  if (currentIndex.value > 0) {
    currentIndex.value--
  }
}

// 다음 슬라이드
const nextSlide = () => {
  if (currentIndex.value < maxIndex.value) {
    currentIndex.value++
  }
}

// DB에서 관광지 데이터 가져오기
const fetchDestinations = async () => {
  try {

    // 랜덤 offset 생성 (0~900 범위에서 랜덤하게 시작)
    const randomOffset = Math.floor(Math.random() * 900)

    // DB에서 관광지 (content_type_id=12) 가져오기
    const response = await api.getTravelSpots({
      content_type_id: '12',
      page_size: 100,
      offset: randomOffset,  // 랜덤 offset으로 매번 다른 데이터 범위 가져오기
      ordering: '?'  // 랜덤 정렬 (백엔드가 지원하는 경우)
    })

    if (response.data && response.data.results) {
      // DB 응답을 기존 형식으로 매핑
      const results = response.data.results.map(item => ({
        id: item.id,  // DB PK 추가
        contentid: item.content_id,
        contenttypeid: item.content_type_id,
        title: item.name,
        addr1: item.address,
        areacode: item.area_code,
        firstimage: item.image_url,
        firstimage2: item.thumbnail_url,
        is_bookmarked: item.is_bookmarked || false  // 북마크 상태 추가
      }))

      // 이미지가 있는 것만 필터링
      const itemsWithImages = results.filter(item => item.firstimage && item.firstimage.trim() !== '')

      // Fisher-Yates 셔플 알고리즘으로 랜덤화
      const shuffled = [...itemsWithImages]
      for (let i = shuffled.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]]
      }

      destinations.value = shuffled.slice(0, 10)
    }
  } catch (error) {
    console.error('❌ 추천 여행지 로드 실패:', error)
    destinations.value = []
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  fetchDestinations()
})
</script>

<style scoped>
.weekly-section {
  background: #ffffff;
  padding: 6rem 0;
}

.container {
  max-width: 1600px;
  margin: 0 auto;
  padding: 0 2rem;
}

/* 헤더 */
.weekly-header {
  text-align: left;
  margin-bottom: 3rem;
  padding: 0 4rem;
}

.weekly-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: #1d1d1d;
  margin-bottom: 1rem;
  letter-spacing: -1px;
}

.weekly-title span{
  color: #394b9e;
}

.subtitle-container {
  background: #e7e7e7;
  padding: 1rem 1.5rem;
  border-radius: 3px;
}

.weekly-subtitle {
  font-size: 1rem;
  color: #242525;
  font-weight: 400;
  margin: 0;
}

/* 로딩 */
.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 0;
  min-height: 300px;
}

.loading-spinner {
  width: 50px;
  height: 50px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading-container p {
  color: #6c757d;
  font-size: 1.1rem;
}

/* 빈 결과 */
.no-results {
  text-align: center;
  padding: 4rem 0;
  color: #6c757d;
  font-size: 1.2rem;
}

/* 캐러셀 */
.carousel-container {
  position: relative;
}

.carousel-wrapper {
  overflow: hidden;
  margin: 0 4rem;
  width: calc(100% - 8rem);
  padding: 1rem 0 2rem 0;
}

.carousel-track {
  display: flex;
  gap: 2rem;
}

.carousel-card {
  flex: 0 0 calc((100% - 6rem) / 4);
  background: white;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  cursor: pointer;
}

.carousel-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 12px 24px rgba(102, 126, 234, 0.2);
}

.card-image {
  position: relative;
  width: 100%;
  height: 200px;
  overflow: hidden;
}

.card-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
}

.carousel-card:hover .card-image img {
  transform: scale(1.1);
}

.bookmark-btn {
  position: absolute;
  top: 1rem;
  right: 1rem;
  width: 40px;
  height: 40px;
  background: rgba(255, 255, 255, 0.9);
  border: none;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.bookmark-btn:hover {
  background: white;
  transform: scale(1.1);
}

.bookmark-btn svg {
  color: #667eea;
}

.bookmark-btn.bookmarked {
  background: #eff6ff;
  border: 2px solid #667eea;
}

.bookmark-btn.bookmarked svg {
  color: #667eea;
}

.card-info {
  padding: 1.5rem;
}

.card-title {
  font-size: 1.125rem;
  font-weight: 700;
  color: #111827;
  margin: 0 0 0.5rem 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.card-description {
  font-size: 0.875rem;
  color: #6b7280;
  margin: 0 0 0.5rem 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.card-region {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  background: #ede9fe;
  color: #7c3aed;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
}

/* 네비게이션 버튼 */
.carousel-nav {
  position: absolute;
  top: 50%;
  left: 0;
  right: 0;
  transform: translateY(-50%);
  display: flex;
  justify-content: space-between;
  pointer-events: none;
}

.nav-btn {
  pointer-events: all;
  width: 48px;
  height: 48px;
  background: white;
  border: 2px solid #e5e7eb;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
  color: #667eea;
}

.nav-btn:hover:not(:disabled) {
  background: #667eea;
  border-color: #667eea;
  color: white;
  transform: scale(1.1);
}

.nav-btn:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

/* 인디케이터 */
.carousel-indicators {
  margin-top: 2rem;
  padding: 0 4rem;
}

.indicator-bar {
  width: 100%;
  height: 4px;
  background: #e5e7eb;
  border-radius: 2px;
  overflow: hidden;
}

.indicator-progress {
  height: 100%;
  background: #4e5da1;
  transition: width 0.5s ease;
}

/* 반응형 */
@media (max-width: 1200px) {
  .carousel-card {
    flex: 0 0 280px;
  }
}

@media (max-width: 768px) {
  .weekly-section {
    padding: 4rem 0;
  }

  .weekly-title {
    font-size: 1.5rem;
  }

  .carousel-wrapper {
    margin: 0 2rem;
  }

  .carousel-card {
    flex: 0 0 260px;
  }

  .carousel-indicators {
    padding: 0 2rem;
  }
}
</style>
