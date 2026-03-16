"""
fetch_wiki_v3.py - Fetch lore text from Anbennar Fandom wiki using the parse API.
Uses action=parse&prop=wikitext to get full wikitext, then strips markup to plain text.
"""

import json
import re
import time
import urllib.request
import urllib.parse
import urllib.error

WIKI_DATA_PATH = r"C:\Users\jjdeg\OneDrive\Desktop\anbennar-guide\wiki_data.json"
ANBENNAR_DATA_PATH = r"C:\Users\jjdeg\OneDrive\Desktop\anbennar-guide\anbennar_data.json"
API_URL = "https://anbennar.fandom.com/api.php"
RATE_LIMIT = 0.4


def strip_wikitext(text):
    """Convert wikitext to plain text."""
    # Remove __TOC__, __NOTOC__, __FORCETOC__ etc.
    text = re.sub(r'__[A-Z]+__', '', text)

    # Remove <ref>...</ref> and <ref ... /> tags
    text = re.sub(r'<ref[^>]*>.*?</ref>', '', text, flags=re.DOTALL)
    text = re.sub(r'<ref[^>]*/>', '', text)

    # Remove other HTML tags
    text = re.sub(r'<[^>]+>', '', text)

    # Remove category links [[Category:...]]
    text = re.sub(r'\[\[Category:[^\]]*\]\]', '', text, flags=re.IGNORECASE)

    # Remove file/image links [[File:...]] or [[Image:...]]
    text = re.sub(r'\[\[(?:File|Image):[^\]]*\]\]', '', text, flags=re.IGNORECASE)

    # Remove {{...}} templates, handling nested braces
    # Do multiple passes to handle nesting
    for _ in range(10):
        new_text = re.sub(r'\{\{[^{}]*\}\}', '', text)
        if new_text == text:
            break
        text = new_text

    # Remove any remaining {{ or }}
    text = text.replace('{{', '').replace('}}', '')

    # Convert [[Link|Display]] to Display
    text = re.sub(r'\[\[[^\]|]*\|([^\]]*)\]\]', r'\1', text)

    # Convert [[Link]] to Link
    text = re.sub(r'\[\[([^\]]*)\]\]', r'\1', text)

    # Remove external links [http://... display] -> display
    text = re.sub(r'\[https?://[^\s\]]+ ([^\]]*)\]', r'\1', text)
    text = re.sub(r'\[https?://[^\]]*\]', '', text)

    # Remove bold and italic markers
    text = re.sub(r"'{2,3}", '', text)

    # Remove ==headings==
    text = re.sub(r'={2,}[^=]+=+', '', text)

    # Remove list markers at start of lines
    text = re.sub(r'^\*+\s*', '', text, flags=re.MULTILINE)
    text = re.sub(r'^#+\s*', '', text, flags=re.MULTILINE)
    text = re.sub(r'^;+\s*', '', text, flags=re.MULTILINE)
    text = re.sub(r'^:+\s*', '', text, flags=re.MULTILINE)

    # Remove table markup
    text = re.sub(r'\{\|.*?\|\}', '', text, flags=re.DOTALL)
    text = re.sub(r'^\|.*$', '', text, flags=re.MULTILINE)
    text = re.sub(r'^!.*$', '', text, flags=re.MULTILINE)

    # Clean up whitespace
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = text.strip()

    return text


def extract_intro(text, max_chars=500):
    """Extract first 2-3 paragraphs up to ~max_chars, ending at sentence boundary."""
    paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
    result = ""
    for p in paragraphs[:3]:
        candidate = (result + "\n\n" + p).strip() if result else p
        if len(candidate) > max_chars and result:
            break
        result = candidate

    # If result is too long, cut at sentence boundary
    if len(result) > max_chars:
        # Find last sentence end before max_chars
        truncated = result[:max_chars]
        last_period = max(truncated.rfind('. '), truncated.rfind('.\n'))
        if last_period > max_chars // 3:
            result = result[:last_period + 1]
        else:
            result = truncated.rstrip()

    return result


