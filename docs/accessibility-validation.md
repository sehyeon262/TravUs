# TravUs 무장애 정보: 원본 응답 → DB → 화면 검증 보고서

검증일: 2026-09-09
기준 커밋: `a87e5a6515aa13094cc7b890f96aa9149787dca3`
작업 브랜치: `fix/accessibility-data-validation`

## 개선 배경과 진행 방식

AI 코딩 도구 OpenAI Codex를 활용해 관광지의 휠체어 정보 판정 오류를 개선했다. 프로젝트 종료 후 배리어프리 여행 서비스 TravUs를 포트폴리오에 정확히 설명하기 위해 데이터 흐름을 정리한 것이 출발점이다.

내가 이해한 흐름을 Codex에 전달해 실제 코드와 대조하던 중, ‘대여 불가’도 글자가 있다는 이유로 가능으로 판정되는 문제를 확인했다. 정보가 없는 경우도 불가로 표시돼 이용 제한과 정보 부족을 구분할 필요가 있었다.

나는 가능과 불가 외에 정보 없음을 구분하는 기준을 제안했다. 조건부 설명은 원문과 함께 ‘확인 필요’로 표시하고, 원문 없는 값은 ‘정보 없음’으로 안내하도록 정했다. Codex에는 코드 수정과 테스트 작성을 요청하면서 수정 이유와 각 테스트의 목적도 설명하도록 했다.

수정안이 오류의 원인을 해결하는지, 테스트가 잘못된 판정과 정보 누락을 확인하는 데 적절한지 검토한 뒤 로컬 환경에서 테스트를 직접 실행했다. 아래에는 수정 내용과 검증 결과, 확인한 범위를 기록했다. 이 결과는 프로젝트 종료 후 진행한 로컬 검증이며 운영 배포 성과는 아니다.

## 무엇을 수정했는가

기존 수집 함수는 `bool(text)`로 값을 만들었다. “대여 불가”도 비어 있지 않은 문자열이어서 True가 됐다. 반대로 빈 응답은 False로 저장되어, 시설이 없다는 것과 정보가 없다는 것을 구분할 수 없었다.

수집 코드는 24개 항목에 값을 할당했지만 기존 모델에는 상태 필드가 16개, 원문 필드가 6개뿐이었다. `setattr`로 만든 나머지 속성은 DB 재조회 시 사라졌다. 상세 API에도 일부 정보가 빠져 있었다. 화면에는 동일한 청각장애 객실 값을 서로 다른 시설처럼 표시하는 매핑도 있었다.

| 구분 | 수정 |
| --- | --- |
| 상태 값 | True=이용 가능, False=이용 불가, null=판단 미확인 |
| 원문 | 24개 항목 모두 원문 필드와 전체 응답 JSON 저장 |
| 조건부 안내 | 판정은 null로 두고 “확인 필요”와 원문을 함께 표시 |
| 정보 누락 | “정보 없음”으로 표시 |
| API | 기존 필드를 유지하면서 24개 facilities 목록에 상태·설명 제공 |
| 화면 | 상세 화면에 실제 AccessibilityPanel.vue 컴포넌트 연결. 원문과 상태를 텍스트로 표시 |
| 오류 응답 | 오류 코드·잘못된 자료형·다른 관광지 ID는 기존 무장애 정보를 덮어쓰지 않음 |
| 기존 데이터 | 보존된 원문으로 재판정. 근거가 없는 과거 플래그는 미확인 처리하고 legacy_flags에 보존 |
| API 로그 | 인증키가 들어 있는 요청 URL과 예외 원문을 로그에 쓰지 않도록 수정 |

## 실제로 수행한 검증

