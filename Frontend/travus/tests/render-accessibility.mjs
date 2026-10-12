import assert from 'node:assert/strict'
import fs from 'node:fs/promises'
import path from 'node:path'
import { pathToFileURL } from 'node:url'
import { createSSRApp, h } from 'vue'
import { renderToString } from 'vue/server-renderer'
import { parse, compileScript } from 'vue/compiler-sfc'

const results = path.resolve('../../results/accessibility')
const before = JSON.parse(await fs.readFile(path.join(results, 'before.json'), 'utf8'))
const after = JSON.parse(await fs.readFile(path.join(results, 'after.json'), 'utf8'))
const live = JSON.parse(await fs.readFile(path.join(results, 'live-after.json'), 'utf8'))
const source = await fs.readFile('src/components/travel/AccessibilityPanel.vue', 'utf8')
const { descriptor } = parse(source)
const compiled = compileScript(descriptor, { id: 'validation-panel', inlineTemplate: true, genDefaultAs: '__sfc__' })
const generatedDir = path.resolve('.validation')
await fs.mkdir(generatedDir, { recursive: true })
const generatedPath = path.join(generatedDir, 'AccessibilityPanel.mjs')
await fs.writeFile(generatedPath, compiled.content.replace("'@/utils/accessibility'", "'../src/utils/accessibility.js'") + '\nexport default __sfc__\n')
const Panel = (await import(pathToFileURL(generatedPath).href)).default
const escape = (text) => String(text ?? '').replaceAll('&', '&amp;').replaceAll('<', '&lt;').replaceAll('>', '&gt;').replaceAll('"', '&quot;')
const rows = [...after.rows, ...live.rows]
const rendered = []
for (const row of rows) {
  const markup = await renderToString(createSSRApp({ render: () => h(Panel, { accessibility: row.api.accessibility }) }))
  assert.equal((markup.match(/data-facility=/g) || []).length, 24)
  for (const facility of row.api.accessibility.facilities) {
    assert.ok(markup.includes('data-facility="' + facility.field + '" data-status="' + facility.status + '"'))
    assert.ok(markup.includes(escape(facility.description)))
  }
  rendered.push({ row, markup })
}
const attack = await renderToString(createSSRApp({ render: () => h(Panel, { accessibility: { facilities: [
  { field: 'test', label: '검증', available: null, status_label: '확인 필요', description: '<script>alert(1)</script>' }
] } }) }))
assert.ok(attack.includes('&lt;script&gt;alert(1)&lt;/script&gt;'))
assert.ok(!attack.includes('<script>alert(1)</script>'))
const comparison = after.rows.map(row => {
  const original = before.rows.find(old => old.id === row.id)
  const status = row.api.accessibility.facilities.find(f => f.field === 'wheelchair')
  return '<tr><td>' + escape(row.id.replace('validation-', '')) + '</td><td>' + escape(row.input.wheelchair ?? '(누락/null)') + '</td><td>' + escape(original.db.wheelchair) + '</td><td>' + escape(row.db.wheelchair === null ? 'null' : row.db.wheelchair) + '</td><td>' + escape(status.status_label) + '</td></tr>'
}).join('')
const panels = rendered.map(({row, markup}, index) => '<article id="case-' + index + '" class="case" ' + (index ? 'hidden' : '') + '><p class="eyebrow">' + (row.id.startsWith('validation-') ? '재현 입력 · 실제 API 호출 아님' : '실제 관광공사 응답 · 2026-09-09 수신') + '</p><h2>' + escape(row.id) + '</h2>' + markup + '<details><summary>원본 응답과 DB 값 보기</summary><pre>' + escape(JSON.stringify({input: row.input, db: row.db}, null, 2)) + '</pre></details></article>').join('')
const html = '<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>TravUs 무장애 데이터 검증</title><style>' +
'body{margin:0;background:#f5f7fa;color:#182132;font-family:Segoe UI,Malgun Gothic,sans-serif}main{max-width:1150px;margin:40px auto;padding:0 24px}h1{font-size:30px;letter-spacing:-1px}header p{line-height:1.8;max-width:900px}.eyebrow{font-size:12px;font-weight:700;color:#2563eb;letter-spacing:.04em}.summary{display:flex;gap:16px;flex-wrap:wrap;margin:24px 0}.summary div{flex:1;min-width:160px;padding:20px;border:1px solid #dce3ec;border-radius:14px;background:white}.summary b{display:block;font-size:26px;margin-bottom:8px}table{border-collapse:collapse;width:100%;font-size:13px;background:white}th,td{text-align:left;padding:12px;border-bottom:1px solid #dce3ec}th{background:#eaf0f7}nav{display:flex;gap:8px;flex-wrap:wrap;margin:30px 0 20px}button{padding:9px 13px;border:1px solid #b8c4d4;background:white;border-radius:8px;cursor:pointer;font:inherit;font-size:13px}button[aria-pressed=true]{background:#163d7a;color:white;border-color:#163d7a}.case{background:white;padding:24px;border:1px solid #dce3ec;border-radius:14px}.case[hidden]{display:none}pre{white-space:pre-wrap;overflow-wrap:anywhere;background:#f5f7fa;padding:16px;font-size:12px;line-height:1.6}details{margin-top:20px}summary{cursor:pointer;color:#1d4ed8}footer{padding:28px 0;font-size:13px;color:#596579}.table-wrap{overflow:auto}' +
descriptor.styles.map(style => style.content).join('\n') +
'</style><main><header><p class="eyebrow">TRAVUS / DATA VALIDATION / 2026-09-09</p><h1>원본 설명이 화면의 안내가 되기까지</h1><p>“대여 불가”를 이용 가능으로 처리하던 흐름을 수정했습니다. 원문을 보존하고, 이용 가능·이용 불가·판단 미확인을 구분합니다. 조건이 있는 설명은 확인 필요로 표시합니다.</p></header><section class="summary"><div><b>1 → 9 / 9</b>선정한 회귀 사례의 기대값 일치</div><div><b>24개</b>항목별 원문 저장·직렬화 검증</div><div><b>2곳</b>관광공사 실제 응답 재처리</div><div><b>11개 화면</b>운영 컴포넌트 렌더링 검증</div></section><p>9개 재현 사례는 이번 오류를 검증하기 위해 만든 입력입니다. 실제 관광지 전체의 정확도 개선율을 뜻하지 않습니다.</p><div class="table-wrap"><table><thead><tr><th>사례</th><th>원본 wheelchair</th><th>수정 전 DB</th><th>수정 후 DB</th><th>화면 안내</th></tr></thead><tbody>' + comparison + '</tbody></table></div><nav aria-label="검증 사례 선택">' +
rows.map((row, i) => '<button type="button" aria-pressed="' + (i === 0) + '" data-case="' + i + '">' + escape(row.id.replace('validation-', '재현 · ')) + '</button>').join('') +
'</nav>' + panels + '<footer>실제 프로젝트의 AccessibilityPanel.vue를 Vue로 렌더링한 결과입니다. Common/Intro 기본 정보는 로컬 검증용이며 WithTour 원문 2건은 실제 API 응답입니다. 운영 DB 반영·GitHub 푸시는 수행하지 않았습니다.</footer></main><script>document.querySelectorAll("[data-case]").forEach(button=>button.addEventListener("click",()=>{document.querySelectorAll(".case").forEach(panel=>panel.hidden=panel.id!=="case-"+button.dataset.case);document.querySelectorAll("[data-case]").forEach(item=>item.setAttribute("aria-pressed",String(item===button)));}));</script></html>'
await fs.writeFile(path.join(results, 'index.html'), html, 'utf8')
await fs.writeFile(path.join(results, 'rendering.json'), JSON.stringify({ component: 'AccessibilityPanel.vue', pages: rows.length, fieldsPerPage: 24, assertions: 'status attributes and source descriptions rendered; markup escaped', result: 'passed' }, null, 2))
console.log('Production Vue component: 11 cases x 24 fields rendered; labels, descriptions and escaping passed.')
