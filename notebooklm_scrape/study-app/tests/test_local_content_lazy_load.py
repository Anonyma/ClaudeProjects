import pathlib
import sys

index_path = pathlib.Path(__file__).resolve().parents[1] / "index.html"
html = index_path.read_text()

if "queueLocalContentLoad" not in html:
    print("Missing queueLocalContentLoad scheduling.")
    sys.exit(1)

if "await loadLocalContent()" in html:
    print("loadLocalContent is still awaited during initial load.")
    sys.exit(1)

print("OK: Local content loading is scheduled (lazy).")
