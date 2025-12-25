<template>
  <div class="travel-view">
    <NavigationBar
      :isTTSEnabled="isTTSEnabled"
      @toggle-tts="toggleTTS"
      @font-size-change="handleFontSizeChange"
      @focus="handleTTSFocus"
    />

    <!-- 헤더 섹션 -->
    <section class="travel-header" :class="headerBackgroundClass">
      <div class="header-overlay"></div>
      <div class="container header-content">
        <h1 class="page-title">{{ pageTitle }}</h1>
        <p class="page-subtitle">{{ pageSubtitle }}</p>

        <!-- 검색바 -->
        <div class="search-bar">
          <input
            type="text"
            v-model="searchQuery"
            placeholder="여행지를 검색하세요..."
            @keyup.enter="handleSearch"
            class="search-input"
          />
          <button class="search-btn" @click="handleSearch">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
              <path d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
            </svg>
          </button>
        </div>
      </div>
    </section>

    <!-- 무장애 검색 섹션 -->
    <section class="filter-section">
      <div class="container">
        <div class="filter-card">
          <!-- 무장애 검색 헤더 -->
          <div class="filter-header" @click="toggleFilterCollapse">
            <h3 class="filter-main-title">무장애 검색</h3>
            <button class="collapse-btn">
              <span v-if="isFilterCollapsed">▼</span>
              <span v-else>▲</span>
            </button>
          </div>

          <!-- 필터 내용 -->
          <div v-show="!isFilterCollapsed" class="filter-content">
            <!-- 무장애 유형 -->
            <div class="filter-row">
              <div class="accessibility-types">
                <button
                  class="accessibility-type-btn"
                  :class="{ active: selectedAccessibilityTypes.includes('wheelchair') }"
                  @click="toggleAccessibilityType('wheelchair')"
                >
                  <div class="icon-wrapper">
                    <img src="@/assets/icon_body.png" alt="지체장애" />
                  </div>
                  <span>지체장애</span>
                </button>

                <button
                  class="accessibility-type-btn"
                  :class="{ active: selectedAccessibilityTypes.includes('visual') }"
                  @click="toggleAccessibilityType('visual')"
                >
                  <div class="icon-wrapper">
                    <img src="@/assets/icon_eye.png" alt="시각장애" />
                  </div>
                  <span>시각장애</span>
                </button>

                <button
                  class="accessibility-type-btn"
                  :class="{ active: selectedAccessibilityTypes.includes('hearing') }"
                  @click="toggleAccessibilityType('hearing')"
                >
                  <div class="icon-wrapper">
                    <img src="@/assets/icon_ear.png" alt="청각장애" />
                  </div>
                  <span>청각장애</span>
                </button>

                <button
                  class="accessibility-type-btn"
                  :class="{ active: selectedAccessibilityTypes.includes('family') }"
                  @click="toggleAccessibilityType('family')"
                >
                  <div class="icon-wrapper">
                    <img src="@/assets/icon_baby.png" alt="영유아 가족" />
                  </div>
                  <span>영유아 가족</span>
                </button>

                <button
                  class="accessibility-type-btn"
                  :class="{ active: selectedAccessibilityTypes.includes('senior') }"
                  @click="toggleAccessibilityType('senior')"
                >
                  <div class="icon-wrapper">
                    <img src="@/assets/icon_old.png" alt="고령자" />
                  </div>
                  <span>고령자</span>
                </button>
              </div>
            </div>

            <!-- 시설 정보 (무장애 유형별 동적 표시) -->
            <div class="filter-row" v-if="selectedAccessibilityTypes.length > 0">
              <h4 class="facility-title">시설 정보</h4>

              <!-- 각 무장애 유형별로 그룹화 -->
              <div v-for="(type, index) in selectedAccessibilityTypes" :key="type" class="facility-group">
                <div class="facility-group-header">
                  <span class="facility-group-icon">
                    <img v-if="type === 'wheelchair'" src="@/assets/icon_body.png" alt="지체장애" />
                    <img v-else-if="type === 'visual'" src="@/assets/icon_eye.png" alt="시각장애" />
                    <img v-else-if="type === 'hearing'" src="@/assets/icon_ear.png" alt="청각장애" />
                    <img v-else-if="type === 'family'" src="@/assets/icon_baby.png" alt="영유아가족" />
                    <img v-else-if="type === 'senior'" src="@/assets/icon_old.png" alt="고령자" />
                  </span>
                  <span class="facility-group-label">{{ getAccessibilityLabel(type) }}</span>
                </div>

                <div class="facility-types">
                  <button
                    v-for="facility in facilityOptions[type]"
                    :key="facility.value"
                    class="facility-btn"
                    :class="{ active: selectedFacilities.includes(facility.value) }"
                    @click="toggleFacility(facility.value)"
                  >
                    {{ facility.label }}
                  </button>
                </div>

                <!-- 구분선 (마지막 그룹 제외) -->
                <div v-if="index < selectedAccessibilityTypes.length - 1" class="facility-divider"></div>
              </div>
            </div>

            <!-- 지역 선택 및 검색 -->
            <div class="filter-row">
              <div class="region-search-row">
                <div class="region-select-wrapper">
                  <label>지역선택</label>
                  <select v-model="selectedRegion" class="region-select">
                    <option value="">시도 선택</option>
                    <option value="1">서울</option>
                    <option value="2">인천</option>
                    <option value="3">대전</option>
                    <option value="4">대구</option>
                    <option value="5">광주</option>
                    <option value="6">부산</option>
                    <option value="7">울산</option>
                    <option value="8">세종</option>
                    <option value="31">경기</option>
                    <option value="32">강원</option>
                    <option value="33">충북</option>
                    <option value="34">충남</option>
                    <option value="35">경북</option>
                    <option value="36">경남</option>
                    <option value="37">전북</option>
                    <option value="38">전남</option>
                    <option value="39">제주</option>
                  </select>
                </div>

                <div class="region-select-wrapper">
                  <label>전체</label>
                  <select class="region-select">
                    <option value="">전체</option>
                  </select>
                </div>

                <button class="search-filter-btn" @click="handleFilterSearch">
                  검색
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- 로딩 -->
    <div v-if="loading" class="loading-container">
      <div class="loading-spinner"></div>
      <p>데이터를 불러오는 중...</p>
    </div>

    <!-- 여행지 리스트 -->
    <section class="destinations-section" v-else>
      <div class="container">
        <div v-if="destinations.length === 0" class="no-results">
          <p>검색 결과가 없습니다.</p>
        </div>
        <div v-else class="destinations-grid">
          <TravelCard
            v-for="(destination, index) in filteredDestinations"
            :key="index"
            :destination="formatDestination(destination)"
            @click="handleCardClick(destination)"
            @bookmark-changed="handleBookmarkChanged"
          />
        </div>

        <!-- 페이지네이션 -->
        <div class="pagination" v-if="totalPages > 1">
          <!-- 이전 그룹 -->
          <button
            class="page-btn nav-btn"
            :disabled="displayedPages[0] === 1"
            @click="changePageGroup(-1)"
            title="이전 그룹"
          >
            ◀◀
          </button>

          <!-- 이전 -->
          <button
            class="page-btn nav-btn"
            :disabled="currentPage === 1"
            @click="changePage(currentPage - 1)"
            title="이전"
          >
            ◀
          </button>

          <!-- 페이지 번호들 -->
          <button
            v-for="page in displayedPages"
            :key="page"
            class="page-btn"
            :class="{ active: page === currentPage }"
            @click="changePage(page)"
          >
            {{ page }}
          </button>

          <!-- 다음 -->
          <button
            class="page-btn nav-btn"
            :disabled="currentPage === totalPages"
            @click="changePage(currentPage + 1)"
            title="다음"
          >
            ▶
          </button>

          <!-- 다음 그룹 -->
          <button
            class="page-btn nav-btn"
            :disabled="displayedPages[displayedPages.length - 1] === totalPages"
            @click="changePageGroup(1)"
            title="다음 그룹"
          >
            ▶▶
          </button>
        </div>
      </div>
    </section>

    <FooterSection />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import NavigationBar from '@/components/common/NavigationBar.vue'
