"""
Extract mission data (triggers, effects, provinces_to_highlight, potential)
from Anbennar EU4 mod mission files, with localisation resolution.
"""

import os
import json
import re
import sys
from pathlib import Path

MISSIONS_DIR = r"C:\Program Files (x86)\Steam\steamapps\workshop\content\236850\1385440355\missions"
LOCALISATION_DIR = r"C:\Program Files (x86)\Steam\steamapps\workshop\content\236850\1385440355\localisation"
OUTPUT_FILE = r"C:\Users\jjdeg\OneDrive\Desktop\anbennar-guide\mission_triggers.json"

ENCODINGS = ["utf-8-sig", "utf-8", "latin-1", "cp1252"]


def read_file(filepath):
    """Read file with encoding fallbacks."""
    for enc in ENCODINGS:
        try:
            with open(filepath, "r", encoding=enc) as f:
                return f.read()
        except (UnicodeDecodeError, UnicodeError):
            continue
    print(f"  WARNING: Could not read {filepath} with any encoding")
    return None


def strip_comments(text):
    """Remove # comments from text, but not inside quoted strings."""
    result = []
    i = 0
    in_quote = False
    while i < len(text):
        ch = text[i]
        if ch == '"':
            in_quote = not in_quote
            result.append(ch)
        elif ch == '#' and not in_quote:
            # Skip to end of line
            while i < len(text) and text[i] != '\n':
                i += 1
            # Don't skip the newline itself
            continue
        else:
            result.append(ch)
        i += 1
    return ''.join(result)


def extract_brace_block(text, start_pos):
    """
    Given text and the position of an opening '{', extract everything
    between the braces (handling nesting). Returns (content, end_pos)
    where end_pos is the position after the closing '}'.
    """
    assert text[start_pos] == '{', f"Expected '{{' at position {start_pos}, got '{text[start_pos]}'"
    depth = 1
    i = start_pos + 1
    in_quote = False
    while i < len(text) and depth > 0:
        ch = text[i]
        if ch == '"':
            in_quote = not in_quote
        elif not in_quote:
            if ch == '{':
                depth += 1
            elif ch == '}':
                depth -= 1
        i += 1
    content = text[start_pos + 1:i - 1]
    return content.strip(), i


def find_block(text, key):
    """
    Find 'key = {' in text and extract the brace block content.
    Returns the content string or None.
    """
    # Match key = { with possible whitespace
    pattern = re.compile(r'\b' + re.escape(key) + r'\s*=\s*\{')
    m = pattern.search(text)
    if not m:
        return None
    brace_pos = m.end() - 1  # position of '{'
    content, _ = extract_brace_block(text, brace_pos)
    return content


def parse_top_level_blocks(text):
    """
    Parse the top-level blocks in a mission file.
    Returns list of (block_name, block_content, block_start, block_end).
    """
    blocks = []
    i = 0
    length = len(text)
    while i < length:
        # Skip whitespace
        while i < length and text[i] in ' \t\r\n':
            i += 1
        if i >= length:
            break
        # Read identifier
        if text[i] == '{' or text[i] == '}':
            i += 1
            continue
        start = i
        while i < length and text[i] not in ' \t\r\n={':
            i += 1
        name = text[start:i]
        if not name:
            i += 1
            continue
        # Skip whitespace
        while i < length and text[i] in ' \t\r\n':
            i += 1
        if i >= length:
            break
        # Expect = {
        if text[i] == '=':
            i += 1
            while i < length and text[i] in ' \t\r\n':
                i += 1
            if i < length and text[i] == '{':
                content, end = extract_brace_block(text, i)
                blocks.append((name, content))
                i = end
            else:
                i += 1
        elif text[i] == '{':
            content, end = extract_brace_block(text, i)
            blocks.append((name, content))
            i = end
        else:
            i += 1
    return blocks


def extract_simple_values(text, key):
    """Extract all 'key = VALUE' from text (non-block values)."""
    pattern = re.compile(r'\b' + re.escape(key) + r'\s*=\s*(\S+)')
    return [m.group(1) for m in pattern.finditer(text)]


def extract_potential_tags(potential_text):
    """Extract tag values from a potential block."""
    if not potential_text:
        return []
    tags = re.findall(r'\btag\s*=\s*(\w+)', potential_text)
    return tags


def extract_tooltip_keys(text):
    """Extract tooltip/custom_trigger_tooltip keys from trigger text."""
    keys = set()
    # tooltip = key_name
    for m in re.finditer(r'\btooltip\s*=\s*(\w+)', text):
        keys.add(m.group(1))
    # custom_tooltip = key_name
    for m in re.finditer(r'\bcustom_tooltip\s*=\s*(\w+)', text):
        keys.add(m.group(1))
    return keys


