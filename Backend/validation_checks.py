"""Isolated regression suite. Run: python validation_checks.py (no external API calls)."""
import io
import json
import os
import unittest
from pathlib import Path
from unittest.mock import patch
os.environ["DJANGO_SETTINGS_MODULE"] = "travus.validation_settings"
os.environ["TRAVUS_VALIDATION_DB"] = ":memory:"
import django
django.setup()
from django.db import connection
from django.core.management import call_command
from rest_framework.test import APIClient
from api.models import TravelSpot, AccessibilityInfo
from api.accessibility import ACCESSIBILITY_FIELDS, availability
from api.serializers import AccessibilityInfoSerializer
from validation_capture import envelope

class AccessibilityChecks(unittest.TestCase):
    def setUp(self):
        with connection.schema_editor() as editor:
            editor.create_model(TravelSpot)
            editor.create_model(AccessibilityInfo)
        self.spot = TravelSpot.objects.create(content_id="validation-test", content_type_id="12",
            name="검증용 장소", address="검증 전용", rating=0, review_count=0,
            view_count=0, bookmark_count=0, is_active=True)

    def tearDown(self):
        with connection.schema_editor() as editor:
            editor.delete_model(AccessibilityInfo)
            editor.delete_model(TravelSpot)

    def sync(self, payload=None, response=None):
        output = io.StringIO()
        if response is None:
            response = envelope({"contentid": self.spot.content_id, **(payload or {})})
        with patch("api.management.commands.sync_detail_info.tour_api_service.get_detail_common", return_value=envelope({"contentid": self.spot.content_id})), \
             patch("api.management.commands.sync_detail_info.tour_api_service.get_detail_intro", return_value=envelope({})), \
             patch("api.management.commands.sync_detail_info.tour_api_service.get_detail_with_tour", return_value=response), \
             patch("api.management.commands.sync_detail_info.time.sleep"):
            call_command("sync_detail_info", content_id=self.spot.content_id, stdout=output)
        return output.getvalue()

    def test_nine_regressions_persist_expected_values(self):
        cases = json.loads(Path("api/fixtures/accessibility_validation.json").read_text(encoding="utf-8"))["cases"]
        for case in cases:
            with self.subTest(case=case["id"]):
                self.sync(case["input"])
                saved = AccessibilityInfo.objects.get(travel_spot=self.spot)
                self.assertIs(saved.wheelchair, case["expected"])
                self.assertEqual(saved.wheelchair_info, case["input"].get("wheelchair"))
                self.assertEqual(saved.source_payload["contentid"], self.spot.content_id)

    def test_all_24_fields_survive_database_reread_and_serialization(self):
        self.assertEqual(len(ACCESSIBILITY_FIELDS), 24)
        payload = {key: ("가능" if index % 2 else "불가") for index, (key, _, _) in enumerate(ACCESSIBILITY_FIELDS)}
        self.sync(payload)
        saved = AccessibilityInfo.objects.get(travel_spot=self.spot)
        data = AccessibilityInfoSerializer(saved).data
        self.assertEqual(len(data["facilities"]), 24)
        for index, (key, field, _) in enumerate(ACCESSIBILITY_FIELDS):
            with self.subTest(field=field):
                self.assertIs(getattr(saved, field), bool(index % 2))
                self.assertEqual(getattr(saved, field + "_info"), payload[key])
                self.assertEqual(data[field + "_info"], payload[key])
                self.assertIs(data[field], bool(index % 2))

    def test_real_detail_endpoint_returns_three_states(self):
        self.sync({"wheelchair": "대여 불가", "parking": "가능"})
        response = APIClient().get("/api/travel-spots/by_content_id/", {"content_id": self.spot.content_id})
        self.assertEqual(response.status_code, 200)
        data = response.json()["accessibility"]
        self.assertIs(data["wheelchair"], False)
        self.assertIs(data["parking"], True)
        self.assertIsNone(data["audio_guide"])
        self.assertEqual({f["field"]: f for f in data["facilities"]}["wheelchair"]["status_label"], "이용 불가")

    def test_condition_preserved_and_labeled_for_review(self):
        raw = "사전 예약 시 대여 가능"
        self.sync({"wheelchair": raw})
        saved = AccessibilityInfo.objects.get(travel_spot=self.spot)
        facility = next(f for f in AccessibilityInfoSerializer(saved).data["facilities"] if f["field"] == "wheelchair")
        self.assertIsNone(saved.wheelchair)
        self.assertEqual(facility["status_label"], "확인 필요")
        self.assertEqual(facility["description"], raw)

    def test_unknown_not_in_available_filter(self):
        self.sync({"wheelchair": ""})
        self.assertFalse(TravelSpot.objects.filter(accessibility__wheelchair=True).exists())

    def test_single_object_response_supported(self):
        response = envelope({})
        response["response"]["body"]["items"]["item"] = {"wheelchair": "대여 불가"}
        self.sync(response=response)
        self.assertIs(AccessibilityInfo.objects.get(travel_spot=self.spot).wheelchair, False)

    def test_error_envelope_does_not_overwrite(self):
        self.sync({"wheelchair": "가능"})
        before = AccessibilityInfo.objects.get(travel_spot=self.spot).source_payload
        result = self.sync(response={"response": {"header": {"resultCode": "9999"}, "body": {"items": {"item": [{"wheelchair": ""}]}}}})
        self.assertIn("실패: 1개", result)
        self.assertEqual(AccessibilityInfo.objects.get(travel_spot=self.spot).source_payload, before)

    def test_empty_response_preserves_previous_data(self):
        self.sync({"wheelchair": "가능"})
        self.sync(response={"response": {"header": {"resultCode": "0000"}, "body": {"items": ""}}})
        self.assertIs(AccessibilityInfo.objects.get(travel_spot=self.spot).wheelchair, True)

    def test_malformed_field_does_not_partially_update(self):
        self.sync({"wheelchair": "가능"})
        before = AccessibilityInfo.objects.get(travel_spot=self.spot).source_payload
        result = self.sync({"wheelchair": "불가", "audioguide": {"unexpected": "object"}})
        self.assertIn("실패: 1개", result)
        saved = AccessibilityInfo.objects.get(travel_spot=self.spot)
        self.assertIs(saved.wheelchair, True)
        self.assertEqual(saved.source_payload, before)

    def test_repeated_sync_updates_without_duplicate_or_stale_flag(self):
        self.sync({"wheelchair": "가능"})
        self.sync({"wheelchair": None})
        self.assertEqual(AccessibilityInfo.objects.count(), 1)
        self.assertIsNone(AccessibilityInfo.objects.get(travel_spot=self.spot).wheelchair)

    def test_text_markup_does_not_change_raw_evidence(self):
        raw = "<b>휠체어 대여 불가</b><br/>"
        self.sync({"wheelchair": raw})
        saved = AccessibilityInfo.objects.get(travel_spot=self.spot)
        self.assertIs(saved.wheelchair, False)
        self.assertEqual(saved.wheelchair_info, raw)
        self.assertEqual(saved.source_payload["wheelchair"], raw)

    def test_unrecognized_and_negated_prose_not_available(self):
        for value in ("불가능", "대여 가능 여부 문의", "없지 않음", "무료 이용 불가 / 유료 이용 가능", "미설치 예정"):
            with self.subTest(value=value):
                self.assertIsNot(availability(value, "wheelchair"), True)

    def test_live_tourapi_notes_do_not_erase_conditions(self):
        self.assertIs(availability("장애인 주차장 있음(2)_무장애 편의시설", "parking"), True)
        self.assertIs(availability("출입구까지 턱이 없어 휠체어 접근 가능함", "route"), True)
        self.assertIsNone(availability("해변가에 접근 가능한 경사로가 있으나 모래로 된 길임", "route"))
        self.assertIsNone(availability("대여 가능(주말 이용 불가)", "wheelchair"))
        self.assertIsNone(availability("대여 가능(사전 예약)", "wheelchair"))
        self.assertIsNone(availability("대여 가능(보호자 동반 필요)", "wheelchair"))
        self.assertIsNone(availability("대여 가능(상세 정책 참고)", "wheelchair"))
        self.assertIs(availability("대여 불가능", "wheelchair"), False)

    def test_wrong_content_id_does_not_overwrite(self):
        self.sync({"wheelchair": "가능"})
        self.sync(response=envelope({"contentid": "another-place", "wheelchair": "불가"}))
        self.assertIs(AccessibilityInfo.objects.get(travel_spot=self.spot).wheelchair, True)

    def test_request_failure_log_does_not_include_credentials(self):
        import requests
        from api.services.tour_api import TourAPIService
        service = TourAPIService()
        service.api_key = 'credential-regression-placeholder'
        with patch('api.services.tour_api.requests.get', side_effect=requests.RequestException('URL includes credential-regression-placeholder')), \
             self.assertLogs('api.services.tour_api', level='INFO') as logs:
            self.assertIsNone(service._make_request('detailWithTour2', {'contentId': 'validation-test'}))
        self.assertNotIn(service.api_key, '\n'.join(logs.output))

if __name__ == "__main__":
    result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(AccessibilityChecks))
    output = Path('../results/accessibility/backend-tests.json')
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps({'tests': result.testsRun, 'failures': len(result.failures),
        'errors': len(result.errors), 'passed': result.wasSuccessful()}, indent=2), encoding='utf-8')
    raise SystemExit(0 if result.wasSuccessful() else 1)
