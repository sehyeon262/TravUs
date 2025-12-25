import { ref, watch, onMounted } from 'vue'

const TTS_STORAGE_KEY = 'travus-tts-enabled'

// 전역 상태로 선언하여 모든 컴포넌트가 같은 인스턴스를 공유
const loadTTSState = () => {
  const saved = localStorage.getItem(TTS_STORAGE_KEY)
  return saved !== null ? saved === 'true' : true
}

const isTTSEnabled = ref(loadTTSState())
const isSpeaking = ref(false)

// SpeechSynthesis 지원 확인
const isSupported = 'speechSynthesis' in window

/**
 * 텍스트를 음성으로 읽기
 */
const speak = (text) => {
  if (!isSupported || !isTTSEnabled.value || !text) {
    return
  }

  // 이전 음성 중지
  window.speechSynthesis.cancel()

  const utterance = new SpeechSynthesisUtterance(text)
  utterance.lang = 'ko-KR'
  utterance.rate = 1.0
  utterance.pitch = 1.0
  utterance.volume = 1.0

  utterance.onstart = () => {
    isSpeaking.value = true
  }

  utterance.onend = () => {
    isSpeaking.value = false
  }

  utterance.onerror = () => {
    isSpeaking.value = false
  }

  window.speechSynthesis.speak(utterance)
}

/**
 * TTS 중지
 */
const stop = () => {
  if (isSupported) {
    window.speechSynthesis.cancel()
    isSpeaking.value = false
  }
}

/**
 * TTS 토글
 */
const toggleTTS = () => {
  isTTSEnabled.value = !isTTSEnabled.value
  // localStorage에 상태 저장
  localStorage.setItem(TTS_STORAGE_KEY, isTTSEnabled.value.toString())
  if (!isTTSEnabled.value) {
    stop()
  }
}

// TTS가 비활성화되면 자동으로 중지 (전역에서 한 번만 등록)
watch(isTTSEnabled, (enabled) => {
  if (!enabled) {
    stop()
  }
  // 상태 변경 시 localStorage에 저장
  localStorage.setItem(TTS_STORAGE_KEY, enabled.toString())
})

/**
 * TTS(Text-to-Speech) 기능을 제공하는 Composable
 * 싱글톤 패턴으로 모든 컴포넌트가 같은 상태를 공유합니다
 */
export function useTTS() {
  return {
    isTTSEnabled,
    isSpeaking,
    isSupported,
    speak,
    stop,
    toggleTTS
  }
}
