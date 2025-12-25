<template>
  <footer class="footer-section" tabindex="0" @focus="handleFocus">
    <div class="footer-container">
      <!-- 상단 영역: 소셜 아이콘 & 연락처 -->
      <div class="footer-top">
        <div class="social-links">
          <a href="https://github.com/travus-project" target="_blank" class="social-icon" aria-label="GitHub"><i class="fa-brands fa-github"></i></a>
          <a href="mailto:support@travus.com" class="social-icon" aria-label="이메일"><i class="fa-solid fa-envelope"></i></a>
          <a href="https://www.youtube.com/@travus" target="_blank" class="social-icon" aria-label="YouTube"><i class="fa-brands fa-youtube"></i></a>
          <a href="https://www.instagram.com/travus_official" target="_blank" class="social-icon" aria-label="Instagram"><i class="fa-brands fa-instagram"></i></a>
          <a href="https://www.google.com/maps" target="_blank" class="social-icon" aria-label="여행지 찾기"><i class="fa-solid fa-location-dot"></i></a>
        </div>
        <div class="contact-info">
          <span><strong>M.</strong> tjfls295@naver.com</span>
          <span><strong>M.</strong> ssehyeoniz@naver.com</span>
        </div>
      </div>

      <!-- 중간 영역: 큰 로고 + 메뉴 링크 -->
      <div class="footer-content">
        <!-- 큰 로고 -->
        <div class="large-logo">TRAVUS</div>

        <!-- 메뉴 링크 -->
        <div class="footer-menu">
          <div class="menu-column">
            <span class="menu-link">Services</span>
            <div class="sub-menu">
              <router-link to="/travel">여행지 탐색</router-link>
              <router-link to="/course">여행 코스 만들기</router-link>
              <router-link to="/camera">AI 카메라</router-link>
              <router-link to="/board">커뮤니티</router-link>
            </div>
          </div>
          <div class="menu-column">
            <span class="menu-link">Accessibility</span>
            <div class="sub-menu">
              <a href="#" @click.prevent>음성 안내 (TTS)</a>
              <a href="#" @click.prevent>확대/축소 기능</a>
              <a href="#" @click.prevent>키보드 네비게이션</a>
              <a href="#" @click.prevent>무장애 여행 정보</a>
            </div>
          </div>
          <div class="menu-column">
            <span class="menu-link">Support</span>
            <div class="sub-menu">
              <a href="mailto:support@travus.com">1:1 문의</a>
              <router-link to="/about">서비스 소개</router-link>
            </div>
          </div>
        </div>
      </div>

      <!-- 최하단: 회사 정보 -->
      <div class="footer-bottom">
        <div class="copyright">© 2025 TRAVUS. 모두를 위한 여행, 모두의 여행.</div>
        <div class="footer-info">
          <span>TRAVUS Team</span>
          <span>|</span>
          <a href="#" @click.prevent>개인정보처리방침</a>
          <span>|</span>
          <a href="#" @click.prevent>이용약관</a>
        </div>
      </div>

      <!-- 맨 위로 버튼 -->
      <button
        class="scroll-to-top"
        @click="scrollToTop"
        tabindex="0"
        @focus="handleFocus"
        aria-label="맨 위로 이동"
      >
        <div class="rotating-text">
          <svg viewBox="0 0 200 200" class="circular-text">
            <defs>
              <path
                id="circlePath"
                d="M 100, 100 m -75, 0 a 75,75 0 1,1 150,0 a 75,75 0 1,1 -150,0"
              />
            </defs>
            <text class="rotating-svg-text">
              <textPath href="#circlePath">
                Travus · Travus · Travus · Travus · Travus · Travus ·
              </textPath>
            </text>
          </svg>
        </div>
        <img :src="topbtn" alt="Top Button" class="center-character" />
      </button>
    </div>
  </footer>
</template>

<script setup>
import topbtn from '@/assets/topbtn.png'

const emit = defineEmits(['focus'])

const scrollToTop = () => {
  window.scrollTo({
    top: 0,
    behavior: 'smooth'
  })
}


const handleFocus = (event) => {
  const text =
    event.target.getAttribute('data-text') ||
    event.target.getAttribute('aria-label') ||
    event.target.innerText
  emit('focus', text)
}
</script>

<style scoped>
.footer-section {
  background: #f5f5f5;
  color: #000;
  padding: 3rem 2rem 2rem;
  position: relative;
}

.footer-section:focus {
  outline: 3px solid #ffd700;
  outline-offset: -3px;
}

.footer-container {
  max-width: 1400px;
  margin: 0 auto;
}

/* 상단 영역 - 소셜 아이콘 & 연락처 */
.footer-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 3rem;
  border-bottom: 1px solid #ddd;
  margin-bottom: 2rem;
}

.social-links {
  display: flex;
  gap: 1rem;
}

.social-icon {
  width: 45px;
  height: 45px;
  border: 1px solid #000;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  text-decoration: none;
  color: #000;
  font-weight: 600;
  font-size: 1.1rem;
  transition: all 0.3s ease;
}

