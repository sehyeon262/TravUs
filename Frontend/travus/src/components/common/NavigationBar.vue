<template>
  <nav class="navbar" :class="{ 'dark-mode': isDarkMode }" :style="{ fontSize: `${fontSize}px` }">
  <nav
    class="navbar"
    :class="{ 'auth-mode': isAuthPage }"
    :style="{ fontSize: `${fontSize}px` }"
  >
    <div class="navbar-container">
      <!-- 로고 -->
      <router-link to="/" class="navbar-logo" tabindex="0" @focus="handleFocus">
        <h1>TRAVUS</h1>
      </router-link>

      <!-- 메뉴 -->
      <div class="navbar-menu">
        <router-link to="/about" class="menu-item" tabindex="0" @focus="handleFocus">소개</router-link>
        <div
          class="menu-item-wrapper"
          @mouseenter="openMenu"
          @mouseleave="closeMenu"
        >
          <span class="menu-item" tabindex="0" @click="toggleMenu" @focus="openMenu">
            여행
            <svg class="dropdown-arrow" :class="{ open: showTravelMenu }" width="16" height="16" viewBox="0 0 24 24" fill="none">
              <path d="M7 10l5 5 5-5" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </span>
          <div
            class="dropdown-menu"
            v-show="showTravelMenu"
            @mouseenter="openMenu"
            @mouseleave="closeMenu"
          >
            <router-link to="/travel?category=12" class="dropdown-item" tabindex="0" @focus="handleFocus" @click="closeMenuImmediate">관광지/명소</router-link>
            <router-link to="/travel?category=32" class="dropdown-item" tabindex="0" @focus="handleFocus" @click="closeMenuImmediate">숙박</router-link>
            <router-link to="/travel?category=39" class="dropdown-item" tabindex="0" @focus="handleFocus" @click="closeMenuImmediate">음식점</router-link>
          </div>
        </div>
        <router-link to="/course" class="menu-item" tabindex="0" @focus="handleFocus">여행 코스</router-link>
        <router-link to="/camera" class="menu-item" tabindex="0" @focus="handleFocus">AI 카메라</router-link>
        <router-link to="/board" class="menu-item" tabindex="0" @focus="handleFocus">게시판</router-link>
      </div>

      <!-- 우측 컨트롤 -->
      <div class="navbar-controls">
        <!-- 글자 작게 -->
        <button class="icon-btn" tabindex="0" @click="decreaseFontSize" @focus="handleFocus" aria-label="글자 크기 줄이기">
          <span class="btn-text">-</span>
        </button>

        <!-- 글자 크게 -->
        <button class="icon-btn" tabindex="0" @click="increaseFontSize" @focus="handleFocus" aria-label="글자 크기 키우기">
          <span class="btn-text">+</span>
        </button>

        <!-- TTS -->
        <button class="icon-btn" tabindex="0" @click="toggleTTS" @focus="handleFocus" :aria-label="isTTSEnabled ? 'TTS 끄기' : 'TTS 켜기'">
          <svg v-if="isTTSEnabled" class="icon-svg" width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M3 9v6h4l5 5V4L7 9H3zm13.5 3c0-1.77-1.02-3.29-2.5-4.03v8.05c1.48-.73 2.5-2.25 2.5-4.02z" fill="currentColor"/>
          </svg>
          <svg v-else class="icon-svg" width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M16.5 12c0-1.77-1.02-3.29-2.5-4.03v2.21l2.45 2.45c.03-.2.05-.41.05-.63zm2.5 0c0 .94-.2 1.82-.54 2.64l1.51 1.51C20.63 14.91 21 13.5 21 12c0-4.28-2.99-7.86-7-8.77v2.06c2.89.86 5 3.54 5 6.71zM4.27 3L3 4.27 7.73 9H3v6h4l5 5v-6.73l4.25 4.25c-.67.52-1.42.93-2.25 1.18v2.06c1.38-.31 2.63-.95 3.69-1.81L19.73 21 21 19.73l-9-9L4.27 3zM12 4L9.91 6.09 12 8.18V4z" fill="currentColor"/>
          </svg>
        </button>

        <!-- 로그인 -->
        <button class="icon-btn" tabindex="0" @click="goLogin" @focus="handleFocus" aria-label="로그인">
          <svg class="icon-svg" width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z" fill="currentColor"/>
          </svg>
        </button>
      </div>
    </div>
  </nav>
  </nav>
</template>

<script setup>

