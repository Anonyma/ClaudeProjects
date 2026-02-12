import pathlib
import re
import sys

index_path = pathlib.Path(__file__).resolve().parents[1] / "index.html"
html = index_path.read_text()

if "notable_entities" not in html:
    print("Missing notable_entities handling in index.html")
    sys.exit(1)

load_all = re.search(r"async function loadAllData\(\)[\s\S]*?\n\s*}\n", html)
if not load_all:
    print("loadAllData function not found")
    sys.exit(1)

block = load_all.group(0)
if "Promise.all" in block:
    print("loadAllData still uses Promise.all; expected sequential loading")
    sys.exit(1)

required_calls = ["await loadLessons();", "await loadEntities();"]
for call in required_calls:
    if call not in block:
        print(f"Missing {call} in loadAllData")
        sys.exit(1)

if block.find("await loadLessons();") > block.find("await loadEntities();"):
    print("loadEntities is called before loadLessons")
    sys.exit(1)

print("OK: loadAllData sequentially loads lessons before entities and handles notable_entities.")
