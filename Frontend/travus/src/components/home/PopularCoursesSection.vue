<template>
  <div class="popular-wrapper">
    <section class="popular-courses-section">
      <div class="popular-courses-inner">
        <div class="title-container">
          <h2 class="popular-courses-title">
            현재 <span class="title-accent">인기 있는</span> 여행지 코스
          </h2>
          <div class="subtitle-container">
            <p class="popular-courses-subtitle">많은 분들이 선택해 주신 인기 코스만 담았어요. 편안하고 즐거운 여정을 만나보세요.</p>
          </div>
        </div>

        <div v-if="loading" class="loading-state">
          <div class="spinner"></div>
          <p>인기 코스를 불러오는 중...</p>
        </div>

        <div v-else-if="popularCourses.length > 0" class="courses-grid">
          <div
            v-for="(course, index) in popularCourses"
            :key="course.id"
            class="course-card"
            :class="{ 'center-card': index === 1 }"
            @click="navigateToCourse(course.id)"
          >
            <div class="course-image">
              <img
                :src="getCourseImage(course)"
                :alt="course.title"
                @error="handleImageError"
              />
              <div class="image-badge">{{ getAreaName(course) }}</div>
              <div class="overlay"></div>
            </div>
            <div class="course-info">
              <h3 class="course-title">{{ course.title }}</h3>
              <p class="course-description">{{ course.description || '함께 걷기 좋은 무장애 여행 코스입니다.' }}</p>
              <div class="course-meta">
                <span class="course-duration" v-if="course.estimated_duration">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                    <path d="M12 2C6.5 2 2 6.5 2 12s4.5 10 10 10 10-4.5 10-10S17.5 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8zm.5-13H11v6l5.25 3.15.75-1.23-4.5-2.67z" fill="currentColor" />
                  </svg>
                  {{ formatDuration(course.estimated_duration) }}
                </span>
                <span class="course-likes">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                    <path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z" fill="currentColor" />
                  </svg>
                  {{ course.like_count || 0 }}
                </span>
                <span class="course-views">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                    <path d="M12 4.5C7 4.5 2.73 7.61 1 12c1.73 4.39 6 7.5 11 7.5s9.27-3.11 11-7.5c-1.73-4.39-6-7.5-11-7.5zM12 17c-2.76 0-5-2.24-5-5s2.24-5 5-5 5 2.24 5 5-2.24 5-5 5zm0-8c-1.66 0-3 1.34-3 3s1.34 3 3 3 3-1.34 3-3-1.34-3-3-3z" fill="currentColor" />
                  </svg>
                  {{ course.view_count || 0 }}
                </span>
              </div>
            </div>
          </div>
        </div>

        <div v-else class="empty-state">
          <p>아직 인기 코스가 없습니다.</p>
        </div>
      </div>
    </section>

    <section class="story-banner-section">
      <div class="story-inner program-layout">
        <div class="program-list">
          <div class="program-item">
            <div class="program-image-wrapper">
              <div class="program-image">
                <img :src="bannerSources.banner1" alt="바다를 바라보는 여행자와 안내견" />
              </div>
              <span class="vertical-label">Safe Journey</span>
            </div>
            <div class="program-text">
              <h4 class="program-heading">당신의 여행이 안전하도록</h4>
              <p class="program-desc">작은 불편함도 놓치지 않아요. <br><span class="highlight-text">모든 이동과 숙박, 안내</span>까지 세심하게 준비해서 <span class="highlight-text">편안한 출발</span>을 약속드려요.</p>
            </div>
          </div>

          <div class="program-item reversed">
            <div class="program-text">
              <h4 class="program-heading">함께라서 더 즐거운 길</h4>
              <p class="program-desc"><span class="highlight-text">휠체어도, 유모차도 자유롭게</span> 지나갈 수 있어요. <br>쉼터와 편의시설까지 꼼꼼히 살펴 <span class="highlight-text">누구나 편안한 여행길</span>을 만들어요.</p>
            </div>
            <div class="program-image-wrapper">
              <div class="program-image">
                <img :src="bannerSources.banner2" alt="숲길을 함께 걷는 여행자들" />
              </div>
              <span class="vertical-label">Easy Walking</span>
            </div>
          </div>

          <div class="program-item">
            <div class="program-image-wrapper">
              <div class="program-image">
                <img :src="bannerSources.banner3" alt="노을이 비치는 해변에서 즐거운 시간" />
              </div>
              <span class="vertical-label">Beautiful Moment</span>
            </div>
            <div class="program-text">
              <h4 class="program-heading">마음에 남을 순간들</h4>
              <p class="program-desc"><span class="highlight-text">웃고, 쉬고, 함께 즐기는</span> 특별한 장소들을 연결했어요. <br>돌아와서도 <span class="highlight-text">오래도록 떠올릴 따뜻한 기억</span>을 만들어 드릴게요.</p>
            </div>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/services/api'
