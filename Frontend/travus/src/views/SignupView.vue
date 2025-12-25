<template>
  <div class="signup-view">
    <NavigationBar
      :is-t-t-s-enabled="isTTSEnabled"
      @toggle-tts="toggleTTS"
      @focus="handleFocus"
    />
    <div class="signup-card">
      <h1 class="signup-title">회원가입</h1>

      <form class="signup-form" @submit.prevent="handleSubmit">
        <!-- 아이디 -->
        <div class="form-group">
          <label class="form-label">
            아이디
            <span v-if="usernameError" class="required">{{ usernameError }}</span>
          </label>
          <div class="input-wrapper">
            <input
              class="form-input"
              :class="{ 'error': usernameError, 'success': usernameAvailable }"
              type="text"
              placeholder="아이디 입력 (4~20자)"
              v-model="form.username"
              @input="checkUsername"
              @focus="handleFocus"
              aria-label="아이디"
            />
            <button
              type="button"
              class="check-btn"
              :class="{ 'active': usernameAvailable }"
              @click="checkUsername"
            >
              중복 확인
            </button>
          </div>
          <p v-if="usernameAvailable" class="success-message">사용 가능한 아이디입니다</p>
        </div>

        <!-- 비밀번호 -->
        <div class="form-group">
          <label class="form-label">비밀번호 <span class="hint">20자 이하의 비밀번호를 입력해주세요</span></label>
          <input
            class="form-input"
            type="password"
            placeholder="비밀번호 입력 (영문, 숫자, 특수문자 포함 8~20자)"
            v-model="form.password"
            @focus="handleFocus"
            aria-label="비밀번호"
          />
        </div>

        <!-- 비밀번호 확인 -->
        <div class="form-group">
          <label class="form-label">
            비밀번호 확인
            <span v-if="passwordConfirmError" class="error-text">비밀번호가 일치하지 않습니다</span>
          </label>
          <input
            class="form-input"
            :class="{ 'error': passwordConfirmError }"
            type="password"
            placeholder="비밀번호 재입력"
            v-model="form.passwordConfirm"
            @input="checkPasswordMatch"
            @focus="handleFocus"
            aria-label="비밀번호 확인"
          />
        </div>

        <!-- 이름 -->
        <div class="form-group">
          <label class="form-label">이름</label>
          <input
            class="form-input"
            type="text"
            placeholder="이름을 입력해주세요"
            v-model="form.name"
            @focus="handleFocus"
            aria-label="이름"
          />
        </div>

        <!-- 전화번호 -->
        <div class="form-group">
          <label class="form-label">전화번호</label>
          <input
            class="form-input"
            type="tel"
            placeholder="숫자만 입력 (01012345678)"
            v-model="form.phone"
            @input="formatPhone"
            @focus="handleFocus"
            aria-label="전화번호"
            maxlength="11"
          />
        </div>

        <!-- 이메일 주소 -->
        <div class="form-group">
          <label class="form-label">이메일 주소</label>
          <div class="email-wrapper">
            <input
              class="form-input email-local"
              type="text"
              placeholder="이메일 주소"
              v-model="emailLocal"
              @focus="handleFocus"
              aria-label="이메일 아이디"
            />
            <span class="email-at">@</span>
            <select
              class="form-select email-domain"
              v-model="emailDomain"
              @focus="handleFocus"
              aria-label="이메일 도메인"
            >
              <option value="">naver.com</option>
              <option value="gmail.com">gmail.com</option>
              <option value="daum.net">daum.net</option>
              <option value="kakao.com">kakao.com</option>
              <option value="custom">직접입력</option>
            </select>
            <input
              v-if="emailDomain === 'custom'"
              class="form-input email-custom"
              type="text"
              placeholder="도메인 입력"
              v-model="emailCustomDomain"
              @focus="handleFocus"
            />
          </div>
        </div>

        <!-- 생년월일 -->
        <div class="form-group">
          <label class="form-label">생년월일</label>
          <div class="birth-wrapper">
            <select
              class="form-select birth-select"
              v-model="birthYear"
              @focus="handleFocus"
              aria-label="연도"
            >
              <option value="">년도</option>
              <option v-for="year in years" :key="year" :value="year">{{ year }}</option>
            </select>
            <select
              class="form-select birth-select"
              v-model="birthMonth"
              @focus="handleFocus"
              aria-label="월"
            >
              <option value="">월</option>
              <option v-for="month in 12" :key="month" :value="month">{{ month }}</option>
            </select>
            <select
              class="form-select birth-select"
              v-model="birthDay"
              @focus="handleFocus"
              aria-label="일"
            >
              <option value="">일</option>
              <option v-for="day in 31" :key="day" :value="day">{{ day }}</option>
            </select>
          </div>
        </div>

        <p v-if="errorMessage" class="form-error" role="alert">
          {{ errorMessage }}
        </p>

        <button class="signup-submit" type="submit" @focus="handleFocus" aria-label="가입하기">
          가입하기
        </button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref, computed } from 'vue'
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
  passwordConfirm: '',
  name: '',
  phone: ''
})