| 검증 | 결과 | 해석 |
| --- | --- | --- |
| 선정한 회귀 사례 9개 | 수정 전 1/9 → 수정 후 9/9 기대값 일치 | 오류 재현용으로 만든 입력의 결과. 운영 데이터 정확도가 아님 |
| 백엔드 검사 | 15개 통과 | 실제 수집 명령, SQLite 재조회, 상세 HTTP API, 오류 응답, 재동기화, 로그 검사 |
| 마이그레이션 | 적용 → 되돌리기 → 재적용 통과 | 기존 True + “대여 불가”는 False, 근거 없는 True는 null로 재판정 |
| 프런트 상태 표시 검사 | 3개 통과 | 세 가지 상태, 조건부 설명, 문자열 “false”의 오인식 방지 |
| Vue 렌더링 | 11개 사례 × 24개 항목 통과 | 실제 프로젝트 컴포넌트로 상태 속성과 설명 출력 및 HTML 이스케이프 검사 |
| 프로덕션 빌드 | Vite 7.2.6 빌드 통과 | Windows 실행 환경에서는 `--configLoader native` 사용 |
| 스키마 일치 | `makemigrations --check --dry-run` 통과 | 모델과 마이그레이션 간 추가 변경 없음 |
| 실제 TourAPI | 관광지 2곳 HTTP 200·resultCode 0000 | 공개 무장애 응답을 직접 수신한 뒤 같은 수집·저장 경로로 재처리 |
| 브라우저 확인 | 실제 응답 126273 선택 후 화면 확인 | “주차장 있음”은 이용 가능, 모래길 조건은 확인 필요, 빈 응답은 정보 없음 |

원본·DB·API·화면을 연결한 추적표는 11개 사례 × 24개 항목 = 264행이다. 원문이 DB 재조회와 API 직렬화 이후에도 보존되는지 검사했다. 이 수치는 독립적인 관광지 264곳을 조사했다는 의미가 아니다.

## 대표 사례

| 원본 설명 | 기존 DB | 수정 DB | 화면 |
| --- | --- | --- | --- |
| 휠체어 대여 가능 | True | True | 이용 가능 |
| 대여 불가 | True | False | 이용 불가 |
| 빈 문자열·null·키 누락 | False | null | 정보 없음 |
| 사전 예약 시 대여 가능 | True | null | 확인 필요 + 원문 |
| 일부 구간 이용 가능, 계단 구간은 이용 불가 | True | null | 확인 필요 + 원문 |
| 대여 가능하지 않음 | True | False | 이용 불가 |
| 매표소에 문의 | True | null | 확인 필요 + 원문 |

실제 응답 126273의 접근로 설명:
“해변가에 접근 가능한 경사로가 있으나 모래로 된 길임”

이 설명을 단순히 “가능”으로 바꾸지 않았다. 사용자가 이동 조건을 판단할 수 있도록 원문과 “확인 필요”를 함께 표시했다. 실제 응답 1433504의 “출입구까지 턱이 없어 휠체어 접근 가능함”은 명확한 접근 안내로 분류했다.

## 판정 기준과 한계

- 모델이 자유로운 한국어 문장을 이해하는 방식이 아니다. 시설별 명시 표현을 인식하는 규칙이며 규칙 버전은 explicit-v1이다.
- 명확한 긍정·부정 표현만 자동 분류한다. 알 수 없는 문장과 조건은 null로 남긴다.
- 관광공사의 편의시설 분류 접미사와 확인된 위치·수량 부연은 판정 시 분리하지만 원문에서는 삭제하지 않는다.
- 모든 한국어 표현에 대한 정확도를 검증하지 않았다. 실제 응답이 추가되면 조건·부정 표현 사례를 검토하며 회귀 테스트를 추가해야 한다.
- 실제 무장애 응답은 2건이다. Common/Intro 응답과 기본 여행지 레코드는 이번 검증의 범위를 좁히기 위한 로컬 입력이다. 세 종류의 API 전체에 대한 운영 환경 검증은 포함하지 않았다.
- 독립 SQLite 환경에서 실행했다. 운영 DB에 적용하거나 운영 데이터를 수정하지 않았다. 실제 운영 DB가 MySQL이면 그 환경에서 마이그레이션을 추가 확인해야 한다.
- 원문이 남아 있지 않은 과거 자료는 원래 표현을 복원할 수 없다. 해당 항목은 미확인 처리 후 API 재동기화가 필요하다.

