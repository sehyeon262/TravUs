<template>
  <div class="board-page">
    <NavigationBar @focus="handleFocus" />

    <main class="board-main">
      <div class="board-container">
        <!-- 헤더 섹션 -->
        <div class="board-header">
          <div class="header-content">
            <div class="header-text">
              <h1 class="board-title">여행 정보 검색</h1>
              <p class="board-subtitle">세상의 모든 여행 정보를 한 곳에서</p>
              <p class="board-description">블로그, 뉴스, 영상으로 여행지를 탐색하세요</p>
            </div>
            <div class="search-box">
              <div class="search-input-wrapper">
                <svg class="search-icon" width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M11 19C15.4183 19 19 15.4183 19 11C19 6.58172 15.4183 3 11 3C6.58172 3 3 6.58172 3 11C3 15.4183 6.58172 19 11 19Z" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  <path d="M21 21L16.65 16.65" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
                <input
                  v-model="searchQuery"
                  type="text"
                  placeholder="여행지를 검색하세요"
                  class="search-input"
                  @keyup.enter="handleSearch"
                  @focus="handleFocus"
                  aria-label="여행지 검색"
                />
              </div>
            </div>
          </div>
          <div class="header-character">
            <img src="@/assets/search.png" alt="캐릭터" class="character-icon" />
          </div>
        </div>

        <!-- 로딩 -->
        <div v-if="isLoading" class="loading-container">
          <div class="loading-spinner"></div>
          <p>검색 중...</p>
        </div>

        <!-- 검색 결과 -->
        <div v-else-if="hasSearched" class="results-container">
          <!-- 블로그 결과 -->
          <section class="result-section">
            <img src="@/assets/blog.png" alt="블로그" class="category-blog-icon" />
            <div class="result-content">
              <div v-if="blogs.length > 0" class="slider-container">
                <button class="slider-arrow slider-arrow-left" @click="scrollLeft('blog')" aria-label="이전">
                  <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                    <path d="M15 18L9 12L15 6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  </svg>
                </button>
                <div
                  ref="blogWrapper"
                  class="cards-wrapper"
                  @mousedown="(e) => handleMouseDown(e, $event.currentTarget)"
                  @mousemove="handleMouseMove"
                  @mouseup="handleMouseUp"
                  @mouseleave="handleMouseLeave"
                >
                  <a
                    v-for="(blog, index) in blogs"
                    :key="index"
                    :href="blog.link"
                    target="_blank"
                    rel="noopener noreferrer"
                    class="result-card"
                  >
                    <div v-if="blog.thumbnail" class="card-thumbnail">
                      <img :src="blog.thumbnail" :alt="blog.title" />
                    </div>
                    <div class="card-content">
                      <h3 class="card-title" v-html="blog.title"></h3>
                      <p class="card-description" v-html="blog.description"></p>
                      <div class="card-meta">
                        <span class="card-author">{{ blog.bloggername || '네이버 블로그' }}</span>
                      </div>
                    </div>
                  </a>
                </div>
                <button class="slider-arrow slider-arrow-right" @click="scrollRight('blog')" aria-label="다음">
                  <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                    <path d="M9 18L15 12L9 6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  </svg>
                </button>
              </div>
              <div v-else class="no-results">
                <p>블로그 검색 결과가 없습니다.</p>
              </div>
            </div>
          </section>

          <!-- 뉴스 결과 -->
          <section class="result-section">
            <img src="@/assets/news.png" alt="뉴스" class="category-icon" />
            <div class="result-content">
              <div v-if="news.length > 0" class="slider-container">
                <button class="slider-arrow slider-arrow-left" @click="scrollLeft('news')" aria-label="이전">
                  <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                    <path d="M15 18L9 12L15 6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  </svg>
                </button>
                <div
                  ref="newsWrapper"
                  class="cards-wrapper"
                  @mousedown="(e) => handleMouseDown(e, $event.currentTarget)"
                  @mousemove="handleMouseMove"
                  @mouseup="handleMouseUp"
                  @mouseleave="handleMouseLeave"
                >
                  <a
                    v-for="(article, index) in news"
                    :key="index"
                    :href="article.link"
                    target="_blank"
                    rel="noopener noreferrer"
                    class="result-card"
                  >
                    <div v-if="article.thumbnail" class="card-thumbnail">
                      <img :src="article.thumbnail" :alt="article.title" />
                    </div>
                    <div class="card-content">
                      <h3 class="card-title" v-html="article.title"></h3>
                      <p class="card-description" v-html="article.description"></p>
                    </div>
                  </a>
                </div>
                <button class="slider-arrow slider-arrow-right" @click="scrollRight('news')" aria-label="다음">
                  <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                    <path d="M9 18L15 12L9 6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  </svg>
                </button>
              </div>
              <div v-else class="no-results">
                <p>뉴스 검색 결과가 없습니다.</p>
              </div>
            </div>
          </section>

          <!-- 유튜브 결과 -->
          <section class="result-section youtube-section">
            <div class="youtube-left">
              <img src="@/assets/youtube.png" alt="유튜브" class="category-icon-large" />
            </div>
            <div class="result-content youtube-content">
              <div v-if="videos.length > 0" class="video-grid-container">
                <a
                  v-for="(video, index) in videos.slice(0, 6)"
                  :key="index"
                  :href="`https://www.youtube.com/watch?v=${video.id.videoId}`"
                  target="_blank"
                  rel="noopener noreferrer"
                  class="video-grid-card"
                >
                  <div class="video-grid-thumbnail">
                    <img :src="video.snippet.thumbnails.medium.url" :alt="video.snippet.title" />
                    <div class="play-button">
                      <svg width="48" height="48" viewBox="0 0 48 48">
                        <circle cx="24" cy="24" r="24" fill="rgba(0,0,0,0.7)" />
                        <path d="M18 14L34 24L18 34V14Z" fill="white"/>
                      </svg>
                    </div>
                  </div>
                  <div class="video-grid-info">
                    <h3 class="video-grid-title">{{ video.snippet.title }}</h3>
                    <p class="video-grid-channel">{{ video.snippet.channelTitle }}</p>
                  </div>
                </a>
              </div>
              <div v-else class="no-results">
                <p>영상 검색 결과가 없습니다.</p>
              </div>
            </div>
          </section>
        </div>

        <!-- 초기 상태 -->
        <div v-else class="empty-state">
          <img src="@/assets/searchicon.png" alt="검색" class="empty-icon" />
          <h3>여행지를 검색해보세요</h3>
        </div>
      </div>
    </main>

    <FooterSection @focus="handleFocus" />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import NavigationBar from '@/components/common/NavigationBar.vue'
