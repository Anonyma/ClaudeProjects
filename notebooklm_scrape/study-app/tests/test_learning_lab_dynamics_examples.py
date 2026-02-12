import pathlib
import sys

html_path = pathlib.Path(__file__).resolve().parents[1] / "prototypes" / "learning-lab-dynamics.html"
html = html_path.read_text()

required_ids = [
    "graph-detail",
    "graph-chips",
    "orbit-title",
    "orbit-detail",
    "scenario-output",
    "lens-summary",
    "heatmap-detail",
    "artifact-preview",
    "artifact-image",
    "concept-matrix",
    "matrix-detail",
]

missing = [item for item in required_ids if item not in html]
if missing:
    print("Missing required prototype ids:")
    for item in missing:
        print(f"- {item}")
    sys.exit(1)

required_markers = [
    "orbit-chip",
    "data-detail",
    "artifact-card",
    "data-note",
    "data-image",
    "heatmap-cell",
]

missing_markers = [item for item in required_markers if item not in html]
if missing_markers:
    print("Missing required prototype markers:")
    for item in missing_markers:
        print(f"- {item}")
    sys.exit(1)

required_hooks = [
    "graph-title",
    "graph-meta",
    "graph-tags",
    "heatmap-detail",
    "artifact-note",
    "matrix-detail",
    "scenario-output",
]

missing_hooks = [item for item in required_hooks if f"getElementById('{item}')" not in html and f'getElementById("{item}")' not in html]
if missing_hooks:
    print("Missing JS hooks for interactive prototype elements:")
    for item in missing_hooks:
        print(f"- {item}")
    sys.exit(1)

print("OK: learning-lab dynamics has example content and interaction hooks.")
