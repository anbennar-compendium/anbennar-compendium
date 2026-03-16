#!/usr/bin/env python3
"""
Fetch proper lore from the Anbennar Fandom wiki for all countries.
Resolves redirects, extracts full page text, and uses search API
for countries not yet matched.
"""

import json
import time
import urllib.request
import urllib.parse
import urllib.error
import sys
import os

# Force unbuffered output
sys.stdout.reconfigure(line_buffering=True)
sys.stderr.reconfigure(line_buffering=True)

WIKI_API = "https://anbennar.fandom.com/api.php"
RATE_LIMIT = 0.3


def api_call(params):
    """Make a MediaWiki API call and return parsed JSON."""
    params["format"] = "json"
    url = WIKI_API + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": "AnbennarGuideBot/2.0"})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, OSError) as e:
            if attempt < 2:
                time.sleep(1)
                continue
            print(f"  API error after 3 attempts: {e}")
            return None


def resolve_and_fetch(title):
    """
    Resolve redirects + fetch extract + page size in a single API call.
    Returns (final_title, extract_text, page_size) or (None, None, None).
    """
    data = api_call({
        "action": "query",
        "titles": title,
        "redirects": "1",
        "prop": "extracts|revisions",
        "explaintext": "1",
        "exsectionformat": "plain",
        "rvprop": "size",
    })
    time.sleep(RATE_LIMIT)
    if not data or "query" not in data:
        return None, None, None

    pages = data["query"].get("pages", {})
    page = next(iter(pages.values()))
    if "missing" in page:
        return None, None, None

    final_title = page["title"]
    extract = page.get("extract", "")
    revisions = page.get("revisions", [{}])
    page_size = revisions[0].get("size", 0) if revisions else 0

    return final_title, extract, page_size


def search_wiki(name):
    """
    Use opensearch to find a page matching the country name.
    Returns list of page titles found.
    """
    data = api_call({
        "action": "opensearch",
        "search": name,
        "limit": "5",
        "namespace": "0",
    })
    time.sleep(RATE_LIMIT)
    if not data or len(data) < 2:
        return []
    return data[1]  # list of title strings


def get_lore_intro(full_text):
    """Extract the first 1-2 meaningful paragraphs from the full extract."""
    if not full_text:
        return ""
    paragraphs = [p.strip() for p in full_text.split("\n") if p.strip()]
    intro_parts = []
    for p in paragraphs:
        # Skip very short lines that look like section headers
        if len(p) < 5:
            continue
        intro_parts.append(p)
        if len(intro_parts) >= 2:
            break
    return "\n\n".join(intro_parts)


def make_wiki_url(title):
    """Build a proper wiki URL from a page title."""
    encoded = urllib.parse.quote(title.replace(" ", "_"), safe="/:_")
    return f"https://anbennar.fandom.com/wiki/{encoded}"


def make_entry(final_title, extract, page_size):
    return {
        "wiki_url": make_wiki_url(final_title),
        "wiki_title": final_title,
        "lore_intro": get_lore_intro(extract),
        "lore_full": extract,
        "page_size": page_size,
        "found": True,
    }


def empty_entry():
    return {
        "wiki_url": "",
        "wiki_title": "",
        "lore_intro": "",
        "lore_full": "",
        "page_size": 0,
        "found": False,
    }


def save_data(wiki_data, wiki_path):
    with open(wiki_path, "w", encoding="utf-8") as f:
        json.dump(wiki_data, f, indent=2, ensure_ascii=False)


