"""
Build script for the Anbennar Interactive Guide v3.
Generates a single self-contained index.html that loads JSON data at runtime.
Changes from v2:
- Mission detail as modal overlay instead of bottom panel
- SVG-based arrows/connectors between mission nodes
- Better pills/tags with colors and interactivity
- Removed excessive italics
- Cleaner effects/requirements display (filter noise)
- Missing mission icon placeholders
- Lore truncation + "Has Lore" filter
- Culture click -> filter
- Improved mission grid styling
"""

def build():
    html = r'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Anbennar Compendium</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=IM+Fell+English+SC&family=IM+Fell+English:ital@0;1&family=Cinzel+Decorative:wght@400;700&family=Lora:ital,wght@0,400;0,600;1,400&display=swap" rel="stylesheet">
<style>
:root {
  --bg: #0e0e12;
  --card: #16161e;
  --card-hover: #1c1c28;
  --border: #2a2a35;
  --gold: #c9a84c;
  --gold-dim: #8a7333;
  --gold-bright: #e8c84a;
  --text: #d4d4e0;
  --text-secondary: #9e9eb0;
  --text-muted: #5e5e70;
  --green: #4aba6a;
  --red: #e05252;
  --blue: #5b9bd5;
  --purple: #9b72cf;
  --parchment: #1a1710;
  --sidebar-w: 320px;
  --header-h: 80px;
}

* { margin: 0; padding: 0; box-sizing: border-box; }

body {
  font-family: 'Lora', Georgia, serif;
  background: var(--bg);
  color: var(--text);
  min-height: 100vh;
  overflow: hidden;
}

/* HEADER */
#header {
  height: var(--header-h);
  background: linear-gradient(135deg, #12100c 0%, #1e1814 30%, #2a1f15 50%, #1e1814 70%, #12100c 100%);
  border-bottom: 2px solid var(--gold-dim);
  display: flex;
  align-items: center;
  padding: 0 32px;
  position: relative;
  z-index: 100;
}
#header::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0; bottom: 0;
  background: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23c9a84c' fill-opacity='0.03'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
  pointer-events: none;
  opacity: 0.5;
}
#header::after {
  content: '';
  position: absolute;
  bottom: 0; left: 0; right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, var(--gold), transparent);
}
#header-content {
  position: relative;
  z-index: 1;
}
#header h1 {
  font-family: 'IM Fell English SC', serif;
  color: var(--gold);
  font-size: 30px;
  font-weight: 400;
  letter-spacing: 4px;
  text-shadow: 0 2px 12px rgba(201,168,76,0.4), 0 0 40px rgba(201,168,76,0.1);
}
#header .subtitle {
  font-family: 'IM Fell English', serif;
  font-style: italic;
  color: var(--text-secondary);
  font-size: 12px;
  margin-top: 2px;
  letter-spacing: 1px;
}

/* LAYOUT */
#layout {
  display: flex;
  height: calc(100vh - var(--header-h));
}

/* SIDEBAR */
#sidebar {
  width: var(--sidebar-w);
  min-width: var(--sidebar-w);
  background: var(--card);
  border-right: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
#search-box {
  padding: 12px;
  border-bottom: 1px solid var(--border);
}
#search-input {
  width: 100%;
  padding: 8px 12px;
  background: #0e0e12;
  border: 1px solid var(--gold-dim);
  border-radius: 4px;
  color: var(--text);
  font-family: 'Lora', serif;
  font-size: 13px;
  outline: none;
  transition: border-color 0.2s;
}
#search-input:focus { border-color: var(--gold); }
#search-input::placeholder { color: var(--text-muted); }

#filters {
  padding: 8px 12px;
  border-bottom: 1px solid var(--border);
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}
.filter-btn {
  padding: 3px 10px;
  font-size: 11px;
  font-family: 'Lora', serif;
  border: 1px solid var(--border);
  border-radius: 12px;
  background: transparent;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.2s;
}
.filter-btn:hover { border-color: var(--gold-dim); color: var(--text); }
.filter-btn.active { background: var(--gold-dim); color: #fff; border-color: var(--gold); }

#region-filter {
  padding: 8px 12px;
  border-bottom: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.filter-select {
  width: 100%;
  padding: 6px 8px;
  background: #0e0e12;
  border: 1px solid var(--gold-dim);
  border-radius: 4px;
  color: var(--text);
  font-family: 'Lora', serif;
  font-size: 12px;
  outline: none;
}
.filter-select option { background: var(--card); }
#active-filters {
  padding: 4px 12px;
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  align-items: center;
}
#active-filters:empty { display: none; }
.active-chip {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 2px 8px;
  font-size: 10px;
  background: var(--gold-dim);
  color: #fff;
  border-radius: 10px;
  cursor: default;
}
.active-chip .chip-x {
  cursor: pointer;
  font-size: 13px;
  line-height: 1;
  opacity: 0.7;
}
.active-chip .chip-x:hover { opacity: 1; }
.clear-all-btn {
  font-size: 10px;
  color: var(--gold);
  cursor: pointer;
  padding: 2px 6px;
  text-decoration: underline;
}
.clear-all-btn:hover { color: var(--gold-bright); }

#country-list {
  flex: 1;
  overflow-y: auto;
  scrollbar-width: thin;
  scrollbar-color: var(--border) transparent;
}
#country-list::-webkit-scrollbar { width: 6px; }
#country-list::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }

.country-item {
  display: flex;
  align-items: center;
  padding: 8px 12px;
  cursor: pointer;
  border-bottom: 1px solid #1a1a24;
  transition: background 0.15s;
  gap: 8px;
}
.country-item:hover { background: var(--card-hover); }
.country-item.selected { background: #1e1a14; border-left: 3px solid var(--gold); }
.country-item img.flag {
  width: 32px; height: 32px;
  image-rendering: pixelated;
  border: 1px solid var(--border);
  border-radius: 2px;
  flex-shrink: 0;
}
.country-item .name {
  flex: 1;
  font-size: 13px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.country-item .status-badge {
  font-size: 9px;
  padding: 1px 5px;
  border-radius: 8px;
  font-family: monospace;
  flex-shrink: 0;
}
.status-badge.formable { background: rgba(155,114,207,0.2); color: var(--purple); border: 1px solid rgba(155,114,207,0.3); }
.country-item .badges {
  display: flex;
  gap: 3px;
  flex-shrink: 0;
}
.badge-dot {
  width: 6px; height: 6px;
  border-radius: 50%;
  display: inline-block;
}
.badge-dot.missions { background: var(--blue); }
.badge-dot.ideas { background: var(--gold); }
.country-item .tag-label {
  font-size: 10px;
  color: var(--text-muted);
  font-family: monospace;
  flex-shrink: 0;
}
#country-count {
  padding: 6px 12px;
  font-size: 11px;
  color: var(--text-muted);
  border-top: 1px solid var(--border);
  text-align: center;
}

/* MAIN CONTENT */
#main {
  flex: 1;
  overflow-y: auto;
  padding: 24px 32px;
  scrollbar-width: thin;
  scrollbar-color: var(--border) transparent;
}
#main::-webkit-scrollbar { width: 6px; }
#main::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }

#welcome {
  text-align: center;
  padding: 80px 20px;
  color: var(--text-muted);
}
#welcome h2 {
  font-family: 'IM Fell English SC', serif;
  color: var(--gold-dim);
  font-size: 24px;
  margin-bottom: 12px;
  letter-spacing: 2px;
}
#welcome p {
  font-family: 'IM Fell English', serif;
  font-style: italic;
}

/* COUNTRY DETAIL */
#detail { display: none; }
#detail.visible { display: block; }

.detail-header {
  display: flex;
  align-items: flex-start;
  gap: 20px;
  margin-bottom: 20px;
}
.detail-header img.flag {
  width: 80px; height: 80px;
  image-rendering: pixelated;
  border: 2px solid var(--gold-dim);
  border-radius: 4px;
  flex-shrink: 0;
  background: #111;
}
.detail-header .info h2 {
  font-family: 'IM Fell English SC', serif;
  color: var(--gold);
  font-size: 26px;
  margin-bottom: 4px;
  letter-spacing: 2px;
}
.detail-header .info .tag-adj {
  color: var(--text-secondary);
  font-size: 13px;
  margin-bottom: 10px;
}
.pills {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}
.pill {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 3px 10px;
  background: #1e1e2a;
  border: 1px solid var(--border);
  border-radius: 14px;
  font-size: 12px;
  color: var(--text-secondary);
  cursor: default;
  transition: all 0.2s;
}
.pill img {
  width: 16px; height: 16px;
  image-rendering: pixelated;
}
.pill.clickable { cursor: pointer; }
.pill.clickable:hover { border-color: var(--gold-dim); color: var(--text); }

/* Pill color variants */
.pill.pill-gov { border-color: rgba(91,155,213,0.5); color: var(--blue); }
.pill.pill-religion { }
.pill.pill-culture { border-color: rgba(155,114,207,0.5); color: var(--purple); }
.pill.pill-region { border-color: rgba(74,186,106,0.5); color: var(--green); }
.pill.pill-region:hover { border-color: var(--green); background: rgba(74,186,106,0.1); }
.pill.pill-playable { border-color: var(--green); color: var(--green); background: rgba(74,186,106,0.1); }
.pill.pill-formable { border-color: var(--purple); color: var(--purple); background: rgba(155,114,207,0.1); }

.wiki-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 14px;
  background: linear-gradient(135deg, #2a2518, #1e1a14);
  border: 1px solid var(--gold-dim);
  border-radius: 4px;
  color: var(--gold);
  font-family: 'IM Fell English', serif;
  font-size: 13px;
  text-decoration: none;
  margin-top: 10px;
  transition: all 0.2s;
}
.wiki-btn:hover { background: #2a2518; border-color: var(--gold); }

/* LORE BOX */
.lore-box {
  background: linear-gradient(135deg, #1a1710, #161410);
  border: 1px solid var(--gold-dim);
  border-left: 3px solid var(--gold);
  border-radius: 0 6px 6px 0;
  padding: 16px 20px;
  margin-bottom: 20px;
  font-family: 'Lora', serif;
  font-size: 14px;
  line-height: 1.8;
  color: var(--text-secondary);
}
.lore-box .first-line {
  font-style: italic;
  color: var(--text);
}
.lore-read-more {
  color: var(--gold);
  text-decoration: underline;
  cursor: pointer;
  font-size: 13px;
  margin-left: 4px;
}
.lore-read-more:hover { color: var(--gold-bright); }
.lore-table {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 16px;
}
.lore-table td {
  padding: 6px 12px;
  border-bottom: 1px solid rgba(255,255,255,0.06);
  font-size: 13px;
  vertical-align: top;
}
.lore-table .lore-label {
  color: var(--gold);
  font-weight: 600;
  width: 160px;
  white-space: nowrap;
}
.lore-text-full {
  background: linear-gradient(135deg, #1a1710, #161410);
  border: 1px solid var(--gold-dim);
  border-left: 3px solid var(--gold);
  border-radius: 0 6px 6px 0;
  padding: 16px 20px;
  margin-top: 16px;
  font-family: 'Lora', serif;
  font-size: 14px;
  line-height: 1.8;
  color: var(--text-secondary);
}

/* SECTION */
.section-title {
  font-family: 'IM Fell English SC', serif;
  color: var(--gold);
  font-size: 16px;
  margin-bottom: 10px;
  padding-bottom: 6px;
  border-bottom: 1px solid var(--border);
  letter-spacing: 1px;
}

/* TABS */
.tabs {
  display: flex;
  gap: 0;
  border-bottom: 2px solid var(--border);
  margin-bottom: 16px;
}
.tab-btn {
  padding: 10px 20px;
  background: transparent;
  border: none;
  font-family: 'IM Fell English SC', serif;
  font-size: 14px;
  color: var(--text-muted);
  cursor: pointer;
  border-bottom: 2px solid transparent;
  margin-bottom: -2px;
  transition: all 0.2s;
  letter-spacing: 1px;
}
.tab-btn:hover { color: var(--text-secondary); }
.tab-btn.active { color: var(--gold); border-bottom-color: var(--gold); }
.tab-btn .count {
  font-family: monospace;
  font-size: 10px;
  color: var(--text-muted);
  margin-left: 4px;
}

.tab-content { display: none; }
.tab-content.active { display: block; }

/* IDEAS */
.idea-group { margin-bottom: 16px; }
.idea-label {
  font-family: 'IM Fell English SC', serif;
  font-size: 13px;
  color: var(--gold-dim);
  margin-bottom: 8px;
  letter-spacing: 1px;
}
.idea-card {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 4px;
  padding: 10px 14px;
  margin-bottom: 6px;
}
.idea-card h4 {
  font-size: 13px;
  color: var(--text);
  margin-bottom: 4px;
}
.idea-card .idea-desc {
  font-size: 12px;
  color: var(--text-secondary);
  margin-bottom: 6px;
  font-style: normal;
  font-weight: 400;
  line-height: 1.6;
}

/* MODIFIER CHIPS */
.mod-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}
.mod-chip {
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 11px;
  font-family: monospace;
}
.mod-chip.positive { background: rgba(74,186,106,0.15); color: var(--green); border: 1px solid rgba(74,186,106,0.3); }
.mod-chip.negative { background: rgba(224,82,82,0.15); color: var(--red); border: 1px solid rgba(224,82,82,0.3); }
.mod-chip.neutral { background: rgba(158,158,176,0.1); color: var(--text-secondary); border: 1px solid var(--border); }

/* MISSIONS */
.mission-grid-container {
  overflow-x: auto;
  padding-bottom: 12px;
  position: relative;
}
.mission-grid {
  display: grid;
  gap: 10px;
  min-width: max-content;
  position: relative;
  z-index: 2;
}
.mission-node.has-prereq-above::before {
  content: '';
  position: absolute;
  top: -10px;
  left: 50%;
  transform: translateX(-50%);
  width: 2px;
  height: 10px;
  background: var(--gold);
  opacity: 0.4;
  pointer-events: none;
}
.cross-prereq-badge {
  position: absolute;
  top: -2px;
  left: 4px;
  font-size: 9px;
  color: var(--text-muted);
  background: rgba(14,14,18,0.85);
  padding: 1px 5px;
  border-radius: 6px;
  border: 1px solid var(--border);
  white-space: nowrap;
  pointer-events: none;
  z-index: 3;
  line-height: 1.2;
}
.mission-node {
  background: linear-gradient(180deg, #1c1c28 0%, #16161e 100%);
  border: 1px solid var(--border);
  border-radius: 6px;
  padding: 8px 10px;
  cursor: pointer;
  text-align: center;
  font-size: 11px;
  transition: all 0.2s;
  min-width: 140px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 5px;
  position: relative;
}
.mission-node:hover { border-color: var(--blue); background: linear-gradient(180deg, #222235 0%, #1c1c28 100%); box-shadow: 0 0 8px rgba(91,155,213,0.2); }
.mission-node.selected { border-color: var(--gold); background: linear-gradient(180deg, #2a2518 0%, #1e1a14 100%); box-shadow: 0 0 12px rgba(201,168,76,0.3); }
.mission-node .mission-icon {
  width: 40px; height: 40px;
  image-rendering: auto;
  border-radius: 2px;
  opacity: 0.9;
}
.mission-node .mission-icon-fallback, .mission-icon-fallback {
  width: 40px; height: 40px;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  color: rgba(201,168,76,0.5);
  background: linear-gradient(135deg, #2a2518 0%, #1a1a2a 100%);
  border: 1px solid rgba(201,168,76,0.2);
}
.mission-node .mission-title {
  color: var(--text);
  font-size: 11px;
  line-height: 1.2;
}

/* MISSION DETAIL MODAL */
#mission-modal-overlay {
  display: none;
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.6);
  z-index: 999;
}
#mission-modal-overlay.visible { display: block; }
#mission-modal {
  display: none;
  position: fixed;
  top: 50%; left: 50%;
  transform: translate(-50%, -50%);
  background: var(--card);
  border: 2px solid var(--gold-dim);
  border-radius: 8px;
  padding: 24px;
  z-index: 1000;
  max-width: 600px;
  width: 90%;
  max-height: 80vh;
  overflow-y: auto;
}
#mission-modal.visible { display: block; }
#mission-modal .close-btn {
  position: absolute; top: 12px; right: 12px;
  background: none; border: none; color: var(--text-muted);
  font-size: 20px; cursor: pointer;
}
#mission-modal .close-btn:hover { color: var(--text); }
#mission-modal::-webkit-scrollbar { width: 6px; }
#mission-modal::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }
#mission-modal h3 {
  font-family: 'IM Fell English SC', serif;
  color: var(--gold);
  font-size: 18px;
  margin-bottom: 8px;
  letter-spacing: 1px;
  display: flex;
  align-items: center;
  gap: 10px;
}
#mission-modal h3 img {
  width: 48px; height: 48px;
  border-radius: 3px;
  border: 1px solid var(--border);
}
#mission-modal h3 .modal-icon-placeholder {
  width: 48px; height: 48px;
  border-radius: 4px;
  flex-shrink: 0;
}
#mission-modal .mission-desc {
  color: var(--text-secondary);
  font-size: 13px;
  margin-bottom: 12px;
  line-height: 1.6;
  font-style: normal;
}
#mission-modal .prereqs {
  margin-bottom: 12px;
}
.prereqs .prereq-link {
  color: var(--blue);
  cursor: pointer;
  text-decoration: underline;
  font-size: 12px;
}
.prereqs .prereq-link:hover { color: var(--gold); }

/* Requirements display */
.requirements-box {
  background: #0f0f14;
  border: 1px solid var(--border);
  border-left: 3px solid var(--blue);
  border-radius: 0 4px 4px 0;
  padding: 10px 14px;
  margin: 8px 0;
  font-size: 12px;
  line-height: 1.7;
}
.requirements-box .req-label {
  font-family: 'IM Fell English SC', serif;
  color: var(--blue);
  font-size: 12px;
  margin-bottom: 6px;
  letter-spacing: 1px;
}
.requirements-box ul {
  list-style: none;
  padding: 0;
}
.requirements-box li {
  color: var(--text-secondary);
  padding: 2px 0;
  padding-left: 14px;
  position: relative;
}
.requirements-box li::before {
  content: '\2022';
  color: var(--gold-dim);
  position: absolute;
  left: 0;
}
.requirements-box li .kw { color: var(--purple); }
.requirements-box li .val { color: var(--gold); }
.requirements-box li .tag { color: var(--blue); }

