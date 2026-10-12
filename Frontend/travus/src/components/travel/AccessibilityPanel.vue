<script setup>
import { computed } from 'vue'
import { presentFacility } from '@/utils/accessibility'
const props = defineProps({ accessibility: { type: Object, default: null } })
const facilities = computed(() => (props.accessibility?.facilities ?? []).map(presentFacility))
</script>

<template>
  <section class="accessibility-section" aria-labelledby="accessibility-title">
    <h2 id="accessibility-title" class="section-title">무장애 관광 정보</h2>
    <p class="accessibility-note">제공된 설명을 함께 확인해 주세요. 이용 조건이 있거나 판단하기 어려운 항목은 확인이 필요합니다.</p>
    <p v-if="facilities.length === 0" class="accessibility-empty">등록된 무장애 정보가 없습니다.</p>
    <dl v-else class="facility-grid">
      <div v-for="item in facilities" :key="item.field" class="facility-card"
           :data-facility="item.field" :data-status="item.status">
        <dt class="facility-heading">
          <span>{{ item.label }}</span>
          <span class="facility-status" :class="item.status">{{ item.statusLabel }}</span>
        </dt>
        <dd class="facility-description">{{ item.description || '제공된 설명이 없습니다.' }}</dd>
      </div>
    </dl>
  </section>
</template>

<style scoped>
.accessibility-section { margin-bottom: 3rem; color: #1f2937; }
.section-title { font-size: 1.5rem; font-weight: 700; margin-bottom: 0.75rem; }
.accessibility-note, .accessibility-empty { color: #4b5563; font-size: 0.9rem; line-height: 1.6; }
.facility-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 0.9rem; margin-top: 1.25rem; }
.facility-card { padding: 1rem; border: 1px solid #d1d5db; border-radius: 12px; background: #fff; min-width: 0; }
.facility-heading { display: flex; justify-content: space-between; align-items: flex-start; gap: 0.5rem; font-weight: 600; }
.facility-status { flex-shrink: 0; border-radius: 6px; padding: 0.2rem 0.45rem; font-size: 0.75rem; font-weight: 600; }
.available { background: #dcfce7; color: #166534; }
.unavailable { background: #fee2e2; color: #991b1b; }
.unknown { background: #f3f4f6; color: #4b5563; }
.facility-description { margin: 0.65rem 0 0; font-size: 0.85rem; line-height: 1.65; color: #4b5563; white-space: pre-line; overflow-wrap: anywhere; }
@media (max-width: 900px) { .facility-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
@media (max-width: 540px) { .facility-grid { grid-template-columns: minmax(0, 1fr); } }
</style>