import FooterSection from '@/components/common/FooterSection.vue'
import TravelCard from '@/components/travel/TravelCard.vue'
import api from '@/services/api'

// 라우트에서 카테고리 가져오기
const route = useRoute()
const contentTypeId = computed(() => route.query.category || '')

// 페이지 타이틀 동적 변경
const pageTitle = computed(() => {
  switch (contentTypeId.value) {
    case '12': return '관광지/명소'
    case '32': return '숙박'
    case '39': return '음식점'
    default: return '여행지 정보'
  }
})

const pageSubtitle = computed(() => {
  switch (contentTypeId.value) {
    case '12': return '전국의 무장애 관광지를 찾아보세요'
    case '32': return '편안한 무장애 숙박시설을 찾아보세요'
    case '39': return '접근 가능한 음식점을 찾아보세요'
    default: return '전국의 다양한 무장애 여행지를 찾아보세요'
  }
})

// 헤더 배경 이미지 클래스
const headerBackgroundClass = computed(() => {
  switch (contentTypeId.value) {
    case '12': return 'header-beach'
    case '32': return 'header-room'
    case '39': return 'header-restaurant'
    default: return 'header-default'
  }
})

// TTS 상태
const isTTSEnabled = ref(true)
const synthesis = window.speechSynthesis