def fetch_wikitext(page_title):
    """Fetch wikitext for a page using the parse API."""
    params = urllib.parse.urlencode({
        'action': 'parse',
        'page': page_title,
        'prop': 'wikitext',
        'format': 'json',
        'redirects': '1',
    })
    url = f"{API_URL}?{params}"
    req = urllib.request.Request(url, headers={'User-Agent': 'AnbennarGuideBot/1.0'})
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = json.loads(resp.read().decode('utf-8'))

    if 'error' in data:
        return None, data['error'].get('info', 'Unknown error')

    wikitext = data.get('parse', {}).get('wikitext', {}).get('*', '')
    return wikitext, None


def main():
    print("Loading data files...")
    with open(WIKI_DATA_PATH, encoding='utf-8') as f:
        wiki_data = json.load(f)

    with open(ANBENNAR_DATA_PATH, encoding='utf-8') as f:
        anbennar_data = json.load(f)

    # Build list of tags to fetch
    to_fetch = []
    for tag, entry in wiki_data.items():
        if entry.get('found') and entry.get('page_length', 0) > 200:
            to_fetch.append(tag)

    print(f"Total entries: {len(wiki_data)}")
    print(f"To fetch (found=true, page_length>200): {len(to_fetch)}")
    print()

    success_count = 0
    error_count = 0

    for i, tag in enumerate(to_fetch):
        entry = wiki_data[tag]
        wiki_url = entry.get('wiki_url', '')
        name = anbennar_data.get(tag, {}).get('name', tag)

        # Extract page title from URL
        if '/wiki/' in wiki_url:
            page_title = wiki_url.split('/wiki/')[-1]
            page_title = urllib.parse.unquote(page_title)
        else:
            print(f"  [{tag}] {name}: No valid wiki URL, skipping")
            error_count += 1
            continue

        try:
            wikitext, err = fetch_wikitext(page_title)
            if err:
                print(f"  [{tag}] {name}: API error: {err}")
                error_count += 1
                time.sleep(RATE_LIMIT)
                continue

            if not wikitext:
                print(f"  [{tag}] {name}: Empty wikitext")
                error_count += 1
                time.sleep(RATE_LIMIT)
                continue

            plain = strip_wikitext(wikitext)
            lore_intro = extract_intro(plain, max_chars=500)
            lore_full = plain[:3000]
            # Trim lore_full at sentence boundary if possible
            if len(plain) > 3000:
                last_dot = lore_full.rfind('. ')
                if last_dot > 2000:
                    lore_full = lore_full[:last_dot + 1]

            entry['lore_intro'] = lore_intro
            entry['lore_full'] = lore_full
            success_count += 1

        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as e:
            print(f"  [{tag}] {name}: Network error: {e}")
            error_count += 1
        except Exception as e:
            print(f"  [{tag}] {name}: Unexpected error: {e}")
            error_count += 1

        if (i + 1) % 25 == 0:
            print(f"Progress: {i + 1}/{len(to_fetch)} processed ({success_count} ok, {error_count} errors)")

        time.sleep(RATE_LIMIT)

    print()
    print(f"Done! {success_count} succeeded, {error_count} errors out of {len(to_fetch)} attempted.")

    # Save
    print(f"Saving to {WIKI_DATA_PATH}...")
    with open(WIKI_DATA_PATH, 'w', encoding='utf-8') as f:
        json.dump(wiki_data, f, indent=2, ensure_ascii=False)

    # Show a few samples
    print("\nSample lore_intro entries:")
    shown = 0
    for tag in to_fetch:
        entry = wiki_data[tag]
        if entry.get('lore_intro') and len(entry['lore_intro']) > 50:
            name = anbennar_data.get(tag, {}).get('name', tag)
            print(f"\n--- {tag} ({name}) ---")
            print(entry['lore_intro'][:300])
            shown += 1
            if shown >= 3:
                break


if __name__ == '__main__':
    main()
