"""Generate map images for the Anbennar Compendium.

Outputs:
  - map_base.png: Political map colored by country ownership
  - province_id_map.png: Province IDs encoded in R(high)/G(low) channels
"""
import os
import re
import json
import csv
from PIL import Image
import numpy as np

MOD_PATH = r"C:\Program Files (x86)\Steam\steamapps\workshop\content\236850\1385440355"
PROVINCES_BMP = os.path.join(MOD_PATH, "map", "provinces.bmp")
DEFINITION_CSV = os.path.join(MOD_PATH, "map", "definition.csv")
DEFAULT_MAP = os.path.join(MOD_PATH, "map", "default.map")

OUT_DIR = os.path.dirname(__file__)
PROVINCE_OWNERS = os.path.join(OUT_DIR, "province_owners.json")
ANBENNAR_DATA = os.path.join(OUT_DIR, "anbennar_data.json")


def load_definition():
    """Load definition.csv: RGB -> province_id mapping."""
    rgb_to_id = {}
    id_to_rgb = {}
    with open(DEFINITION_CSV, 'r', encoding='utf-8-sig') as f:
        reader = csv.reader(f, delimiter=';')
        header = next(reader)  # skip header
        for row in reader:
            if len(row) < 4:
                continue
            try:
                prov_id = int(row[0])
                r, g, b = int(row[1]), int(row[2]), int(row[3])
                rgb_to_id[(r, g, b)] = prov_id
                id_to_rgb[prov_id] = (r, g, b)
            except (ValueError, IndexError):
                continue
    return rgb_to_id, id_to_rgb


def load_sea_provinces():
    """Load sea province IDs from default.map."""
    sea = set()
    with open(DEFAULT_MAP, 'r', encoding='utf-8-sig') as f:
        text = f.read()
    # Find sea_starts block
    m = re.search(r'sea_starts\s*=\s*\{([^}]+)\}', text, re.DOTALL)
    if m:
        for num in re.findall(r'\d+', m.group(1)):
            sea.add(int(num))
    # Also look for lakes
    m = re.search(r'lakes\s*=\s*\{([^}]+)\}', text, re.DOTALL)
    if m:
        for num in re.findall(r'\d+', m.group(1)):
            sea.add(int(num))
    return sea


