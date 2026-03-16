"""
Convert all TGA country flags to small PNGs for the web guide.
Also creates base64-encoded versions embedded in a JSON for single-file use.
"""
import os
import json
import base64
from io import BytesIO
from PIL import Image

MOD = r"C:\Program Files (x86)\Steam\steamapps\workshop\content\236850\1385440355"
FLAGS_DIR = os.path.join(MOD, "gfx", "flags")
OUT_DIR = os.path.join(os.path.dirname(__file__), "flags")
BASE_DIR = os.path.dirname(__file__)

def convert_flags():
    os.makedirs(OUT_DIR, exist_ok=True)

    flag_data = {}
    count = 0
    errors = 0

    for fname in os.listdir(FLAGS_DIR):
        if not fname.endswith('.tga'):
            continue

        tag = fname.replace('.tga', '')
        src = os.path.join(FLAGS_DIR, fname)

        try:
            img = Image.open(src)
            # Resize to 64x64 for web use (smaller file size)
            img = img.resize((64, 64), Image.LANCZOS)

            # Save as PNG file
            out_path = os.path.join(OUT_DIR, f"{tag}.png")
            img.save(out_path, "PNG", optimize=True)

            # Also create base64 for embedding
            buf = BytesIO()
            img.save(buf, "PNG", optimize=True)
            b64 = base64.b64encode(buf.getvalue()).decode('ascii')
            flag_data[tag] = b64

            count += 1
        except Exception as e:
            print(f"  Error converting {fname}: {e}")
            errors += 1

    # Save base64 data as JSON
    json_path = os.path.join(BASE_DIR, "flag_data.json")
    with open(json_path, 'w') as f:
        json.dump(flag_data, f)

    print(f"Converted {count} flags ({errors} errors)")
    print(f"PNG files saved to: {OUT_DIR}")
    print(f"Base64 JSON saved to: {json_path} ({os.path.getsize(json_path) / 1024 / 1024:.1f} MB)")

if __name__ == '__main__':
    convert_flags()
