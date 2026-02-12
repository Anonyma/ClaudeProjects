import pathlib
import sys

index_path = pathlib.Path(__file__).resolve().parents[1] / "index.html"
html = index_path.read_text()

required_markers = [
    "renderImageGallery",
    "position",
    "gallery",
]

missing = [m for m in required_markers if m not in html]

if missing:
    print("Missing gallery filter markers:")
    for m in missing:
        print(f"- {m}")
    sys.exit(1)

if "position === 'gallery'" not in html and "position === \"gallery\"" not in html:
    print("Gallery filter does not explicitly check for position === 'gallery'.")
    sys.exit(1)

print("OK: Gallery filters inline images.")
