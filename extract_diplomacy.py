"""Extract 1444 diplomatic subject relationships from Anbennar mod."""
import os
import re
import json

MOD_PATH = r"C:\Program Files (x86)\Steam\steamapps\workshop\content\236850\1385440355"
DIPLOMACY_DIR = os.path.join(MOD_PATH, "history", "diplomacy")
OUTPUT = os.path.join(os.path.dirname(__file__), "diplomacy_data.json")

ENCODINGS = ["utf-8-sig", "utf-8", "latin-1", "cp1252"]

# Display names for subject types
SUBJECT_NAMES = {
    "vassal": "Vassal",
    "march": "March",
    "personal_union": "Personal Union",
    "tributary_state": "Tributary",
    "tributary_state_anb": "Tributary",
    "colony": "Colony",
    "autonomous_vassal": "Autonomous Vassal",
    "slave_state": "Slave State",
    "subsidiary_command": "Subsidiary Command",
    "centaur_dominion": "Centaur Dominion",
    "centaur_follower": "Centaur Follower",
    "amlharaz_hold": "Amlharaz Hold",
    "acolyte_dominion": "Acolyte Dominion",
    "infernal_collaborator": "Infernal Collaborator",
    "infernal_order_state_subject": "Infernal Order State",
    "oni_governorship": "Oni Governorship",
    "seghdihr_syndicate": "Seghdihr Syndicate",
    "ynnic_iosahar": "Ynnic Iosahar",
    "gylikheion": "Gylikheion",
    "patronate": "Patronate",
    "medasi_subject": "Medasi Subject",
    "imperial_bodyguard": "Imperial Bodyguard",
    "nekhei": "Nekhei",
    "loyal_crathanor_subject": "Loyal Crathanor Subject",
    "loyal_trade_protectorate": "Trade Protectorate",
    "sanghariyar_trade_state": "Sanghariyar Trade State",
    "dao": "Dao",
    "sponsored_adventurer_subject": "Sponsored Adventurer",
    "vizier_vassal": "Vizier Vassal",
    "daimyo_vassal": "Daimyo Vassal",
    "appanage": "Appanage",
    "client_vassal": "Client State",
    "trade_protectorate": "Trade Protectorate",
    "eyalet": "Eyalet",
    "core_eyalet": "Core Eyalet",
}


def read_file(filepath):
    for enc in ENCODINGS:
        try:
            with open(filepath, "r", encoding=enc) as f:
                return f.read()
        except (UnicodeDecodeError, UnicodeError):
            continue
    return None


def parse_date(datestr):
    """Parse EU4 date string to comparable tuple."""
    try:
        parts = datestr.strip().split('.')
        return (int(parts[0]), int(parts[1]), int(parts[2]))
    except (ValueError, IndexError):
        return None


def main():
    relationships = []  # {overlord, subject, type, type_name}

    for fname in os.listdir(DIPLOMACY_DIR):
        if not fname.endswith('.txt'):
            continue

        text = read_file(os.path.join(DIPLOMACY_DIR, fname))
        if not text:
            continue

        # Remove comments
        text = re.sub(r'#.*', '', text)

        # Find all relationship blocks: vassal = {}, march = {}, dependency = {}
        # Standard types: vassal, march, personal_union
        for rel_type in ['vassal', 'march', 'personal_union']:
            pattern = rf'{rel_type}\s*=\s*\{{([^}}]+)\}}'
            for m in re.finditer(pattern, text, re.DOTALL):
                block = m.group(1)
                first = re.search(r'first\s*=\s*(\w+)', block)
                second = re.search(r'second\s*=\s*(\w+)', block)
                start = re.search(r'start_date\s*=\s*([\d.]+)', block)
                end = re.search(r'end_date\s*=\s*([\d.]+)', block)

                if not (first and second):
                    continue

                # Check if active in 1444
                start_date = parse_date(start.group(1)) if start else (1, 1, 1)
                end_date = parse_date(end.group(1)) if end else (9999, 1, 1)

                if start_date <= (1444, 11, 11) and end_date > (1444, 11, 11):
                    relationships.append({
                        "overlord": first.group(1),
                        "subject": second.group(1),
                        "type": rel_type,
                        "type_name": SUBJECT_NAMES.get(rel_type, rel_type.replace('_', ' ').title()),
                    })

        # Dependency blocks (custom subject types)
        for m in re.finditer(r'dependency\s*=\s*\{([^}]+)\}', text, re.DOTALL):
            block = m.group(1)
            sub_type_m = re.search(r'subject_type\s*=\s*"?(\w+)"?', block)
            first = re.search(r'first\s*=\s*(\w+)', block)
            second = re.search(r'second\s*=\s*(\w+)', block)
            start = re.search(r'start_date\s*=\s*([\d.]+)', block)
            end = re.search(r'end_date\s*=\s*([\d.]+)', block)

            if not (first and second and sub_type_m):
                continue

            sub_type = sub_type_m.group(1)
            start_date = parse_date(start.group(1)) if start else (1, 1, 1)
            end_date = parse_date(end.group(1)) if end else (9999, 1, 1)

            if start_date <= (1444, 11, 11) and end_date > (1444, 11, 11):
                relationships.append({
                    "overlord": first.group(1),
                    "subject": second.group(1),
                    "type": sub_type,
                    "type_name": SUBJECT_NAMES.get(sub_type, sub_type.replace('_', ' ').title()),
                })

    # Build indexed structure:
    # tag -> {overlord_of: [{tag, type, type_name}], subject_of: {tag, type, type_name}}
    diplomacy = {}

    for rel in relationships:
        o = rel["overlord"]
        s = rel["subject"]

        if o not in diplomacy:
            diplomacy[o] = {"overlord_of": [], "subject_of": None}
        if s not in diplomacy:
            diplomacy[s] = {"overlord_of": [], "subject_of": None}

        diplomacy[o]["overlord_of"].append({
            "tag": s,
            "type": rel["type"],
            "type_name": rel["type_name"],
        })
        diplomacy[s]["subject_of"] = {
            "tag": o,
            "type": rel["type"],
            "type_name": rel["type_name"],
        }

    # Clean up empty entries
    for tag in list(diplomacy.keys()):
        if not diplomacy[tag]["overlord_of"] and not diplomacy[tag]["subject_of"]:
            del diplomacy[tag]
        else:
            if not diplomacy[tag]["overlord_of"]:
                del diplomacy[tag]["overlord_of"]
            if not diplomacy[tag]["subject_of"]:
                del diplomacy[tag]["subject_of"]

    with open(OUTPUT, 'w', encoding='utf-8') as f:
        json.dump(diplomacy, f, separators=(',', ':'))

    total_rels = len(relationships)
    overlords = sum(1 for d in diplomacy.values() if 'overlord_of' in d)
    subjects = sum(1 for d in diplomacy.values() if 'subject_of' in d)

    print(f"Extracted {total_rels} diplomatic relationships")
    print(f"  {overlords} overlords, {subjects} subjects")
    print(f"  {len(diplomacy)} countries with diplomatic ties")
    print(f"Output: {OUTPUT} ({os.path.getsize(OUTPUT):,} bytes)")


if __name__ == '__main__':
    main()