import FooterSection from '@/components/common/FooterSection.vue'
import { useTTS } from '@/composables/useTTS'
import { searchBlog, searchNews, searchYoutube } from '@/services/boardApi'

const { speak } = useTTS()

const searchQuery = ref('')
const isLoading = ref(false)
const hasSearched = ref(false)

const blogs = ref([])
const news = ref([])
const videos = ref([])

// Refs for scroll containers
const blogWrapper = ref(null)
const newsWrapper = ref(null)
const videoWrapper = ref(null)

// 드래그 스크롤 상태
const isDragging = ref(false)
const startX = ref(0)
const scrollLeftPos = ref(0)
const currentWrapper = ref(null)

const handleSearch = async () => {
  if (!searchQuery.value.trim()) {
    return
  }

  isLoading.value = true
  hasSearched.value = true
  blogs.value = []
  news.value = []
  videos.value = []

  try {
    const query = searchQuery.value.trim() + ' 여행'

    // 병렬로 API 호출 - 더 많은 결과 가져오기
    const [blogResults, newsResults, videoResults] = await Promise.all([
      searchBlog(query, 20),
      searchNews(query, 20),
      searchYoutube(query, 20)
    ])

    blogs.value = blogResults || []
    news.value = newsResults || []
    videos.value = videoResults || []
  } catch (error) {
    console.error('검색 실패:', error)
  } finally {
    isLoading.value = false
  }
}

const scrollLeft = (type) => {
  const wrapperMap = {
    blog: blogWrapper,
    news: newsWrapper,
    video: videoWrapper
  }

  const wrapper = wrapperMap[type]?.value
  if (wrapper) {
    wrapper.scrollBy({
      left: -400,
      behavior: 'smooth'
    })
  }
}

const scrollRight = (type) => {
  const wrapperMap = {
    blog: blogWrapper,
    news: newsWrapper,
    video: videoWrapper
  }

  const wrapper = wrapperMap[type]?.value
  if (wrapper) {
    wrapper.scrollBy({
      left: 400,
      behavior: 'smooth'
    })
  }
}

const handleFocus = (text) => {
  if (text) {
    speak(text)
  }
}

// 드래그 스크롤 함수
const handleMouseDown = (e, wrapper) => {
  isDragging.value = true
  currentWrapper.value = wrapper
  startX.value = e.pageX - wrapper.offsetLeft
  scrollLeftPos.value = wrapper.scrollLeft
  wrapper.style.cursor = 'grabbing'
  wrapper.style.userSelect = 'none'
}

const handleMouseMove = (e) => {
  if (!isDragging.value || !currentWrapper.value) return
  e.preventDefault()
  const x = e.pageX - currentWrapper.value.offsetLeft
  const walk = (x - startX.value) * 2 // 스크롤 속도 조절
  currentWrapper.value.scrollLeft = scrollLeftPos.value - walk
}

