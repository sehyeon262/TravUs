<template>
  <div class="login-view">
    <NavigationBar
      :is-t-t-s-enabled="isTTSEnabled"
      @toggle-tts="toggleTTS"
      @focus="handleFocus"
    />
    <div class="login-card">
      <h1 class="login-title">로그인</h1>

      <form class="login-form" @submit.prevent="handleSubmit">
        <input
          class="login-input"
          type="text"
          placeholder="아이디 또는 전화번호"
          autocomplete="username"
          v-model="form.username"
          @focus="handleFocus"
          aria-label="아이디 또는 전화번호"
        />
        <input
          class="login-input"
          type="password"
          placeholder="비밀번호"
          autocomplete="current-password"
          v-model="form.password"
          @focus="handleFocus"
          aria-label="비밀번호"
        />

        <div class="login-options">
          <label class="keep-login">
            <input type="checkbox" v-model="form.keep" />
            <span @focus="handleFocus" tabindex="0">로그인 상태 유지</span>
          </label>
        </div>

        <button
          class="login-submit"
          type="submit"
          @focus="handleFocus"
          aria-label="로그인"
        >
          로그인
        </button>

        <p v-if="errorMessage" class="login-error" role="alert">
          {{ errorMessage }}
        </p>


        <div class="login-links">
          <button
            class="text-link"
            type="button"
            @click="showPasswordResetModal = true"
            @focus="handleFocus"
            aria-label="비밀번호 찾기"
          >
            비밀번호 찾기
          </button>
          <span class="link-separator">|</span>
          <router-link class="text-link" to="/signup" @focus="handleFocus" aria-label="회원가입">
            회원가입
          </router-link>
        </div>
      </form>
    </div>

    <!-- 비밀번호 찾기 모달 -->
    <div v-if="showPasswordResetModal" class="modal-overlay" @click="closePasswordResetModal">
      <div class="modal-content" @click.stop>
        <button class="modal-close" @click="closePasswordResetModal" aria-label="닫기">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path d="M18 6L6 18M6 6l12 12" stroke-width="2" stroke-linecap="round"/>
          </svg>
        </button>

        <h2 class="modal-title">비밀번호 찾기</h2>
        <p class="modal-description">가입 시 등록한 이메일 주소를 입력해주세요.</p>

        <form @submit.prevent="handlePasswordReset" class="reset-form">
          <input
            class="login-input"
            type="email"
            placeholder="이메일 주소"
            v-model="resetEmail"
            required
            aria-label="이메일 주소"
          />

          <p v-if="resetMessage" :class="['reset-message', resetSuccess ? 'success' : 'error']">
            {{ resetMessage }}
          </p>

          <button type="submit" class="reset-submit" :disabled="isResetting">
            {{ isResetting ? '전송 중...' : '비밀번호 재설정 링크 전송' }}
          </button>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useTTS } from '@/composables/useTTS'
import { useAuthStore } from '@/stores/auth'
import NavigationBar from '@/components/common/NavigationBar.vue'
import axios from 'axios'

const { isTTSEnabled, speak, toggleTTS: ttsToggle } = useTTS()
const authStore = useAuthStore()
const router = useRouter()

const form = reactive({
  username: '',
  password: '',
  keep: true,
  ipSecurity: true
})

const errorMessage = ref('')

// 비밀번호 찾기 모달 관련
const showPasswordResetModal = ref(false)
const resetEmail = ref('')
const resetMessage = ref('')
const resetSuccess = ref(false)
const isResetting = ref(false)

const toggleTTS = () => {
  const wasEnabled = isTTSEnabled.value
  ttsToggle()

  // Only speak if we just turned TTS ON (wasEnabled was false, now it's true)
  if (!wasEnabled && isTTSEnabled.value) {
    speak('TTS가 켜졌습니다')
  }
  // Silent when turning OFF
}

const closePasswordResetModal = () => {
  showPasswordResetModal.value = false
  resetEmail.value = ''
  resetMessage.value = ''
  resetSuccess.value = false
}

const handlePasswordReset = async () => {
  resetMessage.value = ''
  isResetting.value = true

  try {
    const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api'
    const response = await axios.post(`${API_BASE_URL}/auth/password-reset/`, {
      email: resetEmail.value
    })

    resetSuccess.value = true

    // 임시 비밀번호가 있으면 표시 (개발 환경용)
    if (response.data.temp_password) {
      resetMessage.value = `임시 비밀번호: ${response.data.temp_password}\n(이 비밀번호로 로그인 후 변경해주세요)`
    } else {
      resetMessage.value = '비밀번호 재설정 링크가 이메일로 전송되었습니다.'
    }

    setTimeout(() => {
      closePasswordResetModal()
    }, 5000)
  } catch (error) {
    console.error('비밀번호 재설정 실패:', error)
    resetSuccess.value = false
    resetMessage.value = error.response?.data?.error ||
                        error.response?.data?.detail ||
                        '이메일 전송에 실패했습니다. 다시 시도해주세요.'
  } finally {
    isResetting.value = false
  }
}

const handleFocus = (payload) => {
  const text = typeof payload === 'string'
    ? payload
    : payload?.target?.innerText ||
      payload?.target?.getAttribute('aria-label') ||
      payload?.target?.getAttribute('placeholder') ||
      ''

  if (text && isTTSEnabled.value) {
    speak(text)
  }
}

