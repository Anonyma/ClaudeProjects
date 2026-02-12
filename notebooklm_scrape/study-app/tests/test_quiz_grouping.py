import pathlib
import sys

index_path = pathlib.Path(__file__).resolve().parents[1] / "index.html"
html = index_path.read_text()

required = [
    "quiz-group",
    "quiz-group-header",
    "renderQuizzes",
]

missing = [m for m in required if m not in html]
if missing:
    print("Missing quiz grouping markers:")
    for m in missing:
        print(f"- {m}")
    sys.exit(1)

print("OK: Quiz grouping markers present.")
