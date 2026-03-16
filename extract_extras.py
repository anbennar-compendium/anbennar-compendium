"""
Extract government reforms and region/continent mapping from Anbennar mod files.
Part 1: Government reforms -> reforms_data.json
Part 2: Country -> superregion/continent mapping -> regions_data.json
"""

import os
import re
import json
import glob

BASE = r"C:\Program Files (x86)\Steam\steamapps\workshop\content\236850\1385440355"
OUTPUT_DIR = r"C:\Users\jjdeg\OneDrive\Desktop\anbennar-guide"
REFORMS_DIR = os.path.join(BASE, "common", "government_reforms")
LOCALISATION_DIR = os.path.join(BASE, "localisation")
MAP_DIR = os.path.join(BASE, "map")
HISTORY_DIR = os.path.join(BASE, "history", "countries")


def read_file(path):
    """Read file with multiple encoding fallbacks."""
    for enc in ("utf-8-sig", "utf-8", "latin-1", "cp1252"):
        try:
            with open(path, "r", encoding=enc) as f:
                return f.read()
        except (UnicodeDecodeError, UnicodeError):
            continue
    return ""


def load_all_localisation():
    """Load all _l_english.yml localisation files into a dict."""
    loc = {}
    pattern = os.path.join(LOCALISATION_DIR, "*_l_english.yml")
    files = glob.glob(pattern)
    print(f"Loading {len(files)} localisation files...")
    for fpath in files:
        text = read_file(fpath)
        for line in text.splitlines():
            line = line.strip()
            if not line or line.startswith("#") or line.startswith("l_english"):
                continue
            # Match: key:N "value"
            m = re.match(r'^\s*([A-Za-z0-9_.:-]+):\d*\s+"(.*)"', line)
            if m:
                loc[m.group(1)] = m.group(2)
    print(f"Loaded {len(loc)} localisation entries.")
    return loc


def strip_comments(text):
    """Remove # comments from text (but not inside quotes)."""
    lines = []
    for line in text.splitlines():
        # Simple approach: strip from first # that's not inside quotes
        in_quote = False
        result = []
        for ch in line:
            if ch == '"':
                in_quote = not in_quote
            if ch == '#' and not in_quote:
                break
            result.append(ch)
        lines.append("".join(result))
    return "\n".join(lines)


def parse_brace_block(text, start):
    """Given text and the position of an opening '{', return the content inside
    the matching '}' and the position after the closing '}'."""
    depth = 0
    i = start
    assert text[i] == '{', f"Expected '{{' at position {i}, got '{text[i]}'"
    while i < len(text):
        if text[i] == '{':
            depth += 1
        elif text[i] == '}':
            depth -= 1
            if depth == 0:
                return text[start + 1:i], i + 1
        i += 1
    return text[start + 1:], len(text)


def parse_modifiers(block_text):
    """Extract modifier key = value pairs from a modifiers block."""
    mods = {}
    for m in re.finditer(r'(\w+)\s*=\s*(-?[\d.]+)', block_text):
        key = m.group(1)
        val_str = m.group(2)
        try:
            val = int(val_str)
        except ValueError:
            val = float(val_str)
        mods[key] = val
    return mods


def detect_gov_type(filepath):
    """Detect government type from filename."""
    fname = os.path.basename(filepath).lower()
    if "monarchies" in fname or "monarchy" in fname:
        return "monarchy"
    elif "republics" in fname or "republic" in fname:
        return "republic"
    elif "theocracies" in fname or "theocracy" in fname:
        return "theocracy"
    elif "tribes" in fname or "tribal" in fname:
        return "tribal"
    elif "natives" in fname or "native" in fname:
        return "native"
    elif "common" in fname:
        return "common"
    return "unknown"


