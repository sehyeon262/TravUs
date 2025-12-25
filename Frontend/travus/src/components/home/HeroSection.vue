<template>
  <section class="hero-section" tabindex="0" @focus="handleFocus">
    <div class="hero-slider">
      <transition name="fade">
        <div
          :key="currentSlide"
          class="hero-slide"
          :style="{ backgroundImage: `url(${images[currentSlide]})` }"
        >
          <div class="hero-overlay"></div>
          <div class="hero-content">
            <div class="hero-badge">
              <span class="badge-text">{{ content.badge }}</span>
            </div>
            <h1 class="hero-title" data-text="모두를 위한 여행, TRAVUS">
              {{ content.title }}
            </h1>
            <p class="hero-subtitle">{{ content.subtitle }}</p>
            <button class="hero-cta" @click="handleCTA" @focus="handleFocus" :aria-label="content.ctaText">
              {{ content.ctaText }}
              <span class="cta-arrow">→</span>
            </button>
          </div>
        </div>
      </transition>
    </div>

    <!-- 슬라이드 컨트롤 -->
    <div class="slide-controls">
      <button
        class="control-btn pause-btn"
        @click="toggleAutoPlay"
        @focus="handleFocus"
        :aria-label="isPlaying ? '슬라이드 일시정지' : '슬라이드 재생'"
      >
        <span v-if="isPlaying">⏸</span>
        <span v-else>▶</span>
      </button>
      <div class="slide-pagination">
        <button
          class="prev-btn"
          @click="prevSlide"
          @focus="handleFocus"
          aria-label="이전 슬라이드"
        >
          ‹
        </button>
        <span class="page-number">{{ currentSlide + 1 }} / {{ images.length }}</span>
        <button
          class="next-btn"
          @click="nextSlide"
          @focus="handleFocus"
          aria-label="다음 슬라이드"
        >
          ›
        </button>
      </div>
    </div>

    <!-- 스크롤 인디케이터 -->
    <div class="scroll-indicator">
      <span class="scroll-text">Scroll</span>
      <span class="scroll-icon">↓</span>
    </div>
  </section>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import hero1 from '@/assets/hero1.jpg'
import hero2 from '@/assets/hero2.jpg'

const emit = defineEmits(['focus'])

// 배경 이미지 목록
const images = ref([hero1, hero2])

// 고정된 텍스트 콘텐츠
const content = {
  badge: '모두를 위한 여행, TRAVUS',
  title: '함께라서 더 넓은 여행',
  subtitle: '걸음의 속도가 달라도,\n바라보는 높이가 달라도 괜찮습니다.\nTravUs가 여행의 모든 순간을 함께할게요.',
  ctaText: 'TRAVUS와 함께하기'
}

const currentSlide = ref(0)
const isPlaying = ref(true)
const isImagesLoaded = ref(false)
let slideInterval = null

const nextSlide = () => {
  currentSlide.value = (currentSlide.value + 1) % images.value.length
}

const prevSlide = () => {
  currentSlide.value = (currentSlide.value - 1 + images.value.length) % images.value.length
}

const toggleAutoPlay = () => {
  isPlaying.value = !isPlaying.value
  if (isPlaying.value) {
    slideInterval = setInterval(nextSlide, 5000)
  } else {
    if (slideInterval) {
      clearInterval(slideInterval)
      slideInterval = null
    }
  }
}

const handleCTA = () => {
  // 실제 동작 추가 가능
}

const handleFocus = (event) => {
  const text =
    event.target.getAttribute('data-text') ||
    event.target.innerText ||
    event.target.getAttribute('aria-label')
  emit('focus', text)
}

// 이미지 프리로드 최적화 - 첫 번째 이미지 우선 로딩
const preloadImages = async () => {
  try {
    // 첫 번째 이미지를 우선 로드
    const firstImg = new Image()
    await new Promise((resolve, reject) => {
      firstImg.onload = resolve
      firstImg.onerror = reject
      firstImg.src = images.value[0]
    })

    // 첫 번째 이미지 로드 완료
    isImagesLoaded.value = true

    // 나머지 이미지는 백그라운드에서 로드
    images.value.slice(1).forEach((src) => {
      const img = new Image()
      img.src = src
    })
  } catch (error) {
    console.error('이미지 로드 실패:', error)
    isImagesLoaded.value = true // 에러가 나도 컨텐츠는 보여줌
  }
}

onMounted(async () => {
  // 이미지 미리 로드
  await preloadImages()

  // 자동 슬라이드 (10초마다)
  slideInterval = setInterval(nextSlide, 10000)
})

onUnmounted(() => {
  if (slideInterval) {
    clearInterval(slideInterval)
  }
})
</script>

<style scoped>
.hero-section {
  position: relative;
  width: 100%;
  height: 100vh;
  overflow: hidden;
  background-color: #000; /* 검은색 배경으로 변경 */
}

.hero-slider {
  width: 100%;
  height: 100%;
  position: relative;
}

.hero-slide {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
  display: flex;
  align-items: center;
  justify-content: flex-start;
  /* GPU 가속 및 성능 최적화 */
  will-change: opacity;
  transform: translateZ(0);
  backface-visibility: hidden;
}

