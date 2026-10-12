"""Read-only TourAPI capture. Never print the key, request URL, or exception text."""
import datetime
import json
import os
from pathlib import Path
from urllib.parse import unquote
import requests

key = os.environ.get("TOUR_API_KEY", "")
if not key:
    raise SystemExit("TOUR_API_KEY is required in the process environment.")
folder = Path("../results/accessibility")
folder.mkdir(parents=True, exist_ok=True)
for content_id in ("126273", "1433504"):
    endpoint = "https://apis.data.go.kr/B551011/KorWithService2/detailWithTour2"
    try:
        response = requests.get(endpoint, params={
            "serviceKey": unquote(key), "MobileOS": "ETC", "MobileApp": "TravUs",
            "_type": "json", "contentId": content_id,
        }, timeout=25)
        try:
            body = response.json()
        except ValueError:
            print(json.dumps({"content_id": content_id, "http_status": response.status_code,
                "result": "non_json_response"}, ensure_ascii=False))
            continue
        # Public tourism response only. Credentials and the query URL are excluded.
        record = {"provenance": "live TourAPI read-only response",
            "retrieved_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "endpoint": endpoint, "content_id": content_id,
            "http_status": response.status_code, "response": body}
        filename = folder / ("live-tourapi-" + content_id + ".json")
        filename.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
        header = body.get("response", {}).get("header", {})
        items = body.get("response", {}).get("body", {}).get("items")
        print(json.dumps({"content_id": content_id, "http_status": response.status_code,
            "result_code": header.get("resultCode"), "has_items": bool(items),
            "file": str(filename)}, ensure_ascii=False))
    except requests.RequestException as exc:
        print(json.dumps({"content_id": content_id, "result": type(exc).__name__}))
