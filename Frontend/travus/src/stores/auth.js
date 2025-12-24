import { defineStore } from 'pinia'

const STORAGE_KEY = 'travus-auth'

const loadState = () => {
  if (typeof window === 'undefined') {
    return { users: [], currentUser: null, isLoggedIn: false, token: null }
  }

  try {
    const raw = window.localStorage.getItem(STORAGE_KEY)
    const token = window.localStorage.getItem('access_token')

    // 토큰이 없으면 무조건 로그아웃 상태
    if (!token) {
      // 잘못된 데이터가 남아있을 수 있으니 정리
      window.localStorage.removeItem(STORAGE_KEY)
      return { users: [], currentUser: null, isLoggedIn: false, token: null }
    }

    if (!raw) {
      return { users: [], currentUser: null, isLoggedIn: false, token: null }
    }

    const parsed = JSON.parse(raw)

    // 토큰과 저장된 로그인 상태가 모두 있어야 로그인으로 인정
    const isLoggedIn = !!token && Boolean(parsed.isLoggedIn) && parsed.currentUser

    return {
      users: Array.isArray(parsed.users) ? parsed.users : [],
      currentUser: isLoggedIn ? parsed.currentUser : null,
      isLoggedIn: isLoggedIn,
      token: token || null
    }
  } catch {
    // 에러 발생 시 localStorage 정리
    window.localStorage.removeItem(STORAGE_KEY)
    window.localStorage.removeItem('access_token')
    window.localStorage.removeItem('refresh_token')
    return { users: [], currentUser: null, isLoggedIn: false, token: null }
  }
}

const saveState = (state, storage = window.localStorage) => {
  if (typeof window === 'undefined') return

  const payload = {
    users: state.users,
    currentUser: state.currentUser,
    isLoggedIn: state.isLoggedIn,
    token: state.token
  }

  storage.setItem(STORAGE_KEY, JSON.stringify(payload))
}

export const useAuthStore = defineStore('auth', {
  state: () => ({
    ...loadState()
  }),
  actions: {
    // JWT 토큰 기반 사용자 정보 설정
    setUser(user) {
      this.currentUser = user
      this.isLoggedIn = true
      saveState(this)
    },
    // JWT 토큰 설정
    setToken(token) {
      this.token = token
      this.isLoggedIn = true
      saveState(this)
    },
    signUp({ username, password, name, phone, email = '', birth = '', gender = '' }) {
      const exists = this.users.some((user) => user.username === username)
      if (exists) {
        return { ok: false, message: '이미 가입된 아이디입니다.' }
      }

      this.users.push({
        username: username.trim(),
        password,
        name,
        phone,
        email,
        birth: (birth || '').trim(),
        gender
      })
      saveState(this)
      return { ok: true }
    },
    login(username, password, remember = true) {
      const user = this.users.find(
        (item) => item.username === username && item.password === password
      )

      if (!user) {
        return { ok: false, message: '아이디와 비밀번호가 올바르지 않습니다.' }
      }

      this.currentUser = {
        username: user.username,
        name: user.name,
        phone: user.phone,
        email: user.email,
        birth: user.birth,
        gender: user.gender
      }
      this.isLoggedIn = true

      if (typeof window !== 'undefined') {
        const storage = remember ? window.localStorage : window.sessionStorage
        if (!remember) {
          window.localStorage.removeItem(STORAGE_KEY)
        }
        saveState(this, storage)
      }

      return { ok: true }
    },
    logout() {
      this.currentUser = null
      this.isLoggedIn = false
      this.token = null
      if (typeof window !== 'undefined') {
        window.localStorage.removeItem(STORAGE_KEY)
        window.localStorage.removeItem('access_token')
        window.localStorage.removeItem('refresh_token')
        window.sessionStorage.removeItem(STORAGE_KEY)
      }
    },
    updateProfile(payload) {
      if (!this.currentUser) {
        return { ok: false, message: '로그인 후 이용해 주세요.' }
      }

      const index = this.users.findIndex((user) => user.username === this.currentUser.username)
      if (index === -1) {
        return { ok: false, message: '사용자 정보를 찾을 수 없습니다.' }
      }

      const updated = {
        ...this.users[index],
        ...payload,
        username: this.users[index].username
      }

      this.users.splice(index, 1, updated)
      this.currentUser = { ...this.currentUser, ...payload }
      saveState(this)
      return { ok: true }
    }
  }
})
