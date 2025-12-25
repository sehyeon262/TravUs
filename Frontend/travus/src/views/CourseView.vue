<template>
  <div class="course-view">
    <!-- NavigationBar는 결과 화면에서만 숨김 -->
    <NavigationBar v-if="currentStep !== 'result'" />

    <!-- ① 시작 화면 -->
    <CourseStart
      v-if="currentStep === 'start'"
      @next="goToRegionSelect"
      @select-course="showCourseDetail"
    />

    <!-- ② 지역 선택 -->
    <RegionSelect
      v-if="currentStep === 'region'"
      @next="goToDurationSelect"
      @back="currentStep = 'start'"
    />

    <!-- ③ 여행 기간 선택 -->
    <DurationSelect
      v-if="currentStep === 'duration'"
      @next="goToRegionConfigOrTheme"
      @back="currentStep = 'region'"
    />

    <!-- ④ 지역 구성 선택 (2박 3일만) -->
    <RegionConfig
      v-if="currentStep === 'regionConfig'"
      @next="goToThemeSelect"
      @back="currentStep = 'duration'"
    />

    <!-- ⑤ 여행 테마 선택 -->
    <ThemeSelect
      v-if="currentStep === 'theme'"
      @next="generateCourse"
      @back="goBackFromTheme"
    />

    <!-- ⑥ 로딩 화면 -->
    <CourseLoading
      v-if="currentStep === 'loading'"
    />

    <!-- ⑦ 여행 결과 -->
    <CourseResult
      v-if="currentStep === 'result'"
      :course-data="generatedCourse"
      @restart="restartCourse"
    />

  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import NavigationBar from '@/components/common/NavigationBar.vue'
import CourseStart from '@/components/course/CourseStart.vue'
import RegionSelect from '@/components/course/RegionSelect.vue'
import DurationSelect from '@/components/course/DurationSelect.vue'
import RegionConfig from '@/components/course/RegionConfig.vue'
import ThemeSelect from '@/components/course/ThemeSelect.vue'
import CourseLoading from '@/components/course/CourseLoading.vue'
import CourseResult from '@/components/course/CourseResult.vue'
import api from '@/services/api'

const route = useRoute()
const currentStep = ref('start')
const selectedRegions = ref([])
const selectedDuration = ref(null)
const selectedRegionCount = ref(null)
const selectedThemes = ref([])
const generatedCourse = ref(null)

// 지역 코드 → 이름 매핑
const regionNameMap = {
  '1': '서울',
  '2': '인천',
  '3': '대전',
  '4': '대구',
  '5': '광주',
  '6': '부산',
  '7': '울산',
  '8': '세종',
  '31': '경기',
  '32': '강원',
  '33': '충북',
  '34': '충남',
  '35': '경북',
  '36': '경남',
  '37': '전북',
  '38': '전남',
  '39': '제주'
}

const goToRegionSelect = () => {
  currentStep.value = 'region'
}

// 코스 상세 보기
const showCourseDetail = async (courseId) => {
  try {
    const response = await api.getCourseDetail(courseId)
    const courseData = response.data

    // CourseResult에 맞는 형식으로 변환
    const dayGroups = {}
    const regionCodes = new Set()

    courseData.course_spots.forEach(spot => {
      const day = spot.day || 1
      if (!dayGroups[day]) {
        dayGroups[day] = []
      }

      // 여행지 데이터 구조 통일 (AI 생성과 동일한 형식으로)
      const travelSpot = spot.travel_spot
      dayGroups[day].push({
        order: spot.order,
        type: spot.spot_type || 'attraction',
        id: travelSpot.id,
        spot: {
          id: travelSpot.id,
          name: travelSpot.name,
          address: travelSpot.address,
          latitude: travelSpot.latitude,
          longitude: travelSpot.longitude,
          content_type_id: travelSpot.content_type_id,
          image_url: travelSpot.image_url,
          tel: travelSpot.tel
        }
      })

      // 지역 코드 수집 (여행지의 area_code)
      if (travelSpot.area_code) {
        regionCodes.add(travelSpot.area_code)
      }
    })

    const days = Object.keys(dayGroups).map(dayNum => ({
      day: parseInt(dayNum),
      spots: dayGroups[dayNum].sort((a, b) => a.order - b.order)
    }))

    // 여행 기간 계산
    const dayCount = days.length
    let durationName = '당일치기'
    if (dayCount === 2) durationName = '1박 2일'
    else if (dayCount === 3) durationName = '2박 3일'

    generatedCourse.value = {
      id: courseData.id,
      title: courseData.title,
      description: courseData.description,
      days: days,
      regions: Array.from(regionCodes), // 지역 코드 배열
      duration: {
        days: dayCount,
        name: durationName
      },
      themes: [], // 기존 코스는 테마 정보가 없을 수 있음
      isExisting: true // 기존 코스임을 표시
    }

    currentStep.value = 'result'
  } catch (error) {
    console.error('코스 불러오기 실패:', error)
    alert('코스를 불러오는데 실패했습니다.')
  }
}