/* Effects display */
.effects-box {
  background: #0f0f14;
  border: 1px solid var(--border);
  border-left: 3px solid var(--green);
  border-radius: 0 4px 4px 0;
  padding: 10px 14px;
  margin: 8px 0;
  font-size: 12px;
  line-height: 1.7;
}
.effects-box .eff-label {
  font-family: 'IM Fell English SC', serif;
  color: var(--green);
  font-size: 12px;
  margin-bottom: 6px;
  letter-spacing: 1px;
}
.effects-box ul {
  list-style: none;
  padding: 0;
}
.effects-box li {
  color: var(--text-secondary);
  padding: 2px 0;
  padding-left: 14px;
  position: relative;
}
.effects-box li::before {
  content: '\2022';
  color: var(--green);
  position: absolute;
  left: 0;
}
.effects-box li .val { color: var(--gold); }
.effects-box li .tag { color: var(--blue); }
.requirements-box li .tag { color: var(--blue); }

/* Modifier tooltips */
.mod-ref {
  color: var(--blue);
  cursor: help;
  border-bottom: 1px dotted var(--blue);
  position: relative;
}
.mod-tooltip {
  display: none;
  position: fixed;
  background: #1a1a24;
  border: 1px solid var(--gold-dim);
  border-radius: 6px;
  padding: 8px 12px;
  min-width: 220px;
  max-width: 320px;
  z-index: 99999;
  font-size: 13px;
  line-height: 1.5;
  box-shadow: 0 4px 16px rgba(0,0,0,0.5);
  pointer-events: none;
}
/* tooltip positioning handled by JS mouseover */
.mod-tooltip .mod-tt-name {
  color: var(--gold);
  font-weight: 600;
  font-size: 14px;
  margin-bottom: 4px;
  font-family: 'Cinzel Decorative', serif;
}
.mod-tooltip .mod-tt-effect {
  display: flex;
  justify-content: space-between;
  gap: 12px;
}
.mod-tooltip .mod-tt-val {
  white-space: nowrap;
  font-weight: 600;
}
.mod-tooltip .mod-tt-val.positive { color: var(--green); }
.mod-tooltip .mod-tt-val.negative { color: var(--red); }

.script-block {
  background: #0c0c10;
  border: 1px solid var(--border);
  border-radius: 4px;
  padding: 10px 12px;
  font-family: 'Consolas', 'Courier New', monospace;
  font-size: 11px;
  line-height: 1.5;
  overflow-x: auto;
  white-space: pre-wrap;
  color: var(--text-muted);
  max-height: 250px;
  overflow-y: auto;
  margin-top: 6px;
}

/* RELIGION PANEL */
#religion-panel {
  display: none;
  position: fixed;
  top: 50%; left: 50%;
  transform: translate(-50%, -50%);
  background: var(--card);
  border: 2px solid var(--gold-dim);
  border-radius: 8px;
  padding: 24px;
  z-index: 1000;
  max-width: 500px;
  width: 90%;
  max-height: 70vh;
  overflow-y: auto;
}
#religion-panel.visible { display: block; }
#religion-overlay {
  display: none;
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.6);
  z-index: 999;
}
#religion-overlay.visible { display: block; }
#religion-panel h3 {
  font-family: 'IM Fell English SC', serif;
  color: var(--gold);
  font-size: 18px;
  margin-bottom: 12px;
  display: flex;
  align-items: center;
  gap: 10px;
}
#religion-panel h3 img { width: 32px; height: 32px; image-rendering: pixelated; }
#religion-panel .religion-group { color: var(--text-secondary); font-size: 13px; margin-bottom: 10px; }
#religion-panel .close-btn {
  position: absolute; top: 12px; right: 12px;
  background: none; border: none; color: var(--text-muted);
  font-size: 20px; cursor: pointer;
}
#religion-panel .close-btn:hover { color: var(--text); }
#religion-panel::-webkit-scrollbar { width: 6px; }
#religion-panel::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }

/* RESPONSIVE */
@media (max-width: 768px) {
  #sidebar { display: none; }
  #sidebar.mobile-open { display: flex; position: fixed; z-index: 200; top: var(--header-h); left: 0; bottom: 0; }
  #mobile-toggle {
    display: block !important;
    position: absolute; right: 16px; top: 50%; transform: translateY(-50%);
    background: none; border: 1px solid var(--gold-dim); border-radius: 4px;
    color: var(--gold); padding: 6px 10px; cursor: pointer; font-size: 18px;
    z-index: 1;
  }
  #main { padding: 16px; }
}

#mobile-toggle { display: none; }

.color-dot {
  display: inline-block;
  width: 12px; height: 12px;
  border-radius: 50%;
  border: 1px solid var(--border);
  vertical-align: middle;
}

.loading {
  text-align: center;
  padding: 40px;
  color: var(--text-muted);
  font-family: 'IM Fell English SC', serif;
}

/* Toggle for raw script view */
.toggle-raw {
  font-size: 11px;
  color: var(--text-muted);
  cursor: pointer;
  text-decoration: underline;
  margin-top: 4px;
  display: inline-block;
}
.toggle-raw:hover { color: var(--text-secondary); }
</style>
</head>
<body>

<div id="header">
  <div id="header-content">
    <h1>ANBENNAR COMPENDIUM</h1>
    <div class="subtitle">An Interactive Guide to the World of Halcann</div>
  </div>
  <button id="mobile-toggle">&#9776;</button>
</div>

<div id="layout">
  <div id="sidebar">
    <div id="search-box">
      <input type="text" id="search-input" placeholder="Search countries, tags, cultures...">
    </div>
    <div id="filters">
      <button class="filter-btn" data-filter="playable">Playable 1444</button>
      <button class="filter-btn" data-filter="formable">Formable</button>
      <button class="filter-btn" data-filter="missions">Has Missions</button>
    </div>
    <div id="region-filter">
      <select id="region-select" class="filter-select"><option value="">All Regions</option></select>
      <select id="culture-select" class="filter-select"><option value="">All Culture Groups</option></select>
      <select id="religion-select" class="filter-select"><option value="">All Religions</option></select>
      <select id="tech-select" class="filter-select"><option value="">All Tech Groups</option></select>
      <select id="gov-select" class="filter-select"><option value="">All Governments</option></select>
    </div>
    <div id="active-filters"></div>
    <div id="country-list"></div>
    <div id="country-count"></div>
  </div>

  <div id="main">
    <div id="welcome">
      <h2>Welcome, Adventurer</h2>
      <p>Select a country from the sidebar to explore its history, missions, and national ideas.</p>
    </div>
    <div id="detail"></div>
  </div>
</div>

<div id="religion-overlay"></div>
<div id="religion-panel"></div>

<div id="mission-modal-overlay"></div>
<div id="mission-modal"></div>

<script>
// --- DATA ---
let DATA = {}, RELIGIONS = {}, WIKI = {}, REGIONS = {}, TRIGGERS = {}, STATUS = {}, ICON_MAP = {}, PROVINCES = {}, MODIFIERS = {}, STARTUP_LORE = {};
let countries = [];
let filteredCountries = [];
let selectedTag = null;
let renderLimit = 200;
let activeFilters = new Set();

async function loadData() {
  const el = document.getElementById('country-list');
  el.innerHTML = '<div class="loading">Loading data...</div>';
  try {
    const [d1, d2, d3, d5, d6, d7, d8, d9, d10, d11] = await Promise.all([
      fetch('anbennar_data.json').then(r => r.json()),
      fetch('religions_data.json').then(r => r.json()),
      fetch('wiki_data.json').then(r => r.json()),
      fetch('regions_data.json').then(r => r.json()),
      fetch('mission_triggers.json').then(r => r.json()),
      fetch('country_status.json').then(r => r.json()).catch(() => ({})),
      fetch('mission_icon_map.json').then(r => r.json()).catch(() => ({})),
      fetch('province_names.json').then(r => r.json()).catch(() => ({})),
      fetch('modifiers_data.json').then(r => r.json()).catch(() => ({})),
      fetch('startup_lore.json').then(r => r.json()).catch(() => ({})),
    ]);
    DATA = d1; RELIGIONS = d2; WIKI = d3; REGIONS = d5; TRIGGERS = d6; STATUS = d7; ICON_MAP = d8; PROVINCES = d9; MODIFIERS = d10 || {}; STARTUP_LORE = d11 || {};

    countries = Object.values(DATA);
    countries.sort(countrySorter);
    populateRegions();
    populateFilterDropdowns();
    applyFilters();
  } catch(e) {
    el.innerHTML = '<div class="loading">Error loading data: ' + e.message + '</div>';
    console.error(e);
  }
}

function countrySorter(a, b) {
  const wa = WIKI[a.tag], wb = WIKI[b.tag];
  const hasWikiA = wa && wa.found ? 1 : 0;
  const hasWikiB = wb && wb.found ? 1 : 0;
  if (hasWikiA !== hasWikiB) return hasWikiB - hasWikiA;
  const sizeA = wa ? (wa.page_size || wa.page_length || 0) : 0;
  const sizeB = wb ? (wb.page_size || wb.page_length || 0) : 0;
  if (sizeA !== sizeB) return sizeB - sizeA;
  return a.name.localeCompare(b.name);
}

function titleCase(s) {
  if (!s) return '';
  return s.replace(/\b\w/g, c => c.toUpperCase());
}

function levenshtein(a, b) {
  if (a.length === 0) return b.length;
  if (b.length === 0) return a.length;
  const matrix = [];
  for (let i = 0; i <= b.length; i++) matrix[i] = [i];
  for (let j = 0; j <= a.length; j++) matrix[0][j] = j;
  for (let i = 1; i <= b.length; i++) {
    for (let j = 1; j <= a.length; j++) {
      const cost = b[i-1] === a[j-1] ? 0 : 1;
      matrix[i][j] = Math.min(matrix[i-1][j] + 1, matrix[i][j-1] + 1, matrix[i-1][j-1] + cost);
    }
  }
  return matrix[b.length][a.length];
}

function fuzzyScore(query, text) {
  if (!text) return 0;
  const q = query.toLowerCase();
  const t = text.toLowerCase();
  if (t === q) return 200; // exact match
  if (t.includes(q)) return 100; // substring match
  if (t.startsWith(q)) return 150; // prefix match
  if (q.length < 2) return 0;
  // Subsequence match: all chars in order
  let qi = 0;
  for (let ti = 0; ti < t.length && qi < q.length; ti++) {
    if (t[ti] === q[qi]) qi++;
  }
  if (qi === q.length) return 50;
  // Levenshtein for typo tolerance (check words)
  if (q.length >= 3) {
    const words = t.split(/[\s_-]+/);
    for (const word of words) {
      const sub = word.substring(0, q.length + 2);
      const dist = levenshtein(q, sub);
      if (dist <= 1) return 40;
      if (dist <= 2 && q.length >= 5) return 25;
    }
    // Also check whole name
    if (levenshtein(q, t.substring(0, q.length + 2)) <= 1) return 35;
  }
  return 0;
}

function populateRegions() {
  const sel = document.getElementById('region-select');
  const srs = new Set();
  for (const r of Object.values(REGIONS)) {
    if (r.superregion_name) srs.add(r.superregion_name);
  }
  [...srs].sort().forEach(sr => {
    const opt = document.createElement('option');
    opt.value = sr; opt.textContent = sr;
    sel.appendChild(opt);
  });
}

function populateFilterDropdowns() {
  updateFilterDropdowns();
}

function updateFilterDropdowns() {
  const region = document.getElementById('region-select').value;
  const culture = document.getElementById('culture-select').value;
  const religion = document.getElementById('religion-select').value;
  const tech = document.getElementById('tech-select').value;
  const gov = document.getElementById('gov-select').value;

  // Get eligible countries (those that pass non-dropdown filters)
  const eligible = countries.filter(c => {
    const w = WIKI[c.tag];
    const hasWiki = w && w.found && (w.page_size || w.page_length || 0) > 500;
    const hasMissions = c.missions && c.missions.length > 0;
    const hasIdeas = c.ideas && c.ideas.ideas && c.ideas.ideas.length > 0;
    if (!hasWiki && !hasMissions && !hasIdeas) return false;
    return passesFilter(c);
  });

  // For each dropdown, compute valid options based on all OTHER active filters
  function matchesOtherFilters(c, skipFilter) {
    if (skipFilter !== 'region' && region) {
      const reg = REGIONS[c.tag];
      if (!reg || reg.superregion_name !== region) return false;
    }
    if (skipFilter !== 'culture' && culture && c.culture_group !== culture) return false;
    if (skipFilter !== 'religion' && religion && c.religion !== religion) return false;
    if (skipFilter !== 'tech' && tech && c.technology_group !== tech) return false;
    if (skipFilter !== 'gov' && gov && c.government !== gov) return false;
    return true;
  }

  const validCultures = new Set(), validReligions = new Set(), validTechs = new Set(), validGovs = new Set(), validRegions = new Set();
  eligible.forEach(c => {
    const reg = REGIONS[c.tag];
    if (matchesOtherFilters(c, 'culture') && c.culture_group) validCultures.add(c.culture_group);
    if (matchesOtherFilters(c, 'religion') && c.religion) validReligions.add(c.religion);
    if (matchesOtherFilters(c, 'tech') && c.technology_group) validTechs.add(c.technology_group);
    if (matchesOtherFilters(c, 'gov') && c.government) validGovs.add(c.government);
    if (matchesOtherFilters(c, 'region') && reg && reg.superregion_name) validRegions.add(reg.superregion_name);
  });

  const repopulate = (id, values, currentVal) => {
    const sel = document.getElementById(id);
    const defaultText = sel.options[0].textContent;
    sel.innerHTML = '';
    const defOpt = document.createElement('option');
    defOpt.value = ''; defOpt.textContent = defaultText;
    sel.appendChild(defOpt);
    [...values].sort().forEach(v => {
      const opt = document.createElement('option');
      opt.value = v; opt.textContent = titleCase(v);
      sel.appendChild(opt);
    });
    sel.value = values.has(currentVal) ? currentVal : '';
  };

  repopulate('culture-select', validCultures, culture);
  repopulate('religion-select', validReligions, religion);
  repopulate('tech-select', validTechs, tech);
  repopulate('gov-select', validGovs, gov);
  repopulate('region-select', validRegions, region);
}

function passesFilter(c) {
  if (activeFilters.size === 0) return true;
  const s = STATUS[c.tag] || {};
  if (activeFilters.has('playable') && !(s.status === 'playable' || s.status === 'both')) return false;
  if (activeFilters.has('formable') && !(s.status === 'formable' || s.status === 'both')) return false;
  if (activeFilters.has('missions') && !(c.missions && c.missions.length > 0)) return false;
  return true;
}

function applyFilters() {
  const query = document.getElementById('search-input').value.toLowerCase().trim();
  const region = document.getElementById('region-select').value;
  const culture = document.getElementById('culture-select').value;
  const religion = document.getElementById('religion-select').value;
  const tech = document.getElementById('tech-select').value;
  const gov = document.getElementById('gov-select').value;

  let scored = [];
  countries.forEach(c => {
    // By default hide countries with no wiki, no missions, no ideas
    const w = WIKI[c.tag];
    const hasWiki = w && w.found && (w.page_size || w.page_length || 0) > 500;
    const hasMissions = c.missions && c.missions.length > 0;
    const hasIdeas = c.ideas && c.ideas.ideas && c.ideas.ideas.length > 0;
    if (!hasWiki && !hasMissions && !hasIdeas) return;

    if (!passesFilter(c)) return;

    // Dropdown filters
    if (culture && c.culture_group !== culture) return;
    if (religion && c.religion !== religion) return;
    if (tech && c.technology_group !== tech) return;
    if (gov && c.government !== gov) return;
    if (region) {
      const reg = REGIONS[c.tag];
      if (!reg || reg.superregion_name !== region) return;
    }

    // Text search with fuzzy matching
    let score = 0;
    if (query) {
      score = Math.max(
        fuzzyScore(query, c.name),
        fuzzyScore(query, c.tag),
        fuzzyScore(query, c.primary_culture),
        fuzzyScore(query, c.religion),
        fuzzyScore(query, c.culture_group),
        fuzzyScore(query, c.government),
        fuzzyScore(query, c.technology_group),
        fuzzyScore(query, c.adjective)
      );
      if (score === 0) return;
    }
    scored.push({ c, score });
  });

  // Sort by score (if searching), then by existing sort order
  if (query) {
    scored.sort((a, b) => b.score - a.score || countrySorter(a.c, b.c));
  } else {
    scored.sort((a, b) => countrySorter(a.c, b.c));
  }

  filteredCountries = scored.map(s => s.c);
  renderLimit = 200;
  renderCountryList();
  renderActiveFilters();
  updateFilterDropdowns();
}

function renderActiveFilters() {
  const container = document.getElementById('active-filters');
  const chips = [];
  const query = document.getElementById('search-input').value.trim();
  if (query) chips.push({ label: 'Search: "' + query + '"', clear: () => { document.getElementById('search-input').value = ''; } });
  const selectors = [
    { id: 'region-select', label: 'Region' },
    { id: 'culture-select', label: 'Culture' },
    { id: 'religion-select', label: 'Religion' },
    { id: 'tech-select', label: 'Tech' },
    { id: 'gov-select', label: 'Government' },
  ];
  selectors.forEach(s => {
    const val = document.getElementById(s.id).value;
    if (val) chips.push({ label: s.label + ': ' + titleCase(val), clear: () => { document.getElementById(s.id).value = ''; } });
  });
  activeFilters.forEach(f => {
    chips.push({ label: titleCase(f), clear: () => { activeFilters.delete(f); document.querySelector(`.filter-btn[data-filter="${f}"]`).classList.remove('active'); } });
  });

  if (chips.length === 0) { container.innerHTML = ''; return; }

  container.innerHTML = chips.map((ch, i) =>
    `<span class="active-chip">${esc(ch.label)} <span class="chip-x" data-idx="${i}">&times;</span></span>`
  ).join('') + '<span class="clear-all-btn">Clear All</span>';

  container.querySelectorAll('.chip-x').forEach(x => {
    x.addEventListener('click', () => { chips[parseInt(x.dataset.idx)].clear(); applyFilters(); });
  });
  container.querySelector('.clear-all-btn').addEventListener('click', clearAllFilters);
}

function clearAllFilters() {
  document.getElementById('search-input').value = '';
  document.getElementById('region-select').value = '';
  document.getElementById('culture-select').value = '';
  document.getElementById('religion-select').value = '';
  document.getElementById('tech-select').value = '';
  document.getElementById('gov-select').value = '';
  activeFilters.clear();
  document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
  applyFilters();
}

function renderCountryList() {
  const list = document.getElementById('country-list');
  const count = document.getElementById('country-count');
  const toRender = filteredCountries.slice(0, renderLimit);

  list.innerHTML = toRender.map(c => {
    const hasMissions = c.missions && c.missions.length > 0;
    const hasIdeas = c.ideas && c.ideas.ideas && c.ideas.ideas.length > 0;
    const s = STATUS[c.tag] || {};
    const isFormable = s.status === 'formable' || s.status === 'both';
    let badges = '';
    if (hasMissions) badges += '<span class="badge-dot missions" title="Has missions"></span>';
    if (hasIdeas) badges += '<span class="badge-dot ideas" title="Has ideas"></span>';
    let statusBadge = isFormable ? '<span class="status-badge formable">Formable</span>' : '';

    return `<div class="country-item${selectedTag === c.tag ? ' selected' : ''}" data-tag="${c.tag}">
      <img class="flag" src="flags/${c.tag}.png" onerror="this.style.display='none'" loading="lazy">
      <span class="name">${esc(c.name)}</span>
      ${statusBadge}
      <span class="badges">${badges}</span>
      <span class="tag-label">${c.tag}</span>
    </div>`;
  }).join('');

  count.textContent = `${filteredCountries.length} countries`;

  list.querySelectorAll('.country-item').forEach(el => {
    el.addEventListener('click', () => selectCountry(el.dataset.tag));
  });
}

