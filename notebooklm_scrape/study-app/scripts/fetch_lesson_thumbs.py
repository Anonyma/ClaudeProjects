import json
import os
import sys
import time
from pathlib import Path
import requests

LESSON_MAP = {
    "Why_Brutalism_Started_With_Floral_Wallpaper": "Barbican Estate",
    "Art_Nouveau_The_Brief_Beautiful_Dream": "Art Nouveau",
    "Art_Deco_Fused_King_Tut_With_Chrome": "Tutankhamun",
    "Rococo_curves_to_Brutalist_blocks": "Rococo",
    "The_Glamour_and_Geometry_of_Art_Deco": "Rockefeller Center",
    "Ornament_to_Austerity_Political_Necessity_or_Purity": "Adolf Loos",
    "Architecture_as_a_Trauma_Response": "Boston City Hall",
    "How_Irony_Killed_the_Glass_Box": "550 Madison Avenue",
    "Big_History_in_25_Anchor_Dates": "Earth",
    "The_American_Experiment_From_Cahokia_to_Reconstruction": "Cahokia",
    "The_Rise_and_Fracture_of_Modern_America": "United States Capitol",
    "Washington_the_Town_Destroyer_and_Fragile_Experiments": "George Washington",
    "Versailles_Was_Actually_A_Golden_Prison": "Palace of Versailles",
    "Native_Cities_and_the_Sovereignty_Straitjacket": "Indigenous peoples of the Americas",
    "How_American_Literature_Shattered_Reality": "American literature",
    "Murder_Jazz_and_the_Birth_of_the_Beats": "Louis Armstrong",
    "The_Beat_Generation_Started_With_Murder": "Beat Generation",
    "The_Great_Refusal_of_the_American_Dream": "Herbert Marcuse",
    "Mapping_Americas_Inner_Life_Through_Fiction": "The Great Gatsby",
    "Selling_The_Revolution_At_A_Markup": "Edward Bernays",
    "The_Six_Materials_That_Built_Civilization": "Steel",
    "How_Physical_Materials_Dictate_History": "Bronze Age",
    "How_Materials_Rewired_Human_History": "Industrial Revolution",
    "Iron_Sugar_and_Mirrors_Rewired_Humanity": "Sugar",
    "The_Bomb_LSD_and_Silicon_Valley": "Silicon Valley",
    "Automation_Shock_and_the_Post-Work_Transition": "Automation",
    "Universal_Basic_Income_vs_The_Jobless_Future": "Negative income tax",
    "Exploding_Buildings_And_The_End_Of_Truth": "September 11 attacks",
    "BBB_Crossing_Technologies": "Brain",
    "CRISPR_2_Base_Prime_Epigenetic_Editing": "CRISPR",
    "Microbiome_Gut_Brain_Axis": "Human microbiome",
    "Neuroscience_Consciousness_Perception": "Neuroscience",
    "Senolytics_Cellular_Senescence": "Cellular senescence",
    "Philosophy_Technology_AI_Ethics": "Deep learning",
    "Architecture_Beyond_Postmodernism": "Heydar Aliyev Center",
    "Adolf_Loos_Ornament_and_Crime": "Looshaus",
    "Japanese_History_Culture_Power_Transformation": "Japan",
    "Fin_de_Siecle_Vienna_The_Explosion_That_Changed_Everything": "Vienna Secession",
    "Freuds_Vienna_How_One_City_Invented_the_Unconscious": "Sigmund Freud",
    "Red_Vienna_The_Socialist_Utopia_That_Got_Built": "Karl-Marx-Hof",
    "The_Habsburg_Machine_How_an_Empire_Shaped_a_City": "House of Habsburg",
    "The_Ringstrasse_Vienna_Rebuilt_Itself_as_a_Statement": "Ringstrasse",
    "Vienna_1938_1955_Anschluss_War_and_the_Cold_War_City": "Anschluss",
    "Viennas_Sound_From_Mozart_to_the_Death_of_Tonality": "Wolfgang Amadeus Mozart",
}