// 이메일 관련
const emailLocal = ref('')
const emailDomain = ref('')
const emailCustomDomain = ref('')

// 생년월일 관련
const birthYear = ref('')
const birthMonth = ref('')
const birthDay = ref('')

// 연도 목록 생성 (1900 ~ 현재년도)
const currentYear = new Date().getFullYear()
const years = computed(() => {
  const yearList = []
  for (let year = currentYear; year >= 1900; year--) {
    yearList.push(year)
  }
  return yearList
})

const errorMessage = ref('')
const checkingUsername = ref(false)
const usernameAvailable = ref(false)
const usernameError = ref('')
const passwordConfirmError = ref(false)
let usernameCheckTimeout = null

const toggleTTS = () => {
  const wasEnabled = isTTSEnabled.value
  ttsToggle()

  // Only speak if we just turned TTS ON (wasEnabled was false, now it's true)
  if (!wasEnabled && isTTSEnabled.value) {
    speak('TTS가 켜졌습니다')
  }
  // Silent when turning OFF
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

// 전화번호 포맷팅 (숫자만)
const formatPhone = (event) => {
  form.phone = event.target.value.replace(/\D/g, '')
}

// 비밀번호 확인
const checkPasswordMatch = () => {
  if (form.passwordConfirm && form.password !== form.passwordConfirm) {
    passwordConfirmError.value = true
  } else {
    passwordConfirmError.value = false
  }
}

// 아이디 중복 체크
const checkUsername = async () => {
  const username = form.username.trim()

  // 초기화
  usernameAvailable.value = false
  usernameError.value = ''

  if (!username) {
    return
  }

  // 아이디 유효성 검사 (4-20자, 영문+숫자)
  if (username.length < 4 || username.length > 20) {
    usernameError.value = '4-20자로 입력해주세요'
    return
  }

  if (!/^[a-zA-Z0-9]+$/.test(username)) {
    usernameError.value = '영문과 숫자만 사용 가능합니다'
    return
  }

  // 디바운스: 500ms 후에 API 호출
  clearTimeout(usernameCheckTimeout)
  usernameCheckTimeout = setTimeout(async () => {
    try {
      checkingUsername.value = true
      const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api'

      // 백엔드에 아이디 중복 체크 API 호출
      const response = await axios.get(`${API_BASE_URL}/auth/check-username/`, {
        params: { username }
      })

      if (response.data.available) {
        usernameAvailable.value = true
        usernameError.value = ''
      } else {
        usernameAvailable.value = false
        usernameError.value = '이미 사용중인 아이디입니다'
      }
    } catch (error) {
      console.error('아이디 중복 체크 실패:', error)
      // 중복 체크 실패 시 무시 (서버 에러)
      usernameError.value = ''
    } finally {
      checkingUsername.value = false
    }
  }, 500)
}

const handleSubmit = async () => {
  errorMessage.value = ''

  // 필수 입력 검증
  if (!form.username || !form.password) {
    errorMessage.value = '아이디와 비밀번호를 입력해 주세요.'
    speak(errorMessage.value)
    return
  }

  // 비밀번호 확인 검증
  if (!form.passwordConfirm) {
    errorMessage.value = '비밀번호 확인을 입력해 주세요.'
    speak(errorMessage.value)
    return
  }

  if (form.password !== form.passwordConfirm) {
    errorMessage.value = '비밀번호가 일치하지 않습니다.'
    speak(errorMessage.value)
    return
  }

  // 비밀번호 강도 검증 (8-20자, 영문+숫자+특수문자)
  const passwordRegex = /^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,20}$/
  if (!passwordRegex.test(form.password)) {
    errorMessage.value = '비밀번호는 8-20자, 영문, 숫자, 특수문자를 포함해야 합니다.'
    speak(errorMessage.value)
    return
  }

  if (!form.name) {
    errorMessage.value = '이름을 입력해 주세요.'
    speak(errorMessage.value)
    return
  }

  if (!form.phone) {
    errorMessage.value = '전화번호를 입력해 주세요.'
    speak(errorMessage.value)
    return
  }

  // 전화번호 형식 검증 (11자리)
  if (form.phone.length !== 11) {
    errorMessage.value = '전화번호는 11자리를 입력해주세요.'
    speak(errorMessage.value)
    return
  }

  // 아이디 사용 가능 여부 확인
  if (!usernameAvailable.value) {
    errorMessage.value = '사용 가능한 아이디인지 확인해주세요.'
    speak(errorMessage.value)
    return
  }

  try {
    // 이메일 조합
    let email = ''
    if (emailLocal.value) {
      const domain = emailDomain.value === 'custom' ? emailCustomDomain.value : (emailDomain.value || 'naver.com')
      email = `${emailLocal.value}@${domain}`
    }

    // 생년월일 조합
    let birth = ''
    if (birthYear.value && birthMonth.value && birthDay.value) {
      const month = String(birthMonth.value).padStart(2, '0')
      const day = String(birthDay.value).padStart(2, '0')
      birth = `${birthYear.value}-${month}-${day}`
    }

    // 백엔드 회원가입 API 호출
    const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api'

    const response = await axios.post(`${API_BASE_URL}/auth/signup/`, {
      username: form.username.trim(),
      password: form.password,
      name: form.name,
      phone: form.phone,
      email: email,
      birth: birth,
      gender: ''  // 성별 선택 제거됨
    })


    // 회원가입 성공 시 자동 로그인 처리
    if (response.data && response.data.tokens && response.data.user) {
      // 토큰 저장
      localStorage.setItem('access_token', response.data.tokens.access)
      localStorage.setItem('refresh_token', response.data.tokens.refresh)


      // 사용자 정보를 store에 저장
      authStore.setUser(response.data.user)
      authStore.setToken(response.data.tokens.access)


      speak('회원가입이 완료되었습니다. 자동으로 로그인됩니다.')

      // 약간의 딜레이 후 홈으로 이동
      setTimeout(() => {
        router.push('/')
      }, 500)
    } else {
      console.error('응답 데이터 형식 오류:', response.data)
      speak('회원가입이 완료되었습니다')
      router.push('/login')
    }
  } catch (error) {
    console.error('회원가입 실패:', error)
    console.error('에러 응답:', error.response?.data)

    const message = error.response?.data?.error ||
                   error.response?.data?.username?.[0] ||
                   error.response?.data?.detail ||
                   '회원가입에 실패했습니다. 다시 시도해주세요.'

    errorMessage.value = message
    speak(message)
  }
}
</script>

