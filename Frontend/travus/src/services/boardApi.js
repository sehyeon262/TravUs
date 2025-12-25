import axios from 'axios'

// API 키 설정
const YOUTUBE_API_KEY = 'AIzaSyDe0FYArq5BSyYz5Hz9Q9sPterrMyHPK3w'
const NAVER_CLIENT_ID = 'ehMeVNZQ4tPiZrqNxnzi'
const NAVER_CLIENT_SECRET = 'k3HrwuBrmV'

// 네이버 API는 CORS 문제로 백엔드 프록시를 통해 호출해야 합니다
// 여기서는 직접 호출을 시도하지만, CORS 에러가 발생하면 백엔드에서 프록시 필요
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api'

/**
 * 네이버 블로그 검색
 */
export async function searchBlog(query, display = 10) {
  try {
    // 백엔드 프록시를 통한 검색
    const response = await axios.get(`${API_BASE_URL}/board/blog`, {
      params: { query, display }
    })
    return response.data.items || []
  } catch (error) {
    console.error('블로그 검색 실패:', error)
    return []
  }
}

/**
 * 네이버 뉴스 검색
 */
export async function searchNews(query, display = 10) {
  try {
    // 백엔드 프록시를 통한 검색
    const response = await axios.get(`${API_BASE_URL}/board/news`, {
      params: { query, display }
    })
    return response.data.items || []
  } catch (error) {
    console.error('뉴스 검색 실패:', error)
    return []
  }
}

/**
 * 유튜브 검색
 */
export async function searchYoutube(query, maxResults = 12) {
  try {
    // 백엔드 프록시를 통한 검색
    const response = await axios.get(`${API_BASE_URL}/board/youtube`, {
      params: { query, maxResults }
    })
    return response.data.items || []
  } catch (error) {
    console.error('유튜브 검색 실패:', error)
    return []
  }
}