import banner1 from '@/assets/banner1.jpg'
import banner2 from '@/assets/banner2.jpg'
import banner3 from '@/assets/banner3.jpg'

const router = useRouter()
const popularCourses = ref([])
const loading = ref(true)

const bannerSources = { banner1, banner2, banner3 }

const areaNames = {
  1: '서울',
  2: '인천',
  3: '대전',
  4: '대구',
  5: '광주',
  6: '부산',
  7: '울산',
  8: '세종',
  31: '경기',
  32: '강원',
  33: '충북',
  34: '충남',
  35: '경북',
  36: '경남',
  37: '전북',
  38: '전남',
  39: '제주'
}

const fetchPopularCourses = async () => {
  try {
    loading.value = true
    const response = await api.getCourses({ ordering: '-like_count', page_size: 3 })
    const results = response.data.results || response.data
    popularCourses.value = (results || [])
      .sort((a, b) => (b.like_count || 0) - (a.like_count || 0))
      .slice(0, 3)
  } catch (error) {
    console.error('인기 코스 불러오기 실패:', error)
    popularCourses.value = []
  } finally {
    loading.value = false
  }
}

const getPrimarySpot = (course) => {
  if (!course?.course_spots || course.course_spots.length === 0) return null
  const firstSpot = course.course_spots[0]
  return firstSpot.travel_spot || firstSpot
}

const getCourseImage = (course) => {
  const firstSpot = getPrimarySpot(course)
  if (firstSpot) {
    if (firstSpot.image_url) return firstSpot.image_url
    if (firstSpot.thumbnail_url) return firstSpot.thumbnail_url
  }
  return 'https://images.unsplash.com/photo-1469854523086-cc02fe5d8800?w=800&q=80'
}

const getAreaName = (course) => {
  const firstSpot = getPrimarySpot(course)
  const areaCode = firstSpot?.area_code || firstSpot?.areacode || course.area_code
  if (areaCode && areaNames[areaCode]) {
    return areaNames[areaCode]
  }
  return firstSpot?.name || firstSpot?.title || '여행지'
}

const formatDuration = (minutes) => {
  if (!minutes) return ''
  const hours = Math.floor(minutes / 60)
  const mins = minutes % 60
  if (hours > 0 && mins > 0) {
    return `${hours}시간 ${mins}분`
  } else if (hours > 0) {
    return `${hours}시간`
  } else {
    return `${mins}분`
  }
}

const handleImageError = (event) => {
  event.target.src = 'https://images.unsplash.com/photo-1469854523086-cc02fe5d8800?w=800&q=80'
}

const navigateToCourse = (courseId) => {
  router.push(`/course/${courseId}`)
}

onMounted(() => {
  fetchPopularCourses()
})
</script>

<style scoped>
.popular-wrapper {
  background: #eff2f8;
}

.popular-courses-section {
  padding: 4.5rem 2rem 5rem;
  margin-top: -2.5rem;
}

.popular-courses-inner {
  max-width: 1260px;
  margin: 0 auto;
}

.title-container {
  margin-bottom: 3rem;
}

.popular-courses-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: #1d1d1d;
  margin: 0 0 1rem 0;
  letter-spacing: -1px;
}

.title-accent {
  color: #394b9e;
}

.popular-courses-subtitle {
  margin: 0;
  font-size: 1rem;
  color: #242525;
  font-weight: 400;
}

.subtitle-container {
  background: #e7e7e7;
  padding: 1rem 1.5rem;
  border-radius: 3px;
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 0;
}

.spinner {
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

.loading-state p {
  color: #666;
  font-size: 1rem;
}

.empty-state {
  text-align: center;
  padding: 4rem 0;
  color: #999;
}

.courses-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 1rem;
  align-items: stretch;
  justify-items: center;
}

.course-card {
  position: relative;
  background: #ffffff;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 12px 30px rgba(0, 0, 0, 0.08);
  border: 1px solid #eef1f6;
  transition: all 0.4s ease;
  cursor: pointer;
  width: 100%;
  max-width: 360px;
  display: flex;
  flex-direction: column;
}

.course-card:hover {
  transform: translateY(-12px);
  box-shadow: 0 18px 36px rgba(86, 111, 254, 0.18);
}

.course-card.center-card {
  transform: translateY(-10px) scale(1.06);
  z-index: 2;
  max-width: 400px;
  box-shadow: 0 20px 44px rgba(86, 111, 254, 0.2);
  border-color: #e4e9ff;
}

