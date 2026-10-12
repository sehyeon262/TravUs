"""Capture real command -> SQLite reread -> serializer for synthetic inputs."""
import argparse
import io
import json
import os
from pathlib import Path
from unittest.mock import patch

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "travus.validation_settings")
import django
django.setup()
from django.core.management import call_command
from django.db import connection
from api.models import TravelSpot, AccessibilityInfo
from api.serializers import TravelSpotDetailSerializer
from api.accessibility import ACCESSIBILITY_FIELDS

def envelope(item):
    return {"response": {"header": {"resultCode": "0000"}, "body": {"items": {"item": [item]}}}}

def create_unmanaged_table():
    if TravelSpot._meta.db_table not in connection.introspection.table_names():
        with connection.schema_editor() as editor:
            editor.create_model(TravelSpot)

def capture(stage, output, fixture_path=Path('api/fixtures/accessibility_validation.json')):
    create_unmanaged_table()
    if AccessibilityInfo._meta.db_table not in connection.introspection.table_names():
        with connection.schema_editor() as editor:
            editor.create_model(AccessibilityInfo)
    fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
    rows = []
    for case in fixture["cases"]:
        spot, _ = TravelSpot.objects.get_or_create(
            content_id=case["id"], defaults=dict(content_type_id="12", name=case["id"],
            address="검증용 가상 장소", rating=0, review_count=0, view_count=0,
            bookmark_count=0, is_active=True))
        raw = {"contentid": case["id"], **case["input"]}
        stdout = io.StringIO()
        with patch("api.management.commands.sync_detail_info.tour_api_service.get_detail_common", return_value=envelope({"contentid": case["id"]})), \
             patch("api.management.commands.sync_detail_info.tour_api_service.get_detail_intro", return_value=envelope({})), \
             patch("api.management.commands.sync_detail_info.tour_api_service.get_detail_with_tour", return_value=envelope(raw)), \
             patch("api.management.commands.sync_detail_info.time.sleep"):
            call_command("sync_detail_info", content_id=case["id"], stdout=stdout)
        acc = AccessibilityInfo.objects.get(travel_spot=spot)  # fresh DB read, not in-memory setattr
        saved = {}
        for field in [name for _, field, _ in ACCESSIBILITY_FIELDS for name in (field, field + '_info')] + ['source_payload', 'normalization_version']:
            saved[field] = getattr(acc, field, "__MISSING_MODEL_FIELD__")
        fresh_spot = TravelSpot.objects.get(pk=spot.pk)
        serialized = TravelSpotDetailSerializer(fresh_spot).data
        if stage != 'before':
            assert len(serialized['accessibility']['facilities']) == 24
            for api_key, field, _ in ACCESSIBILITY_FIELDS:
                assert getattr(acc, field + '_info') == raw.get(api_key)
                assert serialized['accessibility'][field + '_info'] == raw.get(api_key)
            assert acc.source_payload == raw
        rows.append({"id": case["id"], "input": raw, "expected_wheelchair": case["expected"],
            "db": saved, "api": serialized, "command_output": stdout.getvalue(),
            "wheelchair_matches_expected": acc.wheelchair is case["expected"]})
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps({"stage": stage, "provenance": fixture["provenance"], "rows": rows},
        ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"stage": stage, "cases": len(rows), "matching": sum(r["wheelchair_matches_expected"] for r in rows),
        "report": str(output)}, ensure_ascii=False))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage", choices=['after', 'live-replay'], required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--fixture", type=Path, default=Path('api/fixtures/accessibility_validation.json'))
    args = parser.parse_args()
    capture(args.stage, args.output, args.fixture)
