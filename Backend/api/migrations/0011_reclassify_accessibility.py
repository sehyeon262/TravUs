"""Re-evaluate retained descriptions; unknown legacy flags are not evidence."""
from django.db import migrations
from ._accessibility_v1 import ACCESSIBILITY_FIELDS, EXTRA_TEXT_FIELDS, normalized_values

def forwards(apps, schema_editor):
    Model = apps.get_model("api", "AccessibilityInfo")
    alias = schema_editor.connection.alias
    for row in Model.objects.using(alias).iterator(chunk_size=500):
        flags = {field: getattr(row, field) for _, field, _ in ACCESSIBILITY_FIELDS}
        payload = {"_provenance": "legacy_info_fields"}
        for api_key, field, _ in ACCESSIBILITY_FIELDS:
            value = getattr(row, field + "_info")
            if value is not None:
                payload[api_key] = value
        for api_key, field in EXTRA_TEXT_FIELDS.items():
            value = getattr(row, field)
            if value is not None:
                payload[api_key] = value
        values = normalized_values(payload)
        row.legacy_flags = flags
        for field, value in values.items():
            setattr(row, field, value)
        row.save(using=alias, update_fields=["legacy_flags", *values])

def backwards(apps, schema_editor):
    Model = apps.get_model("api", "AccessibilityInfo")
    alias = schema_editor.connection.alias
    for row in Model.objects.using(alias).iterator(chunk_size=500):
        for _, field, _ in ACCESSIBILITY_FIELDS:
            # Original schema cannot represent null. Preserve recorded legacy values when available.
            setattr(row, field, bool(row.legacy_flags.get(field, getattr(row, field))))
        row.normalization_version = ""
        row.save(using=alias, update_fields=[field for _, field, _ in ACCESSIBILITY_FIELDS] + ["normalization_version"])

class Migration(migrations.Migration):
    dependencies = [("api", "0010_accessibility_tristate")]
    operations = [migrations.RunPython(forwards, backwards)]
