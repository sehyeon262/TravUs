<template>
  <div class="personal-info-view">
    <NavigationBar
      :is-t-t-s-enabled="isTTSEnabled"
      @toggle-tts="toggleTTS"
      @focus="handleFocus"
    />

    <div class="container">
      <header class="page-header">
        <h1>개인정보 수정</h1>
      </header>

      <section class="section">
        <div class="section-title">기본정보</div>

        <div class="form-group">
          <label class="label">아이디</label>
          <input
            class="input readonly"
            type="text"
            :value="user?.username || ''"
            readonly
            @focus="handleFocus"
          />
        </div>

        <div class="form-group inline">
          <div class="inline-field">
            <label class="label">이름</label>
            <input
              class="input"
              type="text"
              v-model="form.name"
              placeholder="이름을 입력해 주세요."
              @focus="handleFocus"
            />
          </div>
          <div class="inline-field gender-field">
            <label class="label">성별</label>
            <input
              class="input readonly"
              type="text"
              :value="form.gender || '여'"
              readonly
              @focus="handleFocus"
            />
          </div>
        </div>

        <div class="form-group">
          <label class="label">생년월일</label>
          <input
            class="input readonly"
            type="text"
            :value="form.birth || '정보가 없습니다'"
            readonly
            @focus="handleFocus"
          />
        </div>

        <p class="note">*이름, 성별 변경은 연락처 변경의 본인인증 후 반영됩니다.</p>
      </section>

      <section class="section">
        <div class="section-title row">
          <span>연락처</span>
          <button class="text-btn" type="button" @click="saveProfile" @focus="handleFocus">
            연락처 변경
          </button>
        </div>

        <div class="form-group phone-group">
          <label class="label">휴대전화번호</label>
          <div class="phone-input">
            <span class="phone-icon">☎</span>
            <input
              class="input"
              type="tel"
              v-model="form.phone"
              placeholder="휴대전화번호를 입력해 주세요."
              @focus="handleFocus"
            />
          </div>
        </div>
      </section>

      <section class="section">
        <div class="section-title row">
          <span>이메일</span>
          <button class="text-btn" type="button" @click="saveProfile" @focus="handleFocus">
            변경사항 저장
          </button>
        </div>

        <div class="form-group inline email-row">
          <div class="inline-field">
            <label class="label">이메일</label>
            <input
              class="input"
              type="text"
              v-model="emailLocal"
              placeholder="아이디"
              aria-label="이메일 아이디"
              @focus="handleFocus"
            />
          </div>
          <div class="inline-field at-sign">@</div>
          <div class="inline-field">
            <label class="label sr-only">도메인</label>
            <select
              class="input"
              v-model="emailDomain"
              aria-label="이메일 도메인"
              @focus="handleFocus"
            >
              <option value="naver.com">naver.com</option>
              <option value="gmail.com">gmail.com</option>
              <option value="daum.net">daum.net</option>
            </select>
          </div>
        </div>
      </section>

      <p v-if="errorMessage" class="error">{{ errorMessage }}</p>
      <p v-if="successMessage" class="success">{{ successMessage }}</p>
    </div>
  </div>
</template>

