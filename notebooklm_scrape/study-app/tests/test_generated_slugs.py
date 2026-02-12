import json
import pathlib
import sys

GENERATED_DIR = pathlib.Path(__file__).resolve().parents[1] / "generated"

failures = []

for path in sorted(GENERATED_DIR.glob("*.json")):
    data = json.loads(path.read_text())

    # Only validate lesson-style JSON (must have article + title)
    if "article" not in data or "title" not in data:
        continue

    if not data.get("slug") or not data.get("id"):
        failures.append(path.name)

if failures:
    print("Missing slug/id for lesson JSON:")
    for name in failures:
        print(f"- {name}")
    sys.exit(1)

print("OK: All lesson JSON files have slug and id.")
