<script setup>
import { RouterView } from 'vue-router'
import { ref, onMounted, watch } from 'vue'

const FONT_SIZE_STORAGE_KEY = 'travus-font-size'
const DEFAULT_FONT_SIZE = 16
const MIN_FONT_SIZE = 12
const MAX_FONT_SIZE = 24

// localStorage에서 폰트 크기 불러오기
const loadFontSize = () => {
  const saved = localStorage.getItem(FONT_SIZE_STORAGE_KEY)
  return saved ? parseInt(saved) : DEFAULT_FONT_SIZE
}

const baseFontSize = ref(loadFontSize())

// 폰트 크기 변경 시 CSS 변수 업데이트 및 저장
const updateFontSize = () => {
  document.documentElement.style.setProperty('--base-font-size', `${baseFontSize.value}px`)
  localStorage.setItem(FONT_SIZE_STORAGE_KEY, baseFontSize.value.toString())
}

// 전역 이벤트 리스너
const handleFontSizeChange = (event) => {
  baseFontSize.value = event.detail
}

onMounted(() => {
  updateFontSize()
  window.addEventListener('font-size-change', handleFontSizeChange)
})

watch(baseFontSize, () => {
  updateFontSize()
})
</script>

<template>
  <RouterView />
</template>

<style>
:root {
  --base-font-size: 16px;
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html {
  font-size: var(--base-font-size);
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial,
    sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  font-size: 1rem;
}

#app {
  width: 100%;
  min-height: 100vh;
}
</style>