def parse_government_reforms():
    """Parse all government reform files and extract reform data."""
    loc = load_all_localisation()
    all_reforms = {}

    reform_files = sorted(glob.glob(os.path.join(REFORMS_DIR, "*.txt")))
    print(f"Found {len(reform_files)} government reform files.")

    for fpath in reform_files:
        gov_type_from_file = detect_gov_type(fpath)
        text = read_file(fpath)
        text = strip_comments(text)

        # Find top-level blocks: name = { ... }
        # We iterate through looking for identifier = { at the top brace level
        i = 0
        depth = 0
        while i < len(text):
            if depth == 0:
                # Look for: identifier = {
                m = re.match(r'\s*(\w+)\s*=\s*\{', text[i:])
                if m:
                    reform_id = m.group(1)
                    brace_pos = i + m.start() + m.end() - m.start() - 1
                    # Find the actual '{' position
                    brace_pos = text.index('{', i + m.start())
                    block_content, end_pos = parse_brace_block(text, brace_pos)

                    # Skip certain non-reform blocks
                    if reform_id in ("defaults_reform",):
                        i = end_pos
                        continue

                    # Extract icon
                    icon_m = re.search(r'icon\s*=\s*"([^"]*)"', block_content)
                    icon = icon_m.group(1) if icon_m else ""

                    # Extract modifiers block
                    modifiers = {}
                    mod_m = re.search(r'modifiers\s*=\s*\{', block_content)
                    if mod_m:
                        mod_brace = block_content.index('{', mod_m.start())
                        mod_content, _ = parse_brace_block(block_content, mod_brace)
                        modifiers = parse_modifiers(mod_content)

                    # Detect government type flags from block content
                    gov_types = {}
                    for gtype in ("monarchy", "republic", "tribal", "theocracy"):
                        gm = re.search(rf'\b{gtype}\s*=\s*(yes|no)', block_content)
                        if gm:
                            gov_types[gtype] = gm.group(1) == "yes"

                    # Also check basic_reform flag
                    basic_m = re.search(r'basic_reform\s*=\s*(yes|no)', block_content)
                    is_basic = basic_m and basic_m.group(1) == "yes"

                    # Localisation
                    display_name = loc.get(reform_id, reform_id)
                    description = loc.get(f"{reform_id}_desc", "")

                    reform_data = {
                        "id": reform_id,
                        "name": display_name,
                        "description": description,
                        "icon": icon,
                        "modifiers": modifiers,
                        "government_types": gov_types,
                        "is_basic_reform": is_basic,
                        "source_file": os.path.basename(fpath),
                        "file_gov_type": gov_type_from_file,
                    }
                    all_reforms[reform_id] = reform_data
                    i = end_pos
                    continue
            i += 1

    print(f"Extracted {len(all_reforms)} government reforms.")
    return all_reforms


def parse_area_file():
    """Parse area.txt: area_name = { province_ids ... }"""
    text = read_file(os.path.join(MAP_DIR, "area.txt"))
    text = strip_comments(text)
    areas = {}  # area_name -> list of province ids
    for m in re.finditer(r'(\w+)\s*=\s*\{', text):
        name = m.group(1)
        brace_pos = text.index('{', m.start())
        content, _ = parse_brace_block(text, brace_pos)
        # Check if content has province numbers (not area names)
        provs = re.findall(r'\b(\d+)\b', content)
        if provs:
            areas[name] = [int(p) for p in provs]
    print(f"Parsed {len(areas)} areas.")
    return areas


def parse_region_file():
    """Parse region.txt: region_name = { areas = { area_name ... } }"""
    text = read_file(os.path.join(MAP_DIR, "region.txt"))
    text = strip_comments(text)
    regions = {}  # region_name -> list of area names
    i = 0
    while i < len(text):
        m = re.match(r'\s*(\w+)\s*=\s*\{', text[i:])
        if m:
            region_name = m.group(1)
            brace_pos = text.index('{', i + m.start())
            content, end_pos = parse_brace_block(text, brace_pos)
            # Find areas = { ... } inside
            areas_m = re.search(r'areas\s*=\s*\{', content)
            if areas_m:
                areas_brace = content.index('{', areas_m.start())
                areas_content, _ = parse_brace_block(content, areas_brace)
                area_names = re.findall(r'(\w+)', areas_content)
                regions[region_name] = area_names
            else:
                # Empty region or no areas block
                regions[region_name] = []
            i = end_pos
            continue
        i += 1
    print(f"Parsed {len(regions)} regions.")
    return regions


def parse_superregion_file():
    """Parse superregion.txt: superregion_name = { region_names ... }"""
    text = read_file(os.path.join(MAP_DIR, "superregion.txt"))
    text = strip_comments(text)
    superregions = {}  # superregion_name -> list of region names
    i = 0
    while i < len(text):
        m = re.match(r'\s*(\w+)\s*=\s*\{', text[i:])
        if m:
            sr_name = m.group(1)
            brace_pos = text.index('{', i + m.start())
            content, end_pos = parse_brace_block(text, brace_pos)
            # Extract region names (words, not keywords like restrict_charter)
            tokens = re.findall(r'(\w+)', content)
            # Filter: region names end with _region
            region_names = [t for t in tokens if t.endswith("_region")]
            superregions[sr_name] = region_names
            i = end_pos
            continue
        i += 1
    print(f"Parsed {len(superregions)} superregions.")
    return superregions


