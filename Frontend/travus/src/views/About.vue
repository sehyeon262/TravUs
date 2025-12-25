<template>
  <div class="about-page" :style="{ fontSize: `${baseFontSize}px` }">
    <!-- 네비게이션 바 -->
    <NavigationBar
      :is-t-t-s-enabled="isTTSEnabled"
      @toggle-tts="toggleTTS"
      @font-size-change="handleFontSizeChange"
      @focus="handleFocus"
    />

    <!-- 메인 컨텐츠 -->
    <main class="main-content">
      <!-- About 섹션 -->
      <section class="section" data-section="about">
        <AboutSection @focus="handleFocus" />
      </section>

      <!-- 그라데이션 텍스트 섹션 -->
      <section class="section" data-section="gradient-text">
        <GradientTextSection @focus="handleFocus" />
      </section>

      <!-- 이미지 배너 섹션 -->
      <section class="section" data-section="image-banner">
        <ImageBannerSection @focus="handleFocus" />
      </section>

      <!-- 푸터 -->
      <FooterSection @focus="handleFocus" />
    </main>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useTTS } from '@/composables/useTTS'
import NavigationBar from '@/components/common/NavigationBar.vue'
import AboutSection from '@/components/about/AboutSection.vue'
import GradientTextSection from '@/components/about/GradientTextSection.vue'
import ImageBannerSection from '@/components/about/ImageBannerSection.vue'
import FooterSection from '@/components/common/FooterSection.vue'

// TTS 기능
const { isTTSEnabled, speak, toggleTTS: ttsToggle } = useTTS()

// 기본 폰트 사이즈
const baseFontSize = ref(16)

/**
 * TTS 토글 핸들러
 */
const toggleTTS = () => {
  const wasEnabled = isTTSEnabled.value
  ttsToggle()

  // Only speak if we just turned TTS ON (wasEnabled was false, now it's true)
  if (!wasEnabled && isTTSEnabled.value) {
    speak('TTS가 켜졌습니다')
  }
  // Silent when turning OFF
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
</script>

<style scoped>
.about-page {
  width: 100%;
  min-height: 100vh;
  overflow-x: hidden;
}

.main-content {
  width: 100%;
}

.section {
  width: 100%;
  min-height: 100vh;
}

.section[data-section='gradient-text'] {
  min-height: auto;
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