import { computed, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const props = defineProps({
  isTTSEnabled: {
    type: Boolean,
    default: true
  }
})

const emit = defineEmits(['toggle-tts', 'font-size-change', 'focus'])

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

// 상단바 글씨색 검정색으로 바뀜!
const isAuthPage = computed(() => ['login', 'signup', 'mypage', 'mypage-info', 'mypage-comments'].includes(route.name))

const fontSize = ref(16)
const minFontSize = 12
const maxFontSize = 24
const showTravelMenu = ref(false)
let menuTimeout = null

// 상세 페이지 (/travel/:id) 감지
const isDarkMode = computed(() => {
  return route.path.startsWith('/travel/') && route.params.id
})

const increaseFontSize = () => {
  if (fontSize.value < maxFontSize) {
    fontSize.value += 2
    emit('font-size-change', fontSize.value)
  }
}

const decreaseFontSize = () => {
  if (fontSize.value > minFontSize) {
    fontSize.value -= 2
    emit('font-size-change', fontSize.value)
  }
}

const toggleTTS = () => {
  emit('toggle-tts')
}

const openMenu = () => {
  if (menuTimeout) {
    clearTimeout(menuTimeout)
    menuTimeout = null
  }
  showTravelMenu.value = true
}

const closeMenu = () => {
  menuTimeout = setTimeout(() => {
    showTravelMenu.value = false
  }, 150)
}

const toggleMenu = () => {
  showTravelMenu.value = !showTravelMenu.value
}

const closeMenuImmediate = () => {
  if (menuTimeout) {
    clearTimeout(menuTimeout)
    menuTimeout = null
  }
  showTravelMenu.value = false
}

const goLogin = () => {
  if (authStore.isLoggedIn) {
    router.push('/mypage')
    return
  }
  router.push('/login')
}

const handleFocus = (event) => {
  const text = event.target.innerText || event.target.getAttribute('aria-label')
  emit('focus', text)
}
</script>

<style scoped>
.navbar {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  background: rgba(255, 255, 255, 0);
  padding: 1.25rem 0;
  z-index: 1000;
  transition: all 0.3s ease;
}

.navbar-container {
  max-width: 1600px;
  margin: 0 auto;
  padding: 0 3rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.navbar-logo {
  text-decoration: none;
  display: block;
}

.navbar-logo h1 {
  color: #ffffff;
  font-size: 1.75rem;
  font-weight: 800;
  margin: 0;
  cursor: pointer;
  transition: all 0.3s ease;
  letter-spacing: -0.5px;
  font-family: 'Poppins', sans-serif;
}

.navbar-logo h1:hover,
.navbar-logo:focus h1 {
  color: #ffffff;
  transform: translateY(-1px);
}

/* 상세 페이지일 때 검정색 */
.navbar.dark-mode .navbar-logo h1 {
  color: #111827;
}

.navbar.dark-mode .navbar-logo h1:hover,
.navbar.dark-mode .navbar-logo:focus h1 {
  color: #374151;
}

.navbar-logo:focus {
  outline: 2px solid #3b82f6;
  outline-offset: 4px;
  border-radius: 8px;
}

.navbar.auth-mode .navbar-logo h1,
.navbar.auth-mode .navbar-logo h1:hover,
.navbar.auth-mode .navbar-logo:focus h1 {
  color: #111827;
}

.navbar-menu {
  display: flex;
  gap: 2rem;
  align-items: center;
}

.menu-item-wrapper {
  position: relative;
}

.menu-item {
  color: #ffffff;
  text-decoration: none;
  font-size: 1rem;
  font-weight: 600;
  padding: 0.5rem 0;
  transition: all 0.2s ease;
  position: relative;
  display: flex;
  align-items: center;
  gap: 0.25rem;
  cursor: pointer;
}

.navbar.auth-mode .menu-item {
  color: #111827;
}

.menu-item:hover {
  color: #111827;
}

/* 상세 페이지일 때 메뉴 글씨 검정색 */
.navbar.dark-mode .menu-item {
  color: #111827;
}

.navbar.dark-mode .menu-item:hover {
  color: #667eea;
}

.dropdown-arrow {
  transition: transform 0.3s ease;
}

.dropdown-arrow.open {
  transform: rotate(180deg);
}

.menu-item::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  width: 0;
  height: 2px;
  background: #111827;
  transition: width 0.3s ease;
}

.menu-item:hover::after,
.menu-item:focus::after {
  width: 100%;
}

.menu-item:focus {
  outline: 2px solid #3b82f6;
  outline-offset: 4px;
  border-radius: 4px;
}

.menu-item.router-link-active {
  color: #111827;
}

.menu-item.router-link-active::after {
  width: 100%;
}

/* 상세 페이지일 때 underline 색상 */
.navbar.dark-mode .menu-item::after {
  background: #667eea;
}

.navbar.dark-mode .menu-item.router-link-active {
  color: #667eea;
}

.dropdown-menu {
  position: absolute;
  top: 100%;
  left: 0;
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  margin-top: 0.5rem;
  min-width: 180px;
  padding: 0.5rem 0;
  z-index: 1000;
}

.dropdown-item {
  display: block;
  color: #374151;
  text-decoration: none;
  font-size: 0.95rem;
  font-weight: 600;
  padding: 0.75rem 1.25rem;
  transition: all 0.2s ease;
  white-space: nowrap;
}

.dropdown-item:hover,
.dropdown-item:focus {
  background: #f3f4f6;
  color: #111827;
  outline: none;
}

.dropdown-item.router-link-active {
  background: #f3f4f6;
  color: #667eea;
}

.navbar-controls {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.icon-btn {
  width: 2.5em;
  height: 2.5em;
  background: rgba(255, 255, 255, 0.9);
  border: none;
  border-radius: 50%;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.icon-btn:hover {
  background: #ffffff;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

.icon-btn:focus {
  outline: 2px solid rgba(255, 255, 255, 0.8);
  outline-offset: 2px;
}

.icon-btn:active {
  transform: translateY(0);
}

.btn-text {
  font-size: 1.2rem;
  font-weight: 600;
  color: #1a1a1a;
  line-height: 1;
}

.icon-svg {
  width: 1.125em;
  height: 1.125em;
  color: #1a1a1a;
}

@media (max-width: 768px) {
  .navbar {
    padding: 0.75rem 0;
  }

  .navbar-container {
    padding: 0 1.5rem;
  }

  .logo-wrapper h1 {
    font-size: 1.25rem;
  }

  .logo-icon {
    font-size: 1.5rem;
  }

  .navbar-menu {
    display: none;
  }

  .navbar-controls {
    gap: 0.4rem;
  }

  .icon-btn {
    width: 36px;
    height: 36px;
  }

  .btn-text {
    font-size: 1rem;
  }

  .icon-svg {
    width: 16px;
    height: 16px;
  }
}
</style>
