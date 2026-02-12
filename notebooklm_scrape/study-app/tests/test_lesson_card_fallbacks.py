import pathlib
import sys

index_path = pathlib.Path(__file__).resolve().parents[1] / "index.html"
html = index_path.read_text()

required = [
    "data-fallbacks",
    "handleCardImageError",
    "fallbackIndex",
]

missing = [m for m in required if m not in html]
if missing:
    print("Missing lesson card fallback markers:")
    for m in missing:
        print(f"- {m}")
    sys.exit(1)

print("OK: Lesson card fallback markers present.")