.social-icon:hover {
  background: #000;
  color: #fff;
  transform: translateY(-3px);
}

.contact-info {
  display: flex;
  gap: 2rem;
  font-size: 0.95rem;
}

.contact-info strong {
  font-weight: 700;
}

.top-menu {
  display: flex;
  gap: 3rem;
}

.menu-item {
  text-decoration: none;
  color: #000;
  font-weight: 600;
  font-size: 1rem;
  transition: all 0.3s ease;
}

.menu-item:hover {
  color: #666;
}

/* 중간 영역 - 큰 로고 + 메뉴 링크 */
.footer-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 3rem 0;
  border-bottom: 1px solid #ddd;
  margin-bottom: 3rem;
}

.large-logo {
  font-size: 8rem;
  font-weight: 900;
  letter-spacing: -0.05em;
  color: #000;
  line-height: 1;
}

.footer-menu {
  display: flex;
  gap: 4rem;
  align-items: flex-start;
}

.menu-column {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.menu-link {
  color: #000;
  font-size: 1.2rem;
  font-weight: 700;
  margin-bottom: 0.5rem;
  display: block;
  cursor: default;
}

.sub-menu {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.sub-menu a {
  color: #666;
  text-decoration: none;
  font-size: 0.95rem;
  transition: all 0.3s ease;
}

.sub-menu a:hover {
  color: #000;
  transform: translateX(3px);
}

/* 최하단 - 회사 정보 */
.footer-bottom {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  padding-top: 1rem;
}

.copyright {
  font-size: 0.9rem;
  color: #333;
  font-weight: 600;
}

.footer-info {
  display: flex;
  gap: 0.75rem;
  align-items: center;
  font-size: 0.8rem;
  color: #666;
  flex-wrap: wrap;
  justify-content: center;
}

.footer-info a {
  color: #666;
  text-decoration: none;
  transition: color 0.2s ease;
}

.footer-info a:hover {
  color: #000;
  text-decoration: underline;
}

.footer-tags {
  display: flex;
  gap: 1.5rem;
  flex-wrap: wrap;
}

.footer-tags span {
  font-size: 0.85rem;
  color: #666;
}

.scroll-to-top {
  position: fixed;
  bottom: 3rem;
  right: 3rem;
  width: 150px;
  height: 150px;
  background: white;
  color: white;
  border: none;
  border-radius: 50%;
  cursor: pointer;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
  transition: all 0.3s ease;
  z-index: 100;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0;
  overflow: visible;
}

.scroll-to-top:hover {
  transform: translateY(-5px);
  box-shadow: 0 6px 30px rgba(0, 0, 0, 0.3);
}


.rotating-text {
  position: absolute;
  width: 100%;
  height: 100%;
  animation: rotate 20s linear infinite;
}

.circular-text {
  width: 100%;
  height: 100%;
}

.rotating-svg-text {
  fill: #9b8854;
  font-size: 14px;
  font-weight: 600;
  letter-spacing: 2.5px;
}

.center-character {
  position: relative;
  width: 80px;
  height: 80px;
  z-index: 1;
  object-fit: contain;
}

@keyframes rotate {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

/* 반응형 디자인 */
@media (max-width: 1200px) {
  .large-logo {
    font-size: 6rem;
  }
}

@media (max-width: 1024px) {
  .footer-top {
    flex-direction: column;
    align-items: flex-start;
    gap: 2rem;
  }

  .top-menu {
    width: 100%;
    justify-content: space-between;
  }

  .footer-content {
    flex-direction: column;
    align-items: flex-start;
    gap: 2rem;
    padding: 3rem 0;
  }

  .large-logo {
    font-size: 5rem;
  }

  .footer-menu {
    gap: 3rem;
  }

  .menu-link {
    font-size: 1.1rem;
  }

  .sub-menu a {
    font-size: 0.9rem;
  }

  .footer-bottom {
    flex-direction: column;
    gap: 1rem;
  }
}

@media (max-width: 768px) {
  .footer-top {
    flex-direction: column;
    gap: 1.5rem;
    align-items: flex-start;
  }

  .social-links {
    gap: 0.75rem;
  }

  .social-icon {
    width: 40px;
    height: 40px;
    font-size: 1rem;
  }

  .contact-info {
    flex-direction: column;
    gap: 0.5rem;
    font-size: 0.9rem;
  }

  .top-menu {
    flex-direction: column;
    gap: 1rem;
  }

  .large-logo {
    font-size: 3rem;
  }

  .footer-menu {
    flex-direction: column;
    gap: 2rem;
    align-items: flex-start;
    width: 100%;
  }

  .menu-column {
    width: 100%;
  }

  .menu-link {
    font-size: 1.1rem;
  }

  .sub-menu a {
    font-size: 0.9rem;
  }

  .scroll-to-top {
    bottom: 2rem;
    right: 2rem;
    width: 80px;
    height: 80px;
  }

  .center-character {
    width: 50px;
    height: 50px;
  }

  .rotating-svg-text {
    font-size: 10px;
    letter-spacing: 1px;
  }
}
</style>