const toggleTTS = () => {
  const wasEnabled = isTTSEnabled.value
  isTTSEnabled.value = !isTTSEnabled.value

  if (!isTTSEnabled.value) {
    // Cancel any ongoing speech when turning OFF
    synthesis.cancel()
  } else if (!wasEnabled && isTTSEnabled.value) {
    // Only speak confirmation when turning ON
    synthesis.cancel()
    const utterance = new SpeechSynthesisUtterance('TTS가 켜졌습니다')
    utterance.lang = 'ko-KR'
    utterance.rate = 0.9
    synthesis.speak(utterance)
  }
}

const handleFontSizeChange = (size) => {
  document.documentElement.style.fontSize = `${size}px`
}

const handleTTSFocus = (text) => {
  if (isTTSEnabled.value && text) {
    synthesis.cancel()
    const utterance = new SpeechSynthesisUtterance(text)
    utterance.lang = 'ko-KR'
    utterance.rate = 0.9
    synthesis.speak(utterance)
  }
}

// 검색 및 필터 상태
const searchQuery = ref('')
const selectedAccessibilityTypes = ref([]) // 무장애 유형 (다중 선택)
const selectedFacilities = ref([]) // 시설 정보 (다중 선택)
const selectedRegion = ref('')
const sortBy = ref('latest')
const isFilterCollapsed = ref(false) // 필터 접기/펼치기 상태

// 무장애 유형별 시설 정보 매핑 (API 명세 기반)
const facilityOptions = {
  wheelchair: [ // 지체장애
    { value: 'parking', label: '주차' },
    { value: 'public_transport', label: '대중교통' },
    { value: 'route', label: '접근로' },
    { value: 'wheelchair', label: '휠체어' },
    { value: 'exit', label: '출입통로' },
    { value: 'elevator', label: '엘리베이터' },
    { value: 'restroom', label: '화장실' }
  ],
  visual: [ // 시각장애
    { value: 'braile_block', label: '점자블록' },
    { value: 'help_dog', label: '보조견 동반' },
    { value: 'audio_guide', label: '오디오가이드' },
    { value: 'guide_system', label: '유도 안내 설비' }
  ],
  hearing: [ // 청각장애
    { value: 'sign_guide', label: '수화 안내' },
    { value: 'video_guide', label: '자막 비디오' },
    { value: 'hearing_room', label: '객실' }
  ],
  family: [ // 영유아가족
    { value: 'stroller', label: '유모차' },
    { value: 'lactation_room', label: '수유실' }
  ],
  senior: [ // 고령자 (지체장애 시설 중 일부 적용)
    { value: 'parking', label: '주차' },
    { value: 'public_transport', label: '대중교통' },
    { value: 'route', label: '접근로' },
    { value: 'exit', label: '출입통로' },
    { value: 'elevator', label: '엘리베이터' },
    { value: 'restroom', label: '화장실' }
  ]
}