def parse_missions_from_group(group_content):
    """
    Parse individual missions from a mission group's content.
    A mission is identified by having known sub-keys like icon, position, trigger, effect.
    """
    missions = {}
    # Parse sub-blocks within the group
    blocks = parse_top_level_blocks(group_content)

    # Known group-level keys (not missions)
    group_keys = {'slot', 'generic', 'ai', 'has_country_shield', 'potential', 'potential_on_load'}

    for name, content in blocks:
        if name in group_keys:
            continue
        # Check if this looks like a mission (has icon or position or trigger)
        if re.search(r'\b(icon|position|trigger|effect)\s*=', content):
            mission_data = {}

            # Extract slot and position
            slot_vals = extract_simple_values(content, 'position')
            if slot_vals:
                mission_data['position'] = slot_vals[0]

            icon_vals = extract_simple_values(content, 'icon')
            if icon_vals:
                mission_data['icon'] = icon_vals[0]

            # Extract required_missions
            req = find_block(content, 'required_missions')
            if req is not None:
                mission_data['required_missions'] = req.split()
            else:
                mission_data['required_missions'] = []

            # Extract trigger block
            trigger = find_block(content, 'trigger')
            mission_data['trigger_raw'] = trigger if trigger else ""

            # Extract effect block
            effect = find_block(content, 'effect')
            mission_data['effect_raw'] = effect if effect else ""

            # Extract provinces_to_highlight block
            pth = find_block(content, 'provinces_to_highlight')
            mission_data['provinces_to_highlight_raw'] = pth if pth else ""

            missions[name] = mission_data

    return missions


def load_localisation(loc_dir):
    """Load all _l_english.yml localisation files into a dict."""
    loc = {}
    if not os.path.isdir(loc_dir):
        print(f"WARNING: Localisation directory not found: {loc_dir}")
        return loc

    count = 0
    for fname in os.listdir(loc_dir):
        if not fname.endswith('.yml'):
            continue
        filepath = os.path.join(loc_dir, fname)
        text = read_file(filepath)
        if text is None:
            continue
        for line in text.split('\n'):
            line = line.strip()
            if not line or line.startswith('#') or line.startswith('l_english'):
                continue
            # Format: key:N "value"  (N is optional digit)
            m = re.match(r'^(\S+?):\d*\s+"(.*)"', line)
            if m:
                loc[m.group(1)] = m.group(2)
                count += 1
    print(f"Loaded {count} localisation entries from {loc_dir}")
    return loc


def main():
    print("Loading localisation files...")
    loc = load_localisation(LOCALISATION_DIR)

    print(f"\nProcessing mission files from: {MISSIONS_DIR}")
    all_missions = {}
    file_count = 0
    mission_count = 0

    for fname in sorted(os.listdir(MISSIONS_DIR)):
        if not fname.endswith('.txt'):
            continue
        filepath = os.path.join(MISSIONS_DIR, fname)
        text = read_file(filepath)
        if text is None:
            continue

        file_count += 1
        text = strip_comments(text)

        # Parse top-level mission groups
        groups = parse_top_level_blocks(text)

        for group_name, group_content in groups:
            # Extract group-level data
            # Get slot for the group
            slot_vals = extract_simple_values(group_content, 'slot')
            group_slot = slot_vals[0] if slot_vals else None

            # Get potential block
            potential_text = find_block(group_content, 'potential')
            potential_tags = extract_potential_tags(potential_text) if potential_text else []

            # Parse individual missions
            missions = parse_missions_from_group(group_content)

            for mid, mdata in missions.items():
                mdata['group'] = group_name
                mdata['slot'] = group_slot
                mdata['potential_raw'] = potential_text if potential_text else ""
                mdata['potential_tags'] = potential_tags

                # Resolve tooltip keys from trigger
                tooltip_keys = extract_tooltip_keys(mdata.get('trigger_raw', ''))
                # Also check effect for custom_tooltip
                tooltip_keys.update(extract_tooltip_keys(mdata.get('effect_raw', '')))

                trigger_tooltips = {}
                for tk in tooltip_keys:
                    if tk in loc:
                        trigger_tooltips[tk] = loc[tk]
                mdata['trigger_tooltips'] = trigger_tooltips

                # Resolve title and description from localisation
                for suffix in ['_title', '']:
                    key = mid + suffix
                    if key in loc:
                        mdata['title'] = loc[key]
                        break

                desc_key = mid + '_desc'
                if desc_key in loc:
                    mdata['desc'] = loc[desc_key]

                all_missions[mid] = mdata
                mission_count += 1

        if file_count % 50 == 0:
            print(f"  Processed {file_count} files, {mission_count} missions so far...")

    print(f"\nDone! Processed {file_count} mission files.")
    print(f"Total missions extracted: {mission_count}")
    print(f"Missions with non-empty triggers: {sum(1 for m in all_missions.values() if m.get('trigger_raw'))}")
    print(f"Missions with non-empty effects: {sum(1 for m in all_missions.values() if m.get('effect_raw'))}")
    print(f"Missions with tooltip resolutions: {sum(1 for m in all_missions.values() if m.get('trigger_tooltips'))}")
    print(f"Missions with titles resolved: {sum(1 for m in all_missions.values() if m.get('title'))}")

    # Save
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(all_missions, f, indent=2, ensure_ascii=False)

    print(f"\nSaved to: {OUTPUT_FILE}")
    size_mb = os.path.getsize(OUTPUT_FILE) / (1024 * 1024)
    print(f"File size: {size_mb:.1f} MB")


if __name__ == '__main__':
    main()
