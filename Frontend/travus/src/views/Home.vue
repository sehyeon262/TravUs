<template>
  <div class="home-page" :style="{ fontSize: `${baseFontSize}px` }">
    <!-- 네비게이션 바 -->
    <NavigationBar
      :is-t-t-s-enabled="isTTSEnabled"
      @toggle-tts="toggleTTS"
      @font-size-change="handleFontSizeChange"
      @focus="handleFocus"
    />

    <!-- 메인 컨텐츠 - Scroll Snap Container -->
    <main class="main-content scroll-snap-container">
      <!-- Hero 섹션 -->
      <section class="section scroll-snap-section" data-section="hero">
        <HeroSection @focus="handleFocus" />
      </section>

      <!-- 카테고리 배지 섹션 -->
      <section data-section="badge">
        <BadgeSection @focus="handleFocus" />
      </section>

      <!-- 이번주 추천 섹션 -->
      <section class="section scroll-snap-section" data-section="weekly">
        <WeeklyRecommendSection @focus="handleFocus" />
      </section>

      <!-- 여행 대상 섹션
      <section class="section scroll-snap-section" data-section="target">
        <TravelTargetSection @focus="handleFocus" />
      </section> -->

      <!-- 여행지 섹션 -->
      <section class="section scroll-snap-section" data-section="destination">
        <DestinationSection @focus="handleFocus" />
      </section>

      <!-- AI 카메라 섹션 -->
      <!-- <section class="section scroll-snap-section" data-section="ai-camera">
        <AICameraSection @focus="handleFocus" />
      </section> -->

      <!-- 푸터 -->
      <FooterSection @focus="handleFocus" />
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useTTS } from '@/composables/useTTS'
import gsap from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'
import NavigationBar from '@/components/common/NavigationBar.vue'
import HeroSection from '@/components/home/HeroSection.vue'
import WeeklyRecommendSection from '@/components/home/WeeklyRecommendSection.vue'
import TravelTargetSection from '@/components/home/TravelTargetSection.vue'
import DestinationSection from '@/components/home/DestinationSection.vue'
import AICameraSection from '@/components/ai/AICameraSection.vue'
import FooterSection from '@/components/common/FooterSection.vue'
import BadgeSection from '@/components/home/BadgeSection.vue'

// GSAP ScrollTrigger 등록
gsap.registerPlugin(ScrollTrigger)

// TTS 기능
const { isTTSEnabled, speak, toggleTTS: ttsToggle } = useTTS()

// 기본 폰트 사이즈
const baseFontSize = ref(16)

/**
 * TTS 토글 핸들러
 */
const toggleTTS = () => {
  ttsToggle()
  speak(isTTSEnabled.value ? 'TTS가 켜졌습니다' : 'TTS가 꺼졌습니다')
}

/**
 * 폰트 사이즈 변경 핸들러
 */
const handleFontSizeChange = (size) => {
  baseFontSize.value = size
  speak(`글자 크기가 ${size}픽셀로 변경되었습니다`)
}

/**
 * 포커스 핸들러 (TTS 읽기)
 */
const handleFocus = (text) => {
  if (text && isTTSEnabled.value) {
    speak(text)
  }
}

onMounted(() => {
  // 각 섹션이 부드럽게 올라오는 애니메이션 (hero, target-section, destination, weekly 제외)
  const sections = document.querySelectorAll('.section:not([data-section="hero"]):not([data-section="target"]):not([data-section="destination"]):not([data-section="weekly"])')

  sections.forEach((section) => {
    gsap.fromTo(
      section,
      {
        opacity: 0,
        y: 100 // 아래에서 시작
      },
      {
        opacity: 1,
        y: 0,
        duration: 1.2,
        ease: 'power3.out',
        scrollTrigger: {
          trigger: section,
          start: 'top 80%', // 섹션이 뷰포트 80% 지점에 도달하면 시작
          end: 'top 20%',
          toggleActions: 'play none none reverse'
        }
      }
    )
  })

  // hero, target-section, destination, weekly는 즉시 보이도록
  const heroSection = document.querySelector('.section[data-section="hero"]')
  if (heroSection) {
    gsap.set(heroSection, { opacity: 1, y: 0 })
  }

  const targetSection = document.querySelector('.section[data-section="target"]')
  if (targetSection) {
    gsap.set(targetSection, { opacity: 1, y: 0 })
  }

  const destinationSection = document.querySelector('.section[data-section="destination"]')
  if (destinationSection) {
    gsap.set(destinationSection, { opacity: 1, y: 0 })
  }

  const weeklySection = document.querySelector('.section[data-section="weekly"]')
  if (weeklySection) {
    gsap.set(weeklySection, { opacity: 1, y: 0 })
  }
})

onUnmounted(() => {
  // ScrollTrigger 정리
  ScrollTrigger.getAll().forEach((trigger) => trigger.kill())
})
</script>

<style scoped>
.home-page {
  width: 100%;
  min-height: 100vh;
  overflow-x: hidden;
}

.main-content {
  width: 100%;
}

.scroll-snap-section {
  min-height: 100vh;
}

.section {
  width: 100%;
  min-height: 100vh;
  will-change: transform, opacity;
}

.section[data-section='hero'] {
  opacity: 1;
  transform: none;
}

.section[data-section='target'] {
  opacity: 1;
  transform: none;
}

.section[data-section='destination'] {
  opacity: 1;
  transform: none;
  min-height: 120vh !important;
  height: auto !important;
}

.section[data-section='weekly'] {
  opacity: 1;
  transform: none;
}

/* 전역 스타일 */
:deep(*) {
  box-sizing: border-box;
}

:deep(button),
:deep(a) {
  cursor: pointer;
}

:deep(button:focus),
:deep(a:focus),
:deep([tabindex='0']:focus) {
  outline: 3px solid #ffd700;
  outline-offset: 3px;
}

/* 스크롤바 스타일 */
:deep(::-webkit-scrollbar) {
  width: 10px;
}

:deep(::-webkit-scrollbar-track) {
  background: #f1f1f1;
}

:deep(::-webkit-scrollbar-thumb) {
  background: #667eea;
  border-radius: 5px;
}

:deep(::-webkit-scrollbar-thumb:hover) {
  background: #5568d3;
}

/* 반응형 디자인 */
@media (max-width: 768px) {
  .main-content {
    margin-top: 0;
  }
}
</style>
