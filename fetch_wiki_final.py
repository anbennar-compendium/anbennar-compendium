"""
Fetch wiki lore for all Anbennar countries from the Fandom wiki.
Uses action=parse API with redirect following.
"""
import urllib.request, json, re, time, os

WIKI_API = 'https://anbennar.fandom.com/api.php'
GUIDE_DIR = r'C:\Users\jjdeg\OneDrive\Desktop\anbennar-guide'

def strip_wikitext(text):
    """Remove wiki markup and return plain text."""
    # Remove templates {{...}} (handle nesting)
    depth = 0
    result = []
    i = 0
    while i < len(text):
        if text[i:i+2] == '{{':
            depth += 1; i += 2
        elif text[i:i+2] == '}}' and depth > 0:
            depth -= 1; i += 2
        elif depth == 0:
            result.append(text[i]); i += 1
        else:
            i += 1
    text = ''.join(result)
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    # Remove tables
    text = re.sub(r'\{\|.*?\|\}', '', text, flags=re.DOTALL)
    # [[Link|Display]] -> Display, [[Link]] -> Link
    text = re.sub(r'\[\[[^\]]*\|([^\]]+)\]\]', r'\1', text)
    text = re.sub(r'\[\[([^\]]+)\]\]', r'\1', text)
    # Remove external links
    text = re.sub(r'\[https?://[^\]]*\]', '', text)
    # Remove headings markup but keep text
    text = re.sub(r'={2,}\s*([^=]+?)\s*={2,}', r'\n\1\n', text)
    # Remove bold/italic
    text = re.sub(r"'{2,}", '', text)
    # Remove categories
    text = re.sub(r'\[\[Category:[^\]]+\]\]', '', text)
    # Remove __KEYWORDS__
    text = re.sub(r'__\w+__', '', text)
    # Collapse whitespace
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r'[ \t]+', ' ', text)
    return text.strip()

def fetch_page(title, follow_redirects=True):
    """Fetch and parse a wiki page. Returns (wikitext, page_size, final_url) or None."""
    encoded = urllib.parse.quote(title.replace(' ', '_'))
    url = f'{WIKI_API}?action=parse&page={encoded}&prop=wikitext&format=json&redirects=1'

    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'AnbennarGuide/1.0'})
        resp = urllib.request.urlopen(req, timeout=15)
        data = json.loads(resp.read().decode('utf-8'))

        if 'error' in data:
            return None

        parse = data.get('parse', {})
        wikitext = parse.get('wikitext', {}).get('*', '')
        page_title = parse.get('title', title)

        # Check for manual redirect (some pages have #REDIRECT [[Target]])
        if wikitext.startswith('#REDIRECT') and follow_redirects:
            m = re.search(r'\[\[([^\]]+)\]\]', wikitext)
            if m:
                return fetch_page(m.group(1), follow_redirects=False)

        wiki_url = f'https://anbennar.fandom.com/wiki/{urllib.parse.quote(page_title.replace(" ", "_"))}'
        return wikitext, len(wikitext), wiki_url, page_title
    except Exception as e:
        return None

def extract_lore(wikitext):
    """Extract lore intro and full text from wikitext."""
    plain = strip_wikitext(wikitext)

    # Get meaningful paragraphs (skip short lines, headings)
    paragraphs = []
    for p in plain.split('\n\n'):
        p = p.strip()
        if len(p) > 40 and not p.startswith('|') and not p.startswith('{'):
            paragraphs.append(p)

    if not paragraphs:
        return '', ''

    # Intro: first paragraph, capped at ~500 chars at sentence boundary
    intro = paragraphs[0]
    if len(intro) > 500:
        # Find sentence end
        for end in range(400, min(len(intro), 600)):
            if intro[end] == '.' and (end + 1 >= len(intro) or intro[end+1] == ' '):
                intro = intro[:end+1]
                break

    # Full: first ~3000 chars of all paragraphs
    full = '\n\n'.join(paragraphs)
    if len(full) > 3000:
        for end in range(2800, min(len(full), 3200)):
            if full[end] == '.' and (end + 1 >= len(full) or full[end+1] in ' \n'):
                full = full[:end+1]
                break
        else:
            full = full[:3000]

    return intro, full

def main():
    # Load existing wiki data
    wiki_path = os.path.join(GUIDE_DIR, 'wiki_data.json')
    with open(wiki_path, 'r', encoding='utf-8') as f:
        wiki_data = json.load(f)

    # Load country data for names
    with open(os.path.join(GUIDE_DIR, 'anbennar_data.json'), 'r', encoding='utf-8') as f:
        countries = json.load(f)

    # Build search titles for each country
    total = 0
    found = 0
    errors = 0

    for tag, entry in wiki_data.items():
        if not entry.get('found'):
            continue

        total += 1
        country_name = countries.get(tag, {}).get('name', tag)

        # Try the wiki_title first if we have it, otherwise try the country name
        titles_to_try = []
        if entry.get('wiki_title'):
            titles_to_try.append(entry['wiki_title'])
        titles_to_try.append(country_name)
        # Also try common patterns
        for prefix in ['Kingdom of ', 'Duchy of ', 'Republic of ', 'Empire of ', 'Realm of ', 'Free City of ', 'County of ', 'Elfrealm of ', 'Grand Duchy of ']:
            titles_to_try.append(prefix + country_name)

        result = None
        for title in titles_to_try:
            result = fetch_page(title)
            if result and len(result[0]) > 200:
                break
            result = None

        if result:
            wikitext, page_size, wiki_url, page_title = result
            intro, full = extract_lore(wikitext)

            entry['wiki_url'] = wiki_url
            entry['wiki_title'] = page_title
            entry['page_size'] = page_size
            entry['lore_intro'] = intro
            entry['lore_full'] = full

            if intro:
                found += 1
                print(f'  [{found}/{total}] {tag} ({country_name}): {len(intro)} intro / {len(full)} full')
            else:
                print(f'  [{total}] {tag} ({country_name}): page found but no extractable lore')
        else:
            entry['lore_intro'] = ''
            entry['lore_full'] = ''
            print(f'  [{total}] {tag} ({country_name}): not found')

        # Rate limit
        time.sleep(0.15)

        # Save periodically
        if total % 50 == 0:
            with open(wiki_path, 'w', encoding='utf-8') as f:
                json.dump(wiki_data, f, ensure_ascii=False, indent=2)
            print(f'  --- Saved at {total} ---')

    # Final save
    with open(wiki_path, 'w', encoding='utf-8') as f:
        json.dump(wiki_data, f, ensure_ascii=False, indent=2)

    print(f'\nDone! {found} pages with lore out of {total} wiki entries. {errors} errors.')

if __name__ == '__main__':
    main()
