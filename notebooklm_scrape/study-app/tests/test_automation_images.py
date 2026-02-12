import json
import pathlib
import sys

path = pathlib.Path(__file__).resolve().parents[1] / "generated" / "Automation_Shock_and_the_Post-Work_Transition.json"
if not path.exists():
    print("Missing Automation_Shock_and_the_Post-Work_Transition.json")
    sys.exit(1)

data = json.loads(path.read_text())

blocked = [
    "https://upload.wikimedia.org/wikipedia/commons/thumb/b/ba/Barrow_Steelworks.jpg/400px-Barrow_Steelworks.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0b/Spinning_jenny.jpg/400px-Spinning_jenny.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/thumb/8/82/SelfCheckoutsWalmart.jpg/400px-SelfCheckoutsWalmart.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/thumb/e/eb/StateLibQld_1_113036_Horse_drawn_vehicle_for_carrying_goods%2C_1900-1910.jpg/400px-StateLibQld_1_113036_Horse_drawn_vehicle_for_carrying_goods%2C_1900-1910.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0a/Automation_of_foundry_with_robot.jpg/400px-Automation_of_foundry_with_robot.jpg",
]

bad = []
for img in data.get("images", []):
    url = img.get("thumbnail_url") or img.get("url") or ""
    if url in blocked:
        bad.append(url)

if bad:
    print("Found blocked automation image URLs:")
    for b in bad:
        print(f"- {b}")
    sys.exit(1)

print("OK: Automation images no longer use known broken URLs.")
