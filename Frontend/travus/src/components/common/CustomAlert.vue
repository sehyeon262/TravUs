<template>
  <Transition name="modal">
    <div v-if="modelValue" class="modal-overlay" @click="handleOverlayClick">
      <div class="modal-container" @click.stop>
        <div class="modal-icon">
          <img src="@/assets/alert.png" alt="알림" />
        </div>
        <div class="modal-body">
          <h3 class="modal-title">{{ title }}</h3>
          <p class="modal-message">{{ message }}</p>
        </div>
        <div class="modal-footer">
          <button class="btn-confirm" @click="confirm">
            {{ confirmText }}
          </button>
          <button v-if="showCancel" class="btn-cancel" @click="close">
            {{ cancelText }}
          </button>
        </div>
      </div>
    </div>
  </Transition>
</template>

<script setup>
const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  title: {
    type: String,
    default: '알림'
  },
  message: {
    type: String,
    required: true
  },
  type: {
    type: String,
    default: 'info', // info, warning, error, success
    validator: (value) => ['info', 'warning', 'error', 'success'].includes(value)
  },
  confirmText: {
    type: String,
    default: '확인'
  },
  cancelText: {
    type: String,
    default: '취소'
  },
  showCancel: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:modelValue', 'confirm', 'cancel'])

const close = () => {
  emit('update:modelValue', false)
  emit('cancel')
}

const confirm = () => {
  emit('update:modelValue', false)
  emit('confirm')
}

const handleOverlayClick = () => {
  // showCancel이 true일 때만 오버레이 클릭으로 닫기 허용
  if (props.showCancel) {
    close()
  }
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  padding: 1rem;
}

.modal-container {
  background: #667eea;
  border-radius: 24px;
  max-width: 400px;
  width: 100%;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  overflow: hidden;
  animation: slideUp 0.3s ease;
  padding: 2.5rem 2rem;
  text-align: center;
}

@keyframes slideUp {
  from {
    transform: translateY(30px) scale(0.95);
    opacity: 0;
  }
  to {
    transform: translateY(0) scale(1);
    opacity: 1;
  }
}

.modal-icon {
  margin: 0 auto 1.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal-icon img {
  width: 120px;
  height: 120px;
  object-fit: contain;
  filter: drop-shadow(0 4px 12px rgba(0, 0, 0, 0.2));
}

.modal-body {
  margin-bottom: 2rem;
}

.modal-title {
  font-size: 1.5rem;
  font-weight: 800;
  color: #ffffff;
  margin: 0 0 1rem 0;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.modal-message {
  font-size: 1.05rem;
  color: #ffffff;
  line-height: 1.6;
  margin: 0;
  opacity: 0.95;
}

.modal-footer {
  display: flex;
  gap: 0.75rem;
  flex-direction: column;
}

.btn-confirm,
.btn-cancel {
  padding: 1rem 1.5rem;
  font-size: 1rem;
  font-weight: 700;
  border-radius: 14px;
  border: none;
  cursor: pointer;
  transition: all 0.2s ease;
  width: 100%;
}

.btn-confirm {
  background: #ffffff;
  color: #667eea;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.btn-confirm:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.2);
  background: #f8f9ff;
}

.btn-confirm:active {
  transform: translateY(0);
}

.btn-cancel {
  background: rgba(255, 255, 255, 0.2);
  color: #ffffff;
  border: 2px solid rgba(255, 255, 255, 0.4);
  backdrop-filter: blur(10px);
}

.btn-cancel:hover {
  background: rgba(255, 255, 255, 0.3);
  border-color: rgba(255, 255, 255, 0.6);
}

/* 트랜지션 효과 */
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.3s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-active .modal-container,
.modal-leave-active .modal-container {
  transition: transform 0.3s ease, opacity 0.3s ease;
}

.modal-enter-from .modal-container,
.modal-leave-to .modal-container {
  transform: scale(0.9) translateY(20px);
  opacity: 0;
}

/* 반응형 */
@media (max-width: 480px) {
  .modal-container {
    border-radius: 20px;
    padding: 2rem 1.5rem;
  }

  .modal-icon img {
    width: 80px;
    height: 80px;
  }

  .modal-title {
    font-size: 1.3rem;
  }

  .modal-message {
    font-size: 0.95rem;
  }

  .btn-confirm,
  .btn-cancel {
    padding: 0.875rem 1.25rem;
    font-size: 0.95rem;
  }
}
</style>