// 무장애 유형 레이블 가져오기
const getAccessibilityLabel = (type) => {
  const labels = {
    wheelchair: '지체장애',
    visual: '시각장애',
    hearing: '청각장애',
    family: '영유아가족',
    senior: '고령자'
  }
  return labels[type] || type
}

// 데이터 상태
const destinations = ref([])
const loading = ref(false)
const totalCount = ref(0)

// 페이지네이션 상태
const currentPage = ref(1)
const itemsPerPage = 20

const totalPages = computed(() => {
  return Math.ceil(totalCount.value / itemsPerPage)
})

const displayedPages = computed(() => {
  const pages = []
  const maxDisplayed = 5

  // 전체 페이지가 없으면 빈 배열 반환
  if (totalPages.value === 0) {
    return pages
  }

  // 현재 페이지가 속한 그룹의 시작 페이지 계산
  const groupStart = Math.floor((currentPage.value - 1) / maxDisplayed) * maxDisplayed + 1
  const groupEnd = Math.min(groupStart + maxDisplayed - 1, totalPages.value)

  for (let i = groupStart; i <= groupEnd; i++) {
    pages.push(i)
  }

  return pages
})

// 필터링된 여행지 (백엔드에서 이미 이미지 필터링됨)
const filteredDestinations = computed(() => {
  return destinations.value
})

// 지역 이름 매핑
const getRegionName = (areaCode) => {
  const regionMap = {
    '1': '서울', '2': '인천', '3': '대전', '4': '대구', '5': '광주',
    '6': '부산', '7': '울산', '8': '세종', '31': '경기', '32': '강원',
    '33': '충북', '34': '충남', '35': '경북', '36': '경남',
    '37': '전북', '38': '전남', '39': '제주'
  }
  return regionMap[String(areaCode)] || '기타'
}

// 여행지 데이터 포맷 변환
const formatDestination = (destination) => {
  return {
    id: destination.id,  // DB PK 사용
    contentid: destination.contentid || destination.content_id,
    name: destination.title || destination.name,
    description: destination.addr1 || destination.address || '주소 정보 없음',
    image: destination.firstimage || destination.image_url || 'https://via.placeholder.com/400x300?text=No+Image',
    rating: destination.rating || 0,
    reviews: destination.review_count || 0,
    tags: [],
    region: getRegionName(destination.areacode || destination.area_code),
    is_bookmarked: destination.is_bookmarked || false
  }
}

