#!/usr/bin/env python3
"""Bouwt de statische toolkaarten in index.html uit data.json."""
import html
import json
import re
import urllib.request
from pathlib import Path
from urllib.parse import quote

START_MARKER = ""
END_MARKER = ""
AIBM_B2B = "https://aibuildermarketplace.com/b2b/"

CARD = """\
                <div class="tool-card group bg-slate-900/40 p-6 rounded-xl border border-slate-800 hover:border-indigo-500 hover:bg-slate-900/70 transition-all duration-300 flex flex-col h-full shadow-lg shadow-black/20" data-category="{category_attr}">
                    <div class="flex items-start justify-between mb-5">
                        <div class="w-12 h-12 rounded-lg bg-white p-1.5 border border-slate-700 shadow-sm flex items-center justify-center overflow-hidden">
                            <img src="https://www.google.com/s2/favicons?domain={domain}&amp;sz=128" alt="{name} logo" class="w-full h-full object-contain" loading="lazy" width="48" height="48">
                        </div>
                        <span class="text-[10px] uppercase font-mono tracking-widest text-indigo-400 bg-indigo-950/40 px-2.5 py-1 rounded border border-indigo-900/30 text-right max-w-[60%]">{category}</span>
                    </div>
                    <h3 class="font-bold text-xl text-white group-hover:text-indigo-400 transition-colors mb-3">{name}</h3>{reviews_row}
                    <p class="text-sm text-slate-400 leading-relaxed mb-6 flex-grow">{desc}</p>
                    <a href="{link}" target="_blank" rel="sponsored noopener noreferrer" class="text-sm font-medium text-slate-300 hover:text-white flex items-center justify-between w-full mt-auto border-t border-slate-800/60 pt-4 group/link">
                        <span>View Software</span>
                        <span class="text-indigo-500 group-hover/link:translate-x-1 transition-transform">&rarr;</span>
                    </a>
                </div>"""

REVIEWS_ROW = """
                    <a href="{reviews_url}" target="_blank" rel="noopener" class="inline-flex items-center gap-1.5 text-xs text-indigo-300 hover:text-white mb-3 transition-colors"><span class="text-emerald-400">&#9679;</span> {n} in-depth review{s} &rarr;</a>"""

def norm(name):
    return re.sub(r"[^a-z0-9]", "", name.lower())

def main():
    root = Path(__file__).parent
    all_tools = json.loads((root / "data.json").read_text(encoding="utf-8"))
    
    target_cats = {"Growth & Revenue", "Communication & Voice", "CRM"}
    tools = [t for t in all_tools if t.get("category") in target_cats]
    tools.sort(key=lambda t: t["name"].lower())

    # Haal AIBM reviews op
    cache = root / "reviews.json"
    counts = {}
    try:
        with urllib.request.urlopen(AIBM_B2B, timeout=20) as r:
            page = r.read().decode("utf-8", errors="replace")
        for tool in re.findall(r'data-tool="([^"]+)"', page):
            counts[tool] = counts.get(tool, 0) + 1
        if counts:
            cache.write_text(json.dumps(counts, indent=1, ensure_ascii=False, sort_keys=True), encoding="utf-8")
    except Exception as e:
        if cache.exists():
            counts = json.loads(cache.read_text(encoding="utf-8"))

    norm_counts = {norm(k): (k, v) for k, v in counts.items()}

    # Bouw de kaarten op (als platte string)
    html_cards = []
    for t in tools:
        hit = norm_counts.get(norm(t["name"]))
        if hit:
            aibm_name, n = hit
            url = f"{AIBM_B2B}?tool={quote(aibm_name)}"
            rev_str = REVIEWS_ROW.format(reviews_url=url, n=n, s="" if n == 1 else "s")
        else:
            rev_str = ""
            
        card_html = CARD.format(
            category_attr=html.escape(t["category"], quote=True),
            category=html.escape(t["category"]),
            domain=html.escape(t.get("domain", "example.com"), quote=True),
            name=html.escape(t["name"]),
            desc=html.escape(t["desc"]),
            link=html.escape(t["link"], quote=True),
            reviews_row=rev_str,
        )
        html_cards.append(card_html)
    
    cards_str = "\n".join(html_cards)
    block_str = f"{START_MARKER}\n{cards_str}\n                {END_MARKER}"

    # Open index.html
    index_path = root / "index.html"
    index_content = index_path.read_text(encoding="utf-8")
    
    if START_MARKER not in index_content or END_MARKER not in index_content:
        raise SystemExit("Error: START of END marker ontbreekt in index.html!")

    # Vlijmscherp splitsen op de markers (100% veilig)
    pre_part = index_content.split(START_MARKER)[0]
    post_part = index_content.split(END_MARKER)[-1]
    
    # Zeker weten dat alles platte tekst is om errors te voorkomen
    new_index = str(pre_part) + str(block_str) + str(post_part)

    # Schema.org JSON updaten
    items = [
        {
            "@type": "ListItem",
            "position": i + 1,
            "name": t["name"],
            "url": f"https://{t['domain']}" if t.get("domain") else None,
        }
        for i, t in enumerate(tools)
    ]
    for it in items:
        if it["url"] is None:
            del it["url"]
            
    itemlist = json.dumps({
        "@context": "https://schema.org",
        "@type": "ItemList",
        "name": "Marketing & Sales Software directory",
        "numberOfItems": len(tools),
        "itemListElement": items,
    }, ensure_ascii=False)
    
    schema_start_tag = '<script type="application/ld+json" id="itemlist-schema">'
    schema_end_tag = '</script>'
    
    if schema_start_tag in new_index:
        s_pre = new_index.split(schema_start_tag)[0]
        s_post = new_index.split(schema_start_tag)[1].split(schema_end_tag, 1)[-1]
        schema_block = f"{schema_start_tag}\n{itemlist}\n{schema_end_tag}"
        new_index = str(s_pre) + str(schema_block) + str(s_post)

    # Schrijf weg naar index.html
    if new_index != index_content:
        index_path.write_text(new_index, encoding="utf-8")
        print(f"✅ index.html bijgewerkt: {len(tools)} kaarten geplaatst.")
    else:
        print("Geen wijzigingen nodig.")

if __name__ == "__main__":
    main()