.course-card.center-card:hover {
  transform: translateY(-16px) scale(1.08);
}

.course-image {
  position: relative;
  width: 100%;
  height: 220px;
  overflow: hidden;
}

.course-card.center-card .course-image {
  height: 250px;
}

.course-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.4s ease;
}

.course-card:hover .course-image img {
  transform: scale(1.08);
}

.overlay {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 55%;
  background: linear-gradient(to top, rgba(0, 0, 0, 0.45), transparent);
  pointer-events: none;
}

.image-badge {
  position: absolute;
  top: 12px;
  left: 12px;
  padding: 6px 12px;
  background: rgba(255, 255, 255, 0.92);
  color: #1a1a1a;
  border-radius: 12px;
  font-weight: 700;
  font-size: 0.95rem;
  box-shadow: 0 6px 18px rgba(0, 0, 0, 0.12);
}

.course-info {
  padding: 1rem 1.2rem 1.2rem;
  flex: 1;
  display: flex;
  flex-direction: column;
}

.course-title {
  font-size: 1.15rem;
  font-weight: 700;
  color: #1a1a1a;
  margin: 0 0 0.65rem 0;
  line-height: 1.3;
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.course-card:hover .course-title {
  color: #667eea;
}

.course-description {
  font-size: 0.9rem;
  color: #596072;
  line-height: 1.5;
  margin: 0 0 1rem 0;
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  min-height: 2.5em;
}

.course-meta {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding-top: 0.75rem;
  margin-top: auto;
  border-top: 1px solid #f0f0f0;
  font-size: 0.85rem;
}

.course-duration,
.course-likes,
.course-views {
  display: flex;
  align-items: center;
  gap: 0.3rem;
  font-weight: 600;
}

.course-duration svg,
.course-likes svg,
.course-views svg {
  width: 16px;
  height: 16px;
}

.course-duration {
  color: #667eea;
  background: rgba(102, 126, 234, 0.08);
  padding: 6px 10px;
  border-radius: 10px;
}

.course-likes {
  color: #e85d75;
}

.course-views {
  color: #888;
}

.story-banner-section {
  padding: 14rem 2rem 15rem;
  background: #ffffff;
}

.story-inner {
  max-width: 1260px;
  margin: 0 auto;
}


.program-list {
  display: flex;
  flex-direction: column;
  gap: 5rem;
}

.program-item {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 3rem;
  align-items: center;
}

.program-item.reversed {
  grid-template-columns: 1fr 1fr;
}

.program-image-wrapper {
  position: relative;
  display: flex;
  align-items: center;
  gap: 1rem;
}

.program-image {
  position: relative;
  border-radius: 0;
  overflow: hidden;
  box-shadow: none;
  flex: 1;
}

.program-image img {
  width: 100%;
  height: auto;
  display: block;
  object-fit: cover;
  filter: none;
}

.vertical-label {
  position: static;
  writing-mode: vertical-rl;
  text-orientation: mixed;
  font-size: 0.7rem;
  font-weight: 600;
  letter-spacing: 0.1em;
  color: #4169E1;
  text-transform: capitalize;
  white-space: nowrap;
}

.program-item.reversed .program-image-wrapper {
  flex-direction: row-reverse;
}

.program-text {
  padding: 0 1rem;
}

.program-heading {
  margin: 0 0 1rem 0;
  font-size: 1.25rem;
  font-weight: 700;
  color: #000000;
  letter-spacing: -0.3px;
}

.program-desc {
  margin: 0;
  font-size: 0.95rem;
  line-height: 1.8;
  color: #333333;
}

.highlight-text {
  color: #4169E1;
  font-weight: 500;
}

@media (max-width: 1180px) {
  .courses-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .program-item,
  .program-item.reversed {
    grid-template-columns: 1fr;
    gap: 2rem;
  }

  .program-image-wrapper,
  .program-item.reversed .program-image-wrapper {
    flex-direction: row;
  }

  .program-list {
    gap: 3rem;
  }
}

@media (max-width: 768px) {
  .popular-courses-section {
    padding: 3rem 1.5rem;
    margin-top: -2rem;
  }

  .popular-courses-title {
    font-size: 1.5rem;
    margin-bottom: 2rem;
  }

  .courses-grid {
    grid-template-columns: 1fr;
  }

  .course-image {
    height: 220px;
  }

  .course-card.center-card {
    transform: none;
  }

  .story-banner-section {
    padding: 5rem 1.5rem 4rem;
  }

  .program-list {
    gap: 2.5rem;
  }

  .program-item,
  .program-item.reversed {
    gap: 1.5rem;
  }

  .program-heading {
    font-size: 1.1rem;
  }

  .program-desc {
    font-size: 0.9rem;
  }
}
</style>