// 데이터 로드 (DB 기반)
const loadDestinations = async () => {
  loading.value = true

  try {

    // DB에서 여행지 목록 가져오기
    const params = {
      page: currentPage.value,
      page_size: itemsPerPage
    }

    // 지역 필터
    if (selectedRegion.value) {
      params.area_code = selectedRegion.value
    }

    // 카테고리 필터 (content_type_id)
    if (contentTypeId.value) {
      params.content_type_id = contentTypeId.value
    }

    // 검색어
    if (searchQuery.value) {
      params.search = searchQuery.value
    }

    // 정렬
    if (sortBy.value === 'popular') {
      params.ordering = 'popular'
    } else if (sortBy.value === 'rating') {
      params.ordering = 'rating'
    }

    // 무장애 시설 필터
    if (selectedFacilities.value.length > 0) {
      params.facilities = selectedFacilities.value.join(',')
    }

    const response = await api.getTravelSpots(params)

    if (response.data) {
      // DB 응답을 기존 API 형식에 맞게 매핑
      let results = (response.data.results || []).map(item => ({
        contentid: item.content_id,
        contenttypeid: item.content_type_id,
        title: item.name,
        addr1: item.address,
        areacode: item.area_code,
        sigungucode: item.sigungu_code,
        mapx: item.longitude,
        mapy: item.latitude,
        firstimage: item.image_url,
        firstimage2: item.thumbnail_url,
        overview: item.description,
        tel: item.tel,
        rating: item.rating,
        review_count: item.review_count
      }))

      destinations.value = results
      totalCount.value = response.data.count || results.length
    }
  } catch (error) {
    console.error('❌ 데이터 로드 실패:', error)
    destinations.value = []
    totalCount.value = 0
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  currentPage.value = 1
  loadDestinations()
}

const toggleAccessibilityType = (type) => {
  const index = selectedAccessibilityTypes.value.indexOf(type)
  if (index > -1) {
    selectedAccessibilityTypes.value.splice(index, 1)
  } else {
    selectedAccessibilityTypes.value.push(type)
  }

  // 무장애 유형 변경 시 시설 정보 초기화
  // 현재 선택된 시설 중 새로운 availableFacilities에 없는 것들 제거
  const availableValues = new Set(
    selectedAccessibilityTypes.value.flatMap(t =>
      (facilityOptions[t] || []).map(f => f.value)
    )
  )
  selectedFacilities.value = selectedFacilities.value.filter(f =>
    availableValues.has(f)
  )
}

const toggleFacility = (facility) => {
  const index = selectedFacilities.value.indexOf(facility)
  if (index > -1) {
    selectedFacilities.value.splice(index, 1)
  } else {
    selectedFacilities.value.push(facility)
  }
}

const toggleFilterCollapse = () => {
  isFilterCollapsed.value = !isFilterCollapsed.value
}

const handleFilterSearch = () => {
  currentPage.value = 1
  loadDestinations()
}

const changePage = (page) => {
  if (page >= 1 && page <= totalPages.value) {
    currentPage.value = page
    loadDestinations()
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }
}

const changePageGroup = (direction) => {
  const maxDisplayed = 5
  let newPage

  if (direction > 0) {
    // 다음 그룹: 현재 표시된 마지막 페이지 + 1
    newPage = displayedPages.value[displayedPages.value.length - 1] + 1
  } else {
    // 이전 그룹: 현재 표시된 첫 페이지 - maxDisplayed
    newPage = displayedPages.value[0] - maxDisplayed
  }

  changePage(newPage)
}

const handleCardClick = (destination) => {
  // 상세 페이지로 이동 (contentTypeId 포함하여 조회 안정성 향상)
  const typeId = destination.contenttypeid || '12'
  window.location.href = `/travel/${destination.contentid}?contentTypeId=${typeId}`
}

// 북마크 상태 변경 핸들러
const handleBookmarkChanged = ({ id, bookmarked }) => {

  // destinations 배열에서 해당 항목 찾아서 업데이트
  const index = destinations.value.findIndex(dest => dest.id === id)
  if (index !== -1) {
    destinations.value[index].is_bookmarked = bookmarked
  }
}

// 카테고리 변경시 데이터 자동 새로고침
watch(() => route.query.category, () => {
  currentPage.value = 1
  selectedRegion.value = ''
  selectedAccessibilityTypes.value = []
  selectedFacilities.value = []
  searchQuery.value = ''
  loadDestinations()
})

// 무장애 시설 필터 변경 시 검색
watch(selectedFacilities, () => {
  currentPage.value = 1
  loadDestinations()
})

onMounted(() => {
  loadDestinations()
})
</script>

<style scoped>
.travel-view {
  min-height: 100vh;
  background: #f9fafb;
}

/* 헤더 섹션 */
.travel-header {
  position: relative;
  padding: 8rem 2rem 6rem;
  color: white;
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
  min-height: 500px;
  display: flex;
  align-items: center;
}

/* 배경 이미지 */
.header-beach {
  background-image: url('@/assets/travel.png');
}

.header-room {
  background-image: url('@/assets/bed.png');
}

.header-restaurant {
  background-image: url('@/assets/food.png');
}

.header-default {
  background: linear-gradient(135deg, #1f2937 0%, #111827 100%);
}

/* 어두운 오버레이 */
.header-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 1;
}

.header-content {
  position: relative;
  z-index: 2;
}

.container {
  max-width: 1400px;
  margin: 0 auto;
  width: 100%;
}

.page-title {
  font-size: 3.5rem;
  font-weight: 900;
  margin: 0 0 1.5rem 0;
  text-align: center;
  text-shadow: 2px 2px 8px rgba(0, 0, 0, 0.3);
}

.page-subtitle {
  font-size: 1.35rem;
  text-align: center;
  margin: 0 0 3rem 0;
  opacity: 0.95;
  text-shadow: 1px 1px 4px rgba(0, 0, 0, 0.3);
}

/* 검색바 */
.search-bar {
  max-width: 1000px;
  width: 90%;
  margin: 0 auto;
  display: flex;
  background: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(10px);
  border-radius: 50px;
  overflow: hidden;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.3);
}