// Lazy load more on scroll
document.addEventListener('DOMContentLoaded', () => {
  const list = document.getElementById('country-list');
  list.addEventListener('scroll', () => {
    if (list.scrollTop + list.clientHeight >= list.scrollHeight - 100) {
      if (renderLimit < filteredCountries.length) {
        renderLimit += 200;
        renderCountryList();
      }
    }
  });
});

// Filter buttons
document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.filter-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const f = btn.dataset.filter;
      if (activeFilters.has(f)) {
        activeFilters.delete(f);
        btn.classList.remove('active');
      } else {
        activeFilters.add(f);
        btn.classList.add('active');
      }
      applyFilters();
    });
  });
  document.getElementById('search-input').addEventListener('input', applyFilters);
  ['region-select','culture-select','religion-select','tech-select','gov-select'].forEach(id => {
    document.getElementById(id).addEventListener('change', applyFilters);
  });
  document.getElementById('mobile-toggle').addEventListener('click', () => {
    document.getElementById('sidebar').classList.toggle('mobile-open');
  });
  document.getElementById('religion-overlay').addEventListener('click', closeReligionPanel);
  document.getElementById('mission-modal-overlay').addEventListener('click', closeMissionModal);
});

function provName(id) {
  const n = PROVINCES[String(id)];
  return n ? n : 'Province ' + id;
}

function esc(s) {
  if (!s) return '';
  const d = document.createElement('div');
  d.textContent = s;
  return d.innerHTML;
}

function formatModifier(name) {
  return name.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
}

function modChip(name, value) {
  const num = parseFloat(value);
  let cls = 'neutral';
  if (!isNaN(num)) {
    const lname = name.toLowerCase();
    // "Less is better" modifiers: negative value = green, positive value = red
    const negIsGood = /cost|unrest|corruption|inflation(?!_reduction)|decay(?!.*_reduction)|attrition(?!.*hostile)|impact|demand|liberty_desire|aggressive_expansion|build_time|interest|ae_impact|core_creation|harsh|stab_hit|power_cost|regiment_cost|ship_cost|maintenance|war_exhaustion|damage_received|morale_damage_received|morale_hit_recieved|landing_penalty|uprising_chance|cooldown|governing_cost|transport_cost|overextension|years_of_nationalism|envoy_travel_time|global_autonomy|min_autonomy|recruit_speed|culture_conversion_time|autonomy_change_time|national_focus_years|global_monthly_devastation|devastation/.test(lname) && !/hostile_attrition|^reduced_|_reduction|karma_decay/.test(lname);
    if (negIsGood) {
      cls = num <= 0 ? 'positive' : 'negative';
    } else {
      cls = num >= 0 ? 'positive' : 'negative';
    }
  }
  let display = value;
  if (!isNaN(num)) {
    if (Math.abs(num) < 1 && Math.abs(num) > 0 && !/max_|num_|amount/.test(name)) {
      display = (num >= 0 ? '+' : '') + (num * 100).toFixed(1).replace(/\.0$/, '') + '%';
    } else {
      display = (num >= 0 ? '+' : '') + num;
    }
  }
  return `<span class="mod-chip ${cls}">${formatModifier(name)}: ${display}</span>`;
}

// --- Wiki URL builder ---
function wikiUrl(name) {
  let slug = name.trim();
  return 'https://anbennar.fandom.com/wiki/' + encodeURIComponent(slug.replace(/ /g, '_'));
}

// --- Filter helpers for clicking pills ---
function setRegionFilter(regionName) {
  const sel = document.getElementById('region-select');
  for (let i = 0; i < sel.options.length; i++) {
    if (sel.options[i].value === regionName) {
      sel.value = regionName;
      applyFilters();
      return;
    }
  }
}

function setCultureSearch(cultureName) {
  document.getElementById('culture-select').value = cultureName;
  applyFilters();
}

function setReligionFilter(religionName) {
  document.getElementById('religion-select').value = religionName;
  applyFilters();
}

function setGovernmentFilter(govName) {
  document.getElementById('gov-select').value = govName;
  applyFilters();
}

function setTechFilter(techName) {
  document.getElementById('tech-select').value = techName;
  applyFilters();
}

// Resolve EU4 script references like [4420.GetName] to province names, strip others
function resolveGameText(text) {
  if (!text) return text;
  return text
    // Province ID references
    .replace(/\[(\d+)\.GetName\]/gi, (m, id) => {
      const name = PROVINCES[String(id)];
      return name || ('Province ' + id);
    })
    // Sensible defaults for common Root scope references
    .replace(/\[Root\.Monarch\.GetTitle\]/gi, 'our ruler')
    .replace(/\[Root\.Monarch\.GetName\]/gi, 'our ruler')
    .replace(/\[Root\.Monarch\.GetHerHis\]/gi, 'their')
    .replace(/\[Root\.Monarch\.GetSheHe\]/gi, 'they')
    .replace(/\[Root\.Monarch\.GetHerHim\]/gi, 'them')
    .replace(/\[Root\.GetName\]/gi, 'our nation')
    .replace(/\[Root\.GetAdjective\]/gi, 'our')
    .replace(/\[Root\.Capital\.GetName\]/gi, 'our capital')
    .replace(/\[Root\.GovernmentName\]/gi, 'our government')
    .replace(/\[Root\.GetSelectableMissionTitle\]/gi, '')
    // Strip remaining bracket references
    .replace(/\[Root\.[\w.]+\]/gi, '')
    .replace(/\[\w+\.[\w.]+\]/gi, '')
    .replace(/\[[\w.]+\]/g, '')
    // Clean icon codes (£icon£)
    .replace(/\u00a3\w+\u00a3/g, '')
    .replace(/£\w+£/g, '')
    // Clean leftover color codes
    .replace(/\u00a7[A-Za-z!]/g, '')
    .replace(/§[A-Za-z!]/g, '')
    // Clean dollar variables with fallbacks
    .replace(/\$MONARCH\$/gi, 'our ruler')
    .replace(/\$MONARCHTITLE\$/gi, 'ruler')
    .replace(/\$DYNASTY\$/gi, 'our dynasty')
    .replace(/\$[^$]+\$/g, '')
    .replace(/\s{2,}/g, ' ')
    .trim();
}

// --- PARSE TRIGGER TO HUMAN READABLE ---
function parseTriggerToReadable(raw) {
  if (!raw || !raw.trim()) return [];
  // Pre-process: collapse multi-line modifier blocks into single lines
  let processed = raw.replace(/add_country_modifier\s*=\s*\{([^}]+)\}/gi, (m, inner) => {
    return 'add_country_modifier = { ' + inner.replace(/\n/g, ' ').replace(/\t/g, ' ') + ' }';
  });
  processed = processed.replace(/add_ruler_modifier\s*=\s*\{([^}]+)\}/gi, (m, inner) => {
    return 'add_ruler_modifier = { ' + inner.replace(/\n/g, ' ').replace(/\t/g, ' ') + ' }';
  });
  processed = processed.replace(/add_province_modifier\s*=\s*\{([^}]+)\}/gi, (m, inner) => {
    return 'add_province_modifier = { ' + inner.replace(/\n/g, ' ').replace(/\t/g, ' ') + ' }';
  });
  processed = processed.replace(/add_permanent_province_modifier\s*=\s*\{([^}]+)\}/gi, (m, inner) => {
    return 'add_permanent_province_modifier = { ' + inner.replace(/\n/g, ' ').replace(/\t/g, ' ') + ' }';
  });
  processed = processed.replace(/remove_country_modifier\s*=\s*\{([^}]+)\}/gi, (m, inner) => {
    return 'remove_country_modifier = { ' + inner.replace(/\n/g, ' ').replace(/\t/g, ' ') + ' }';
  });
  processed = processed.replace(/add_power_projection\s*=\s*\{([^}]+)\}/gi, (m, inner) => {
    return 'add_power_projection = { ' + inner.replace(/\n/g, ' ').replace(/\t/g, ' ') + ' }';
  });
  processed = processed.replace(/country_event\s*=\s*\{([^}]+)\}/gi, (m, inner) => {
    return 'country_event = { ' + inner.replace(/\n/g, ' ').replace(/\t/g, ' ') + ' }';
  });
  processed = processed.replace(/estate_influence\s*=\s*\{([^}]+)\}/gi, (m, inner) => {
    return 'estate_influence = { ' + inner.replace(/\n/g, ' ').replace(/\t/g, ' ') + ' }';
  });
  processed = processed.replace(/estate_loyalty\s*=\s*\{([^}]+)\}/gi, (m, inner) => {
    return 'estate_loyalty = { ' + inner.replace(/\n/g, ' ').replace(/\t/g, ' ') + ' }';
  });
  processed = processed.replace(/add_trust\s*=\s*\{([^}]+)\}/gi, (m, inner) => {
    return 'add_trust = { ' + inner.replace(/\n/g, ' ').replace(/\t/g, ' ') + ' }';
  });
  processed = processed.replace(/num_of_estate_agendas_completed\s*=\s*\{([^}]+)\}/gi, (m, inner) => {
    return 'num_of_estate_agendas_completed = { ' + inner.replace(/\n/g, ' ').replace(/\t/g, ' ') + ' }';
  });
  processed = processed.replace(/num_of_estate_privileges\s*=\s*\{([^}]+)\}/gi, (m, inner) => {
    return 'num_of_estate_privileges = { ' + inner.replace(/\n/g, ' ').replace(/\t/g, ' ') + ' }';
  });
  processed = processed.replace(/is_subject_of_type_with_overlord\s*=\s*\{([^}]+)\}/gi, (m, inner) => {
    return 'is_subject_of_type_with_overlord = { ' + inner.replace(/\n/g, ' ').replace(/\t/g, ' ') + ' }';
  });
  processed = processed.replace(/has_opinion\s*=\s*\{([^}]+)\}/gi, (m, inner) => {
    return 'has_opinion = { ' + inner.replace(/\n/g, ' ').replace(/\t/g, ' ') + ' }';
  });
  processed = processed.replace(/has_government_power\s*=\s*\{([^}]+)\}/gi, (m, inner) => {
    return 'has_government_power = { ' + inner.replace(/\n/g, ' ').replace(/\t/g, ' ') + ' }';
  });
  processed = processed.replace(/check_variable\s*=\s*\{([^}]+)\}/gi, (m, inner) => {
    return 'check_variable = { ' + inner.replace(/\n/g, ' ').replace(/\t/g, ' ') + ' }';
  });
  processed = processed.replace(/(?<!\w)trust\s*=\s*\{([^}]+)\}/gi, (m, inner) => {
    return 'trust = { ' + inner.replace(/\n/g, ' ').replace(/\t/g, ' ') + ' }';
  });
  processed = processed.replace(/has_20_opinion_sent_gift\s*=\s*\{([^}]+)\}/gi, (m, inner) => {
    return 'has_20_opinion_sent_gift = { ' + inner.replace(/\n/g, ' ').replace(/\t/g, ' ') + ' }';
  });
  processed = processed.replace(/has_privateer_share_in_trade_node\s*=\s*\{([^}]+)\}/gi, (m, inner) => {
    return 'has_privateer_share_in_trade_node = { ' + inner.replace(/\n/g, ' ').replace(/\t/g, ' ') + ' }';
  });
  processed = processed.replace(/release_with_religion_and_culture\s*=\s*\{([^}]+)\}/gi, (m, inner) => {
    return 'release_with_religion_and_culture = { ' + inner.replace(/\n/g, ' ').replace(/\t/g, ' ') + ' }';
  });
  processed = processed.replace(/has_\d+_opinion_\w+\s*=\s*\{([^}]+)\}/gi, (m, inner) => {
    return m.match(/^(\w+)/)[1] + ' = { ' + inner.replace(/\n/g, ' ').replace(/\t/g, ' ') + ' }';
  });
  processed = processed.replace(/has_any_opinion_\w+\s*=\s*\{([^}]+)\}/gi, (m, inner) => {
    return m.match(/^(\w+)/)[1] + ' = { ' + inner.replace(/\n/g, ' ').replace(/\t/g, ' ') + ' }';
  });
  processed = processed.replace(/add_estate_influence_modifier\s*=\s*\{([^}]+)\}/gi, (m, inner) => {
    return 'add_estate_influence_modifier = { ' + inner.replace(/\n/g, ' ').replace(/\t/g, ' ') + ' }';
  });
  processed = processed.replace(/add_estate_loyalty_modifier\s*=\s*\{([^}]+)\}/gi, (m, inner) => {
    return 'add_estate_loyalty_modifier = { ' + inner.replace(/\n/g, ' ').replace(/\t/g, ' ') + ' }';
  });
  processed = processed.replace(/add_building_construction\s*=\s*\{([^}]+)\}/gi, (m, inner) => {
    return 'add_building_construction = { ' + inner.replace(/\n/g, ' ').replace(/\t/g, ' ') + ' }';
  });
  processed = processed.replace(/add_casus_belli\s*=\s*\{([^}]+)\}/gi, (m, inner) => {
    return 'add_casus_belli = { ' + inner.replace(/\n/g, ' ').replace(/\t/g, ' ') + ' }';
  });
  processed = processed.replace(/define_general\s*=\s*\{([^}]+)\}/gi, (m, inner) => {
    return 'define_general = { ' + inner.replace(/\n/g, ' ').replace(/\t/g, ' ') + ' }';
  });
  processed = processed.replace(/define_admiral\s*=\s*\{([^}]+)\}/gi, (m, inner) => {
    return 'define_admiral = { ' + inner.replace(/\n/g, ' ').replace(/\t/g, ' ') + ' }';
  });
  processed = processed.replace(/add_siberian_construction\s*=\s*(\d+)/gi, (m, v) => {
    return 'add_siberian_construction = ' + v;
  });
  // calc_true_if handled by collapseBlock above
  // Collapse nested blocks for specific keys using brace counting
  function collapseBlock(text, key) {
    const re = new RegExp(key + '\\s*=\\s*\\{', 'gi');
    let match;
    while ((match = re.exec(text)) !== null) {
      let start = match.index;
      let braceStart = text.indexOf('{', start + key.length);
      let depth = 1, i = braceStart + 1;
      while (i < text.length && depth > 0) {
        if (text[i] === '{') depth++;
        else if (text[i] === '}') depth--;
        i++;
      }
      const inner = text.substring(braceStart + 1, i - 1).replace(/\n/g, ' ').replace(/\t/g, ' ');
      const replacement = key + ' = { ' + inner + ' }';
      text = text.substring(0, start) + replacement + text.substring(i);
      re.lastIndex = start + replacement.length;
    }
    return text;
  }
  processed = collapseBlock(processed, 'num_of_owned_provinces_with');
  processed = collapseBlock(processed, 'calc_true_if');
  const lines = processed.split('\n');
  const results = [];
  let depth = 0;
  let skipDepth = -1; // when >= 0, skip all lines until depth returns to this level
  const SKIP_KEYS = new Set(['who', 'value', 'which', 'type', 'duration', 'name', 'amount', 'limit', 'ai', 'category', 'id', 'days', 'hidden', 'hidden_trigger', 'hidden_effect', 'skill', 'discount', 'female', 'fixed', 'advisor', 'max_random_dip', 'max_random_adm', 'max_random_mil', 'desc', 'influence', 'loyalty', 'fire', 'shock', 'manuever', 'siege', 'months', 'target']);
  // Track current scope (area/region/province) for context-aware claim handling
  const scopeStack = []; // [{name, type, depth}]

  for (let line of lines) {
    let trimmed = line.trim();
    if (!trimmed) continue;

    const opens = (trimmed.match(/\{/g) || []).length;
    const closes = (trimmed.match(/\}/g) || []).length;

    if (trimmed === '{') { depth++; if (skipDepth >= 0 && depth > skipDepth) { /* still skipping */ } continue; }
    if (trimmed === '}') { depth = Math.max(0, depth - 1); if (skipDepth >= 0 && depth <= skipDepth) skipDepth = -1; while (scopeStack.length && scopeStack[scopeStack.length-1].depth >= depth) scopeStack.pop(); continue; }

    // Update depth for this line
    const newDepth = depth + opens - closes;

    // If we're in a skip block, keep skipping
    if (skipDepth >= 0) { depth = Math.max(0, newDepth); continue; }

    if (trimmed.startsWith('#')) { depth = Math.max(0, newDepth); continue; }

    if (depth <= 3) {
      let m;
      if ((m = trimmed.match(/^(\w+)\s*=\s*(.+)$/))) {
        const key = m[1];
        const val = m[2].replace(/[{}]/g, '').trim();
        // Skip known nested/internal keys and their entire block
        if (SKIP_KEYS.has(key)) {
          if (opens > closes) { skipDepth = depth; }
          depth = Math.max(0, newDepth);
          continue;
        }
        // Handle NOT/OR/AND: only parse inline single-line conditions
        if (key === 'NOT' || key === 'OR' || key === 'AND') {
          const innerVal = val.trim();
          if (innerVal) {
            const im = innerVal.match(/^(\w+)\s*=\s*(.+)$/);
            if (im) {
              const innerReadable = triggerToText(im[1], im[2].trim());
              if (innerReadable) {
                if (key === 'NOT') {
                  // Integrate negation into the text
                  const negated = negateCondition(innerReadable.text);
                  results.push({ text: negated, type: innerReadable.type });
                } else {
                  if (key === 'OR') results.push({ text: 'One of the following:', type: 'logic' });
                  results.push(innerReadable);
                }
              }
            }
          } else {
            // Multi-line block: add label for OR/AND, skip NOT labels (they cause false grouping)
            // Suppress OR/AND inside area/region/superregion scopes (structural, not player choices)
            if (!scopeStack.length) {
              if (key === 'OR') results.push({ text: 'One of the following:', type: 'logic' });
              else if (key === 'AND') results.push({ text: 'All of the following:', type: 'logic' });
            }
            // Don't add "Must NOT:" for multi-line NOT blocks — too error-prone
          }
        } else {
          // Check if this is a scope-opening key (area/region/province)
          if ((key.endsWith('_area') || key.endsWith('_region') || key.endsWith('_superregion')) && opens > closes) {
            const sName = key.replace(/_area$|_region$|_superregion$/, '').replace(/_/g, ' ');
            const sType = key.endsWith('_area') ? 'area' : key.endsWith('_region') ? 'region' : 'superregion';
            scopeStack.push({name: sName, type: sType, depth: depth});
          } else if (/^\d+$/.test(key) && opens > closes) {
            scopeStack.push({name: provName(key), type: 'province', depth: depth, id: key});
          }
          // Handle add_permanent_claim = ROOT inside a scope
          // Handle scope-aware effects: when ROOT is used inside a province/area scope
          if (isScopeVar(val) && scopeStack.length) {
            const scope = scopeStack[scopeStack.length - 1];
            if (key === 'add_permanent_claim') {
              results.push({ text: `Gain permanent claims on <span class="tag">${esc(scope.name)}</span> (${scope.type})`, type: 'condition' });
              depth = Math.max(0, newDepth); continue;
            }
            if (key === 'add_core') {
              results.push({ text: `Gain cores on <span class="tag">${esc(scope.name)}</span> (${scope.type})`, type: 'condition' });
              depth = Math.max(0, newDepth); continue;
            }
            if (key === 'add_claim') {
              results.push({ text: `Gain claims on <span class="tag">${esc(scope.name)}</span> (${scope.type})`, type: 'condition' });
              depth = Math.max(0, newDepth); continue;
            }
            if (key === 'country_or_subject_holds' || key === 'country_or_non_sovereign_subject_holds') {
              results.push({ text: `You or subject own <span class="tag">${esc(scope.name)}</span>`, type: 'condition' });
              depth = Math.max(0, newDepth); continue;
            }
            if (key === 'owned_by') {
              results.push({ text: `Own <span class="tag">${esc(scope.name)}</span>`, type: 'condition' });
              depth = Math.max(0, newDepth); continue;
            }
            if (key === 'is_core') {
              results.push({ text: `<span class="tag">${esc(scope.name)}</span> is a core`, type: 'condition' });
              depth = Math.max(0, newDepth); continue;
            }
          }
          const readable = triggerToText(key, val);
          if (readable) results.push(readable);
        }
      } else if (trimmed === 'OR' || trimmed.startsWith('OR ') || trimmed === 'OR={') {
        results.push({ text: 'One of the following:', type: 'logic' });
      }
      // Don't add standalone NOT/AND labels — they cause false grouping
    }

    depth = Math.max(0, newDepth);
  }
  return results.slice(0, 15);
}