def parse_continent_file():
    """Parse continent.txt: continent_name = { province_ids ... }"""
    text = read_file(os.path.join(MAP_DIR, "continent.txt"))
    text = strip_comments(text)
    continents = {}  # continent_name -> set of province ids
    i = 0
    while i < len(text):
        m = re.match(r'\s*(\w+)\s*=\s*\{', text[i:])
        if m:
            cont_name = m.group(1)
            brace_pos = text.index('{', i + m.start())
            content, end_pos = parse_brace_block(text, brace_pos)
            provs = re.findall(r'\b(\d+)\b', content)
            continents[cont_name] = set(int(p) for p in provs)
            i = end_pos
            continue
        i += 1
    print(f"Parsed {len(continents)} continents.")
    return continents


def get_country_capitals():
    """Parse history/countries files to get capital province for each tag."""
    capitals = {}
    history_files = glob.glob(os.path.join(HISTORY_DIR, "*.txt"))
    for fpath in history_files:
        fname = os.path.basename(fpath)
        # Extract tag from filename like "A01 - Lorent.txt"
        tag_m = re.match(r'([A-Z0-9]+)\s*-', fname)
        if not tag_m:
            continue
        tag = tag_m.group(1)
        text = read_file(fpath)
        # Find capital = NUMBER (before any date block)
        cap_m = re.search(r'capital\s*=\s*(\d+)', text)
        if cap_m:
            capitals[tag] = int(cap_m.group(1))
    print(f"Found capitals for {len(capitals)} countries.")
    return capitals


def build_region_mapping():
    """Build country tag -> continent/superregion/region mapping."""
    loc = load_all_localisation()

    # Parse all map files
    areas = parse_area_file()          # area -> [provinces]
    regions = parse_region_file()      # region -> [areas]
    superregions = parse_superregion_file()  # superregion -> [regions]
    continents = parse_continent_file()      # continent -> {provinces}

    # Build province -> area mapping
    prov_to_area = {}
    for area_name, provs in areas.items():
        for p in provs:
            prov_to_area[p] = area_name

    # Build area -> region mapping
    area_to_region = {}
    for region_name, area_list in regions.items():
        for a in area_list:
            area_to_region[a] = region_name

    # Build region -> superregion mapping
    region_to_sr = {}
    for sr_name, region_list in superregions.items():
        for r in region_list:
            region_to_sr[r] = sr_name

    # Build province -> continent mapping
    prov_to_continent = {}
    for cont_name, provs in continents.items():
        for p in provs:
            prov_to_continent[p] = cont_name

    # Load anbennar_data.json to get country list
    anb_path = os.path.join(OUTPUT_DIR, "anbennar_data.json")
    with open(anb_path, "r", encoding="utf-8") as f:
        anbennar_data = json.load(f)

    # Get capitals from history files
    capitals = get_country_capitals()

    # Build the mapping
    result = {}
    matched = 0
    for tag in anbennar_data:
        cap = capitals.get(tag)
        if cap is None:
            continue

        continent = prov_to_continent.get(cap, "")
        area = prov_to_area.get(cap, "")
        region = area_to_region.get(area, "")
        superregion = region_to_sr.get(region, "")

        # Get display names from localisation
        superregion_name = loc.get(superregion, superregion.replace("_superregion", "").replace("_", " ").title()) if superregion else ""
        region_name = loc.get(region, region.replace("_region", "").replace("_", " ").title()) if region else ""

        result[tag] = {
            "continent": continent,
            "superregion": superregion,
            "superregion_name": superregion_name,
            "region": region,
            "region_name": region_name,
            "area": area,
            "capital_province": cap,
        }
        if superregion:
            matched += 1

    print(f"Built region mapping for {len(result)} countries ({matched} with superregion).")
    return result


def main():
    print("=" * 60)
    print("Part 1: Government Reforms")
    print("=" * 60)
    reforms = parse_government_reforms()
    reforms_path = os.path.join(OUTPUT_DIR, "reforms_data.json")
    with open(reforms_path, "w", encoding="utf-8") as f:
        json.dump(reforms, f, indent=2, ensure_ascii=False)
    print(f"Saved reforms to {reforms_path}")

    print()
    print("=" * 60)
    print("Part 2: Region/Continent Mapping")
    print("=" * 60)
    regions = build_region_mapping()
    regions_path = os.path.join(OUTPUT_DIR, "regions_data.json")
    with open(regions_path, "w", encoding="utf-8") as f:
        json.dump(regions, f, indent=2, ensure_ascii=False)
    print(f"Saved regions to {regions_path}")

    # Print some samples
    print("\nSample reforms:")
    for i, (k, v) in enumerate(reforms.items()):
        if i >= 3:
            break
        print(f"  {k}: {v['name']} - modifiers: {v['modifiers']}")

    print("\nSample region mappings:")
    for i, (k, v) in enumerate(regions.items()):
        if i >= 5:
            break
        print(f"  {k}: continent={v['continent']}, superregion={v['superregion_name']}, region={v['region_name']}")


if __name__ == "__main__":
    main()
