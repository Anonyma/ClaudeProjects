import json
import pathlib
import sys

path = pathlib.Path(__file__).resolve().parents[1] / "assets" / "lesson-thumbs" / "overrides.json"
if not path.exists():
    print("Missing overrides.json")
    sys.exit(1)

data = json.loads(path.read_text())
required = [
    "The Ethics of Raw Concrete: Brutalism and the Socialist Dream",
    "The Rococo Rebellion and the Return of the Senses",
]
missing = [k for k in required if k not in data]

if missing:
    print("Missing thumbnail overrides for:")
    for m in missing:
        print(f"- {m}")
    sys.exit(1)

print("OK: Thumbnail overrides cover additional supabase-only lessons.")