function negateCondition(text) {
  // Convert a condition to its negated form
  const stripped = text.replace(/<[^>]+>/g, '').toLowerCase();
  if (/country exists/i.test(text)) return text.replace(/Country exists/i, 'Country does not exist');
  if (/<span class="tag">([^<]+)<\/span> exists/.test(text)) return text.replace('exists', 'does not exist');
  if (/Have at least/i.test(text)) return text.replace(/Have at least/i, 'Have fewer than');
  if (/own /i.test(text)) return text.replace(/^You or subject own/i, 'Do not own or subject own').replace(/^Own/i, 'Do not own');
  if (/Be at war/i.test(text)) return 'Be at peace';
  if (/Be at peace/i.test(text)) return 'Be at war';
  if (/Average autonomy at least/i.test(text)) return text.replace(/Average autonomy at least/i, 'Average autonomy below');
  if (/at least/i.test(text) && !/Have at least/i.test(text)) return text.replace(/at least/i, 'below');
  if (/Control /i.test(text)) return text.replace(/^Control/i, 'Do not control');
  if (/Liberty desire at least/i.test(text)) return text.replace(/Liberty desire at least/i, 'Liberty desire below');
  // Generic fallback: just prefix with "NOT: "
  return 'Not: ' + text;
}

const SCOPE_VARS = new Set(['ROOT', 'FROM', 'PREV', 'THIS', 'root', 'from', 'prev', 'this']);
function tagName(tag) {
  const t = tag.trim();
  const c = DATA[t];
  return c ? c.name : t.replace(/_/g, ' ');
}
function resolveRef(v) {
  // Resolve a value that could be a country tag, province ID, or plain text
  const t = v.trim();
  if (isScopeVar(t)) return t;
  if (/^\d+$/.test(t)) return provName(t);
  if (DATA[t]) return DATA[t].name;
  return t.replace(/_/g, ' ');
}
function isScopeVar(v) { return SCOPE_VARS.has(v.trim()); }
function resolveProvOrTag(v) {
  const t = v.trim();
  if (isScopeVar(t)) return null; // suppress scope vars
  if (/^\d+$/.test(t)) return provName(t);
  return t.replace(/_/g, ' ');
}
function triggerToText(key, val) {
  const map = {
    'army_size': isScopeVar(val) ? null : (/^[A-Z][A-Z0-9]{1,2}$/.test(val) ? `Army size at least equal to <span class="tag">${tagName(val)}</span>` : `Have at least <span class="val">${val}</span> regiments`),
    'army_size_percentage': `Army at <span class="val">${(parseFloat(val)*100)}%</span> of force limit`,
    'navy_size_percentage': `Navy at <span class="val">${(parseFloat(val)*100)}%</span> of naval force limit`,
    'navy_size': `Have at least <span class="val">${val}</span> ships`,
    'manpower_percentage': `Manpower at <span class="val">${(parseFloat(val)*100)}%</span>`,
    'manpower': `Have at least <span class="val">${val}</span>k manpower`,
    'treasury': `Have at least <span class="val">${val}</span> ducats in treasury`,
    'years_of_income': `Have <span class="val">${val}</span> years of income saved`,
    'adm_power': `Have at least <span class="val">${val}</span> administrative power`,
    'dip_power': `Have at least <span class="val">${val}</span> diplomatic power`,
    'mil_power': `Have at least <span class="val">${val}</span> military power`,
    'stability': `Have at least <span class="val">${val}</span> stability`,
    'prestige': `Have at least <span class="val">${val}</span> prestige`,
    'legitimacy': `Have at least <span class="val">${val}</span> legitimacy`,
    'total_development': `Have at least <span class="val">${val}</span> total development`,
    'development': `Province has <span class="val">${val}</span> development`,
    'num_of_cities': isScopeVar(val) ? null : `Own at least <span class="val">${val}</span> provinces`,
    'grown_by_development': `Grown by <span class="val">${val}</span> development`,
    'grown_by_states': `Grown by <span class="val">${val}</span> states`,
    'army_tradition': `Have <span class="val">${val}</span> army tradition`,
    'navy_tradition': `Have <span class="val">${val}</span> navy tradition`,
    'adm_tech': `Admin tech at least <span class="val">${val}</span>`,
    'dip_tech': `Diplo tech at least <span class="val">${val}</span>`,
    'mil_tech': `Military tech at least <span class="val">${val}</span>`,
    'num_of_allies': `Have at least <span class="val">${val}</span> allies`,
    'num_of_subjects': `Have at least <span class="val">${val}</span> subjects`,
    'num_of_provinces_in_states': `Have <span class="val">${val}</span> stated provinces`,
    'num_of_provinces_owned_or_owned_by_non_sovereign_subjects_with': null, // complex nested, handled by tooltip
    'num_of_provinces_owned_or_owned_by_subjects_with': null, // complex nested
    'has_estate': null, // complex nested
    'is_at_war': val === 'no' ? 'Be at peace' : 'Be at war',
    'is_subject': val === 'no' ? 'Be independent (not a subject)' : 'Be a subject nation',
    'war_score': `Have <span class="val">${val}</span> war score`,
    'has_reform': `Have government reform: <span class="tag">${val}</span>`,
    'religion': isScopeVar(val) ? 'Follow our religion' : `Follow religion: <span class="tag">${val}</span>`,
    'tag': isScopeVar(val) ? null : `Be country: <span class="tag">${tagName(val)}</span>`,
    'owns': `Own province <span class="val" title="ID: ${val}">${/^\d+$/.test(val) ? provName(val) : val}</span>`,
    'owns_core_province': `Own and core province <span class="val" title="ID: ${val}">${/^\d+$/.test(val) ? provName(val) : val}</span>`,
    'num_of_merchants': `Have <span class="val">${val}</span> merchants`,
    'num_of_colonists': `Have <span class="val">${val}</span> colonists`,
    'num_of_missionaries': `Have <span class="val">${val}</span> missionaries`,
    'land_forcelimit': `Force limit at least <span class="val">${val}</span>`,
    'monthly_income': /^[A-Z][A-Z0-9]{1,2}$/.test(val) ? `Monthly income at least equal to <span class="tag">${tagName(val)}</span>` : `Monthly income at least <span class="val">${val}</span>`,
    'mercantilism': `Mercantilism at least <span class="val">${val}</span>`,
    'innovativeness': `Innovativeness at least <span class="val">${val}</span>`,
    'government_reform_progress': `Government reform progress at least <span class="val">${val}</span>`,
    'reform_level': `Reform level at least <span class="val">${val}</span>`,
    'corruption': `Corruption below <span class="val">${val}</span>`,
    'inflation': val === '1' ? 'Have no inflation' : `Inflation below <span class="val">${val}</span>`,
    'overextension_percentage': `Overextension below <span class="val">${(parseFloat(val)*100)}%</span>`,
    'has_country_flag': `Has country flag: <span class="tag">${val.replace(/_/g, ' ')}</span>`,
    'has_global_flag': `Global flag set: <span class="tag">${val}</span>`,
    'government_rank': `Government rank at least <span class="val">${val}</span>`,
    'total_own_and_non_tributary_subject_development': `Total dev (with subjects) at least <span class="val">${val}</span>`,
    'production_leader': `Be production leader in: <span class="tag">${val}</span>`,
    'diplomatic_reputation': `Diplomatic reputation at least <span class="val">${val}</span>`,
    'power_projection': `Power projection at least <span class="val">${val}</span>`,
    'religious_unity': `Religious unity at least <span class="val">${(parseFloat(val)*100)}%</span>`,
    'average_autonomy_above_min': `Average autonomy above <span class="val">${val}</span>`,
    'culture_group': `Culture group: <span class="tag">${val}</span>`,
    'primary_culture': `Primary culture: <span class="tag">${val}</span>`,
    'has_ruler_modifier': `Ruler has modifier: <span class="tag">${val}</span>`,
    'has_country_modifier': (() => { return `Has modifier: ${modRef(val.trim())}`; })(),
    'is_core': isScopeVar(val) ? null : `Is a core of <span class="tag">${tagName(val)}</span>`,
    'owned_by': isScopeVar(val) ? null : `Owned by <span class="tag">${tagName(val)}</span>`,
    'controlled_by': isScopeVar(val) ? 'Controlled by us' : `Controlled by <span class="tag">${tagName(val)}</span>`,
    'has_building': `Has building: <span class="tag">${val}</span>`,
    'base_tax': `Base tax at least <span class="val">${val}</span>`,
    'base_production': `Base production at least <span class="val">${val}</span>`,
    'base_manpower': `Base manpower at least <span class="val">${val}</span>`,
    'trade_goods': `Produces: <span class="tag">${val}</span>`,
    'num_of_generals': `Have at least <span class="val">${val}</span> generals`,
    'num_of_admirals': `Have at least <span class="val">${val}</span> admirals`,
    'num_of_heavy_ship': `Have at least <span class="val">${val}</span> heavy ships`,
    'num_of_light_ship': `Have at least <span class="val">${val}</span> light ships`,
    'num_of_galley': `Have at least <span class="val">${val}</span> galleys`,
    'num_of_transport': `Have at least <span class="val">${val}</span> transports`,
    'employed_advisor': `Have employed advisor: <span class="tag">${val === 'yes' ? 'any' : val.replace(/category\s*=\s*/i, '').replace('ADM', 'Administrative').replace('DIP', 'Diplomatic').replace('MIL', 'Military')}</span>`,
    'has_construction': `Currently constructing <span class="tag">${val.replace(/_/g, ' ')}</span> buildings`,
    'has_advisor': `Have advisor: <span class="tag">${val}</span>`,
    'num_of_cavalry': `Have at least <span class="val">${val}</span> cavalry`,
    'num_of_infantry': `Have at least <span class="val">${val}</span> infantry`,
    'num_of_artillery': isScopeVar(val) ? null : `Have at least <span class="val">${val}</span> artillery`,
    'has_idea_group': `Have idea group: <span class="tag">${val.replace(/_/g, ' ')}</span>`,
    'full_idea_group': `Completed idea group: <span class="tag">${val.replace(/_/g, ' ')}</span>`,
    // Subjects & diplomacy
    'num_of_non_tributary_subjects': `Have at least <span class="val">${val}</span> non-tributary subjects`,
    'num_of_royal_marriages': `Have at least <span class="val">${val}</span> royal marriages`,
    'country_or_non_sovereign_subject_holds': isScopeVar(val) ? null : `You or subject own <span class="val" title="ID: ${val}">${/^\d+$/.test(val) ? provName(val) : val}</span>`,
    'country_or_subject_holds': isScopeVar(val) ? null : `You or subject own <span class="val" title="ID: ${val}">${/^\d+$/.test(val) ? provName(val) : tagName(val)}</span>`,
    'share_of_starting_income': `Income at <span class="val">${(parseFloat(val)*100)}%</span> of starting income`,
    // Estate & privileges
    'estate_loyalty': (() => { const em = val.match(/estate\s*=\s*estate_(\w+)/); const lm = val.match(/loyalty\s*=\s*(\d+)/); return (em && lm) ? `${em[1].replace(/_/g, ' ')} loyalty at least <span class="val">${lm[1]}</span>` : null; })(),
    'estate_influence': (() => { const em = val.match(/estate\s*=\s*estate_(\w+)/); const im = val.match(/influence\s*=\s*(\d+)/); return (em && im) ? `${em[1].replace(/_/g, ' ')} influence at least <span class="val">${im[1]}</span>` : null; })(),
    'add_estate_influence_modifier': (() => { const em = val.match(/estate\s*=\s*estate_(\w+)/); const im = val.match(/influence\s*=\s*(-?\d+)/); if (em && im) return `Add <span class="val">${im[1]}</span> ${em[1].replace(/_/g, ' ')} estate influence`; return null; })(),
    'add_estate_loyalty_modifier': (() => { const em = val.match(/estate\s*=\s*estate_(\w+)/); const lm = val.match(/loyalty\s*=\s*(-?\d+)/); if (em && lm) return `Add <span class="val">${lm[1]}</span> ${em[1].replace(/_/g, ' ')} estate loyalty`; return null; })(),
    'has_estate_privilege': `Have estate privilege: <span class="tag">${val.replace(/_/g, ' ')}</span>`,
    // Building triggers
    'has_tax_building_trigger': val === 'yes' ? 'Has a tax building (temple/cathedral)' : 'No tax building',
    'has_production_building_trigger': val === 'yes' ? 'Has a production building (workshop/counting house)' : 'No production building',
    'has_trade_building_trigger': val === 'yes' ? 'Has a trade building (marketplace/trade depot)' : 'No trade building',
    'has_manpower_building_trigger': val === 'yes' ? 'Has a manpower building (barracks/training fields)' : 'No manpower building',
    'has_fort_building_trigger': val === 'yes' ? 'Has a fort' : 'No fort',
    'has_dock_building_trigger': val === 'yes' ? 'Has a dock building' : 'No dock building',
    'has_shipyard_building_trigger': val === 'yes' ? 'Has a shipyard building' : 'No shipyard building',
    'has_port': val === 'yes' ? 'Has a port' : 'Has no port',
    'light_ships_in_province': `Has at least <span class="val">${val}</span> light ships in province`,
    'num_of_owned_provinces_with': (() => {
      const vm = val.match(/value\s*=\s*(\d+)/);
      const count = vm ? vm[1] : '?';
      // Extract meaningful conditions from the block
      const conditions = [];
      const tgMatches = val.matchAll(/trade_goods\s*=\s*(\w+)/g);
      const goods = new Set();
      for (const tg of tgMatches) goods.add(tg[1].replace(/_/g, ' '));
      if (goods.size) conditions.push('produces ' + [...goods].join(' or '));
      if (/has_building\s*=\s*(\w+)/.test(val)) conditions.push('has ' + val.match(/has_building\s*=\s*(\w+)/)[1].replace(/_/g, ' '));
      if (/culture\s*=\s*(\w+)/.test(val) && !/culture_group/.test(val)) { const cv = val.match(/culture\s*=\s*(\w+)/)[1]; if (cv === 'ROOT') conditions.push('our culture'); else conditions.push('culture: ' + cv.replace(/_/g, ' ')); }
      if (/culture_group\s*=\s*(\w+)/.test(val)) { const cv = val.match(/culture_group\s*=\s*(\w+)/)[1]; if (cv === 'ROOT') conditions.push('our culture group'); else conditions.push('culture group: ' + cv.replace(/_/g, ' ')); }
      if (/religion\s*=\s*(\w+)/.test(val)) { const rv = val.match(/religion\s*=\s*(\w+)/)[1]; if (rv === 'ROOT') conditions.push('our religion'); else conditions.push('religion: ' + rv.replace(/_/g, ' ')); }
      if (/has_\w+_minority_trigger/.test(val)) { const mm = val.match(/has_(\w+)_minority_trigger/); if (mm) conditions.push('has ' + mm[1].replace(/_/g, ' ') + ' minority'); }
      if (/development\s*=\s*(\d+)/.test(val)) conditions.push('at least ' + val.match(/development\s*=\s*(\d+)/)[1] + ' development');
      if (/base_production\s*=\s*(\d+)/.test(val)) conditions.push('base production ≥ ' + val.match(/base_production\s*=\s*(\d+)/)[1]);
      if (/has_port\s*=\s*yes/.test(val)) conditions.push('has a port');
      if (/is_city\s*=\s*yes/.test(val)) conditions.push('is a city');
      if (/region\s*=\s*(\w+)/.test(val)) { const rm = val.match(/region\s*=\s*(\w+)/); conditions.push('in ' + rm[1].replace(/_/g, ' ')); }
      if (/area\s*=\s*(\w+)/.test(val)) { const am = val.match(/area\s*=\s*(\w+)/); conditions.push('in ' + am[1].replace(/_/g, ' ')); }
      if (/has_supply_depot\s*=\s*(\w+)/.test(val)) conditions.push('has supply depot');
      if (/has_manpower_building_trigger/.test(val)) conditions.push('has manpower building');
      if (/has_production_building_trigger/.test(val)) conditions.push('has production building');
      if (/has_tax_building_trigger/.test(val)) conditions.push('has tax building');
      if (/has_trade_building_trigger/.test(val)) conditions.push('has trade building');
      if (/has_forcelimit_building_trigger/.test(val)) conditions.push('has forcelimit building');
      if (/province_has_center_of_trade_of_level\s*=\s*(\d+)/.test(val)) conditions.push('center of trade level ≥ ' + val.match(/province_has_center_of_trade_of_level\s*=\s*(\d+)/)[1]);
      if (/fort_level\s*=\s*(\d+)/.test(val)) conditions.push('fort level ≥ ' + val.match(/fort_level\s*=\s*(\d+)/)[1]);
      const condStr = conditions.length ? ' (' + conditions.join(', ') + ')' : '';
      return `Own at least <span class="val">${count}</span> provinces${condStr}`;
    })(),
    'num_of_estate_agendas_completed': (() => { const em = val.match(/estate\s*=\s*estate_(\w+)/); const vm = val.match(/value\s*=\s*(\d+)/); return (em && vm) ? `Have completed <span class="val">${vm[1]}</span> ${em[1].replace(/_/g, ' ')} estate agendas` : null; })(),
    'num_of_estate_privileges': (() => { const em = val.match(/estate\s*=\s*estate_(\w+)/); const vm = val.match(/value\s*=\s*(\d+)/); return (em && vm) ? `Have at least <span class="val">${vm[1]}</span> ${em[1].replace(/_/g, ' ')} estate privileges` : null; })(),
    // Province conditions
    'culture': `Culture is: <span class="tag">${val.replace(/_/g, ' ')}</span>`,
    'culture_group_claim': `Culture group claim on: <span class="tag">${val.replace(/_/g, ' ')}</span>`,
    'has_discovered': isScopeVar(val) ? 'Has been discovered' : `Has discovered <span class="val">${/^\d+$/.test(val) ? provName(val) : val}</span>`,
    'capital_scope': 'In capital province:',
    // Date & time
    'is_year': `Year is at least <span class="val">${val}</span>`,
    'is_month': `Month is at least <span class="val">${val}</span>`,
    // Country state
    'is_emperor': val === 'yes' ? 'Be the Emperor of the HRE' : 'Not be the Emperor',
    'is_elector': val === 'yes' ? 'Be an HRE Elector' : 'Not be an Elector',
    'is_part_of_hre': val === 'yes' ? 'Be part of the HRE' : 'Not be part of the HRE',
    'hre_size': `HRE has at least <span class="val">${val}</span> members`,
    'is_great_power': val === 'yes' ? 'Be a Great Power' : 'Not be a Great Power',
    'is_colonial_nation': val === 'yes' ? 'Be a colonial nation' : 'Not be a colonial nation',
    'is_tribal': val === 'yes' ? 'Be tribal' : 'Not be tribal',
    'is_nomad': val === 'yes' ? 'Be nomadic' : 'Not be nomadic',
    'is_free_or_tributary_trigger': val === 'yes' ? 'Be independent or tributary' : '',
    'is_in_deficit': val === 'no' ? 'Not be running a deficit' : 'Be running a deficit',
    'is_rival': isScopeVar(val) ? null : `Be rivaled with <span class="tag">${tagName(val)}</span>`,
    'is_neighbor_of': isScopeVar(val) ? null : `Be a neighbor of <span class="tag">${tagName(val)}</span>`,
    'is_strongest_trade_power': isScopeVar(val) ? null : `Be the strongest trade power in <span class="tag">${val.replace(/_/g, ' ')}</span>`,
    'is_prosperous': val === 'yes' ? 'Province is prosperous' : 'Province is not prosperous',
    'is_state_core': isScopeVar(val) ? null : `Is a state core`,
    'is_state': val === 'yes' ? 'Is a full state' : null,
    'is_capital': val === 'yes' ? 'Is the capital' : null,
    'is_empty': val === 'yes' ? 'Province is empty/uncolonized' : 'Province is colonized',
    'is_city': val === 'yes' ? 'Is a city (colonized)' : null,
    'is_colony': val === 'yes' ? 'Is a colony' : null,
    'is_revolutionary': val === 'yes' ? 'Be revolutionary' : 'Not be revolutionary',
    'is_hegemon': val === 'yes' ? 'Be a hegemon' : null,
    'is_emperor_of_china': val === 'yes' ? 'Be the Emperor of China' : null,
    'is_ahead_of_time_in_technology': val === 'yes' ? 'Be ahead of time in technology' : null,
    'is_institution_enabled': `Institution <span class="tag">${val.replace(/_/g, ' ')}</span> is enabled`,
    'is_religion_enabled': `Religion <span class="tag">${val.replace(/_/g, ' ')}</span> is enabled`,
    'is_colonial_nation_of': isScopeVar(val) ? null : `Be a colonial nation of <span class="tag">${tagName(val)}</span>`,
    'is_the_raja': val === 'yes' ? 'Be the Raja' : null,
    'government': `Have government type: <span class="tag">${val.replace(/_/g, ' ')}</span>`,
    'technology_group': `Technology group: <span class="tag">${val.replace(/_/g, ' ')}</span>`,
    'exists': val === 'yes' ? 'Country exists' : val === 'no' ? null : `<span class="tag">${tagName(val)}</span> exists`,
    // War & military
    'is_in_war': val === 'no' ? 'Be at peace' : 'Be at war',
    'war_exhaustion': `War exhaustion below <span class="val">${val}</span>`,
    'num_of_rebel_armies': `Have <span class="val">${val}</span> rebel armies`,
    'num_of_rebel_controlled_provinces': `Have <span class="val">${val}</span> rebel-controlled provinces`,
    'alliance_with': isScopeVar(val) ? null : `Be allied with <span class="tag">${tagName(val)}</span>`,
    'marriage_with': isScopeVar(val) ? null : `Have royal marriage with <span class="tag">${tagName(val)}</span>`,
    'truce_with': isScopeVar(val) ? null : `Have truce with <span class="tag">${tagName(val)}</span>`,
    'has_casus_belli_against': isScopeVar(val) ? null : `Have CB against <span class="tag">${tagName(val)}</span>`,
    // Trade
    'trading_part': `Trading part: <span class="val">${val}</span>`,
    'trade_share': `Trade share at least <span class="val">${val}</span>`,
    // Misc
    'calc_true_if': (() => { const am = val.match(/amount\s*=\s*(\d+)/); return am ? `At least <span class="val">${am[1]}</span> of the following:` : `At least <span class="val">${val}</span> of the following:`; })(),
    'any_owned_province': 'Any owned province:',
    'all_owned_province': 'All owned provinces:',
    'any_known_country': 'Any known country:',
    'any_ally': 'Any ally:',
    'any_neighbor_country': 'Any neighbor:',
    'any_subject_country': 'Any subject:',
    'has_disaster': `Has active disaster: <span class="tag">${val.replace(/_/g, ' ')}</span>`,
    'has_institution': `Has embraced institution: <span class="tag">${val.replace(/_/g, ' ')}</span>`,
    'has_great_project': (() => { const pm = val.match(/type\s*=\s*(\w+)/); const tm = val.match(/tier\s*=\s*(\d+)/); if (pm) { const name = pm[1].replace(/_/g, ' '); return `Has great project <span class="tag">${name}</span>${tm ? ' (tier ' + tm[1] + '+)' : ''}`; } return `Has a great project: <span class="tag">${val.replace(/_/g, ' ')}</span>`; })(),
    'has_manufactory_trigger': val === 'yes' ? 'Has a manufactory' : 'No manufactory',
    'has_courthouse_building_trigger': val === 'yes' ? 'Has a courthouse or town hall' : 'No courthouse',
    'has_forcelimit_building_trigger': val === 'yes' ? 'Has a forcelimit building' : 'No forcelimit building',
    'has_production_or_gold_building_trigger': val === 'yes' ? 'Has a production or gold building' : null,
    'has_terrain': `Terrain is: <span class="tag">${val.replace(/_/g, ' ')}</span>`,
    'has_province_modifier': `Has province modifier: <span class="tag">${val.replace(/_/g, ' ')}</span>`,
    'has_spy_network_from': null, // complex scope
    'has_spy_network_in': null, // complex scope
    'has_any_ongoing_construction': val === 'yes' ? 'Has ongoing construction' : null,
    'has_state_edict': `Has state edict: <span class="tag">${val.replace(/_/g, ' ')}</span>`,
    'has_personal_deity': `Worships: <span class="tag">${val.replace(/_/g, ' ')}</span>`,
    'has_seat_in_parliament': val === 'yes' ? 'Has a seat in parliament' : null,
    'has_government_power': (() => { const mm = val.match(/mechanic_type\s*=\s*(\w+)/); const vm = val.match(/power_type\s*=\s*(\w+)/); return mm ? `Has government mechanic power` : null; })(),
    'has_dwarven_hold_4': val === 'yes' ? 'Has a level 4 dwarven hold' : null,
    'army_professionalism': `Army professionalism at least <span class="val">${(parseFloat(val)*100).toFixed(0)}%</span>`,
    'max_years_since': (() => { const ym = val.match(/years\s*=\s*(\d+)/); return ym ? `Within the last <span class="val">${ym[1]}</span> years` : null; })(),
    'all_known_country': 'All known countries:',
    'has_dlc': null, // hide DLC checks
    'normal_or_historical_nations': null,
    'controls': isScopeVar(val) ? null : `Control <span class="val" title="ID: ${val}">${resolveRef(val)}</span>`,
    'is_subject_of': isScopeVar(val) ? null : `Be subject of <span class="tag">${tagName(val)}</span>`,
    'is_subject_of_type': `Be subject of type: <span class="tag">${val.replace(/_/g, ' ')}</span>`,
    'liberty_desire': `Liberty desire at least <span class="val">${val}</span>`,
    'add_building': `Build <span class="tag">${val.replace(/_/g, ' ')}</span>`,
    'remove_building': `Remove building: <span class="tag">${val.replace(/_/g, ' ')}</span>`,
    'num_of_missionaries': `Have at least <span class="val">${val}</span> missionaries`,
    'num_of_diplomats': `Have at least <span class="val">${val}</span> diplomats`,
    'has_missionary': val === 'yes' ? 'Have an available missionary' : null,
    'has_country_flag': null, // internal flags, not useful to player
    'had_country_flag': null,
    'has_province_flag': null,
    'has_global_flag': null,
    'has_ruler_flag': null,
    'units_in_province': null, // complex nested, not useful standalone
    'num_of_units_in_province': null, // complex nested
    'amount': null, // nested param
    'who': null, // nested param
    'advisor': null, // nested inside employed_advisor
    'factor': null, // nested weight
    'ai_will_do': null, // internal AI logic
    'remove_country_modifier': (() => { const mk = val.trim(); return `Remove modifier: ${modRef(mk)}`; })(),
    'owns_or_non_sovereign_subject_of': isScopeVar(val) ? null : `You or subject own <span class="val" title="ID: ${val}">${/^\d+$/.test(val) ? provName(val) : val}</span>`,
    'owns_or_subject_of': isScopeVar(val) ? null : `You or subject own <span class="val" title="ID: ${val}">${/^\d+$/.test(val) ? provName(val) : val}</span>`,
    'war_with': null, // internal scope, not useful standalone
    'owner': null, // internal scope
    'trade_share': `Trade share at least <span class="val">${val}</span>`,
    'share': null, // nested value inside trade_share
    'region': `In region: <span class="tag">${val.replace(/_/g, ' ').replace(/ region$/, '')}</span>`,
    'area': `In area: <span class="tag">${val.replace(/_/g, ' ').replace(/ area$/, '')}</span>`,
    'superregion': `In superregion: <span class="tag">${val.replace(/_/g, ' ').replace(/ superregion$/, '')}</span>`,
    'continent': `On continent: <span class="tag">${val.replace(/_/g, ' ')}</span>`,
    'loyalty': null, // nested inside estate block
    'estate': null, // nested
    // Common EFFECTS
    'add_legitimacy_or_monarch_power': `Add <span class="val">${val.replace(/VAL\s*=\s*/i, '').replace(/[{}]/g, '').trim()}</span> legitimacy (or republican tradition / devotion / horde unity)`,
    'add_stability': `Add <span class="val">${val}</span> stability`,
    'add_prestige': `Add <span class="val">${val}</span> prestige`,
    'add_adm_power': `Add <span class="val">${val}</span> admin power`,
    'add_dip_power': `Add <span class="val">${val}</span> diplo power`,
    'add_mil_power': `Add <span class="val">${val}</span> military power`,
    'add_treasury': `Add <span class="val">${val}</span> ducats`,
    'add_manpower': `Add <span class="val">${val}</span> manpower`,
    'add_sailors': `Add <span class="val">${val}</span> sailors`,
    'add_army_tradition': `Add <span class="val">${val}</span> army tradition`,
    'add_navy_tradition': `Add <span class="val">${val}</span> navy tradition`,
    'add_mercantilism': `Add <span class="val">${val}</span> mercantilism`,
    'add_innovativeness_small_effect': 'Add small innovativeness',
    'add_innovativeness_big_effect': 'Add large innovativeness',
    'add_legitimacy': `Add <span class="val">${val}</span> legitimacy`,
    'add_republican_tradition': `Add <span class="val">${val}</span> republican tradition`,
    'add_devotion': `Add <span class="val">${val}</span> devotion`,
    'add_horde_unity': `Add <span class="val">${val}</span> horde unity`,
    'add_meritocracy': `Add <span class="val">${val}</span> meritocracy`,
    'add_war_exhaustion': `Add <span class="val">${val}</span> war exhaustion`,
    'add_corruption': `Add <span class="val">${val}</span> corruption`,
    'add_inflation': `Add <span class="val">${val}</span> inflation`,
    'add_splendor': `Add <span class="val">${val}</span> splendor`,
    'add_absolutism': `Add <span class="val">${val}</span> absolutism`,
    'add_reform_progress_small_effect': 'Add small reform progress',
    'add_reform_progress_big_effect': 'Add large reform progress',
    'change_government_reform_progress': `Change government reform progress: <span class="val">${val}</span>`,
    'add_government_reform_progress': `Add <span class="val">${val}</span> government reform progress`,
    'add_country_modifier': (() => { const mk = extractModKey(val); return `Add modifier: ${modRef(mk)}`; })(),
    'add_permanent_claim': isScopeVar(val) ? null : `Add permanent claim on <span class="val" title="ID: ${val}">${resolveRef(val)}</span>`,
    'add_claim': isScopeVar(val) ? null : `Add claim on <span class="val" title="ID: ${val}">${resolveRef(val)}</span>`,
    'add_core': isScopeVar(val) ? null : `Add core on <span class="val" title="ID: ${val}">${resolveRef(val)}</span>`,
    'add_base_tax': `Add <span class="val">${val}</span> base tax`,
    'add_base_production': `Add <span class="val">${val}</span> base production`,
    'add_base_manpower': `Add <span class="val">${val}</span> base manpower`,
    'change_government': `Change government to: <span class="tag">${val.replace(/_/g, ' ')}</span>`,
    'change_tag': `Form country: <span class="tag">${tagName(val)}</span>`,
    'change_religion': isScopeVar(val) ? 'Change religion to ours' : `Change religion to: <span class="tag">${val.replace(/_/g, ' ')}</span>`,
    'change_culture': isScopeVar(val) ? 'Change culture to ours' : `Change culture to: <span class="tag">${val.replace(/_/g, ' ')}</span>`,
    'change_primary_culture': isScopeVar(val) ? null : `Change primary culture to: <span class="tag">${val.replace(/_/g, ' ')}</span>`,
    'add_accepted_culture': `Accept culture: <span class="tag">${val.replace(/_/g, ' ')}</span>`,
    'remove_accepted_culture': `Remove accepted culture: <span class="tag">${val.replace(/_/g, ' ')}</span>`,
    'add_government_reform': `Add government reform: <span class="tag">${val.replace(/_/g, ' ')}</span>`,
    'set_government_rank': `Set government rank to <span class="val">${val}</span>`,
    'add_casus_belli': (() => { const tm = val.match(/target\s*=\s*(\w+)/); const tgt = tm ? tagName(tm[1]) : val.replace(/[{}]/g, '').replace(/_/g, ' ').trim(); return `Gain casus belli against <span class="tag">${tgt}</span>`; })(),
    'create_subject': `Create subject: <span class="tag">${val.replace(/[{}]/g, '').replace(/_/g, ' ').trim()}</span>`,
    'vassalize': isScopeVar(val) ? null : `Vassalize: <span class="tag">${tagName(val)}</span>`,
    'inherit': isScopeVar(val) ? null : `Inherit: <span class="tag">${tagName(val)}</span>`,
    'add_historical_friend': isScopeVar(val) ? null : `Add historical friend: <span class="tag">${tagName(val)}</span>`,
    'add_trust': `Add <span class="val">${val.replace(/[{}]/g, '').trim()}</span> trust`,
    'define_advisor': 'Gain a new advisor',
    'define_general': 'Gain a new general',
    'define_admiral': 'Gain a new admiral',
    'create_general': 'Gain a new general',
    'create_admiral': 'Gain a new admiral',
    'add_patriarch_authority': `Add <span class="val">${(parseFloat(val)*100).toFixed(0)}%</span> patriarch authority`,
    'add_ruler_modifier': (() => { const mk = extractModKey(val); return `Add ruler modifier: ${modRef(mk)}`; })(),
    'add_province_modifier': (() => { const mk = extractModKey(val); return `Add province modifier: ${modRef(mk)}`; })(),
    'remove_province_modifier': (() => { const mk = val.trim(); return `Remove province modifier: ${modRef(mk)}`; })(),
    'add_disaster_progress': `Add disaster progress: <span class="tag">${val.replace(/[{}]/g, '').replace(/_/g, ' ').trim()}</span>`,
    'add_permanent_province_modifier': (() => { const mk = extractModKey(val); return `Add permanent province modifier: ${modRef(mk)}`; })(),
    'country_event': 'Triggers an event',
    'province_event': 'Triggers a province event',
    'every_owned_province': 'Every owned province:',
    'random_owned_province': 'Random owned province:',
    'capital_scope': 'In capital:',
    'every_neighbor_country': 'Every neighbor:',
    'every_subject_country': 'Every subject:',
    'every_known_country': 'Every known country:',
    'cede_province': isScopeVar(val) ? null : `Cede province to <span class="tag">${tagName(val)}</span>`,
    'create_march': isScopeVar(val) ? null : `Create march: <span class="tag">${tagName(val)}</span>`,
    'create_vassal': isScopeVar(val) ? null : `Create vassal: <span class="tag">${tagName(val)}</span>`,
    'release': isScopeVar(val) ? null : `Release: <span class="tag">${tagName(val)}</span>`,
    'white_peace': isScopeVar(val) ? null : `White peace with <span class="tag">${tagName(val)}</span>`,
    'add_opinion': null, // complex nested, skip
    'has_opinion': null, // complex nested, skip
    'has_opinion_modifier': null,
    'reverse_add_opinion': null,
    'add_devastation': `Add <span class="val">${val}</span> devastation`,
    'add_random_development': `Add <span class="val">${val}</span> random development`,
    'add_army_professionalism': `Add <span class="val">${(parseFloat(val)*100).toFixed(0)}%</span> army professionalism`,
    'add_yearly_manpower': `Add <span class="val">${val}</span> years of manpower`,
    'add_years_of_income': `Add <span class="val">${val}</span> years of income`,
    'add_power_projection': (() => { const am = val.match(/amount\s*=\s*(-?\d+)/); return am ? `Add <span class="val">${am[1]}</span> power projection` : (!/\{/.test(val) ? `Add <span class="val">${val}</span> power projection` : null); })(),
    'add_papal_influence': `Add <span class="val">${val}</span> papal influence`,
    'add_church_power': `Add <span class="val">${val}</span> church power`,
    'add_fervor': `Add <span class="val">${val}</span> fervor`,
    'add_karma': `Add <span class="val">${val}</span> karma`,
    'add_harmony': `Add <span class="val">${val}</span> harmony`,
    'add_doom': `Add <span class="val">${val}</span> doom`,
    'add_authority': `Add <span class="val">${val}</span> authority`,
    'add_liberty_desire': `Add <span class="val">${val}</span> liberty desire`,
    'add_local_autonomy': `Add <span class="val">${val}</span> local autonomy`,
    'great_power_rank': `Be a top <span class="val">${val}</span> Great Power`,
    'add_prosperity': `Add <span class="val">${val}</span> prosperity`,
    'add_unrest': `Add <span class="val">${val}</span> unrest`,
    'add_colonysize': `Add <span class="val">${val}</span> colony growth`,
    'is_permanent_claim': isScopeVar(val) ? null : `Is permanent claim of <span class="tag">${tagName(val)}</span>`,
    'add_nationalism': `Add <span class="val">${val}</span> years of separatism`,
    'add_center_of_trade_level': `Add <span class="val">${val}</span> center of trade level`,
    'center_of_trade': `Center of trade level <span class="val">${val}</span>`,
    'province_has_center_of_trade_of_level': `Has center of trade level <span class="val">${val}</span>`,
    'swap_non_generic_missions': null,
    'swap_free_idea_group': null,
    'add_liberty_desire_effect': `Add <span class="val">${val}</span> liberty desire`,
    'add_country_modifier_effect': null, // handled by add_country_modifier
    'set_in_empire': null, // internal HRE flag
    'add_opinion_modifier': null, // complex nested
    'add_accepted_culture_or_culture_group_effect': 'Accept a culture group',
    'has_spy_network_in': null, // complex nested
    'owned_by_friendly_nation': null, // complex internal check
    // Suppress internal/complex nested entries
    'dynasty': null, // nested in define_ruler
    'female': null,
    'adm': null,
    'dip': null,
    'mil': null,
    'culture': null, // too many contexts
    'sign': null,
    'var': null,
    'effect': null, // nested
    'first': null, // nested conditional
    'second': null,
    'third': null,
    'influence': null, // estate influence nested
    'territory': null, // nested
    'mutual': null, // nested in add_trust
    'grown_by': null, // internal
    'variable_arithmetic_trigger': null,
    'province_is_on_an_island': null, // island exclusion clause in ownership triggers
    'set_country_flag': null, // internal game flag
    'set_province_flag': null, // internal game flag
    'set_global_flag': null, // internal game flag
    'clr_country_flag': null, // internal game flag
    'clr_province_flag': null, // internal game flag
    'has_country_flag': null, // internal game flag
    'has_province_flag': null, // internal game flag
    'custom_trigger_tooltip': null,
    'is_subject_of_type_with_overlord': (() => { const tm = val.match(/type\s*=\s*(\w+)/); const wm = val.match(/who\s*=\s*(\w+)/); const tLabel = tm ? tm[1].replace(/_/g, ' ') : 'subject'; if (wm && !isScopeVar(wm[1])) return `Is ${tLabel} of <span class="tag">${tagName(wm[1])}</span>`; return `Is a ${tLabel}`; })(),
    'check_variable': (() => { const wm = val.match(/which\s*=\s*(\w+)/); const vm = val.match(/value\s*=\s*(\d+)/); if (wm && vm) return `${wm[1].replace(/_/g, ' ')} at least <span class="val">${vm[1]}</span>`; return null; })(),
    'num_of_hussars': /^\d+$/.test(val) ? `Have at least <span class="val">${val}</span> hussars` : null,
    'num_of_artillery': /^\d+$/.test(val) ? `Have at least <span class="val">${val}</span> artillery` : null,
    'num_of_cavalry': /^\d+$/.test(val) ? `Have at least <span class="val">${val}</span> cavalry` : null,
    'num_of_infantry': /^\d+$/.test(val) ? `Have at least <span class="val">${val}</span> infantry` : null,
    'num_of_heavy_ship': /^\d+$/.test(val) ? `Have at least <span class="val">${val}</span> heavy ships` : null,
    'num_of_light_ship': /^\d+$/.test(val) ? `Have at least <span class="val">${val}</span> light ships` : null,
    'num_of_galley': /^\d+$/.test(val) ? `Have at least <span class="val">${val}</span> galleys` : null,
    'num_of_transport': /^\d+$/.test(val) ? `Have at least <span class="val">${val}</span> transports` : null,
    'has_global_modifier_value': (() => { const wm = val.match(/which\s*=\s*(\w+)/); const vm = val.match(/value\s*=\s*([\d.]+)/); if (wm && vm) return `${wm[1].replace(/_/g, ' ')} at least <span class="val">${vm[1]}</span>`; return null; })(),
    'development_in_provinces': (() => { const vm = val.match(/value\s*=\s*(\d+)/); if (vm) return `Development in provinces at least <span class="val">${vm[1]}</span>`; return null; })(),
    'birth_date': null,
    'monarch_name': null,
    'kill_ruler': null,
    'kill_heir': null,
    'age': null,
    'claim': null, // nested param in some contexts
    'regent': null,
    'trust': (() => { const wm = val.match(/who\s*=\s*(\w+)/); const vm = val.match(/value\s*=\s*(-?\d+)/); if (wm && vm) { if (isScopeVar(wm[1])) return `Trust at least <span class="val">${vm[1]}</span>`; return `Trust with <span class="tag">${tagName(wm[1])}</span> at least <span class="val">${vm[1]}</span>`; } return isScopeVar(val) ? null : `Trust at least <span class="val">${val}</span>`; })(),
    'add_trust': (() => { const wm = val.match(/who\s*=\s*(\w+)/); const vm = val.match(/value\s*=\s*(-?\d+)/); if (wm && vm) { if (isScopeVar(wm[1])) return `Add <span class="val">${vm[1]}</span> trust`; return `Add <span class="val">${vm[1]}</span> trust with <span class="tag">${tagName(wm[1])}</span>`; } return null; })(),
    'release_with_religion_and_culture': null, // complex internal effect
    'create_iosahar': null, // internal effect
    'has_20_opinion_sent_gift': null, // complex nested trigger
    'has_80_opinion_improved_relation': null, // complex nested trigger
    'has_any_opinion_sent_gift': null, // complex nested trigger
    'has_privateer_share_in_trade_node': null, // complex nested
    'move_capital_effect': null, // internal effect
    'average_autonomy': `Average autonomy at least <span class="val">${val}</span>`,
    'army_professionalism': `Army professionalism at least <span class="val">${(parseFloat(val)*100).toFixed(0)}%</span>`,
    'overextension_percentage': `Overextension below <span class="val">${(parseFloat(val)*100).toFixed(0)}%</span>`,
    'religious_unity': `Religious unity at least <span class="val">${(parseFloat(val)*100).toFixed(0)}%</span>`,
    'add_building_construction': (() => { const bm = val.match(/building\s*=\s*(\w+)/); return bm ? `Begin constructing <span class="tag">${bm[1].replace(/_/g, ' ')}</span>` : 'Begin building construction'; })(),
    'add_siberian_construction': `Add <span class="val">${val}</span> colonist progress`,
    // Suppress Paradox scope variables
    'ROOT': null,
    'FROM': null,
    'PREV': null,
    'THIS': null,
    'limit': null,
    'tooltip': null,
    'show_scope_change': null,
  };

  if (map[key] !== undefined) {
    if (map[key] === null) return null;
    // For scope-like labels ending with ':', try to inline the val content as a sub-condition
    if (map[key].endsWith(':') && val && val.length > 2 && !val.includes('{')) {
      const innerMatch = val.match(/^(\w+)\s*=\s*(.+)$/);
      if (innerMatch) {
        const inner = triggerToText(innerMatch[1], innerMatch[2]);
        if (inner && inner.text) return { text: map[key] + ' ' + inner.text, type: 'condition' };
      }
    }
    return { text: map[key], type: 'condition' };
  }

  if (key === 'custom_trigger_tooltip' || key === 'custom_tooltip' || key === 'tooltip') return null;
  if (key === 'if' || key === 'else' || key === 'else_if') return null;
  // Suppress has_XX_opinion_* triggers (complex nested with target = ROOT)
  if (/^has_\d+_opinion_/.test(key) || /^has_any_opinion_/.test(key)) return null;

  // EU4 advisor type checks (e.g. trader = 3, natural_scientist = 5)
  const ADVISOR_TYPES = new Set(['trader','natural_scientist','fortification_expert','artist','army_organiser','army_reformer','commandant','diplomat','colonial_governor','grand_captain','inquisitor','master_of_mint','master_recruiter','naval_reformer','navigator','philosopher','spymaster','statesman','theologian','treasurer']);
  if (ADVISOR_TYPES.has(key) && /^\d+$/.test(val)) {
    const advName = key.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
    return { text: `Have <span class="tag">${advName}</span> advisor (level <span class="val">${val}</span>)`, type: 'condition' };
  }

  // change_trade_goods effect
  if (key === 'change_trade_goods') return { text: `Change trade goods to <span class="tag">${val.replace(/_/g, ' ')}</span>`, type: 'condition' };

  // has_adm/dip/mil_advisor_X checks (e.g. has_adm_advisor_3 = yes, or has_mil_advisor = 5)
  if (/^has_(adm|dip|mil)_advisor_?(\d*)$/.test(key)) {
    const am = key.match(/^has_(adm|dip|mil)_advisor_?(\d*)$/);
    const cat = am[1] === 'adm' ? 'Administrative' : am[1] === 'dip' ? 'Diplomatic' : 'Military';
    const lvl = am[2] || (/^\d+$/.test(val) ? val : '');
    if (lvl) return { text: `Has ${cat} advisor (level <span class="val">${lvl}</span>)`, type: 'condition' };
    return { text: `Has a ${cat} advisor`, type: 'condition' };
  }

  if (/^\d+$/.test(key)) {
    const pn = provName(key);
    // Detect common patterns inside the province scope value
    const rawVal = val;
    // Handle add_permanent_claim/add_core to ROOT (common effect pattern)
    if (/add_permanent_claim\s*=\s*ROOT/.test(rawVal)) return { text: `Gain permanent claim on <span class="tag" title="Province ID: ${key}">${esc(pn)}</span>`, type: 'condition' };
    if (/add_core\s*=\s*ROOT/.test(rawVal)) return { text: `Gain core on <span class="tag" title="Province ID: ${key}">${esc(pn)}</span>`, type: 'condition' };
    if (/change_culture\s*=\s*ROOT/.test(rawVal) || /change_religion\s*=\s*ROOT/.test(rawVal)) {
      let actions = [];
      if (/change_culture\s*=\s*ROOT/.test(rawVal)) actions.push('culture');
      if (/change_religion\s*=\s*ROOT/.test(rawVal)) actions.push('religion');
      return { text: `<span class="tag" title="Province ID: ${key}">${esc(pn)}</span> — Change ${actions.join(' and ')} to ours`, type: 'condition' };
    }
    if (/add_permanent_province_modifier/.test(rawVal)) {
      const modMatch = rawVal.match(/name\s*=\s*(\w+)/);
      if (modMatch) return { text: `<span class="tag" title="Province ID: ${key}">${esc(pn)}</span> — Add modifier: ${modRef(modMatch[1])}`, type: 'condition' };
    }
    // Parse the province condition value for readability
    let provCondition = val.replace(/_/g, ' ');
    // Suppress most conditions that reference ROOT/FROM/PREV (scope variables)
    if (/\b(ROOT|FROM|PREV|THIS)\b/.test(provCondition)) return null;
    // Suppress noisy/internal province conditions
    if (/units in province|has siege|controller|set province flag|province event/i.test(provCondition)) return null;
    // Common province conditions
    provCondition = provCondition.replace(/fort level\s*=\s*/i, 'Fort level ');
    provCondition = provCondition.replace(/has construction\s*=\s*/i, 'Building: ');
    provCondition = provCondition.replace(/has building\s*=\s*/i, 'Has building: ');
    provCondition = provCondition.replace(/culture\s*=\s*/i, 'Culture: ');
    provCondition = provCondition.replace(/religion\s*=\s*/i, 'Religion: ');
    provCondition = provCondition.replace(/is core\s*=\s*/i, 'Core of: ');
    provCondition = provCondition.replace(/owned by\s*=\s*/i, 'Owned by: ');
    provCondition = provCondition.replace(/country or non sovereign subject holds\s*=\s*\S+/i, 'Owned by you or subject');
    provCondition = provCondition.replace(/country or subject holds\s*=\s*(\S+)/i, (m, t) => 'Owned by ' + (DATA[t] ? DATA[t].name : 'you') + ' or subject');
    provCondition = provCondition.replace(/owns or non sovereign subject of\s*=\s*\S+/i, 'Owned by you or subject');
    if (!provCondition.trim()) return null;
    return { text: `<span class="tag" title="Province ID: ${key}">${esc(pn)}</span> — ${provCondition}`, type: 'scope' };
  }

  if (key.endsWith('_area') || key.endsWith('_region') || key.endsWith('_superregion')) {
    const cleanName = key.replace(/_area$|_region$|_superregion$/, '').replace(/_/g, ' ');
    const scopeType = key.endsWith('_area') ? 'area' : key.endsWith('_region') ? 'region' : 'superregion';
    // Detect common patterns inside the scope value
    if (/add_permanent_claim/.test(val)) return { text: `Gain permanent claims on <span class="tag">${cleanName}</span> (${scopeType})`, type: 'condition' };
    if (/add_claim/.test(val)) return { text: `Gain claims on <span class="tag">${cleanName}</span> (${scopeType})`, type: 'condition' };
    if (/add_core/.test(val)) return { text: `Gain cores on <span class="tag">${cleanName}</span> (${scopeType})`, type: 'condition' };
    if (/country_or_non_sovereign_subject_holds|country_or_subject_holds/.test(val)) return { text: `Own all of <span class="tag">${cleanName}</span> (${scopeType}), or subjects own`, type: 'condition' };
    if (/owned_by|owner/.test(val) && /type\s*=\s*all/.test(val)) return { text: `Own all of <span class="tag">${cleanName}</span> (${scopeType})`, type: 'condition' };
    if (/owned_by|owner/.test(val)) return { text: `Own provinces in <span class="tag">${cleanName}</span> (${scopeType})`, type: 'condition' };
    return { text: `In <span class="tag">${cleanName}</span> (${scopeType})`, type: 'scope' };
  }

  // Country tag scopes (e.g. L57 = { is_subject_of = ROOT })
  if (/^[A-Z][A-Z0-9]{1,2}$/.test(key) && DATA[key]) {
    const cName = DATA[key].name || key;
    // Inline single-line patterns
    if (/is_subject_of\s*=\s*ROOT/.test(val)) return { text: `<span class="tag">${esc(cName)}</span> is our subject`, type: 'condition' };
    if (/trade_embargo_by\s*=\s*ROOT/.test(val)) return { text: `<span class="tag">${esc(cName)}</span> has trade embargo from us`, type: 'condition' };
    if (/alliance_with\s*=\s*ROOT/.test(val)) return { text: `<span class="tag">${esc(cName)}</span> is allied with us`, type: 'condition' };
    if (/marriage_with\s*=\s*ROOT/.test(val)) return { text: `Royal marriage with <span class="tag">${esc(cName)}</span>`, type: 'condition' };
    if (/war_with\s*=\s*ROOT/.test(val)) return { text: `At war with <span class="tag">${esc(cName)}</span>`, type: 'condition' };
    if (/has_opinion\s*=.*ROOT/.test(val)) { const om = val.match(/value\s*=\s*(-?\d+)/); return { text: `<span class="tag">${esc(cName)}</span> has opinion of us at least <span class="val">${om?om[1]:'?'}</span>`, type: 'condition' }; }
    if (/is_subject\s*=\s*yes/.test(val)) return { text: `<span class="tag">${esc(cName)}</span> is a subject nation`, type: 'condition' };
    if (/exists\s*=\s*yes/.test(val)) return { text: `<span class="tag">${esc(cName)}</span> exists`, type: 'condition' };
    if (/exists\s*=\s*no/.test(val)) return { text: `<span class="tag">${esc(cName)}</span> does not exist`, type: 'condition' };
    // Multi-line scope opener (val is empty or just braces) — show as scope label
    if (!val || val.length < 3) return { text: `<span class="tag">${esc(cName)}</span>:`, type: 'scope' };
    // Generic: show country name + simplified inner conditions
    if (/\bROOT\b/.test(val)) return null;
    return { text: `<span class="tag">${esc(cName)}</span>: ${val.replace(/_/g, ' ').substring(0, 80)}`, type: 'scope' };
  }

  if (key.startsWith('has_')) {
    if (isScopeVar(val)) return null;
    const cleanKey = key.replace(/_/g, ' ').replace(/\bhas\b/, 'Has').replace(/\btrigger\b/, '');
    const cleanVal = val === 'yes' ? '' : val === 'no' ? ' (no)' : `: <span class="tag">${resolveRef(val)}</span>`;
    return { text: `${cleanKey.trim()}${cleanVal}`, type: 'condition' };
  }
  if (key.startsWith('is_')) {
    if (isScopeVar(val)) return null;
    const label = key.replace(/_/g, ' ').replace(/\bis\b/, 'Is');
    const cleanVal = val === 'yes' ? '' : val === 'no' ? ' — not' : `: <span class="val">${resolveRef(val)}</span>`;
    return { text: `${label}${cleanVal}`, type: 'condition' };
  }
  if (key.startsWith('num_of_')) {
    const label = key.replace(/^num_of_/, '').replace(/_/g, ' ');
    return { text: `Have at least <span class="val">${val}</span> ${label}`, type: 'condition' };
  }

  // Suppress any remaining scope variable references
  if (isScopeVar(val)) return null;

  // Generic fallthrough - format as readable text
  if (val && !val.includes('{') && val.length < 60) {
    const cleanKey = key.replace(/_/g, ' ');
    const resolved = resolveRef(val);
    const cleanVal = /^\d+(\.\d+)?$/.test(val) ? `<span class="val">${val}</span>` : `<span class="tag">${resolved}</span>`;
    return { text: `${cleanKey}: ${cleanVal}`, type: 'raw' };
  }

  return null;
}

// Lines to filter out from effects display
const EFFECT_NOISE_PATTERNS = [
  /province.triggered.modifier/i,
  /^province.event:/i,
  /hidden.effect/i,
  /set.country.flag/i,
  /set.ruler.flag/i,
  /clr.country.flag/i,
  /set.global.flag/i,
  /clr.global.flag/i,
  /change.variable/i,
  /set.variable/i,
  /check.variable/i,
  /custom.tooltip/i,
  /swap.free.idea.group/i,
  /migration.randomiz/i,
  /^Add province modifier:\s*<span[^>]*>\s*<\/span>$/i,
  /^Add modifier:\s*<span[^>]*>\s*<\/span>$/i,
  /^Add ruler modifier:\s*<span[^>]*>\s*<\/span>$/i,
  /increase.ruler.adm.effect/i,
  /increase.ruler.dip.effect/i,
  /increase.ruler.mil.effect/i,
  /complete.campaign.effect/i,
  /define.heir/i,
  /define.ruler/i,
  /define.consort/i,
  /remove.country.modifier:\s*<span[^>]*>\s*<\/span>/i,
  /^Pro/i, // fragment from truncated province scope
  /^Produces:/i, // trade goods in province scope, not a real effect
  /^Random owned province:$/i,
  /^Every owned province:$/i,
  /^In capital/i,
  /^Every neighbor:$/i,
  /^Every subject:$/i,
  /^Every known country:$/i,
  /^Any owned province:$/i,
  /^Any ally:$/i,
  /^Any neighbor:$/i,
  /^Any subject:$/i,
  /var.effect/i, // variable operations
  /force.limit.build/i, // internal
  /^first\b/i, // conditional block labels
  /^second\b/i,
  /^effect:/i,
  /^limit:/i,
  /^sign:/i,
  /^birth.date:/i,
  /^monarch.name:/i,
  /^kill.ruler/i,
  /^kill.heir/i,
  /^Have at least.*time/i, // "Have at least 2 times..." internal check in effects
  /^Add\s+trust$/i, // empty trust (complex nested)
  /^Add\s*<span[^>]*>\s*<\/span>\s*trust$/i,
  /move.capital.effect/i,
  /override.country.name/i,
  /lock.racial/i,
  /swap.non.generic/i,
  /swap.free.idea/i,
  /^owned.by.friendly/i,
  /^has.spy.network/i,
];

function isNoisyEffectLine(text) {
  return EFFECT_NOISE_PATTERNS.some(p => p.test(text));
}

function renderRequirements(trigger) {
  if (!trigger) return '';
  let html = '';

  const tooltips = trigger.trigger_tooltips || {};
  // Split tooltips: check if key appears in effect_raw (→ effect tooltip) or trigger_raw (→ requirement)
  const effectRaw = trigger.effect_raw || '';
  const triggerRaw = trigger.trigger_raw || '';
  const tooltipEntries = Object.entries(tooltips).filter(([k,v]) => {
    if (!v || !v.trim()) return false;
    // If key appears in effect_raw, it's an effect tooltip
    if (effectRaw.includes(k)) return false;
    // If key contains 'effect', it's an effect tooltip
    if (k.includes('effect')) return false;
    return true;
  });
  const hasTooltips = tooltipEntries.length > 0;

  // Parse raw triggers for mechanical conditions
  const parsed = parseTriggerToReadable(trigger.trigger_raw || '');
  const seen = new Set();
  const mechanical = parsed.filter(p => {
    const t = p.text.toLowerCase();
    // Always filter out meta/wrapper lines
    if (/custom.trigger.tooltip/i.test(t)) return false;
    if (/^tooltip\b/i.test(t)) return false;
    // Filter out region/area scope wrappers (not real conditions)
    if (p.type === 'scope' && /^\s*In\s+<span class="tag">/.test(p.text) && /\(region\)|\(area\)|\(superregion\)/.test(p.text)) return false;
    // Filter out lines that still contain raw code-like patterns (= signs in plain text)
    const stripped = t.replace(/<[^>]+>/g, '');
    if (/\w+\s*=\s*\w+/.test(stripped) && !/tech at least|at least \d|modifier:|professionalism|autonomy/.test(stripped)) return false;
    // When tooltips exist, only keep well-known standalone mechanical conditions
    // that give the player actionable info beyond what tooltips say
    if (hasTooltips) {
      const knownMechanical = /have at least|own province|own and core|admin tech|diplo tech|military tech|be at (peace|war)|be independent|government rank|monthly income|have employed advisor|completed idea group|have idea group|army at|manpower at|force limit|total dev|building:/i;
      // Also keep province-scope conditions (they show province names now)
      const isProvScope = p.type === 'scope' && /title="Province ID:/.test(p.text);
      if (!knownMechanical.test(t) && !isProvScope && p.type !== 'logic') return false;
    }
    // Deduplicate (but not logic labels, and reset dedup on scope changes)
    if (p.type === 'scope') {
      seen.clear(); // Reset dedup under new scope — same conditions valid per scope
    } else if (p.type !== 'logic') {
      const key = t.replace(/<[^>]+>/g, '').trim();
      if (seen.has(key)) return false;
      seen.add(key);
    }
    return true;
  });

  // Remove orphaned logic labels with no following content, or "One of:" with only 1 child
  // Run iteratively since removing one label can change child counts of others
  let changed = true;
  while (changed) {
    changed = false;
    for (let i = mechanical.length - 1; i >= 0; i--) {
      if (mechanical[i].type === 'logic') {
        let childCount = 0;
        for (let j = i + 1; j < mechanical.length; j++) {
          if (mechanical[j].type === 'logic') break;
          childCount++;
        }
        if (childCount === 0 || (childCount === 1 && /one of the following/i.test(mechanical[i].text))) {
          mechanical.splice(i, 1);
          changed = true;
        }
      }
    }
  }
  const hasAny = hasTooltips || mechanical.length > 0;
  if (!hasAny) return '';

  html += '<div class="requirements-box"><div class="req-label">Requirements</div><ul>';

  // Show tooltip text as primary (game's own readable strings)
  if (hasTooltips) {
    tooltipEntries.forEach(([key, text]) => {
      let clean = text.replace(/\u00a7[A-Za-z!]/g, '').replace(/\\n/g, '\n').replace(/\$[^$]+\$/g, '').replace(/£\w+£/g, '').trim();
      clean = resolveGameText(clean);
      if (clean) {
        // Find matching raw code for this tooltip key to use as hover
        const rawSnippet = trigger.trigger_raw ? extractTooltipRaw(trigger.trigger_raw, key) : '';
        const titleAttr = rawSnippet ? ` title="${esc(rawSnippet)}"` : '';
        html += `<li${titleAttr}>${esc(clean)}</li>`;
      }
    });
  }

  // Show mechanical conditions NOT wrapped in tooltips
  if (mechanical.length > 0) {
    // If we have tooltips, label these as additional
    if (hasTooltips && mechanical.length > 0) {
      html += '<li style="color:var(--text-muted);font-size:11px;list-style:none;padding-left:0;margin-top:4px;">Additional conditions:</li>';
    }
    mechanical.forEach(p => {
      if (p.type === 'logic') {
        html += `<li style="color:var(--purple);padding-left:0">${p.text}</li>`;
      } else {
        html += `<li>${p.text}</li>`;
      }
    });
  }

  html += '</ul></div>';
  return html;
}

// Create a modifier reference span with data attribute for tooltip lookup
function modRef(modKey, displayName) {
  const mod = MODIFIERS[modKey];
  const name = mod ? mod.name : (displayName || modKey.replace(/_/g, ' '));
  if (mod) {
    return `<span class="mod-ref" data-mod="${modKey}">${esc(name)}</span>`;
  }
  return `<span class="tag">${esc(name)}</span>`;
}

// Extract modifier key from a triggerToText val string (for add_country_modifier etc.)
function extractModKey(val) {
  const nameMatch = val.match(/name\s*=\s*"?(\w+)"?/i);
  return nameMatch ? nameMatch[1] : val.replace(/duration\s*=\s*-?\d+/gi, '').replace(/[{}\s"]/g, '').trim();
}

function extractTooltipRaw(raw, tooltipKey) {
  // Find the raw code block associated with a custom_trigger_tooltip key
  const idx = raw.indexOf(tooltipKey);
  if (idx < 0) return '';
  // Get surrounding context (100 chars before and after)
  const start = Math.max(0, idx - 100);
  const end = Math.min(raw.length, idx + 200);
  return raw.substring(start, end).replace(/\t/g, '  ').replace(/\n/g, ' ').trim();
}

function renderEffects(trigger) {
  if (!trigger) return '';

  // Check for tooltip-based effect descriptions first
  const tooltips = trigger.trigger_tooltips || {};
  const effectRaw = trigger.effect_raw || '';
  const effectTooltips = Object.entries(tooltips).filter(([k,v]) => {
    if (!v || !v.trim()) return false;
    // Key appears in effect_raw → it's an effect tooltip
    if (effectRaw.includes(k)) return true;
    // Key contains 'effect' → it's an effect tooltip
    if (k.includes('effect')) return true;
    return false;
  });

  const parsed = trigger.effect_raw ? parseTriggerToReadable(trigger.effect_raw) : [];
  let filtered = parsed.filter(p => !isNoisyEffectLine(p.text));
  // Filter out lines that still contain raw code-like patterns
  filtered = filtered.filter(p => {
    const stripped = p.text.replace(/<[^>]+>/g, '').toLowerCase();
    // Keep lines that start with known good effect patterns
    if (/^(add |lose |remove |gain |build |change |accept |set |form |create |vassalize|inherit|unlock|trigger)/i.test(stripped)) return true;
    if (/\w+\s*=\s*\w+/.test(stripped) && p.type !== 'logic') return false;
    return true;
  });
  // Remove scope wrapper lines (region/area/superregion) from effects — they're just context
  filtered = filtered.filter(p => p.type !== 'scope' || /Add |Remove |Change |Build |Gain /i.test(p.text));
  // Remove orphaned logic labels (Must NOT:, One of:, All of:) with no following content or single child
  const cleaned = [];
  for (let i = 0; i < filtered.length; i++) {
    if (filtered[i].type === 'logic') {
      let childCount = 0;
      for (let j = i + 1; j < filtered.length; j++) {
        if (filtered[j].type === 'logic') break;
        childCount++;
      }
      if (childCount === 0) continue;
      if (childCount === 1 && /one of the following/i.test(filtered[i].text)) continue;
    }
    cleaned.push(filtered[i]);
  }
  filtered = cleaned;

  if (effectTooltips.length === 0 && filtered.length === 0) return '';

  let html = '<div class="effects-box"><div class="eff-label">On Completion</div>';
  html += '<ul>';

  // Tooltip-based effects first (readable game text)
  effectTooltips.forEach(([key, text]) => {
    let clean = text.replace(/\u00a7[A-Za-z!]/g, '').replace(/\\n/g, '\n').replace(/\$[^$]+\$/g, '').replace(/£\w+£/g, '').trim();
    clean = resolveGameText(clean);
    if (clean) html += `<li>${esc(clean)}</li>`;
  });

  if (effectTooltips.length === 0) {
    // No tooltips — show all parsed mechanical effects
    filtered.forEach(p => {
      let t = p.text.replace(/Add <span class="val">-(\d+)<\/span>/g, 'Lose <span class="val">$1</span>');
      html += `<li>${t}</li>`;
    });
  } else {
    // Tooltips exist — also show key mechanical effects (modifiers, resource changes, etc.)
    const knownEffects = /^(Add |Lose |Remove |Gain |Build |Change |Accept |Set |Form |Create |Vassalize|Inherit|Trigger)/i;
    const supplementary = filtered.filter(p => {
      const stripped = p.text.replace(/<[^>]+>/g, '').trim();
      return knownEffects.test(stripped);
    });
    if (supplementary.length > 0) {
      supplementary.forEach(p => {
        let t = p.text.replace(/Add <span class="val">-(\d+)<\/span>/g, 'Lose <span class="val">$1</span>');
        html += `<li>${t}</li>`;
      });
    }
  }

  html += '</ul>';
  html += '</div>';
  return html;
}

// --- Lore truncation ---
function truncateLore(text, maxLen) {
  if (!text || text.length <= maxLen) return { text: text, truncated: false };
  // Find sentence boundary before maxLen
  const sub = text.substring(0, maxLen);
  const lastDot = sub.lastIndexOf('.');
  if (lastDot > maxLen * 0.4) {
    return { text: sub.substring(0, lastDot + 1), truncated: true };
  }
  return { text: sub + '...', truncated: true };
}

// --- SELECT COUNTRY ---
function selectCountry(tag) {
  selectedTag = tag;
  const c = DATA[tag];
  if (!c) return;

  document.querySelectorAll('.country-item').forEach(el => {
    el.classList.toggle('selected', el.dataset.tag === tag);
  });

  document.getElementById('welcome').style.display = 'none';
  const detail = document.getElementById('detail');
  detail.className = 'visible';

  const w = WIKI[tag] || {};
  const reg = REGIONS[tag] || {};
  const s = STATUS[tag] || {};
  const color = c.color ? `rgb(${c.color[0]},${c.color[1]},${c.color[2]})` : '#666';
  const relColor = getReligionColor(c.religion_id || '');

  // Build wiki URL
  let wikiLink = '';
  if (w.wiki_url && w.found) {
    wikiLink = w.wiki_url;
  } else {
    wikiLink = wikiUrl(c.name);
  }

  // Status pills with proper classes
  let statusHtml = '';
  if (s.status === 'playable' || s.status === 'both') {
    statusHtml += '<span class="pill pill-playable">Playable in 1444</span>';
  }
  if (s.status === 'formable' || s.status === 'both') {
    statusHtml += '<span class="pill pill-formable">Formable Nation</span>';
  }
  if (s.provinces_owned) {
    statusHtml += `<span class="pill">${s.provinces_owned} starting provinces</span>`;
  }

  // Header
  let html = `<div class="detail-header">
    <img class="flag" src="flags/${tag}.png" onerror="this.style.display='none'">
    <div class="info">
      <h2>${esc(c.name)}</h2>
      <div class="tag-adj"><span class="color-dot" style="background:${color}"></span> ${tag} &middot; ${esc(c.adjective || '')}</div>
      <div class="pills">
        ${statusHtml}
        <span class="pill pill-gov clickable" onclick="setGovernmentFilter('${esc(c.government || '')}')">${esc(titleCase(c.government) || 'Unknown')}</span>
        <span class="pill">Rank ${c.government_rank || '?'}</span>
        <span class="pill pill-religion clickable" style="border-color:${relColor}" onclick="setReligionFilter('${esc(c.religion || '')}')">
          <img src="religion_icons/${c.religion_id || ''}.png" onerror="this.style.display='none'">
          ${esc(c.religion || '')}
        </span>
        <span class="pill pill-culture clickable" onclick="setCultureSearch('${esc(c.culture_group || '')}')">${esc(c.culture_group || '')}</span>
        <span class="pill pill-culture clickable" onclick="setCultureSearch('${esc(c.culture_group || '')}')">${esc(c.primary_culture || '')}</span>
        <span class="pill clickable" onclick="setTechFilter('${esc(c.technology_group || '')}')">${esc(c.technology_group || '')}</span>
        ${reg.region_name ? `<span class="pill pill-region clickable" onclick="setRegionFilter('${esc(reg.superregion_name || '')}')">${esc(reg.region_name)}</span>` : ''}
        ${reg.superregion_name ? `<span class="pill pill-region clickable" onclick="setRegionFilter('${esc(reg.superregion_name)}')">${esc(reg.superregion_name)}</span>` : ''}
      </div>
      ${w.found ? `<a href="${esc(wikiLink)}" target="_blank" rel="noopener" class="wiki-btn">&#128214; View on Wiki</a>` : ''}
    </div>
  </div>`;

  // Lore (truncated)
  const loreText = w.lore_full || w.lore_intro || w.intro || '';
  if (loreText.trim()) {
    const { text: loreTrunc, truncated } = truncateLore(loreText.trim(), 800);
    const lines = loreTrunc.split(/(?<=\.)\s+/);
    const firstLine = lines[0] || '';
    const rest = lines.slice(1).join(' ');
    html += `<div class="lore-box">
      <span class="first-line">${esc(firstLine)}</span>${rest ? ' ' + esc(rest) : ''}`;
    if (truncated && wikiLink) {
      html += ` <a class="lore-read-more" href="${esc(wikiLink)}" target="_blank" rel="noopener">Read more...</a>`;
    }
    html += `</div>`;
  }

  // Tabs
  const hasMissions = c.missions && c.missions.length > 0;
  const hasIdeas = c.ideas && c.ideas.ideas && c.ideas.ideas.length > 0;

  const startupLore = STARTUP_LORE[tag] || {};
  const hasLore = !!(loreText.trim() || startupLore.lore || c.primary_culture || c.religion);
  html += '<div class="tabs">';
  let firstTab = null;
  const ideaCount = hasIdeas ? c.ideas.ideas.filter(i => i.name !== 'ai_will_do').length : 0;
  if (hasLore) { html += `<button class="tab-btn active" data-tab="lore">Lore</button>`; firstTab = firstTab || 'lore'; }
  if (hasIdeas) { html += `<button class="tab-btn${!hasLore ? ' active' : ''}" data-tab="ideas">National Ideas<span class="count">${ideaCount}</span></button>`; firstTab = firstTab || 'ideas'; }
  if (hasMissions) { html += `<button class="tab-btn${!hasLore && !hasIdeas ? ' active' : ''}" data-tab="missions">Mission Tree<span class="count">${c.missions.length}</span></button>`; firstTab = firstTab || 'missions'; }
  html += '</div>';

  // Lore tab (default first tab)
  if (hasLore) {
    html += `<div class="tab-content${firstTab === 'lore' ? ' active' : ''}" data-tab="lore">`;
    // Country info table
    html += '<div class="lore-info-table">';
    const infoRows = [];
    if (s.status === 'playable' || s.status === 'both') infoRows.push(['Status', '<span class="pill pill-playable">Playable in 1444</span>']);
    if (s.status === 'formable' || s.status === 'both') infoRows.push(['Status', '<span class="pill pill-formable">Formable Nation</span>']);
    if (c.primary_culture) infoRows.push(['Primary Culture', esc(c.primary_culture)]);
    if (c.culture_group) infoRows.push(['Culture Group', esc(c.culture_group)]);
    if (c.accepted_cultures && c.accepted_cultures.length) infoRows.push(['Accepted Cultures', c.accepted_cultures.map(ac => esc(ac)).join(', ')]);
    if (c.religion) infoRows.push(['Religion', `<img src="religion_icons/${c.religion_id || ''}.png" style="height:14px;vertical-align:middle" onerror="this.style.display='none'"> ${esc(c.religion)}`]);
    if (c.government) infoRows.push(['Government', esc(titleCase(c.government))]);
    if (c.government_rank) infoRows.push(['Government Rank', c.government_rank]);
    if (c.government_reforms && c.government_reforms.length) infoRows.push(['Reforms', c.government_reforms.map(r => esc(r.replace(/_/g, ' '))).join(', ')]);
    if (c.technology_group) infoRows.push(['Technology Group', esc(c.technology_group)]);
    if (reg.region_name) infoRows.push(['Region', esc(reg.region_name)]);
    if (reg.superregion_name) infoRows.push(['Superregion', esc(reg.superregion_name)]);
    if (s.provinces_owned) infoRows.push(['Starting Provinces', s.provinces_owned]);
    if (c.historical_rivals && c.historical_rivals.length) infoRows.push(['Historical Rivals', c.historical_rivals.map(r => { const rn = DATA[r]; return rn ? esc(rn.name) : r; }).join(', ')]);
    if (c.historical_friends && c.historical_friends.length) infoRows.push(['Historical Friends', c.historical_friends.map(r => { const rn = DATA[r]; return rn ? esc(rn.name) : r; }).join(', ')]);
    html += '<table class="lore-table">';
    infoRows.forEach(([label, val]) => { html += `<tr><td class="lore-label">${label}</td><td>${val}</td></tr>`; });
    html += '</table></div>';
    // Lore text (startup lore from game, then wiki lore)
    if (startupLore.lore) {
      if (startupLore.title) {
        html += `<h3 style="color:var(--gold);margin:16px 0 8px;font-size:1.1em">${esc(startupLore.title)}</h3>`;
      }
      html += `<div class="lore-text-full">${esc(startupLore.lore).replace(/\n/g, '<br>')}</div>`;
    }
    if (loreText.trim()) {
      html += `<div class="lore-text-full" style="margin-top:12px">${esc(loreText.trim()).replace(/\\n/g, '<br>')}</div>`;
    }
    if (w.found && wikiLink) {
      html += `<a href="${esc(wikiLink)}" target="_blank" rel="noopener" class="wiki-btn" style="margin-top:12px;display:inline-block">&#128214; Read more on Wiki</a>`;
    }
    html += '</div>';
  }

  // Ideas tab
  if (hasIdeas) {
    html += `<div class="tab-content${firstTab === 'ideas' ? ' active' : ''}" data-tab="ideas">`;
    if (c.ideas.traditions && c.ideas.traditions.length > 0) {
      html += '<div class="idea-group"><div class="idea-label">Traditions</div>';
      html += '<div class="mod-chips">' + c.ideas.traditions.map(t => modChip(t.modifier, t.value)).join('') + '</div></div>';
    }
    c.ideas.ideas.filter(idea => idea.name !== 'ai_will_do').forEach((idea, i) => {
      html += `<div class="idea-card">
        <h4>${i+1}. ${esc(idea.display_name || idea.name)}</h4>
        ${idea.description ? `<div class="idea-desc">${esc(idea.description).replace(/\\n/g, '<br>')}</div>` : ''}
        <div class="mod-chips">${(idea.effects || []).map(e => modChip(e.modifier, e.value)).join('')}</div>
      </div>`;
    });
    if (c.ideas.ambition && c.ideas.ambition.length > 0) {
      html += '<div class="idea-group" style="margin-top:12px"><div class="idea-label">Ambition</div>';
      html += '<div class="mod-chips">' + c.ideas.ambition.map(a => modChip(a.modifier, a.value)).join('') + '</div></div>';
    }
    html += '</div>';
  }

  // Missions tab
  if (hasMissions) {
    html += `<div class="tab-content${firstTab === 'missions' ? ' active' : ''}" data-tab="missions">`;
    html += renderMissions(c);
    html += '</div>';
  }

  detail.innerHTML = html;

  // Tab switching
  detail.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      detail.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
      detail.querySelectorAll('.tab-content').forEach(tc => tc.classList.remove('active'));
      btn.classList.add('active');
      const tabEl = detail.querySelector(`.tab-content[data-tab="${btn.dataset.tab}"]`);
      if (tabEl) tabEl.classList.add('active');
    });
  });

  // Mission node clicks - open modal
  detail.querySelectorAll('.mission-node').forEach(node => {
    node.addEventListener('click', () => showMissionDetail(tag, node.dataset.missionId));
  });

  document.getElementById('main').scrollTop = 0;
}