.search-input {
  flex: 1;
  padding: 1.25rem 2rem;
  border: none;
  font-size: 1.1rem;
  outline: none;
  color: #ffffff;
  background: transparent;
}

.search-input::placeholder {
  color: rgba(255, 255, 255, 0.7);
}

.search-btn {
  padding: 1.25rem 2rem;
  background: rgba(255, 255, 255, 0.25);
  border: none;
  color: white;
  cursor: pointer;
  transition: all 0.3s ease;
}

.search-btn:hover {
  background: rgba(255, 255, 255, 0.35);
}

/* 필터 섹션 */
.filter-section {
  background: #f3f4f6;
  padding: 2rem;
}

.filter-card {
  background: #ffffff;
  border-radius: 5px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.filter-header {
  background: linear-gradient(135deg, #1f2937 0%, #111827 100%);
  padding: 1.5rem 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  cursor: pointer;
  transition: background 0.3s ease;
}

.filter-header:hover {
  background: linear-gradient(135deg, #1f2937 0%, #111827 100%);
}

.filter-main-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: white;
  margin: 0;
}

.collapse-btn {
  background: transparent;
  border: none;
  color: white;
  font-size: 1.25rem;
  cursor: pointer;
  padding: 0.5rem;
  transition: transform 0.3s ease;
}

.filter-content {
  padding: 2rem;
  background: #f9fafb;
}

.filter-row {
  margin-bottom: 2rem;
  background: white;
  padding: 1.5rem;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.filter-row:last-child {
  margin-bottom: 0;
}

/* 무장애 유형 버튼 */
.accessibility-types {
  display: flex;
  gap: 1.5rem;
  flex-wrap: wrap;
  justify-content: center;
}

.accessibility-type-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  padding: 2rem 1.5rem;
  background: white;
  border: 3px solid #d8d8d8;
  border-radius: 7%;
  cursor: pointer;
  transition: all 0.3s ease;
  min-width: 140px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.accessibility-type-btn:hover {
  border-color: #d8d8d8;
  background: #d8d8d8;
  color: white;
  transform: translateY(-4px);
  box-shadow: 0 8px 16px rgba(156, 163, 175, 0.15);
}

.accessibility-type-btn.active {
  border-color: #d8d8d8;
  background: #d8d8d8;
  position: relative;
  color: white;
}

.accessibility-type-btn.active::after {
  content: '';
  position: absolute;
  bottom: -3px;
  left: 50%;
  transform: translateX(-50%);
  width: 92%;
  height: 4px;
  background: #9ca3af;
  border-radius: 3px 3px 0 0;
}

.accessibility-type-btn .icon-wrapper {
  width: 80px;
  height: 80px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f3f4f6;
  border-radius: 15%;
  transition: all 0.3s ease;
}

.accessibility-type-btn .icon-wrapper img {
  width: 50px;
  height: 50px;
  object-fit: contain;
}

.accessibility-type-btn.active .icon-wrapper {
  background: #fdfdfd;
}

.accessibility-type-btn span {
  font-size: 1rem;
  font-weight: 700;
  color: #374151;
}

.accessibility-type-btn.active span {
  color: #6b7280;
}

/* 시설 정보 섹션 */
.facility-title {
  font-size: 1.1rem;
  font-weight: 700;
  color: #374151;
  margin: 0 0 2rem 0;
  text-align: center;
}

/* 시설 정보 그룹 */
.facility-group {
  margin-bottom: 2rem;
}

.facility-group:last-child {
  margin-bottom: 0;
}

.facility-group-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 1.25rem;
  padding-bottom: 0.75rem;
  border-bottom: 2px solid #e5e7eb;
}

.facility-group-icon {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f3f4f6;
  border-radius: 50%;
  padding: 0.4rem;
}

.facility-group-icon img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.facility-group-label {
  font-size: 1rem;
  font-weight: 700;
  color: #1f2937;
}

.facility-divider {
  height: 1px;
  background: linear-gradient(to right, transparent, #d1d5db, transparent);
  margin: 2rem 0;
}

/* 시설 정보 버튼 */
.facility-types {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
  justify-content: flex-start;
}

.facility-btn {
  padding: 0.875rem 2rem;
  background: white;
  border: 2px solid #d1d5db;
  border-radius: 50px;
  cursor: pointer;
  font-size: 1rem;
  font-weight: 600;
  color: #6b7280;
  transition: all 0.3s ease;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.facility-btn:hover {
  border-color: #9ca3af;
  background: #f3f4f6;
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.facility-btn.active {
  background: #9ca3af;
  border-color: #9ca3af;
  color: white;
}

/* 지역 선택 및 검색 버튼 */
.region-search-row {
  display: flex;
  gap: 1rem;
  align-items: flex-end;
  justify-content: center;
  flex-wrap: wrap;
}

.region-select-wrapper {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.region-select-wrapper label {
  font-size: 0.9rem;
  font-weight: 600;
  color: #374151;
}

.region-select {
  padding: 0.875rem 1.5rem;
  border: 2px solid #d1d5db;
  border-radius: 8px;
  font-size: 1rem;
  cursor: pointer;
  background: white;
  transition: all 0.2s ease;
  min-width: 200px;
}

.region-select:hover {
  border-color: #9ca3af;
}

.region-select:focus {
  outline: none;
  border-color: #6b7280;
  box-shadow: 0 0 0 3px rgba(107, 114, 128, 0.1);
}

.search-filter-btn {
  padding: 0.875rem 3rem;
  background: linear-gradient(135deg, #374151 0%, #1f2937 100%);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

.search-filter-btn:hover {
  background: linear-gradient(135deg, #1f2937 0%, #111827 100%);
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.3);
}

.search-filter-btn:active {
  transform: translateY(0);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}


/* 로딩 */
.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  min-height: 400px;
}

.loading-spinner {
  width: 50px;
  height: 50px;
  border: 4px solid #e5e7eb;
  border-top-color: #111827;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.loading-container p {
  margin-top: 1rem;
  color: #6b7280;
  font-size: 1.1rem;
}

/* 결과 없음 */
.no-results {
  text-align: center;
  padding: 4rem 2rem;
  font-size: 1.2rem;
  color: #6b7280;
}

/* 여행지 리스트 */
.destinations-section {
  padding: 3rem 2rem;
}

.destinations-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 2rem;
  margin-bottom: 3rem;
}

/* 페이지네이션 */
.pagination {
  display: flex;
  justify-content: center;
  gap: 0.5rem;
  margin-top: 3rem;
}

.page-btn {
  padding: 0.75rem 1.25rem;
  border: 1px solid #d1d5db;
  background: white;
  color: #374151;
  border-radius: 8px;
  font-size: 0.95rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.page-btn:hover:not(:disabled) {
  background: #f3f4f6;
  border-color: #9ca3af;
}

.page-btn.active {
  background: #111827;
  color: white;
  border-color: #111827;
}

.page-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* 반응형 */
@media (max-width: 768px) {
  .page-title {
    font-size: 2rem;
  }

  .page-subtitle {
    font-size: 1rem;
  }

  .filter-card {
    padding: 1.5rem;
  }

  .filter-main-title {
    font-size: 1.25rem;
  }

  .accessibility-types {
    flex-direction: column;
  }

  .accessibility-type-btn {
    width: 100%;
  }

  .facility-types {
    flex-direction: column;
    gap: 0.75rem;
  }

  .facility-checkbox {
    width: 100%;
  }

  .region-search-row {
    flex-direction: column;
  }

  .region-select {
    width: 100%;
  }

  .search-filter-btn {
    width: 100%;
  }

  .result-info {
    margin-left: 0;
    text-align: center;
  }

  .destinations-grid {
    grid-template-columns: 1fr;
    gap: 1.5rem;
  }

  .pagination {
    flex-wrap: wrap;
  }

  .page-btn {
    padding: 0.5rem 1rem;
    font-size: 0.875rem;
  }
}
</style>