<script setup>
import { computed, reactive, ref, watch, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import NavigationBar from '@/components/common/NavigationBar.vue'
import { useAuthStore } from '@/stores/auth'
import { useTTS } from '@/composables/useTTS'

const authStore = useAuthStore()
const router = useRouter()
const user = computed(() => authStore.currentUser)
const { isTTSEnabled, speak, toggleTTS } = useTTS()

// 로그인 확인
onMounted(() => {
  if (!authStore.isLoggedIn) {
    alert('로그인이 필요한 서비스입니다.')
    router.push('/login')
  }
})

const form = reactive({
  name: '',
  phone: '',
  birth: '',
  gender: '여'
})

const emailLocal = ref('')
const emailDomain = ref('naver.com')
const errorMessage = ref('')
const successMessage = ref('')

const syncForm = () => {
  form.name = user.value?.name || ''
  form.phone = user.value?.phone || ''
  form.birth = user.value?.birth || ''
  form.gender = user.value?.gender || '여'

  const email = user.value?.email || ''
  if (email.includes('@')) {
    const [local, domain] = email.split('@')
    emailLocal.value = local
    emailDomain.value = domain || 'naver.com'
  } else {
    emailLocal.value = email
    emailDomain.value = 'naver.com'
  }
}

watch(
  user,
  () => {
    syncForm()
  },
  { immediate: true }
)

const saveProfile = () => {
  errorMessage.value = ''
  successMessage.value = ''

  if (!form.name.trim()) {
    errorMessage.value = '이름을 입력해 주세요.'
    return
  }

  const email = emailLocal.value ? `${emailLocal.value}@${emailDomain.value}` : ''

  const result = authStore.updateProfile({
    name: form.name.trim(),
    phone: form.phone.trim(),
    email
  })

  if (!result.ok) {
    errorMessage.value = result.message || '변경이 저장되지 않았습니다.'
    return
  }

  successMessage.value = '변경사항이 저장되었습니다.'
}

const handleFocus = (payload) => {
  const text =
    typeof payload === 'string'
      ? payload
      : payload?.target?.value ||
        payload?.target?.innerText ||
        payload?.target?.getAttribute('aria-label') ||
        payload?.target?.getAttribute('placeholder') ||
        ''

  if (text && isTTSEnabled.value) {
    speak(text)
  }
}
</script>

<style scoped>
.personal-info-view {
  min-height: 100vh;
  background: #f7f9fb;
}

.container {
  max-width: 900px;
  margin: 0 auto;
  padding: 6rem 1.25rem 2.5rem;
}

.page-header h1 {
  margin: 0 0 1.25rem;
  font-size: 1.6rem;
  font-weight: 800;
  color: #111827;
  border-bottom: 1px solid #d1d5db;
  padding-bottom: 0.8rem;
}

.section {
  background: #ffffff;
  border-radius: 14px;
  padding: 1.4rem 1.6rem;
  box-shadow: 0 10px 24px rgba(0, 0, 0, 0.05);
  margin-bottom: 1rem;
}

.section-title {
  font-weight: 700;
  color: #111827;
  margin-bottom: 1rem;
  font-size: 1.05rem;
}

.section-title.row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
  margin-bottom: 1rem;
}

.label {
  font-weight: 600;
  color: #374151;
  font-size: 0.95rem;
}

.input {
  width: 100%;
  border: 1.5px solid #d1d5db;
  border-radius: 10px;
  padding: 0.75rem 0.9rem;
  font-size: 0.95rem;
  background: #f9fafb;
}

.readonly {
  background: #f3f4f6;
}

.form-group.inline {
  display: grid;
  grid-template-columns: 1fr 160px;
  gap: 0.8rem;
}

.inline-field {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}

.gender-field .input {
  text-align: center;
}

.phone-group .phone-input {
  display: flex;
  align-items: center;
  gap: 0.6rem;
}

.phone-icon {
  font-size: 1.1rem;
}

.text-btn {
  padding: 0.45rem 0.9rem;
  border-radius: 8px;
  border: 1px solid #d1d5db;
  background: #ffffff;
  cursor: pointer;
  font-weight: 600;
  font-size: 0.9rem;
}

.email-row {
  align-items: flex-end;
}

.at-sign {
  align-self: flex-end;
  padding-bottom: 0.8rem;
  font-weight: 700;
  color: #6b7280;
}

.note {
  margin: 0.2rem 0 0;
  color: #6b7280;
  font-size: 0.9rem;
}

.error {
  color: #ef4444;
  font-weight: 600;
}

.success {
  color: #10b981;
  font-weight: 600;
}

.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}

@media (max-width: 640px) {
  .form-group.inline {
    grid-template-columns: 1fr;
  }

  .section {
    padding: 1.1rem 1.2rem;
  }
}
</style>