## 설계 판단의 근거

1. **미확인 상태를 별도로 둔 이유:** 시설을 이용할 수 없는 경우와 시설 정보가 없는 경우는 의미가 다르다. 원문이 없거나 판단하기 어려운 값은 null로 저장하고 화면에서 구분했다.
2. **원문을 보존한 이유:** 자동 판정의 근거를 확인하고, 규칙이 바뀌었을 때 다시 처리할 수 있어야 한다. 사용자가 예약이나 이동 경로의 조건을 확인하는 데에도 원문이 필요하다.
3. **저장 후 DB를 다시 조회한 이유:** 모델에 없는 속성도 setattr로 생성할 수 있지만 DB에는 저장되지 않는다. 실행 중 객체의 값만 확인하지 않고 저장된 값과 API 응답을 대조했다.
4. **조건부 설명을 가능으로 단정하지 않은 이유:** 예약이나 구간, 지형 조건을 생략하면 이용 가능 여부를 잘못 안내할 수 있다. 조건이 있는 설명은 ‘확인 필요’와 원문을 함께 표시했다.
5. **같은 입력으로 전후를 비교한 이유:** 입력과 기대 결과를 유지해야 수정 효과를 비교할 수 있다. 선정한 9개 사례의 결과와 실제 API 응답 2건의 검증을 구분해 기록했다.

## 실행 방법

아래 명령은 프로젝트의 Backend 또는 Frontend/travus에서 실행한다. 검증 설정은 원래 .env나 운영 DB 연결을 읽지 않는다.

Backend:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe validation_checks.py
.\.venv\Scripts\python.exe validation_migration.py
$env:TRAVUS_VALIDATION_DB = ':memory:'
.\.venv\Scripts\python.exe validation_capture.py --stage after --output ../results/accessibility/after.json
.\.venv\Scripts\python.exe validation_live_pipeline.py
.\.venv\Scripts\python.exe manage.py makemigrations --check --dry-run --settings=travus.validation_settings
```

validation_live_pipeline.py는 저장된 실제 응답을 재처리한다. 새 응답이 필요하면 로컬 프로세스 환경의 TOUR_API_KEY를 설정하고 validation_fetch_live.py를 실행한다. 키 자체를 파일·보고서·Git에 넣지 않는다.

Frontend/travus:

```powershell
npm ci
npm run test:accessibility
npm run validate:accessibility
npm run build -- --configLoader native
```

수정 전 결과는 기준 커밋의 수집 코드를 실제 실행해 보관한 before.json이다. 현재 수정된 코드로 수정 전 결과를 다시 생성하지 않는다.

## 결과 파일

- `results/accessibility/index.html`: 브라우저로 보는 비교 보고서. 단독 HTML 파일로도 열 수 있다.
- `results/accessibility/field-trace.csv`: 원본 → DB → API → 화면 264행 추적표.
- `results/accessibility/before.json`, `after.json`: 9개 재현 사례 결과.
- `results/accessibility/live-tourapi-126273.json`, `live-tourapi-1433504.json`: 인증키 없는 실제 응답과 수신 시각.
- `results/accessibility/live-after.json`: 실제 응답의 DB·API 결과.
- `results/accessibility/backend-tests.json`, `migration.json`, `rendering.json`: 검증 결과.
- `Backend/api/migrations/0010_accessibility_tristate.py`: nullable 상태·원문 필드 추가.
- `Backend/api/migrations/0011_reclassify_accessibility.py`: 기존 자료 재판정.
- `Backend/api/migrations/_accessibility_v1.py`: 데이터 마이그레이션 재현성을 위한 당시 판정 규칙 사본.

설계 참고: [Django BooleanField 및 null](https://docs.djangoproject.com/en/5.2/ref/models/fields/), [Django 데이터 마이그레이션](https://docs.djangoproject.com/en/5.2/topics/migrations/#data-migrations).
