import { createRouter, createWebHistory } from 'vue-router'
import Home from '@/views/Home.vue'
import About from '@/views/About.vue'
import TravelView from '@/views/TravelView.vue'
import TravelDetailView from '@/views/TravelDetailView.vue'
import CourseView from '@/views/CourseView.vue'
import CourseListView from '@/views/CourseListView.vue'
import LoginView from '@/views/LoginView.vue'
import SignupView from '@/views/SignupView.vue'
import MyPageView from '@/views/MyPageView.vue'
import PersonalInfoView from '@/views/PersonalInfoView.vue'
import CommentsView from '@/views/CommentsView.vue'
import ErrorView from '@/views/ErrorView.vue'
import CameraView from '@/views/CameraView.vue'
import BoardView from '@/views/BoardView.vue'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: Home
    },
    {
      path: '/about',
      name: 'about',
      component: About
    },
    {
      path: '/travel',
      name: 'travel',
      component: TravelView
    },
    {
      path: '/travel/:id',
      name: 'travel-detail',
      component: TravelDetailView
    },
    {
      path: '/course',
      name: 'course',
      component: CourseView
    },
    {
      path: '/course-list',
      name: 'course-list',
      component: CourseListView
    },
    {
      path: '/course-detail/:id',
      name: 'course-detail',
      component: CourseView  // 임시로 CourseView 사용, 나중에 CourseDetailView 만들 예정
    },
    {
      path: '/camera',
      name: 'camera',
      component: CameraView
    },
    {
      path: '/board',
      name: 'board',
      component: BoardView
    },
    {
      path: '/login',
      name: 'login',
      component: LoginView
    },
    {
      path: '/signup',
      name: 'signup',
      component: SignupView
    },
    {
      path: '/mypage',
      name: 'mypage',
      component: MyPageView,
      meta: { requiresAuth: true }
    },
    {
      path: '/mypage/info',
      name: 'mypage-info',
      component: PersonalInfoView,
      meta: { requiresAuth: true }
    },
    {
      path: '/mypage/comments',
      name: 'mypage-comments',
      component: CommentsView,
      meta: { requiresAuth: true }
    },
    {
      path: '/error',
      name: 'error',
      component: ErrorView
    },
    {
      path: '/:pathMatch(.*)*',
      name: 'not-found',
      component: ErrorView
    }
  ]
})

router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  if (to.meta.requiresAuth && !authStore.isLoggedIn) {
    next({ name: 'login' })
    return
  }
  next()
})

export default router
