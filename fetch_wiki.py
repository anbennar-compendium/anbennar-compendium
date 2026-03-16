import json
import re
import time
import unicodedata
import requests

DATA_PATH = r"C:\Users\jjdeg\OneDrive\Desktop\anbennar-guide\anbennar_data.json"
OUTPUT_PATH = r"C:\Users\jjdeg\OneDrive\Desktop\anbennar-guide\wiki_data.json"
API_URL = "https://anbennar.fandom.com/api.php"


def strip_accents(text):
    """Replace accented characters with their ASCII equivalents."""
    nfkd = unicodedata.normalize('NFKD', text)
    return ''.join(c for c in nfkd if not unicodedata.combining(c))


def fetch_wiki_info(title, session):
    """Fetch page existence and length for a given title. Returns (page_length, page_title) or None."""
    params = {
        "action": "query",
        "titles": title,
        "prop": "info",
        "format": "json",
    }
    try:
        resp = session.get(API_URL, params=params, timeout=5)
        resp.raise_for_status()
        data = resp.json()
        pages = data.get("query", {}).get("pages", {})
        for page_id, page in pages.items():
            if page_id == "-1" or "missing" in page:
                return None
            length = page.get("length", 0)
            page_title = page.get("title", title)
            return (length, page_title)
    except Exception as e:
        print(f"  Error fetching info for '{title}': {e}")
    return None


def extract_intro_from_wikitext(wikitext):
    """Extract the first paragraph of plain text from wikitext, skipping templates/infoboxes."""
    # Remove nested templates like {{Country ... }}
    # We need to handle nested braces
    result = wikitext
    # Iteratively remove {{ ... }} (handles nesting by repeated passes)
    for _ in range(20):
        new = re.sub(r'\{\{[^{}]*\}\}', '', result)
        if new == result:
            break
        result = new

    # Remove remaining HTML tags
    result = re.sub(r'<[^>]+>', '', result)
    # Remove file/image links [[File:...]] or [[Image:...]]
    result = re.sub(r'\[\[(File|Image):[^\]]*\]\]', '', result, flags=re.IGNORECASE)
    # Convert wiki links [[target|display]] -> display, [[target]] -> target
    result = re.sub(r'\[\[[^\]]*\|([^\]]*)\]\]', r'\1', result)
    result = re.sub(r'\[\[([^\]]*)\]\]', r'\1', result)
    # Remove bold/italic markers
    result = re.sub(r"'{2,}", '', result)
    # Clean up whitespace
    result = result.strip()

    # Get first non-empty paragraph
    paragraphs = result.split('\n')
    for p in paragraphs:
        p = p.strip()
        if len(p) > 30:  # skip very short fragments
            return p
    return ""


def fetch_wiki_intro(page_title, session):
    """Fetch the intro text from a wiki page using the parse API."""
    params = {
        "action": "parse",
        "page": page_title,
        "prop": "wikitext",
        "format": "json",
    }
    try:
        resp = session.get(API_URL, params=params, timeout=5)
        resp.raise_for_status()
        data = resp.json()
        wikitext = data.get("parse", {}).get("wikitext", {}).get("*", "")
        if wikitext:
            return extract_intro_from_wikitext(wikitext)
    except Exception as e:
        print(f"  Error fetching intro for '{page_title}': {e}")
    return ""


def main():
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        countries = json.load(f)

    print(f"Loaded {len(countries)} countries from data file.")

    session = requests.Session()
    session.headers.update({"User-Agent": "AnbennarGuideBot/1.0 (personal project)"})

    results = {}
    total = len(countries)

    # Phase 1: Check which pages exist and get page lengths
    print("\n=== Phase 1: Finding wiki pages ===")
    for i, (tag, info) in enumerate(countries.items(), 1):
        name = info.get("name", tag)

        result = fetch_wiki_info(name, session)

        # If not found, try without accents
        if result is None:
            stripped = strip_accents(name)
            if stripped != name:
                time.sleep(0.2)
                result = fetch_wiki_info(stripped, session)

        if result is not None:
            length, page_title = result
            wiki_url = "https://anbennar.fandom.com/wiki/" + page_title.replace(" ", "_")
            results[tag] = {
                "wiki_url": wiki_url,
                "intro": "",
                "page_length": length,
                "found": True,
                "_page_title": page_title,  # temp field for phase 2
            }
        else:
            results[tag] = {
                "wiki_url": "",
                "intro": "",
                "page_length": 0,
                "found": False,
            }

        if i % 50 == 0 or i == total:
            found_count = sum(1 for v in results.values() if v["found"])
            print(f"  Progress: {i}/{total} processed, {found_count} found so far.")

        time.sleep(0.2)

    found_entries = {k: v for k, v in results.items() if v["found"]}
    print(f"\nFound {len(found_entries)} wiki pages.")

    # Phase 2: Fetch intro text for found pages
    print("\n=== Phase 2: Fetching intro text ===")
    found_list = list(found_entries.items())
    for i, (tag, entry) in enumerate(found_list, 1):
        page_title = entry["_page_title"]
        intro = fetch_wiki_intro(page_title, session)
        results[tag]["intro"] = intro

        if i % 50 == 0 or i == len(found_list):
            with_intro = sum(1 for k, v in results.items() if v.get("intro"))
            print(f"  Progress: {i}/{len(found_list)} intros fetched, {with_intro} have text.")

        time.sleep(0.2)

    # Remove temp field and save
    for v in results.values():
        v.pop("_page_title", None)

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    found_total = sum(1 for v in results.values() if v["found"])
    with_intro = sum(1 for v in results.values() if v.get("intro"))
    print(f"\nDone! {found_total}/{total} countries found on wiki, {with_intro} have intro text.")
    print(f"Results saved to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