function resolveIcon(iconName) {
  if (!iconName) return '';
  if (ICON_MAP[iconName]) return iconName;
  // Try stripping mission_ prefix
  if (iconName.startsWith('mission_')) {
    const stripped = iconName.slice(8);
    if (ICON_MAP[stripped]) return stripped;
  }
  // Try adding mission_ prefix
  const prefixed = 'mission_' + iconName;
  if (ICON_MAP[prefixed]) return prefixed;
  return iconName; // return original even if not found
}

function renderMissions(c) {
  const missions = c.missions;
  let maxSlot = 0, maxPos = 0;
  missions.forEach(m => {
    if (m.slot > maxSlot) maxSlot = m.slot;
    if (m.position > maxPos) maxPos = m.position;
  });
  if (maxSlot === 0) maxSlot = 5;
  if (maxPos === 0) maxPos = 1;

  const color = c.color ? `rgb(${c.color[0]},${c.color[1]},${c.color[2]})` : '#666';

  // Build a lookup of mission id -> mission object for prereq checking
  const missionById = {};
  missions.forEach(mi => { missionById[mi.id] = mi; });

  let html = `<div class="mission-grid-container" id="mission-grid-container"><div class="mission-grid" id="mission-grid" style="grid-template-columns: repeat(${maxSlot}, 1fr);">`;
  for (let pos = 1; pos <= maxPos; pos++) {
    for (let slot = 1; slot <= maxSlot; slot++) {
      const m = missions.find(mi => mi.slot === slot && mi.position === pos);
      if (m) {
        const trigger = TRIGGERS[m.id] || {};
        const iconName = resolveIcon(m.icon || trigger.icon || '');
        const hasIcon = iconName && ICON_MAP[iconName];
        let iconHtml;
        if (hasIcon) {
          iconHtml = `<img class="mission-icon" src="mission_icons/${iconName}.png" onerror="this.onerror=null;this.style.display='none';this.nextElementSibling.style.display='flex'" loading="lazy"><div class="mission-icon-fallback" style="display:none">&#9876;</div>`;
        } else {
          iconHtml = `<div class="mission-icon-fallback">&#9876;</div>`;
        }

        // Check prerequisites for CSS connector classes
        const reqs = m.required_missions || [];
        let extraClasses = '';
        let crossBadgeHtml = '';
        let hasSameCol = false;
        const crossReqs = [];
        reqs.forEach(reqId => {
          const reqM = missionById[reqId];
          if (reqM) {
            if (reqM.slot === slot) {
              hasSameCol = true;
            } else {
              crossReqs.push(reqM);
            }
          }
        });
        if (hasSameCol) extraClasses += ' has-prereq-above';
        if (crossReqs.length > 0) {
          const label = crossReqs.map(r => esc(r.title || r.id)).join(', ');
          crossBadgeHtml = `<div class="cross-prereq-badge">\u2190 ${label}</div>`;
        }

        html += `<div class="mission-node${extraClasses}" data-mission-id="${esc(m.id)}" data-slot="${slot}" data-pos="${pos}" style="grid-column:${slot};grid-row:${pos};">
          ${crossBadgeHtml}${iconHtml}
          <div class="mission-title">${esc(resolveGameText(m.title || m.id))}</div>
        </div>`;
      }
    }
  }
  html += '</div></div>';
  return html;
}

