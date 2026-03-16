"""
Convert EU4 mission icon DDS files to PNG.
Handles DXT1, DXT3, DXT5, uncompressed BGRA, and DX10/DXGI format 91.
Mod icons override base game icons with the same name.
"""

import os
import struct
import json
from PIL import Image

# Paths
MOD_DIR = r"C:\Program Files (x86)\Steam\steamapps\workshop\content\236850\1385440355\gfx\interface\missions"
BASE_DIR = r"C:\Program Files (x86)\Steam\steamapps\common\Europa Universalis IV\gfx\interface\missions"
OUTPUT_DIR = r"C:\Users\jjdeg\OneDrive\Desktop\anbennar-guide\mission_icons"
MAP_FILE = r"C:\Users\jjdeg\OneDrive\Desktop\anbennar-guide\mission_icon_map.json"

os.makedirs(OUTPUT_DIR, exist_ok=True)


def convert_dxgi91(filepath):
    """Handle DX10 header with DXGI format 91 (B8G8R8A8_UNORM)."""
    with open(filepath, "rb") as f:
        magic = f.read(4)
        if magic != b"DDS ":
            return None
        header = f.read(124)
        height = struct.unpack_from("<I", header, 8)[0]
        width = struct.unpack_from("<I", header, 12)[0]
        fourcc = header[80:84]
        if fourcc != b"DX10":
            return None
        dx10_header = f.read(20)
        dxgi_format = struct.unpack_from("<I", dx10_header, 0)[0]
        if dxgi_format != 91:
            return None
        pixel_data = f.read(width * height * 4)

    img = Image.frombytes("RGBA", (width, height), pixel_data, "raw", "BGRA")
    return img


def collect_dds_files(directory):
    """Collect all DDS files from a directory and its subdirectories.
    Returns dict mapping icon_name -> full_path.
    """
    files = {}
    if not os.path.isdir(directory):
        print(f"  Directory not found: {directory}")
        return files

    for root, dirs, filenames in os.walk(directory):
        for fname in filenames:
            if fname.lower().endswith(".dds"):
                name = os.path.splitext(fname)[0]
                files[name] = os.path.join(root, fname)

    return files


def convert_dds(filepath):
    """Try to convert a DDS file to a PIL Image."""
    # Try Pillow first
    try:
        img = Image.open(filepath)
        img.load()
        return img.convert("RGBA")
    except Exception:
        pass

    # Try DXGI format 91 fallback
    try:
        img = convert_dxgi91(filepath)
        if img is not None:
            return img
    except Exception:
        pass

    return None


def main():
    # Collect files: base first, then mod (mod overrides base)
    print("Collecting base game DDS files...")
    all_icons = collect_dds_files(BASE_DIR)
    base_count = len(all_icons)
    print(f"  Found {base_count} base game icons")

    print("Collecting mod DDS files...")
    mod_icons = collect_dds_files(MOD_DIR)
    mod_count = len(mod_icons)
    print(f"  Found {mod_count} mod icons")

    # Mod overrides base
    override_count = sum(1 for k in mod_icons if k in all_icons)
    all_icons.update(mod_icons)
    print(f"  {override_count} mod icons override base game icons")
    print(f"  Total unique icons: {len(all_icons)}")

    # Convert
    success = 0
    failed = 0
    failed_list = []
    icon_map = {}

    total = len(all_icons)
    for i, (name, filepath) in enumerate(sorted(all_icons.items()), 1):
        if i % 200 == 0 or i == total:
            print(f"  Progress: {i}/{total}")

        img = convert_dds(filepath)
        if img is not None:
            out_path = os.path.join(OUTPUT_DIR, f"{name}.png")
            img.save(out_path, "PNG")
            icon_map[name] = True
            success += 1
        else:
            failed += 1
            failed_list.append((name, filepath))

    # Save map
    with open(MAP_FILE, "w") as f:
        json.dump(icon_map, f, indent=2)

    print(f"\nDone!")
    print(f"  Converted: {success}")
    print(f"  Failed: {failed}")
    if failed_list:
        print(f"  Failed files:")
        for name, path in failed_list:
            print(f"    {name}: {path}")
    print(f"  Icon map saved to: {MAP_FILE}")
    print(f"  PNGs saved to: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
