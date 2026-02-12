import pathlib
import sys

index_path = pathlib.Path(__file__).resolve().parents[1] / "index.html"
html = index_path.read_text()

if "article-image img" not in html:
    print("Missing article-image img CSS selector.")
    sys.exit(1)

if "max-height" not in html:
    print("Missing max-height styling for article images.")
    sys.exit(1)

print("OK: Article image size constraints present.")
