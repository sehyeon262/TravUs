export function presentFacility(facility) {
  const value = facility.available
  const status = value === true ? 'available' : value === false ? 'unavailable' : 'unknown'
  const description = typeof facility.description === 'string' ? facility.description : ''
  // Only booleans are accepted; a string such as "false" must never activate a badge.
  const statusLabel = status === 'available' ? '이용 가능'
    : status === 'unavailable' ? '이용 불가'
      : facility.status_label === '확인 필요' ? '확인 필요' : '정보 없음'
  return { ...facility, status, description, statusLabel }
}