def main():
    print("Loading definition.csv...")
    rgb_to_id, id_to_rgb = load_definition()
    print(f"  {len(rgb_to_id)} province color definitions")

    print("Loading province owners...")
    with open(PROVINCE_OWNERS, 'r') as f:
        tag_to_provinces = json.load(f)
    # Invert to province_id -> tag
    prov_to_tag = {}
    for tag, provs in tag_to_provinces.items():
        for p in provs:
            prov_to_tag[p] = tag

    print("Loading country data...")
    with open(ANBENNAR_DATA, 'r', encoding='utf-8') as f:
        data = json.load(f)
    # tag -> color
    tag_to_color = {}
    for tag, info in data.items():
        c = info.get('color', [128, 128, 128])
        tag_to_color[tag] = (c[0], c[1], c[2])

    print("Loading sea provinces...")
    sea_provinces = load_sea_provinces()
    print(f"  {len(sea_provinces)} sea/lake provinces")

    print(f"Loading provinces.bmp...")
    img = Image.open(PROVINCES_BMP).convert('RGB')
    w, h = img.size
    print(f"  {w}x{h} pixels")
    pixels = np.array(img)  # shape: (h, w, 3)

    print("Building province ID map...")
    # Create province ID array from pixel colors
    # Flatten pixels to (h*w, 3) for fast lookup
    flat = pixels.reshape(-1, 3)
    id_map = np.zeros(flat.shape[0], dtype=np.uint16)

    # Build a fast lookup array using color hashing
    # Hash: r*256*256 + g*256 + b -> province_id
    color_hash = {}
    for (r, g, b), pid in rgb_to_id.items():
        key = r * 65536 + g * 256 + b
        color_hash[key] = pid

    flat_hash = flat[:, 0].astype(np.int32) * 65536 + flat[:, 1].astype(np.int32) * 256 + flat[:, 2].astype(np.int32)

    # Vectorized lookup
    unique_hashes = np.unique(flat_hash)
    print(f"  {len(unique_hashes)} unique colors in provinces.bmp")

    for uh in unique_hashes:
        pid = color_hash.get(int(uh), 0)
        if pid:
            id_map[flat_hash == uh] = pid

    id_map_2d = id_map.reshape(h, w)

    # Generate province_id_map.png (encode ID in R=high byte, G=low byte, B=0)
    print("Generating province_id_map.png...")
    id_img = np.zeros((h, w, 3), dtype=np.uint8)
    id_img[:, :, 0] = (id_map_2d >> 8).astype(np.uint8)  # R = high byte
    id_img[:, :, 1] = (id_map_2d & 0xFF).astype(np.uint8)  # G = low byte
    id_img[:, :, 2] = 0

    id_pil = Image.fromarray(id_img, 'RGB')
    id_out = os.path.join(OUT_DIR, "province_id_map.png")
    id_pil.save(id_out, optimize=True)
    print(f"  Saved: {id_out} ({os.path.getsize(id_out):,} bytes)")

    # Generate political base map
    print("Generating map_base.png...")
    base = np.zeros((h, w, 3), dtype=np.uint8)

    # Color water provinces dark blue
    WATER_COLOR = np.array([18, 25, 40], dtype=np.uint8)
    LAND_UNOWNED = np.array([40, 38, 35], dtype=np.uint8)

    # Default all to unowned land color
    base[:] = LAND_UNOWNED

    # Color water
    for pid in sea_provinces:
        mask = id_map_2d == pid
        base[mask] = WATER_COLOR

    # Color owned provinces by country color
    colored_count = 0
    for tag, provs in tag_to_provinces.items():
        color = tag_to_color.get(tag, (128, 128, 128))
        color_arr = np.array(color, dtype=np.uint8)
        for pid in provs:
            mask = id_map_2d == pid
            if mask.any():
                base[mask] = color_arr
                colored_count += 1

    # Add subtle province borders (darken pixels at edges between provinces)
    print("  Adding province borders...")
    # Detect horizontal edges
    h_edges = id_map_2d[:, :-1] != id_map_2d[:, 1:]
    # Detect vertical edges
    v_edges = id_map_2d[:-1, :] != id_map_2d[1:, :]

    # Darken border pixels
    border_mask = np.zeros((h, w), dtype=bool)
    border_mask[:, :-1] |= h_edges
    border_mask[:, 1:] |= h_edges
    border_mask[:-1, :] |= v_edges
    border_mask[1:, :] |= v_edges

    base[border_mask] = (base[border_mask].astype(np.float32) * 0.6).astype(np.uint8)

    base_pil = Image.fromarray(base, 'RGB')
    base_out = os.path.join(OUT_DIR, "map_base.png")
    base_pil.save(base_out, optimize=True, compress_level=9)
    print(f"  Colored {colored_count} province instances")
    print(f"  Saved: {base_out} ({os.path.getsize(base_out):,} bytes)")

    # Also generate province bounding boxes for fast highlighting
    print("Generating province_bounds.json...")
    bounds = {}
    for pid in range(1, 8001):
        ys, xs = np.where(id_map_2d == pid)
        if len(xs) > 0:
            bounds[str(pid)] = [int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())]

    bounds_out = os.path.join(OUT_DIR, "province_bounds.json")
    with open(bounds_out, 'w') as f:
        json.dump(bounds, f, separators=(',', ':'))
    print(f"  {len(bounds)} provinces with bounds")
    print(f"  Saved: {bounds_out} ({os.path.getsize(bounds_out):,} bytes)")

    print("\nDone!")


if __name__ == '__main__':
    main()