function showMissionDetail(tag, missionId) {
  const c = DATA[tag];
  const mission = c.missions.find(m => m.id === missionId);
  if (!mission) return;

  // Highlight selected node in grid
  document.querySelectorAll('.mission-node').forEach(n => n.classList.toggle('selected', n.dataset.missionId === missionId));

  const trigger = TRIGGERS[missionId] || {};
  const modal = document.getElementById('mission-modal');
  const overlay = document.getElementById('mission-modal-overlay');

  const color = c.color ? `rgb(${c.color[0]},${c.color[1]},${c.color[2]})` : '#666';
  const iconName = resolveIcon(mission.icon || trigger.icon || '');
  const hasIcon = iconName && ICON_MAP[iconName];
  let iconHtml;
  if (hasIcon) {
    iconHtml = `<img src="mission_icons/${iconName}.png" onerror="this.onerror=null;this.style.display='none';this.nextElementSibling.style.display='flex'"><div class="mission-icon-fallback" style="display:none;width:32px;height:32px">&#9876;</div>`;
  } else {
    iconHtml = `<div class="mission-icon-fallback" style="width:32px;height:32px">&#9876;</div>`;
  }

  let html = `<button class="close-btn" onclick="closeMissionModal()">&times;</button>`;
  html += `<h3>${iconHtml} ${esc(resolveGameText(mission.title || mission.id))}</h3>`;
  if (mission.desc || trigger.desc) {
    html += `<div class="mission-desc">${esc(resolveGameText(mission.desc || trigger.desc || '')).replace(/\\n/g, '<br>')}</div>`;
  }
  html += `<div style="font-size:11px;color:var(--text-muted);margin-bottom:8px;">Slot ${mission.slot}, Position ${mission.position} &middot; ${esc(mission.group || trigger.group || '')}</div>`;

  // Required missions
  const reqs = mission.required_missions || trigger.required_missions || [];
  if (reqs.length > 0) {
    html += '<div class="prereqs"><strong style="font-size:12px;color:var(--text-secondary);">Required Missions:</strong> ';
    html += reqs.map(r => {
      const rm = c.missions.find(m => m.id === r);
      return `<span class="prereq-link" onclick="closeMissionModal();setTimeout(()=>showMissionDetail('${tag}','${esc(r)}'),100)">${esc(rm ? rm.title : r)}</span>`;
    }).join(', ');
    html += '</div>';
  }

  // Requirements
  const reqHtml = renderRequirements(trigger);
  html += reqHtml;

  // Effects
  let effHtml = '';
  if (trigger.effect_raw) {
    effHtml = renderEffects(trigger);
    html += effHtml;
  }

  // If no requirements, no effects, and no required missions, show a helpful message
  if (!reqHtml && !effHtml && reqs.length === 0) {
    html += '<div style="color:var(--text-muted);font-size:12px;margin:8px 0;">No special requirements \u2014 available from game start.</div>';
  }

  // "Show raw script" toggle
  if (trigger.trigger_raw || trigger.effect_raw) {
    const rawId = 'raw_' + missionId.replace(/[^a-zA-Z0-9]/g, '_');
    html += `<span class="toggle-raw" onclick="document.getElementById('${rawId}').style.display = document.getElementById('${rawId}').style.display === 'none' ? 'block' : 'none'">Show raw script</span>`;
    html += `<div id="${rawId}" style="display:none">`;
    if (trigger.trigger_raw) {
      html += '<div style="font-size:11px;color:var(--text-muted);margin-top:8px">Trigger:</div>';
      html += `<div class="script-block">${esc(trigger.trigger_raw)}</div>`;
    }
    if (trigger.effect_raw) {
      html += '<div style="font-size:11px;color:var(--text-muted);margin-top:8px">Effect:</div>';
      html += `<div class="script-block">${esc(trigger.effect_raw)}</div>`;
    }
    html += '</div>';
  }

  modal.innerHTML = html;
  modal.classList.add('visible');
  overlay.classList.add('visible');
}