.hero-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(
    to right,
    rgba(0, 0, 0, 0.75) 0%,
    rgba(0, 0, 0, 0.5) 50%,
    rgba(0, 0, 0, 0.2) 100%
  );
}

.hero-content {
  position: relative;
  z-index: 1;
  text-align: left;
  color: white;
  padding: 0 5%;
  max-width: 800px;
  margin-left: 5%;
  animation: fadeInUp 0.8s ease-out;
  /* GPU 가속을 위한 속성 추가 */
  will-change: opacity, transform;
  transform: translateZ(0);
  backface-visibility: hidden;
}

.hero-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  background: rgba(255, 255, 255, 0.15);
  padding: 0.5rem 1rem;
  border-radius: 20px;
  margin-bottom: 2rem;
  backdrop-filter: blur(10px);
  font-size: 0.9rem;
  font-weight: 500;
}

.badge-icon {
  font-size: 1.2rem;
}

.hero-title {
  font-size: 3.5rem;
  font-weight: 700;
  margin-bottom: 2rem;
  line-height: 1.3;
  letter-spacing: -0.02em;
}

.hero-subtitle {
  font-size: 1.4rem;
  font-weight: 300;
  line-height: 1.8;
  margin-bottom: 3rem;
  white-space: pre-line;
  opacity: 0.95;
}

.hero-cta {
  display: inline-flex;
  align-items: center;
  gap: 0.75rem;
  background: transparent;
  color: white;
  border: 2px solid white;
  padding: 1rem 2rem;
  font-size: 1rem;
  font-weight: 500;
  border-radius: 30px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.hero-cta:hover {
  background: white;
  color: #000;
  transform: translateX(5px);
}

.hero-cta:focus {
  outline: 3px solid #ffd700;
  outline-offset: 3px;
}

.cta-arrow {
  font-size: 1.2rem;
  transition: transform 0.3s ease;
}

.hero-cta:hover .cta-arrow {
  transform: translateX(5px);
}

/* 슬라이드 컨트롤 */
.slide-controls {
  position: absolute;
  bottom: 3rem;
  left: 5%;
  display: flex;
  align-items: center;
  gap: 2rem;
  z-index: 10;
  color: white;
}

.control-btn {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.2);
  border: 2px solid white;
  color: white;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.2rem;
  backdrop-filter: blur(10px);
}

.control-btn:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: scale(1.1);
}

.control-btn:focus {
  outline: 3px solid #ffd700;
  outline-offset: 3px;
}

.slide-pagination {
  display: flex;
  align-items: center;
  gap: 1rem;
  font-size: 1rem;
  font-weight: 500;
}

.prev-btn,
.next-btn {
  width: 30px;
  height: 30px;
  background: transparent;
  border: none;
  color: white;
  font-size: 1.5rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.prev-btn:hover,
.next-btn:hover {
  transform: scale(1.2);
}

.prev-btn:focus,
.next-btn:focus {
  outline: 2px solid #ffd700;
  outline-offset: 2px;
  border-radius: 4px;
}

.page-number {
  min-width: 50px;
  text-align: center;
}

.scroll-indicator {
  position: absolute;
  left: 50%;
  transform: translateX(-50%);
  bottom: 3rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.9rem;
  color: white;
  z-index: 10;
  animation: bounce 2s infinite;
}

.scroll-icon {
  font-size: 1.5rem;
}

/* 페이드 트랜지션 - 크로스페이드로 빠르게 전환 */
.fade-enter-active {
  transition: opacity 0.6s ease-in-out;
  /* GPU 가속 */
  transform: translateZ(0);
  will-change: opacity;
}

.fade-leave-active {
  transition: opacity 0.6s ease-in-out;
  /* GPU 가속 */
  transform: translateZ(0);
  will-change: opacity;
}

.fade-enter-from {
  opacity: 0;
}

.fade-leave-to {
  opacity: 0;
}

.fade-enter-to {
  opacity: 1;
}

.fade-leave-from {
  opacity: 1;
}

/* 애니메이션 */
@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes bounce {
  0%,
  100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-10px);
  }
}

/* 반응형 */
@media (max-width: 1024px) {
  .hero-content {
    margin-left: 3%;
    padding: 0 3%;
  }

  .hero-title {
    font-size: 2.8rem;
  }

  .hero-subtitle {
    font-size: 1.2rem;
  }

  .slide-controls {
    left: 3%;
    bottom: 2rem;
  }
}

@media (max-width: 768px) {
  .hero-content {
    margin-left: 0;
    padding: 0 1.5rem;
    max-width: 100%;
  }

  .hero-title {
    font-size: 2rem;
  }

  .hero-subtitle {
    font-size: 1rem;
    margin-bottom: 2rem;
  }

  .hero-cta {
    padding: 0.8rem 1.5rem;
    font-size: 0.9rem;
  }

  .slide-controls {
    left: 1.5rem;
    bottom: 1.5rem;
    gap: 1rem;
  }

  .control-btn {
    width: 40px;
    height: 40px;
    font-size: 1rem;
  }

  .scroll-indicator {
    bottom: 1.5rem;
    font-size: 0.8rem;
  }
}
</style>
