<template>
<section class="service-hub-section">
 <div class="service-hub-inner">
  <h2 class="service-hub-title">
    <span>모두의 속도</span>로 떠나는 여행을 위한 서비스
  </h2>

  <div class="service-hub-grid">
    <div class="service-item" @click="navigateTo('/travel?category=12')">
      <div class="icon-circle">
        <img src="@/assets/travel_badge.png" alt="여행지" />
      </div>
      <p class="service-label">여행지</p>
    </div>

    <div class="service-item" @click="navigateTo('/travel?category=32')">
      <div class="icon-circle">
        <img src="@/assets/bed_badge.png" alt="숙소" />
      </div>
      <p class="service-label">숙소</p>
    </div>

    <div class="service-item" @click="navigateTo('/travel?category=39')">
      <div class="icon-circle">
        <img src="@/assets/food_badge.png" alt="음식점" />
      </div>
      <p class="service-label">음식점</p>
    </div>

    <div class="service-item" @click="navigateTo('/course')">
      <div class="icon-circle">
        <img src="@/assets/course_badge.png" alt="코스 추천" />
      </div>
      <p class="service-label">코스 추천</p>
    </div>

    <div class="service-item" @click="navigateTo('/course')">
      <div class="icon-circle">
        <img src="@/assets/ai_badge.png" alt="나만의 코스" />
      </div>
      <p class="service-label">나만의 코스</p>
    </div>

    <div class="service-item" @click="navigateTo('/camera')">
      <div class="icon-circle">
        <img src="@/assets/camera_badge.png" alt="AI 카메라" />
      </div>
      <p class="service-label">AI 카메라</p>
    </div>

    <div class="service-item" @click="navigateTo('/board')">
      <div class="icon-circle">
        <img src="@/assets/board_badge.png" alt="게시판" />
      </div>
      <p class="service-label">게시판</p>
    </div>
   </div>
  </div>

</section>

</template>

<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

const navigateTo = (path) => {
  router.push(path)
}
</script>

<style scoped>
.service-hub-section {
  padding: 5rem 2rem 4rem;
  background: #ffffff;
}

.service-hub-inner {
  max-width: 1400px;
  margin: 0 auto;
  text-align: left;
}

.service-hub-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: #1d1d1d;
  margin-top: 3rem;
  margin-bottom: 3rem;
  letter-spacing: -1px;
}

.service-hub-title span{
  color: #394b9e;
}

.service-hub-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 2rem;
  max-width: 1400px;
  margin: 0 auto;
  justify-items: center;
}

.service-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  cursor: pointer;
}

.icon-circle {
  width: 100px;
  height: 100px;
  border-radius: 30%;
  background: #ffffff;
  border: none;
  box-shadow:
    0 0 0 1px rgba(0, 0, 0, 0.08),   
    0 6px 16px rgba(0, 0, 0, 0.08); 
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 1.5rem;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.icon-circle img {
  width: 60px;       
  height: 60px;
  object-fit: contain;
}


.service-item:hover .icon-circle {
  transform: translateY(-4px);
}

.service-label {
  font-size: 0.95rem;
  color: #3f3f3f;
  line-height: 1.2;
  font-weight: bold;
}

.service-divider {
  margin-top: 4rem;
  height: 1px;
  background: #e5e7eb;
  max-width: 1200px;
  margin-left: auto;
  margin-right: auto;
}

@media (max-width: 1024px) {
  .service-hub-grid {
    grid-template-columns: repeat(4, 1fr);
    row-gap: 2.5rem;
  }
}

@media (max-width: 480px) {
  .service-hub-grid {
    grid-template-columns: repeat(3, 1fr);
  }

  .icon-circle {
    width: 64px;
    height: 64px;
  }
}

</style>
