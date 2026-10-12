"""Conservative interpretation of TourAPI free text; unknown is never False."""
import html
import re

# API key, persisted field, customer-facing facility label.
ACCESSIBILITY_FIELDS = (
    (
        "parking",
        "parking",
        "장애인 주차장"
    ),
    (
        "publictransport",
        "public_transport",
        "대중교통 접근"
    ),
    (
        "route",
        "route",
        "접근로"
    ),
    (
        "ticketoffice",
        "ticket_office",
        "매표소"
    ),
    (
        "promotion",
        "promotion",
        "홍보물"
    ),
    (
        "wheelchair",
        "wheelchair",
        "휠체어 대여"
    ),
    (
        "exit",
        "exit",
        "출입통로"
    ),
    (
        "elevator",
        "elevator",
        "승강기"
    ),
    (
        "restroom",
        "restroom",
        "장애인 화장실"
    ),
    (
        "auditorium",
        "auditorium",
        "관람석"
    ),
    (
        "room",
        "room",
        "장애인 객실"
    ),
    (
        "braileblock",
        "braile_block",
        "점자블록"
    ),
    (
        "helpdog",
        "help_dog",
        "안내견 동반"
    ),
    (
        "guidehuman",
        "guide_human",
        "안내 인력"
    ),
    (
        "audioguide",
        "audio_guide",
        "음성안내"
    ),
    (
        "bigprint",
        "big_print",
        "큰 글자 안내"
    ),
    (
        "brailepromotion",
        "braile_promotion",
        "점자 홍보물"
    ),
    (
        "guidesystem",
        "guide_system",
        "유도 안내 설비"
    ),
    (
        "signguide",
        "sign_guide",
        "수어 안내"
    ),
    (
        "videoguide",
        "video_guide",
        "자막 영상 안내"
    ),
    (
        "hearingroom",
        "hearing_room",
        "청각장애 객실"
    ),
    (
        "stroller",
        "stroller",
        "유모차 대여"
    ),
    (
        "lactationroom",
        "lactation_room",
        "수유실"
    ),
    (
        "babysparechair",
        "baby_spare_chair",
        "유아용 의자"
    )
)
EXTRA_TEXT_FIELDS = {
    "handicapetc": "handicap_etc", "blindhandicapetc": "blind_handicap_etc",
    "hearinghandicapetc": "hearing_handicap_etc", "infantsfamilyetc": "infants_family_etc",
}
NORMALIZATION_VERSION = "explicit-v1"
UNKNOWN_TEXT = {"", "-", "--", "n/a", "null", "none", "정보없음", "정보미제공", "미상", "확인필요", "해당없음"}
POSITIVE = {"y", "yes", "true", "가능", "있음", "유", "제공", "구비", "설치됨", "설치되어있음",
            "이용가능", "대여가능", "제공가능", "동반가능", "동반입장가능"}
NEGATIVE = {"n", "no", "false", "불가", "불가능", "없음", "무", "미제공", "미설치", "미운영", "이용불가", "이용불가능", "대여불가능",
            "대여불가", "동반불가", "제공불가", "동반입장불가", "가능하지않음", "대여가능하지않음"}
PREFIXES = {
    "parking": ("장애인전용주차구역", "장애인주차장", "주차장", "주차"),
    "public_transport": ("대중교통",), "route": ("접근로", "무장애이동경로"),
    "ticket_office": ("매표소",), "promotion": ("홍보물",),
    "wheelchair": ("휠체어대여", "휠체어"), "exit": ("출입통로", "출입구"),
    "elevator": ("장애인용엘리베이터", "엘리베이터", "승강기"),
    "restroom": ("장애인전용화장실", "장애인화장실", "화장실"), "auditorium": ("장애인관람석", "관람석"),
    "room": ("장애인객실",), "braile_block": ("점자블록",), "help_dog": ("안내견동반", "안내견"),
    "guide_human": ("안내인력",), "audio_guide": ("음성안내", "오디오가이드"),
    "big_print": ("큰글자안내",), "braile_promotion": ("점자홍보물",),
    "guide_system": ("유도안내설비",), "sign_guide": ("수어안내", "수화안내"),
    "video_guide": ("자막영상안내", "자막비디오가이드"), "hearing_room": ("청각장애객실",),
    "stroller": ("유모차대여", "유모차"), "lactation_room": ("수유실",), "baby_spare_chair": ("유아용의자",),
}

def clean_text(value):
    if value is None:
        return ""
    if not isinstance(value, str):
        raise ValueError("Accessibility descriptions must be strings or null.")
    value = re.sub(r"<br\s*/?>", "\n", value, flags=re.I)
    return html.unescape(re.sub(r"<[^>]*>", "", value)).strip()

def compact_text(value):
    return re.sub(r"\s+", "", clean_text(value)).lower().rstrip(".。")

def availability(value, field):
    """Only explicit whole-value statements qualify; conditional prose stays unknown."""
    text = compact_text(value)
    if text in UNKNOWN_TEXT:
        return None
    # TourAPI appends category markers and location/count notes to explicit statements.
    # Keep the original in *_info; never discard a condition while interpreting it.
    text = re.sub(r"_(?:무장애|시각장애인|청각장애인|영유아가족)편의시설$", "", text)
    notes = re.findall(r"\(([^()]*)\)", text)
    if any(re.search(r"불가|없|제외|제한|예약|일부|계단|단차|운영|공사|시간|보조|경우|문의|전화|주말|평일|필요|요청|동반|승인|유료|동행|보호자|기간|계절", note) for note in notes):
        return None
    if any(not (re.fullmatch(r"\d+(?:개|면|대|곳)?", note) or re.search(r"근처|주차장|화장실|건물|입구|출입구|층|앞|옆|뒤|경사로설치", note)) for note in notes):
        return None
    text = re.sub(r"\([^()]*\)", "", text)
    if field in {"route", "exit"} and re.fullmatch(r"(?:출입구까지|주출입구는)?턱이없어휠체어접근가능(?:함)?", text):
        return True
    candidates = [text]
    for prefix in PREFIXES.get(field, ()):
        if text.startswith(prefix):
            candidates.append(text[len(prefix):])
    if any(candidate in NEGATIVE for candidate in candidates):
        return False
    if any(candidate in POSITIVE for candidate in candidates):
        return True
    return None

def normalized_values(payload):
    if not isinstance(payload, dict):
        raise ValueError("TourAPI accessibility item must be an object.")
    values = {"source_payload": payload, "normalization_version": NORMALIZATION_VERSION}
    for api_key, field, _ in ACCESSIBILITY_FIELDS:
        raw = payload.get(api_key)
        values[field] = availability(raw, field)
        values[field + "_info"] = raw
    for api_key, field in EXTRA_TEXT_FIELDS.items():
        raw = payload.get(api_key)
        clean_text(raw)  # reject malformed values before any database write
        values[field] = raw
    return values

def facility_details(instance):
    result = []
    for _, field, label in ACCESSIBILITY_FIELDS:
        raw = getattr(instance, field + "_info")
        value = getattr(instance, field)
        status = "available" if value is True else "unavailable" if value is False else "unknown"
        has_description = compact_text(raw) not in UNKNOWN_TEXT
        status_label = "이용 가능" if value is True else "이용 불가" if value is False else "확인 필요" if has_description else "정보 없음"
        result.append({"field": field, "label": label, "available": value, "status": status,
            "status_label": status_label, "description": clean_text(raw)})
    return result
