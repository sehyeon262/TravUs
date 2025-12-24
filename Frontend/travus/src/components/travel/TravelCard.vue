<template>
  <div class="travel-card">
    <!-- 이미지 -->
    <div class="card-image" @click="handleClick">
      <img :src="destination.image" :alt="destination.name" />
      <div class="card-overlay">
        <button
          class="bookmark-btn"
          :class="{ bookmarked: isBookmarked }"
          @click.stop="handleBookmarkClick"
        >
          <svg width="20" height="20" viewBox="0 0 24 24" :fill="isBookmarked ? 'currentColor' : 'none'" stroke="currentColor" stroke-width="2">
            <path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </button>
      </div>
    </div>

    <!-- 내용 -->
    <div class="card-content">
      <div class="card-header">
        <span class="region-badge">{{ destination.region }}</span>
        <h3 class="card-title">{{ destination.name }}</h3>
      </div>

      <p class="card-description">{{ destination.description }}</p>

      <div class="card-tags">
        <span v-for="(tag, index) in destination.tags" :key="index" class="tag">
          {{ tag }}
        </span>
      </div>

      <div class="card-footer">
        <div class="reviews">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path d="M21 11.5a8.38 8.38 0 01-.9 3.8 8.5 8.5 0 01-7.6 4.7 8.38 8.38 0 01-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 01-.9-3.8 8.5 8.5 0 014.7-7.6 8.38 8.38 0 013.8-.9h.5a8.48 8.48 0 018 8v.5z" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          <span>{{ destination.reviews }}</span>
        </div>

        <button class="card-btn">
          상세보기
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path d="M5 12h14M12 5l7 7-7 7" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/services/api'

const router = useRouter()

const props = defineProps({
  destination: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['click', 'bookmark-changed'])

const isBookmarked = ref(false)

// destination의 북마크 상태를 props에서 가져오기
watch(() => props.destination, (newVal) => {
  if (newVal && newVal.is_bookmarked !== undefined) {
    isBookmarked.value = newVal.is_bookmarked
  }
}, { immediate: true })

const handleClick = () => {
  emit('click', props.destination)
}

const handleBookmarkClick = async () => {
  const token = localStorage.getItem('access_token')
  if (!token) {
    alert('로그인 후 이용 가능합니다.')
    router.push('/login')
    return
  }

  if (!props.destination.id) {
    alert('여행지 정보를 불러오는 중입니다.')
    return
  }

  try {
    const response = await api.toggleBookmark(props.destination.id)
    isBookmarked.value = response.data.bookmarked

    // 부모 컴포넌트에 북마크 상태 변경 알림
    emit('bookmark-changed', {
      id: props.destination.id,
      bookmarked: isBookmarked.value
    })
  } catch (error) {
    console.error('❌ 북마크 토글 실패:', error)
    alert('북마크 처리에 실패했습니다.')
  }
}
</script>

<style scoped>
.travel-card {
  background: white;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
  cursor: pointer;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.travel-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.15);
}

.card-image {
  position: relative;
  width: 100%;
  height: 220px;
  overflow: hidden;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.card-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
}

.travel-card:hover .card-image img {
  transform: scale(1.1);
}

.card-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(to bottom, rgba(0,0,0,0.3), transparent);
  display: flex;
  justify-content: flex-start;
  align-items: flex-start;
  padding: 1rem;
}

.bookmark-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  background: rgba(255, 255, 255, 0.95);
  border: none;
  border-radius: 50%;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.bookmark-btn:hover {
  background: white;
  transform: scale(1.1);
}

.bookmark-btn svg {
  color: #6b7280;
}

.bookmark-btn.bookmarked {
  background: #eff6ff;
  border: 2px solid #667eea;
}

.bookmark-btn.bookmarked svg {
  color: #667eea;
}

.card-content {
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  flex: 1;
}

.card-header {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.region-badge {
  display: inline-block;
  align-self: flex-start;
  padding: 0.25rem 0.75rem;
  background: #ede9fe;
  color: #7c3aed;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 600;
  letter-spacing: 0.5px;
}

.card-title {
  font-size: 1.25rem;
  font-weight: 700;
  color: #111827;
  margin: 0;
  line-height: 1.3;
}

.card-description {
  font-size: 0.9rem;
  color: #6b7280;
  line-height: 1.6;
  margin: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.card-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.tag {
  padding: 0.35rem 0.75rem;
  background: #f3f4f6;
  color: #4b5563;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 500;
  transition: all 0.2s ease;
}

.tag:hover {
  background: #e5e7eb;
}

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: auto;
  padding-top: 1rem;
  border-top: 1px solid #e5e7eb;
}

.reviews {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #6b7280;
  font-size: 0.875rem;
}

.reviews svg {
  color: #9ca3af;
}

.card-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background: #111827;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.card-btn:hover {
  background: #e4e4e4;
  color: #111827;
  transform: translateX(2px);
}

.card-btn svg {
  transition: transform 0.2s ease;
}

.card-btn:hover svg {
  transform: translateX(4px);
}

/* 반응형 */
@media (max-width: 768px) {
  .card-image {
    height: 180px;
  }

  .card-content {
    padding: 1.25rem;
  }

  .card-title {
    font-size: 1.1rem;
  }

  .card-description {
    font-size: 0.85rem;
  }
}
</style>