function closeMissionModal() {
  document.getElementById('mission-modal').classList.remove('visible');
  document.getElementById('mission-modal-overlay').classList.remove('visible');
}

function getReligionColor(relId) {
  const r = RELIGIONS[relId];
  if (r && r.color) return `rgb(${r.color[0]},${r.color[1]},${r.color[2]})`;
  return '#666';
}

function showReligion(relId) {
  const r = RELIGIONS[relId];
  if (!r) return;
  const panel = document.getElementById('religion-panel');
  const overlay = document.getElementById('religion-overlay');

  const color = r.color ? `rgb(${r.color[0]},${r.color[1]},${r.color[2]})` : '#666';

  let html = `<button class="close-btn" onclick="closeReligionPanel()">&times;</button>`;
  html += `<h3><img src="religion_icons/${r.id}.png" onerror="this.style.display='none'">${esc(r.name)}</h3>`;
  html += `<div class="religion-group"><span class="color-dot" style="background:${color}"></span> ${esc(r.group || r.group_id || '')}</div>`;

  if (r.modifiers && r.modifiers.length > 0) {
    html += '<div style="margin:10px 0"><strong style="font-size:12px;color:var(--text-secondary)">Modifiers:</strong>';
    html += '<div class="mod-chips" style="margin-top:4px">' + r.modifiers.map(m => modChip(m.modifier, m.value)).join('') + '</div></div>';
  }

  if (r.allowed_conversions && r.allowed_conversions.length > 0) {
    html += '<div style="margin:10px 0"><strong style="font-size:12px;color:var(--text-secondary)">Allowed Conversions:</strong> ';
    html += r.allowed_conversions.map(c => {
      const cr = RELIGIONS[c];
      return esc(cr ? cr.name : c);
    }).join(', ');
    html += '</div>';
  }

  const relCountries = countries.filter(c => c.religion_id === relId);
  if (relCountries.length > 0) {
    html += `<div style="margin:10px 0"><strong style="font-size:12px;color:var(--text-secondary)">Countries (${relCountries.length}):</strong>`;
    html += '<div style="margin-top:6px;display:flex;flex-wrap:wrap;gap:4px;max-height:200px;overflow-y:auto">';
    relCountries.forEach(c => {
      html += `<span class="pill clickable" onclick="closeReligionPanel();selectCountry('${c.tag}')" style="font-size:11px">${esc(c.name)}</span>`;
    });
    html += '</div></div>';
  }

  panel.innerHTML = html;
  panel.classList.add('visible');
  overlay.classList.add('visible');
}

