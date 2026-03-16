"""Extract province details (development, trade goods, culture, religion) for map tooltips."""
import os
import re
import json

MOD_PATH = r"C:\Program Files (x86)\Steam\steamapps\workshop\content\236850\1385440355"
HISTORY_DIR = os.path.join(MOD_PATH, "history", "provinces")
OUTPUT = os.path.join(os.path.dirname(__file__), "province_details.json")

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
    details = {}
    count = 0

    for fname in os.listdir(HISTORY_DIR):
        if not fname.endswith('.txt'):
            continue

        m = re.match(r'(\d+)', fname)
        if not m:
            continue
        prov_id = m.group(1)

        text = read_file(os.path.join(HISTORY_DIR, fname))
        if not text:
            continue

        # Only parse top-level (before date blocks)
        date_match = re.search(r'^\d{3,4}\.\d{1,2}\.\d{1,2}\s*=', text, re.MULTILINE)
        top = text[:date_match.start()] if date_match else text

        # Remove comments
        top = re.sub(r'#.*', '', top)

        info = {}

        # Development
        tax = re.search(r'base_tax\s*=\s*(\d+)', top)
        prod = re.search(r'base_production\s*=\s*(\d+)', top)
        man = re.search(r'base_manpower\s*=\s*(\d+)', top)

        if tax: info['t'] = int(tax.group(1))
        if prod: info['p'] = int(prod.group(1))
        if man: info['m'] = int(man.group(1))

        # Trade goods
        tg = re.search(r'trade_goods\s*=\s*(\w+)', top)
        if tg: info['g'] = tg.group(1)

        # Culture
        cult = re.search(r'\bculture\s*=\s*(\w+)', top)
        if cult: info['c'] = cult.group(1)

        # Religion
        rel = re.search(r'\breligion\s*=\s*(\w+)', top)
        if rel: info['r'] = rel.group(1)

        # Owner
        owner = re.search(r'\bowner\s*=\s*(\w+)', top)
        if owner: info['o'] = owner.group(1)

        # Capital name
        cap = re.search(r'capital\s*=\s*"([^"]+)"', top)
        if cap and cap.group(1): info['n'] = cap.group(1)

        if info:
            details[prov_id] = info
            count += 1

    with open(OUTPUT, 'w', encoding='utf-8') as f:
        json.dump(details, f, separators=(',', ':'))

    print(f"Extracted details for {count} provinces")
    print(f"Output: {OUTPUT} ({os.path.getsize(OUTPUT):,} bytes)")


if __name__ == '__main__':
    main()