const handleSubmit = async () => {
  errorMessage.value = ''

  try {
    // 백엔드 로그인 API 호출
    const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api'
    const response = await axios.post(`${API_BASE_URL}/auth/login/`, {
      username: form.username.trim(),
      password: form.password
    })

    // JWT 토큰 저장
    const { access, refresh, user } = response.data
    localStorage.setItem('access_token', access)
    localStorage.setItem('refresh_token', refresh)

    // auth store 업데이트 (로컬 상태 동기화)
    authStore.currentUser = user
    authStore.isLoggedIn = true

    speak('로그인 성공')
    router.push('/')
  } catch (error) {
    console.error('로그인 실패:', error)

    const message = error.response?.data?.error ||
                   error.response?.data?.detail ||
                   '로그인에 실패했습니다. 아이디와 비밀번호를 확인해주세요.'

    errorMessage.value = message
    speak(message)
  }
}
</script>

<style scoped>
.login-view {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f1f5f9;
  padding: 6rem 1rem 2rem;
}

.login-card {
  width: 640px;
  max-width: 100%;
  background: #ffffff;
  border-radius: 20px;
  padding: 3.6rem 3.4rem 3rem;
  box-shadow: 0 24px 50px rgba(15, 23, 42, 0.18);
}

.login-title {
  margin: 0 0 1.5rem;
  font-size: 2.4rem;
  font-weight: 700;
  color: #111827;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 1.4rem;
}

.login-input {
  width: 100%;
  padding: 1.4rem 1.5rem;
  border-radius: 12px;
  border: 1.6px solid #d1d5db;
  font-size: 1.2rem;
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
}

.login-input:focus {
  outline: none;
  border-color: #a08077;
  box-shadow: 0 0 0 2px rgba(47, 158, 68, 0.15);
}

.login-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 1.1rem;
  color: #4b5563;
  margin: 0.2rem 0 0.4rem;
}

.keep-login {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.ip-toggle {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.ip-label {
  font-weight: 600;
  color: #4b5563;
}

.ip-checkbox {
  position: absolute;
  opacity: 0;
  pointer-events: none;
}

.toggle-pill {
  min-width: 70px;
  height: 32px;
  padding: 0 0.5rem;
  border-radius: 999px;
  background: #2f9e44;
  color: #ffffff;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 0.95rem;
  font-weight: 700;
  transition: background 0.2s ease;
}

.ip-checkbox:not(:checked) + .toggle-pill {
  background: #9ca3af;
}

.login-submit {
  width: 100%;
  padding: 1.35rem 1.5rem;
  border: none;
  border-radius: 12px;
  background: #a08077;
  color: #ffffff;
  font-size: 1.25rem;
  font-weight: 600;
  cursor: pointer;
}

.login-error {
  margin: 0;
  color: #ef4444;
  font-size: 1rem;
}

.login-divider {
  position: relative;
  text-align: center;
  font-size: 1rem;
  color: #9ca3af;
  margin: 0.4rem 0 0.1rem;
}

.login-divider::before,
.login-divider::after {
  content: '';
  position: absolute;
  top: 50%;
  width: 34%;
  height: 1px;
  background: #e5e7eb;
}

.login-divider::before {
  left: 0;
}

.login-divider::after {
  right: 0;
}

.passkey-button {
  width: 100%;
  padding: 1.2rem 1.5rem;
  border-radius: 12px;
  border: 1.6px solid #2f9e44;
  background: #ffffff;
  color: #2f9e44;
  font-weight: 700;
  cursor: pointer;
}

.login-links {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  margin-top: 0.6rem;
  font-size: 1rem;
  color: #6b7280;
}

.text-link {
  border: none;
  background: transparent;
  color: inherit;
  cursor: pointer;
  font-size: 1.2rem;
  padding: 0;
  text-decoration: none;
}

.text-link:hover {
  color: #2f9e44;
}

.link-separator {
  color: #d1d5db;
}

/* 비밀번호 찾기 모달 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  padding: 1rem;
}

.modal-content {
  background: white;
  border-radius: 16px;
  padding: 2.5rem;
  max-width: 500px;
  width: 100%;
  position: relative;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.2);
}

.modal-close {
  position: absolute;
  top: 1rem;
  right: 1rem;
  background: none;
  border: none;
  cursor: pointer;
  padding: 0.5rem;
  color: #6b7280;
  transition: color 0.2s;
}

.modal-close:hover {
  color: #111827;
}

.modal-title {
  font-size: 1.75rem;
  font-weight: 700;
  color: #111827;
  margin: 0 0 0.5rem 0;
}

.modal-description {
  font-size: 1rem;
  color: #6b7280;
  margin: 0 0 1.5rem 0;
}

.reset-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.reset-message {
  margin: 0;
  padding: 0.75rem 1rem;
  border-radius: 8px;
  font-size: 0.95rem;
}

.reset-message.success {
  background: #d1fae5;
  color: #065f46;
}

.reset-message.error {
  background: #fee2e2;
  color: #991b1b;
}

.reset-submit {
  width: 100%;
  padding: 1.2rem 1.5rem;
  border: none;
  border-radius: 12px;
  background: #a08077;
  color: white;
  font-size: 1.1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.reset-submit:hover:not(:disabled) {
  background: #8a6e65;
}

.reset-submit:disabled {
  background: #d1d5db;
  cursor: not-allowed;
}

@media (max-width: 480px) {
  .login-card {
    padding: 2.8rem 2.2rem 2.4rem;
  }

  .modal-content {
    padding: 2rem;
  }

  .modal-title {
    font-size: 1.5rem;
  }
}
</style>