function closeReligionPanel() {
  document.getElementById('religion-panel').classList.remove('visible');
  document.getElementById('religion-overlay').classList.remove('visible');
}

// Shared modifier tooltip element (appended to body to avoid overflow clipping)
const _modTT = document.createElement('div');
_modTT.className = 'mod-tooltip';
_modTT.style.display = 'none';
document.body.appendChild(_modTT);

document.addEventListener('mouseover', (e) => {
  const ref = e.target.closest('.mod-ref');
  if (!ref) { _modTT.style.display = 'none'; return; }
  // Get the modifier key from data attribute
  const key = ref.dataset.mod;
  if (!key || !MODIFIERS[key]) { _modTT.style.display = 'none'; return; }
  const mod = MODIFIERS[key];
  let html = `<div class="mod-tt-name">${esc(mod.name)}</div>`;
  mod.effects.forEach(ef => {
    // Keys where negative = good (green) and positive = bad (red). "Less is better" effects.
    const reversedKeys = ['add_tribal_land_cost','adm_advisor_cost','adm_tech_cost_modifier','admiral_cost','advisor_cost','ae_impact','all_power_cost','army_tradition_decay','artillery_barrage_cost','artillery_cost','assault_fort_cost_modifier','attrition','build_cost','cavalry_cost','cawa_cost_modifier','center_of_trade_upgrade_cost','centralize_state_cost','colony_cost_modifier','core_creation','core_decay_on_your_own','culture_conversion_cost','development_cost','development_cost_in_primary_culture','dip_advisor_cost','dip_tech_cost_modifier','diplomatic_annexation_cost','discovered_relations_impact','drill_decay_modifier','embracement_cost','enforce_religion_cost','envoy_travel_time','establish_order_cost','estate_interaction_cooldown_modifier','expand_administration_cost','expand_infrastructure_cost_modifier','expel_minorities_cost','fabricate_claims_cost','fire_damage_received','flagship_cost','fort_maintenance_modifier','galley_cost','general_cost','global_naval_barrage_cost','global_regiment_cost','global_regiment_recruit_speed','global_ship_cost','global_ship_recruit_speed','global_unrest','governing_cost','great_project_upgrade_cost','harsh_treatment_cost','heavy_ship_cost','idea_cost','infantry_cost','interest','justify_trade_conflict_cost','land_attrition','land_maintenance_modifier','landing_penalty','leader_cost','liberty_desire','liberty_desire_from_subject_development','light_ship_cost','local_build_cost','local_center_of_trade_upgrade_cost','local_centralize_state_cost','local_colony_cost_modifier','local_culture_conversion_cost','local_development_cost','local_fort_maintenance_modifier','local_governing_cost','local_great_project_upgrade_cost','local_missionary_maintenance_cost','local_regiment_cost','local_ship_cost','local_state_maintenance_modifier','local_unrest','local_warscore_cost_modifier','local_years_of_nationalism','merc_maintenance_modifier','mercantilism_cost','mercenary_cost','migration_cost','mil_advisor_cost','mil_tech_cost_modifier','missionary_maintenance_cost','monthly_gold_inflation_modifier','morale_damage_received','move_capital_cost_modifier','native_uprising_chance','naval_attrition','naval_maintenance_modifier','naval_morale_damage_received','navy_tradition_decay','overextension_impact_modifier','prestige_decay','promote_culture_cost','province_warscore_cost','reelection_cost','reinforce_cost_modifier','rival_border_fort_maintenance','rival_change_cost','sailor_maintenance_modifer','same_culture_advisor_cost','same_religion_advisor_cost','settle_cost','shock_damage_received','spy_action_cost_modifier','stability_cost_modifier','stability_cost_to_declare_war','state_governing_cost','state_maintenance_modifier','statewide_governing_cost','technology_cost','trade_company_governing_cost','trade_company_investment_cost','transport_attrition','transport_cost','war_exhaustion','war_exhaustion_cost','war_taxes_cost_modifier','warscore_cost_vs_other_religion','yearly_corruption','years_of_nationalism'];
    const isPos = ef.value.startsWith('+');
    const isNeg = ef.value.startsWith('-');
    let cls = reversedKeys.includes(ef.key) ? (isNeg ? 'positive' : isPos ? 'negative' : '') : (isPos ? 'positive' : isNeg ? 'negative' : '');
    html += `<div class="mod-tt-effect"><span>${esc(ef.name)}</span><span class="mod-tt-val ${cls}">${esc(ef.value)}</span></div>`;
  });
  _modTT.innerHTML = html;
  _modTT.style.display = 'block';
  _modTT.style.left = '0px'; // reset position for measurement
  _modTT.style.top = '0px';
  const rect = ref.getBoundingClientRect();
  const ttW = _modTT.offsetWidth;
  const ttH = _modTT.offsetHeight;
  let left = rect.left;
  let top = rect.top - ttH - 6;
  if (top < 4) top = rect.bottom + 6;
  if (left + ttW > window.innerWidth - 8) left = window.innerWidth - ttW - 8;
  if (left < 4) left = 4;
  _modTT.style.left = left + 'px';
  _modTT.style.top = top + 'px';
});
document.addEventListener('mouseout', (e) => {
  const ref = e.target.closest('.mod-ref');
  if (ref) _modTT.style.display = 'none';
});

// Init
document.addEventListener('DOMContentLoaded', loadData);
</script>
</body>
</html>'''

    output_path = r'C:\Users\jjdeg\OneDrive\Desktop\anbennar-guide\index.html'
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f'Written {len(html):,} bytes to {output_path}')

if __name__ == '__main__':
    build()
