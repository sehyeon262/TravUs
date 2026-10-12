import assert from 'node:assert/strict'
import { test } from 'node:test'
import { presentFacility } from '../src/utils/accessibility.js'

test('available, unavailable and unknown use distinct visible labels', () => {
  for (const [available, statusLabel] of [[true, '이용 가능'], [false, '이용 불가'], [null, '정보 없음']]) {
    assert.equal(presentFacility({ available }).statusLabel, statusLabel)
  }
})
test('conditional descriptions are retained and require confirmation', () => {
  const item = presentFacility({ available: null, status_label: '확인 필요', description: '사전 예약 시 대여 가능' })
  assert.equal(item.status, 'unknown')
  assert.equal(item.statusLabel, '확인 필요')
  assert.equal(item.description, '사전 예약 시 대여 가능')
})
test('truthy strings must not activate an available badge', () => {
  for (const available of ['false', 'true', '불가', 1, undefined]) {
    assert.equal(presentFacility({ available }).status, 'unknown')
  }
})