def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))

    with open(os.path.join(base_dir, "anbennar_data.json"), encoding="utf-8") as f:
        anbennar_data = json.load(f)

    wiki_path = os.path.join(base_dir, "wiki_data.json")
    with open(wiki_path, encoding="utf-8") as f:
        wiki_data = json.load(f)

    total = len(anbennar_data)
    tags = sorted(anbennar_data.keys())

    # Separate into already-found and not-found
    found_tags = [t for t in tags if wiki_data.get(t, {}).get("found")]
    notfound_tags = [t for t in tags if not wiki_data.get(t, {}).get("found")]

    print(f"Total countries: {total}")
    print(f"Already found (will re-fetch with redirects): {len(found_tags)}")
    print(f"Not found (will search): {len(notfound_tags)}")
    print()

    # ========== PHASE 1: Re-fetch already-found countries ==========
    print("=== PHASE 1: Re-fetching found countries ===")
    updated = 0
    phase1_failed = 0

    for i, tag in enumerate(found_tags):
        if (i + 1) % 50 == 0:
            print(f"  Phase 1 progress: {i+1}/{len(found_tags)} (updated={updated})")

        existing = wiki_data[tag]
        wiki_url = existing.get("wiki_url", "")
        if not wiki_url:
            phase1_failed += 1
            continue

        try:
            url_path = urllib.parse.urlparse(wiki_url).path
            raw_title = urllib.parse.unquote(url_path.replace("/wiki/", "").replace("_", " "))

            final_title, extract, page_size = resolve_and_fetch(raw_title)
            if final_title:
                wiki_data[tag] = make_entry(final_title, extract, page_size)
                updated += 1
            else:
                # Page no longer exists, will retry in phase 2
                phase1_failed += 1
        except Exception as e:
            name = anbennar_data[tag].get("name", "")
            print(f"  ERROR on {tag} '{name}': {e}")
            phase1_failed += 1

        # Save periodically
        if (i + 1) % 100 == 0:
            save_data(wiki_data, wiki_path)

    save_data(wiki_data, wiki_path)
    print(f"  Phase 1 done: updated={updated}, failed={phase1_failed}")
    print()

    # ========== PHASE 2: Search for not-found countries ==========
    # Also include phase 1 failures
    search_tags = notfound_tags + [t for t in found_tags if not wiki_data.get(t, {}).get("lore_full") and not wiki_data.get(t, {}).get("wiki_title")]

    print(f"=== PHASE 2: Searching for {len(search_tags)} unfound countries ===")
    newly_found = 0
    not_found = 0

    # Common prefixes to try (fewer than before, just the most common)
    PREFIXES = [
        "",
        "Kingdom of ",
        "Duchy of ",
        "County of ",
        "Free City of ",
        "Republic of ",
        "Empire of ",
        "Principality of ",
        "March of ",
        "Barony of ",
        "Grand Duchy of ",
        "Sultanate of ",
        "Khanate of ",
        "Command of ",
        "Clan ",
        "Hold of ",
    ]

    for i, tag in enumerate(search_tags):
        name = anbennar_data[tag].get("name", "")
        if (i + 1) % 50 == 0:
            print(f"  Phase 2 progress: {i+1}/{len(search_tags)} (found={newly_found}, not_found={not_found})")

        try:
            found_it = False

            # Strategy 1: Use opensearch API (fast, one call)
            results = search_wiki(name)
            for candidate_title in results:
                # Check if the name appears in the result title or vice versa
                name_lower = name.lower()
                title_lower = candidate_title.lower()
                if name_lower in title_lower or title_lower in name_lower:
                    final_title, extract, page_size = resolve_and_fetch(candidate_title)
                    if final_title:
                        wiki_data[tag] = make_entry(final_title, extract, page_size)
                        newly_found += 1
                        found_it = True
                        if extract:
                            print(f"  NEW: {tag} '{name}' -> '{final_title}'")
                        else:
                            print(f"  NEW (stub): {tag} '{name}' -> '{final_title}'")
                        break

            if found_it:
                if (i + 1) % 100 == 0:
                    save_data(wiki_data, wiki_path)
                continue

            # Strategy 2: Try a few common prefixes directly
            for prefix in PREFIXES:
                if not prefix and results:
                    # Already tried bare name via search
                    continue
                candidate = prefix + name
                # Quick existence check (single call with redirect + extract)
                final_title, extract, page_size = resolve_and_fetch(candidate)
                if final_title:
                    wiki_data[tag] = make_entry(final_title, extract, page_size)
                    newly_found += 1
                    found_it = True
                    if extract:
                        print(f"  NEW: {tag} '{name}' -> '{final_title}'")
                    else:
                        print(f"  NEW (stub): {tag} '{name}' -> '{final_title}'")
                    break

            if not found_it:
                wiki_data[tag] = empty_entry()
                not_found += 1

        except Exception as e:
            print(f"  ERROR on {tag} '{name}': {e}")
            wiki_data[tag] = empty_entry()
            not_found += 1

        if (i + 1) % 100 == 0:
            save_data(wiki_data, wiki_path)

    save_data(wiki_data, wiki_path)
    print(f"  Phase 2 done: newly_found={newly_found}, not_found={not_found}")
    print()

    # Final summary
    total_found = sum(1 for v in wiki_data.values() if v.get("found"))
    total_with_lore = sum(1 for v in wiki_data.values() if v.get("lore_full"))
    print(f"=== FINAL SUMMARY ===")
    print(f"Total countries: {total}")
    print(f"With wiki page: {total_found}")
    print(f"With actual lore text: {total_with_lore}")
    print(f"Not found: {total - total_found}")


if __name__ == "__main__":
    main()
