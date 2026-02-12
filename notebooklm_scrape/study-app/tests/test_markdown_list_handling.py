import pathlib
import sys

index_path = pathlib.Path(__file__).resolve().parents[1] / "index.html"
html = index_path.read_text()

patterns = ["\\s*[-•–]", "<li>"]

if "replace(/^" not in html:
    print("Missing markdown list replacement logic.")
    sys.exit(1)

if "-•–" not in html and "[-•–]" not in html:
    print("List regex does not support bullet or en-dash prefixes.")
    sys.exit(1)

if "\\s*" not in html:
    print("List regex does not allow leading whitespace.")
    sys.exit(1)

print("OK: Markdown list handling supports optional whitespace and bullet prefixes.")
