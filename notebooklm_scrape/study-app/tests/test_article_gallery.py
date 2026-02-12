import pathlib
import sys

index_path = pathlib.Path(__file__).resolve().parents[1] / "index.html"
html = index_path.read_text()

required_markers = [
    "image-gallery",
    "image-gallery-item",
    "renderImageGallery",
]

missing = [m for m in required_markers if m not in html]

if missing:
    print("Missing image gallery markers:")
    for m in missing:
        print(f"- {m}")
    sys.exit(1)

print("OK: Image gallery markers present.")