const handleMouseUp = () => {
  if (currentWrapper.value) {
    currentWrapper.value.style.cursor = 'grab'
    currentWrapper.value.style.userSelect = 'auto'
  }
  isDragging.value = false
  currentWrapper.value = null
}

const handleMouseLeave = () => {
  if (isDragging.value && currentWrapper.value) {
    currentWrapper.value.style.cursor = 'grab'
    currentWrapper.value.style.userSelect = 'auto'
  }
  isDragging.value = false
  currentWrapper.value = null
}
</script>

<style scoped>
.board-page {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: #ffffff;
}

.board-main {
  flex: 1;
  padding: 0;
}

.board-container {
  max-width: 100%;
  margin: 0 auto;
  padding: 0;
}

/* 헤더 */
.board-header {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 2rem;
  margin-bottom: 3rem;
  padding: 4rem;
  background-image: url('@/assets/board_background.png');
  background-repeat: no-repeat;
  background-position: center center;
  background-size: cover;
  position: relative;
  overflow: hidden;
  min-height: 500px;
}

.board-header::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  /* background: rgba(0, 0, 0, 0.1); */
  z-index: 1;
}

.header-content {
  position: relative;
  z-index: 2;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2rem;
  text-align: center;
}

.header-text {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
}

.board-title {
  font-size: 3rem;
  font-weight: 900;
  color: #ffffff;
  margin: 0;
  letter-spacing: -3px;
}

.board-subtitle {
  font-size: 1.5rem;
  color: #ffffff;
  margin: 0;
  font-weight: 500;
}

.board-description {
  font-size: 1.1rem;
  color: #ffffff;
  margin: 0;
}

.search-box {
  width: 100%;
  max-width: 600px;
}

.search-input-wrapper {
  position: relative;
  width: 100%;
}

.search-icon {
  position: absolute;
  left: 1.5rem;
  top: 50%;
  transform: translateY(-50%);
  z-index: 1;
  pointer-events: none;
}

.search-input {
  width: 100%;
  padding: 1.2rem 1.75rem 1.2rem 3.5rem;
  font-size: 1.05rem;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: 50px;
  transition: all 0.3s ease;
  background: rgba(255, 255, 255, 0.2);
  color: #ffffff;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.search-input::placeholder {
  color: rgba(255, 255, 255, 0.7);
}

.search-input:focus {
  outline: none;
  background: rgba(255, 255, 255, 0.3);
  border-color: rgba(255, 255, 255, 0.5);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.25);
  transform: translateY(-2px);
}

.header-character {
  position: relative;
  z-index: 2;
  flex-shrink: 0;
}

.character-icon {
  width: 250px;
  height: auto;
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

.empty-state img{
  height: 120px;
  width: 250px;
  transform: rotate(30deg)
}

.empty-state h3 {
  color: #3d3c3c !important;
  font-size: 1.5rem;
  font-weight: 700;
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

/* 결과 섹션 */
.results-container {
  display: flex;
  flex-direction: column;
  gap: 3rem;
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 3rem;
}

.result-section {
  display: flex;
  gap: 2rem;
  align-items: flex-start;
}

.category-blog-icon {
  flex-shrink: 0;
  width: 170px;
  height: 150px;
  object-fit: contain;
  border-radius: 12px;
  padding: 1rem;
  margin-top: 70px;
}


.category-icon {
  flex-shrink: 0;
  width: 210px;
  height: 150px;
  object-fit: contain;
  border-radius: 12px;
  padding: 1rem;
  margin-top: 30px;
  margin-right: -30px;
}

.category-icon-large {
  width: 230px;
  height: 150px;
  object-fit: contain;
  border-radius: 12px;
  padding: 1.5rem;

}

.result-content {
  flex: 1;
  overflow: hidden;
}

/* 슬라이더 컨테이너 */
.slider-container {
  position: relative;
  display: flex;
  align-items: center;
  gap: 1rem;
}

.slider-arrow {
  flex-shrink: 0;
  width: 48px;
  height: 48px;
  border-radius: 50%;
  border: none;
  background: #ffffff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
  color: #667eea;
  z-index: 10;
}

.slider-arrow:hover {
  background: #667eea;
  color: #ffffff;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
  transform: scale(1.1);
}

.slider-arrow:active {
  transform: scale(0.95);
}

.slider-arrow-left {
  margin-right: -0.5rem;
}

.slider-arrow-right {
  margin-left: -0.5rem;
}

.cards-wrapper {
  display: flex;
  gap: 1.5rem;
  overflow-x: hidden;
  padding: 1rem 0;
  scroll-behavior: smooth;
  scrollbar-width: none;
  cursor: grab;
  user-select: none;
}

.cards-wrapper:active {
  cursor: grabbing;
}

.cards-wrapper::-webkit-scrollbar {
  display: none;
}

/* 카드 스타일 */
.result-card {
  flex-shrink: 0;
  width: 320px;
  background: #ffffff;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  text-decoration: none;
  color: inherit;
  display: flex;
  flex-direction: column;
}

.result-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 8px 24px rgba(102, 126, 234, 0.2);
}

.card-thumbnail {
  width: 100%;
  height: 180px;
  background: #f3f4f6;
  overflow: hidden;
  position: relative;
}

.card-thumbnail img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
}