const goToDurationSelect = (regions) => {
  selectedRegions.value = regions
  currentStep.value = 'duration'
}

const goToRegionConfigOrTheme = (duration) => {
  selectedDuration.value = duration

  // 2박 3일이면 지역 구성 선택으로
  if (duration.days === 3) {
    currentStep.value = 'regionConfig'
  } else {
    currentStep.value = 'theme'
  }
}

const goToThemeSelect = (regionCount) => {
  selectedRegionCount.value = regionCount
  currentStep.value = 'theme'
}

const goBackFromTheme = () => {
  if (selectedDuration.value?.days === 3) {
    currentStep.value = 'regionConfig'
  } else {
    currentStep.value = 'duration'
  }
}

const generateCourse = async (themes) => {
  selectedThemes.value = themes
  currentStep.value = 'loading'

  try {
    // selectedRegions.value[0]은 지역 코드 (예: "1", "6")
    const areaCode = selectedRegions.value[0]
    const regionName = regionNameMap[areaCode]

    if (!regionName) {
      console.error('지역 이름을 찾을 수 없습니다. 코드:', areaCode)
      alert('지역 정보를 찾을 수 없습니다. 다시 시도해주세요.')
      currentStep.value = 'theme'
      return
    }


    // AI 코스 생성 API 호출
    const response = await api.generateAICourse({
      region: regionName,
      area_code: areaCode,
      duration: selectedDuration.value.name, // "당일치기", "1박 2일", "2박 3일"
      themes: selectedThemes.value
    })

    // AI 응답 데이터 가공
    const aiData = response.data

    // day별로 그룹핑
    const dayGroups = {}
    aiData.itinerary.forEach(item => {
      const day = item.day || 1
      if (!dayGroups[day]) {
        dayGroups[day] = []
      }
      dayGroups[day].push({
        order: item.order,
        type: item.type,
        id: item.id,
        spot: item.spot_detail
      })
    })

    // days 배열로 변환
    const days = Object.keys(dayGroups).map(dayNum => ({
      day: parseInt(dayNum),
      spots: dayGroups[dayNum].sort((a, b) => a.order - b.order)
    }))

    generatedCourse.value = {
      title: aiData.title || `${regionName} ${selectedDuration.value.name} 여행`,
      description: aiData.description || '',
      regions: selectedRegions.value,
      duration: selectedDuration.value,
      themes: selectedThemes.value,
      days: days,
      rawItinerary: aiData.itinerary // 원본 데이터 보관 (저장시 사용)
    }

    currentStep.value = 'result'
  } catch (error) {
    console.error('AI 코스 생성 실패:', error)

    let errorMessage = 'AI 코스 생성에 실패했습니다.'

    if (error.response?.data?.error) {
      errorMessage = error.response.data.error
    } else if (error.code === 'ECONNABORTED') {
      errorMessage = '요청 시간이 초과되었습니다. 다시 시도해주세요.'
    } else if (error.message) {
      errorMessage = error.message
    }

    alert(errorMessage)
    currentStep.value = 'theme'
  }
}

const restartCourse = () => {
  currentStep.value = 'start'
  selectedRegions.value = []
  selectedDuration.value = null
  selectedRegionCount.value = null
  selectedThemes.value = []
  generatedCourse.value = null
}

// 컴포넌트 마운트 시 URL 파라미터 확인
onMounted(() => {
  const courseId = route.params.id
  if (courseId) {
    // URL로 직접 접근한 경우, 해당 코스 로드
    showCourseDetail(courseId)
  }
})
</script>

<style scoped>
.course-view {
  width: 100%;
  min-height: 100vh;
  background: #ffffff;
}
</style>
