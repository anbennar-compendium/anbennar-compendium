"""Extract area and region province mappings from Anbennar mod."""
import os
import re
import json

MOD_PATH = r"C:\Program Files (x86)\Steam\steamapps\workshop\content\236850\1385440355"
AREA_FILE = os.path.join(MOD_PATH, "map", "area.txt")
REGION_FILE = os.path.join(MOD_PATH, "map", "region.txt")
OUTPUT = os.path.join(os.path.dirname(__file__), "area_data.json")

ENCODINGS = ["utf-8-sig", "utf-8", "latin-1", "cp1252"]


def read_file(filepath):
    for enc in ENCODINGS:
        try:
            with open(filepath, "r", encoding=enc) as f:
                return f.read()
        except (UnicodeDecodeError, UnicodeError):
            continue
    return None


def parse_areas():
    """Parse area.txt: area_name -> [province_ids]"""
    text = read_file(AREA_FILE)
    if not text:
        return {}

    # Remove comments
    text = re.sub(r'#.*', '', text)

    areas = {}
    # Match area_name = { province_ids... }
    for m in re.finditer(r'(\w+)\s*=\s*\{([^}]*)\}', text):
        name = m.group(1)
        body = m.group(2)
        # Handle both "color = { ... }" inside and bare province IDs
        # Skip color definitions
        if name == 'color':
            continue
        provs = [int(x) for x in re.findall(r'\b(\d+)\b', body)]
        if provs:
            areas[name] = provs

    return areas


def parse_regions(areas):
    """Parse region.txt: region_name -> {areas: [area_names], provinces: [province_ids]}"""
    text = read_file(REGION_FILE)
    if not text:
        return {}

    # Remove comments
    text = re.sub(r'#.*', '', text)

    regions = {}
    # Regions have nested structure: region_name = { areas = { area1 area2 } }
    for m in re.finditer(r'(\w+_region)\s*=\s*\{', text):
        name = m.group(1)
        start = m.end()
        # Find matching brace
        depth = 1
        i = start
        while i < len(text) and depth > 0:
            if text[i] == '{':
                depth += 1
            elif text[i] == '}':
                depth -= 1
            i += 1
        body = text[start:i-1]

        # Extract areas block
        areas_match = re.search(r'areas\s*=\s*\{([^}]*)\}', body)
        if areas_match:
            area_names = re.findall(r'(\w+_area)', areas_match.group(1))
            provs = []
            for a in area_names:
                provs.extend(areas.get(a, []))
            if area_names:
                regions[name] = {
                    'areas': area_names,
                    'provinces': provs
                }

    return regions


def main():
    print("Parsing areas...")
    areas = parse_areas()
    print(f"  {len(areas)} areas")

    print("Parsing regions...")
    regions = parse_regions(areas)
    print(f"  {len(regions)} regions")

    # Build output: combined areas and regions
    output = {
        'areas': areas,
        'regions': {k: v['provinces'] for k, v in regions.items()},
    }

    with open(OUTPUT, 'w', encoding='utf-8') as f:
        json.dump(output, f, separators=(',', ':'))

    print(f"Output: {OUTPUT} ({os.path.getsize(OUTPUT):,} bytes)")


if __name__ == '__main__':
    main()