<style scoped>
.signup-view {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f8f9fa;
  padding: 6rem 1rem 2rem;
}

.signup-card {
  width: 480px;
  max-width: 100%;
  background: #ffffff;
  border-radius: 12px;
  padding: 2.5rem 2rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.signup-title {
  font-size: 1.5rem;
  font-weight: 700;
  margin: 0 0 0.5rem 0;
  color: #212529;
}

.signup-subtitle {
  font-size: 0.875rem;
  color: #6c757d;
  margin: 0 0 2rem 0;
}

.signup-form {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-label {
  font-size: 0.875rem;
  font-weight: 600;
  color: #212529;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.form-label .required {
  color: #dc3545;
  font-size: 0.75rem;
  font-weight: 400;
}

.form-label .hint {
  color: #6c757d;
  font-size: 0.75rem;
  font-weight: 400;
}

.form-label .error-text {
  color: #dc3545;
  font-size: 0.75rem;
  font-weight: 400;
}

.input-wrapper {
  display: flex;
  gap: 0.5rem;
}

.form-input {
  width: 100%;
  padding: 0.75rem 1rem;
  border: 1px solid #dee2e6;
  border-radius: 6px;
  font-size: 0.875rem;
  transition: border-color 0.2s;
}

.form-input:focus {
  outline: none;
  border-color: #4dabf7;
}

.form-input.error {
  border-color: #dc3545;
}

.form-input.success {
  border-color: #28a745;
}

.form-input::placeholder {
  color: #adb5bd;
}

.check-btn {
  padding: 0.75rem 1.5rem;
  border: 1px solid #dee2e6;
  border-radius: 6px;
  background: #ffffff;
  color: #495057;
  font-size: 0.875rem;
  cursor: pointer;
  white-space: nowrap;
  transition: all 0.2s;
}

.check-btn:hover {
  background: #f8f9fa;
}

.check-btn.active {
  background: #4dabf7;
  border-color: #4dabf7;
  color: #ffffff;
}

.error-message {
  font-size: 0.75rem;
  color: #dc3545;
  margin: 0;
}

.success-message {
  font-size: 0.75rem;
  color: #28a745;
  margin: 0;
}

.email-wrapper {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.email-local {
  flex: 1;
}

.email-at {
  font-size: 0.875rem;
  color: #495057;
}

.email-domain {
  width: 140px;
}

.email-custom {
  width: 140px;
}

.form-select {
  padding: 0.75rem 1rem;
  border: 1px solid #dee2e6;
  border-radius: 6px;
  font-size: 0.875rem;
  background: #ffffff;
  cursor: pointer;
}

.form-select:focus {
  outline: none;
  border-color: #4dabf7;
}

.birth-wrapper {
  display: flex;
  gap: 0.5rem;
}

.birth-select {
  flex: 1;
}

.form-error {
  margin: 0.5rem 0 0;
  color: #dc3545;
  font-size: 0.875rem;
  text-align: center;
}

.signup-submit {
  margin-top: 1rem;
  padding: 0.875rem 1rem;
  border: none;
  border-radius: 6px;
  background: #4dabf7;
  color: #ffffff;
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s;
}

.signup-submit:hover {
  background: #339af0;
}

@media (max-width: 480px) {
  .signup-card {
    padding: 2rem 1.5rem;
  }

  .email-wrapper {
    flex-wrap: wrap;
  }

  .email-domain,
  .email-custom {
    width: 100%;
  }
}
</style>
