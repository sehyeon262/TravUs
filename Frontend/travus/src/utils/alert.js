import { createApp, h } from 'vue'
import CustomAlert from '@/components/common/CustomAlert.vue'

let currentAlert = null

/**
 * 전역 Alert 함수
 * @param {Object} options - Alert 옵션
 * @param {string} options.title - 제목 (기본값: '알림')
 * @param {string} options.message - 메시지 (필수)
 * @param {string} options.confirmText - 확인 버튼 텍스트 (기본값: '확인')
 * @param {string} options.cancelText - 취소 버튼 텍스트 (기본값: '취소')
 * @param {boolean} options.showCancel - 취소 버튼 표시 여부 (기본값: false)
 * @param {Function} options.onConfirm - 확인 버튼 클릭 시 콜백
 * @param {Function} options.onCancel - 취소 버튼 클릭 시 콜백
 * @returns {Promise} - 사용자 응답 Promise (확인: true, 취소: false)
 */
export function showAlert(options) {
  // 이전 alert가 있으면 제거
  if (currentAlert) {
    currentAlert.unmount()
    currentAlert = null
  }

  return new Promise((resolve) => {
    const {
      title = '알림',
      message,
      confirmText = '확인',
      cancelText = '취소',
      showCancel = false,
      onConfirm,
      onCancel
    } = options

    // 컨테이너 생성
    const container = document.createElement('div')
    document.body.appendChild(container)

    // Alert 앱 생성
    const app = createApp({
      data() {
        return {
          visible: false
        }
      },
      mounted() {
        // 약간의 지연 후 표시 (애니메이션을 위해)
        setTimeout(() => {
          this.visible = true
        }, 10)
      },
      methods: {
        handleConfirm() {
          this.visible = false
          if (onConfirm) onConfirm()
          resolve(true)
          setTimeout(() => {
            app.unmount()
            document.body.removeChild(container)
            currentAlert = null
          }, 300)
        },
        handleCancel() {
          this.visible = false
          if (onCancel) onCancel()
          resolve(false)
          setTimeout(() => {
            app.unmount()
            document.body.removeChild(container)
            currentAlert = null
          }, 300)
        }
      },
      render() {
        return h(CustomAlert, {
          modelValue: this.visible,
          title,
          message,
          confirmText,
          cancelText,
          showCancel,
          'onUpdate:modelValue': (value) => {
            this.visible = value
          },
          onConfirm: this.handleConfirm,
          onCancel: this.handleCancel
        })
      }
    })

    currentAlert = app
    app.mount(container)
  })
}

/**
 * 간단한 Alert (확인 버튼만)
 * @param {string} message - 메시지
 * @param {string} title - 제목 (선택)
 */
export function alert(message, title = '알림') {
  return showAlert({
    title,
    message,
    showCancel: false
  })
}

/**
 * Confirm Dialog (확인/취소 버튼)
 * @param {string} message - 메시지
 * @param {string} title - 제목 (선택)
 */
export function confirm(message, title = '확인') {
  return showAlert({
    title,
    message,
    showCancel: true,
    confirmText: '확인',
    cancelText: '취소'
  })
}

/**
 * 성공 Alert
 * @param {string} message - 메시지
 * @param {string} title - 제목 (선택)
 */
export function success(message, title = '성공') {
  return showAlert({
    title,
    message,
    type: 'success',
    showCancel: false
  })
}

/**
 * 에러 Alert
 * @param {string} message - 메시지
 * @param {string} title - 제목 (선택)
 */
export function error(message, title = '오류') {
  return showAlert({
    title,
    message,
    type: 'error',
    showCancel: false
  })
}

/**
 * 경고 Alert
 * @param {string} message - 메시지
 * @param {string} title - 제목 (선택)
 */
export function warning(message, title = '경고') {
  return showAlert({
    title,
    message,
    type: 'warning',
    showCancel: false
  })
}
