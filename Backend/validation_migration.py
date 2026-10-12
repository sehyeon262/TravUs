"""Validate schema + retained-data forward/backward migration in a disposable SQLite DB."""
import json
import os
from pathlib import Path
os.environ["DJANGO_SETTINGS_MODULE"] = "travus.validation_settings"
os.environ["TRAVUS_VALIDATION_DB"] = ":memory:"
import django
django.setup()
from django.db import connection
from django.db.migrations.executor import MigrationExecutor

old = [("api", "0009_coursespot_day_coursespot_spot_type")]
new = [("api", "0011_reclassify_accessibility")]
executor = MigrationExecutor(connection)
executor.migrate(old)
apps = executor.loader.project_state(old).apps
Spot = apps.get_model("api", "TravelSpot")
Acc = apps.get_model("api", "AccessibilityInfo")
if Spot._meta.db_table not in connection.introspection.table_names():
    with connection.schema_editor() as editor:
        editor.create_model(Spot)
spot = Spot.objects.create(content_id="legacy-test", content_type_id="12", name="기존 데이터 검증",
    address="검증 전용", rating=0, review_count=0, view_count=0, bookmark_count=0, is_active=True)
saved = Acc.objects.create(travel_spot=spot, wheelchair=True, wheelchair_info="대여 불가", audio_guide=True)
row_id = saved.pk
executor = MigrationExecutor(connection)
executor.migrate(new)
NewAcc = executor.loader.project_state(new).apps.get_model("api", "AccessibilityInfo")
row = NewAcc.objects.get(pk=row_id)
assert row.wheelchair is False
assert row.audio_guide is None
assert row.legacy_flags["wheelchair"] is True
assert row.legacy_flags["audio_guide"] is True
assert row.source_payload["wheelchair"] == "대여 불가"
result = {"forward": {"wheelchair": row.wheelchair, "audio_guide": row.audio_guide,
    "retained_legacy_flags": row.legacy_flags, "source_payload": row.source_payload}}
# Also verify rollback of newly inserted unknown values into the legacy non-null schema.
NewAcc.objects.filter(pk=row_id).update(audio_guide=None)
executor = MigrationExecutor(connection)
executor.migrate(old)
OldAcc = executor.loader.project_state(old).apps.get_model("api", "AccessibilityInfo")
row = OldAcc.objects.get(pk=row_id)
assert row.wheelchair is True
assert row.audio_guide is True
result["rollback"] = {"wheelchair": row.wheelchair, "audio_guide": row.audio_guide}
MigrationExecutor(connection).migrate(new)
result["forward_again"] = "passed"
out = Path("../results/accessibility/migration.json")
out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
print("Migration forward, rollback and forward again: passed.")
