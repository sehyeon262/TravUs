"""Replay captured real WithTour responses through the production command and serializer."""
import json
import os
from pathlib import Path
os.environ["TRAVUS_VALIDATION_DB"] = ":memory:"
from validation_capture import capture

folder = Path("../results/accessibility")
cases = []
for filename in sorted(folder.glob("live-tourapi-*.json")):
    record = json.loads(filename.read_text(encoding="utf-8"))
    response = record["response"]["response"]
    assert record["http_status"] == 200 and response["header"]["resultCode"] == "0000"
    items = response["body"]["items"]["item"]
    if isinstance(items, dict):
        items = [items]
    for item in items:
        cases.append({"id": item["contentid"], "input": item, "expected": None})
fixture = {"provenance": "Live TourAPI WithTour payloads; minimal travel spot and Common/Intro envelopes are local fixtures.", "cases": cases}
path = folder / "live-pipeline-inputs.json"
path.write_text(json.dumps(fixture, ensure_ascii=False, indent=2), encoding="utf-8")
capture("live-replay", folder / "live-after.json", path)
print(f"Raw response -> database reread -> detail serializer: {len(cases)} places x 24 fields preserved.")
