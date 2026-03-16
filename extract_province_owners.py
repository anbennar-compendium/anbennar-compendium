"""Extract 1444 province ownership from Anbennar mod history files."""
import os
import re
import json

MOD_PATH = r"C:\Program Files (x86)\Steam\steamapps\workshop\content\236850\1385440355"
HISTORY_DIR = os.path.join(MOD_PATH, "history", "provinces")
OUTPUT = os.path.join(os.path.dirname(__file__), "province_owners.json")

ENCODINGS = ["utf-8-sig", "utf-8", "latin-1", "cp1252"]


def read_file(filepath):
    for enc in ENCODINGS:
        try:
            with open(filepath, "r", encoding=enc) as f:
                return f.read()
        except (UnicodeDecodeError, UnicodeError):
            continue
    return None


def main():
    # province_id -> owner tag (1444 start)
    province_to_owner = {}
    count = 0

    for fname in os.listdir(HISTORY_DIR):
        if not fname.endswith('.txt'):
            continue

        # Extract province ID from filename (e.g. "1 - Far_Isle.txt" -> 1)
        m = re.match(r'(\d+)', fname)
        if not m:
            continue
        prov_id = int(m.group(1))

        text = read_file(os.path.join(HISTORY_DIR, fname))
        if not text:
            continue

        # Get the top-level owner (before any date blocks like "1450.1.1 = {")
        # Only look at content before the first date block
        date_match = re.search(r'^\d{3,4}\.\d{1,2}\.\d{1,2}\s*=', text, re.MULTILINE)
        top_section = text[:date_match.start()] if date_match else text

        owner_match = re.search(r'\bowner\s*=\s*(\w+)', top_section)
        if owner_match:
            province_to_owner[prov_id] = owner_match.group(1)
            count += 1

    # Invert: tag -> [province_ids]
    tag_to_provinces = {}
    for prov_id, tag in province_to_owner.items():
        if tag not in tag_to_provinces:
            tag_to_provinces[tag] = []
        tag_to_provinces[tag].append(prov_id)

    # Sort province lists
    for tag in tag_to_provinces:
        tag_to_provinces[tag].sort()

    with open(OUTPUT, 'w', encoding='utf-8') as f:
        json.dump(tag_to_provinces, f, separators=(',', ':'))

    print(f"Extracted {count} owned provinces across {len(tag_to_provinces)} countries")
    print(f"Output: {OUTPUT} ({os.path.getsize(OUTPUT):,} bytes)")


if __name__ == '__main__':
    main()