.result-card:hover .card-thumbnail img {
  transform: scale(1.05);
}

.card-content {
  padding: 1.25rem;
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.card-title {
  font-size: 1.1rem;
  font-weight: 700;
  color: #1a1a1a;
  line-height: 1.4;
  margin: 0;
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.result-card:hover .card-title {
  color: #667eea;
}

.card-description {
  font-size: 0.95rem;
  color: #666;
  line-height: 1.6;
  margin: 0;
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
}

.card-meta {
  margin-top: auto;
  padding-top: 0.75rem;
  border-top: 1px solid #e5e7eb;
}

.card-author {
  font-size: 0.875rem;
  color: #667eea;
  font-weight: 600;
}

.card-channel {
  font-size: 0.875rem;
  color: #666;
  margin: 0;
}

/* 유튜브 섹션 */
.youtube-section {
  display: flex;
  gap: 3rem;
  align-items: flex-start;
}

.youtube-left {
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.youtube-content {
  flex: 1;
}

.video-grid-container {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1.5rem;
}

.video-grid-card {
  background: #ffffff;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  text-decoration: none;
  color: inherit;
  display: flex;
  flex-direction: column;
}

.video-grid-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 8px 24px rgba(102, 126, 234, 0.2);
}

.video-grid-thumbnail {
  position: relative;
  width: 100%;
  padding-top: 56.25%; /* 16:9 비율 */
  background: #f3f4f6;
  overflow: hidden;
}

.video-grid-thumbnail img {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
}

.video-grid-card:hover .video-grid-thumbnail img {
  transform: scale(1.05);
}

.play-button {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  opacity: 0;
  transition: opacity 0.3s ease;
  pointer-events: none;
}

.video-grid-card:hover .play-button {
  opacity: 1;
}

.video-grid-info {
  padding: 1rem;
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.video-grid-title {
  font-size: 1rem;
  font-weight: 700;
  color: #1a1a1a;
  line-height: 1.4;
  margin: 0;
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.video-grid-card:hover .video-grid-title {
  color: #667eea;
}

.video-grid-channel {
  font-size: 0.875rem;
  color: #666;
  margin: 0;
}


/* 빈 상태 */
.empty-state {
  text-align: center;
  padding: 4rem 2rem;
  min-height: 400px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.empty-icon {
  width: 150px;
  height: 150px;
  margin-bottom: 2rem;
  opacity: 0.7;
}

.empty-state h3 {
  font-size: 1.5rem;
  font-weight: 700;
  color: #1a1a1a;
  margin-bottom: 1rem;
}

.empty-state p {
  font-size: 1.05rem;
  color: #666;
  line-height: 1.8;
}

.no-results {
  text-align: center;
  padding: 3rem 2rem;
  color: #999;
  font-size: 1rem;
}

/* 반응형 */
@media (max-width: 1024px) {
  .board-header {
    flex-direction: column;
    text-align: center;
    padding: 2rem;
  }

  .header-content {
    align-items: center;
  }

  .search-box {
    max-width: 100%;
  }

  .character-icon {
    width: 200px;
  }

  .result-section {
    flex-direction: column;
    align-items: center;
  }

  .category-icon {
    width: 100px;
    height: 100px;
  }

  .category-icon-large {
    width: 120px;
    height: 120px;
  }

  .slider-arrow {
    width: 40px;
    height: 40px;
  }

  .youtube-section {
    flex-direction: column;
  }

  .video-grid-container {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .board-title {
    font-size: 2rem;
  }

  .board-subtitle {
    font-size: 1.2rem;
  }

  .board-description {
    font-size: 1rem;
  }

  .character-icon {
    width: 150px;
  }

  .result-card {
    width: 280px;
  }

  .category-icon {
    width: 80px;
    height: 80px;
  }

  .category-icon-large {
    width: 100px;
    height: 100px;
  }

  .slider-arrow {
    width: 36px;
    height: 36px;
  }

  .video-grid-container {
    grid-template-columns: 1fr;
  }
}
</style>