API_USER_AGENT = "notebooklm-study-hub/1.0 (contact: user@example.com)"
HEADERS_API = {"User-Agent": API_USER_AGENT}
HEADERS_IMG = {"User-Agent": "Mozilla/5.0"}

OUT_DIR = Path("study-app/assets/lesson-thumbs")
OUT_DIR.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT_DIR / "overrides.json"


def fetch_pageimage(title):
    params = {
        "action": "query",
        "prop": "pageimages",
        "piprop": "thumbnail|name",
        "titles": title,
        "pithumbsize": 1200,
        "format": "json",
        "origin": "*",
    }
    r = requests.get("https://en.wikipedia.org/w/api.php", params=params, headers=HEADERS_API, timeout=15)
    r.raise_for_status()
    data = r.json()
    pages = data.get("query", {}).get("pages", {})
    page = next(iter(pages.values()), {})
    return page.get("title"), page.get("pageimage"), page.get("thumbnail", {}).get("source")


def fetch_commons_attribution(file_title):
    if not file_title:
        return "Wikimedia Commons"
    params = {
        "action": "query",
        "titles": f"File:{file_title}",
        "prop": "imageinfo",
        "iiprop": "extmetadata|url",
        "format": "json",
    }
    r = requests.get("https://commons.wikimedia.org/w/api.php", params=params, headers=HEADERS_API, timeout=15)
    r.raise_for_status()
    data = r.json()
    pages = data.get("query", {}).get("pages", {})
    page = next(iter(pages.values()), {})
    info = (page.get("imageinfo") or [{}])[0]
    meta = info.get("extmetadata", {})
    artist = meta.get("Artist", {}).get("value") or ""
    license_name = meta.get("LicenseShortName", {}).get("value") or ""
    artist = artist.replace("<", "").replace(">", "")
    pieces = [p for p in [artist, license_name, "via Wikimedia Commons"] if p]
    return ", ".join(pieces) if pieces else "Wikimedia Commons"


def download_image(url, dest):
    for attempt in range(3):
        r = requests.get(url, headers=HEADERS_IMG, timeout=20)
        if r.status_code != 429:
            r.raise_for_status()
            dest.write_bytes(r.content)
            return
        time.sleep(3.0 + attempt)
    proxy_url = f"https://images.weserv.nl/?url={url}&w=1200"
    r = requests.get(proxy_url, headers=HEADERS_IMG, timeout=20)
    r.raise_for_status()
    dest.write_bytes(r.content)


def main():
    overrides = {}
    missing = []

    for slug, title in LESSON_MAP.items():
        try:
            page_title, pageimage, thumb_url = fetch_pageimage(title)
        except Exception as exc:
            missing.append({"slug": slug, "title": title, "error": str(exc)})
            continue

        if not thumb_url:
            missing.append({"slug": slug, "title": title, "error": "no_thumbnail"})
            continue

        ext = os.path.splitext(thumb_url.split("?")[0])[1].lower() or ".jpg"
        dest_name = f"{slug}{ext}"
        dest_path = OUT_DIR / dest_name

        try:
            download_image(thumb_url, dest_path)
        except Exception as exc:
            missing.append({"slug": slug, "title": title, "error": str(exc)})
            continue

        attribution = fetch_commons_attribution(pageimage)
        overrides[slug] = {
            "path": f"assets/lesson-thumbs/{dest_name}",
            "source_page": f"https://en.wikipedia.org/wiki/{page_title.replace(' ', '_') if page_title else title.replace(' ', '_')}",
            "source_image": pageimage or "",
            "attribution": attribution,
        }
        time.sleep(2.0)

    OUT_JSON.write_text(json.dumps(overrides, indent=2, ensure_ascii=True))

    missing_path = OUT_DIR / "missing.json"
    missing_path.write_text(json.dumps(missing, indent=2, ensure_ascii=True))
    if missing:
        print(f"Missing thumbnails: {len(missing)} (see {missing_path})")
        sys.exit(1)


if __name__ == "__main__":
    main()
