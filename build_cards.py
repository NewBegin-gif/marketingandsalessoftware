#!/usr/bin/env python3
"""Bouwt de statische toolkaarten in index.html uit data.json, zodat de
directory indexeerbaar is zonder JavaScript. Draait in de GitHub Action
(sync-data.yml) na elke update van de centrale affiliate-database.

Telt daarnaast per tool de in-depth reviews op aibuildermarketplace.com
(data-tool-attributen op /b2b/) en toont die op de kaart met een link naar
de artikelen. Lukt het ophalen niet, dan valt het terug op reviews.json.

Gebruik: python3 build_cards.py
"""
import html
import json
import re
import urllib.request
from pathlib import Path
from urllib.parse import quote



KAART_CSS = """/* FILTER */
.filter-bar{display:flex;justify-content:center;gap:8px;margin-bottom:40px;flex-wrap:wrap}
.filter-btn{background:var(--surface);border:1px solid var(--border);color:var(--text-2);padding:8px 16px;border-radius:999px;font-size:.85rem;font-weight:500;transition:all .15s}
.filter-btn:hover{border-color:var(--border-hi);color:var(--text)}
.filter-btn.active{background:var(--text);border-color:var(--text);color:var(--bg)}
/* TOOLS GRID */
.tools-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:20px}
.tool-card{background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);padding:26px 26px 22px;transition:border-color .25s var(--ease),transform .25s var(--ease),box-shadow .25s var(--ease);display:flex;flex-direction:column;position:relative;overflow:hidden;box-shadow:var(--shadow-card)}
.tool-card:hover{border-color:var(--border-hi);transform:translateY(-3px);box-shadow:0 12px 32px -16px rgba(0,0,0,.6)}
.tool-card.featured{border-color:rgba(59,130,246,.4)}
.tool-card.featured::before{content:'';position:absolute;inset:0;background:radial-gradient(circle at 0% 0%,rgba(59,130,246,.08),transparent 50%);pointer-events:none}
.tool-card-top{display:flex;justify-content:space-between;align-items:flex-start;gap:10px;margin-bottom:14px}
.tool-card-header{display:flex;align-items:center;gap:14px;min-width:0}
.tool-logo{width:42px;height:42px;border-radius:10px;flex-shrink:0;display:flex;align-items:center;justify-content:center;font-weight:800;font-size:1.1rem;color:#fff;letter-spacing:-.02em}
.tool-card h3{font-size:1.15rem;font-weight:700;letter-spacing:-.01em}
.tool-badge{font-size:.66rem;font-weight:700;text-transform:uppercase;letter-spacing:.08em;padding:4px 8px;border-radius:6px;white-space:nowrap;flex-shrink:0}
.tool-badge.pick{background:rgba(59,130,246,.12);color:var(--accent-2);border:1px solid rgba(59,130,246,.25)}
.tool-badge.deal{background:rgba(34,197,94,.1);color:var(--green);border:1px solid rgba(34,197,94,.22)}
.tool-rating{display:flex;align-items:center;gap:8px;margin-top:24px;margin-bottom:10px;font-size:.82rem;color:var(--text-2)}
.tool-rating .stars{color:var(--amber);letter-spacing:1px}
.tool-desc{color:var(--text-2);font-size:.92rem;line-height:1.6;flex-grow:1;margin-bottom:16px}
.tool-tags{display:flex;flex-wrap:wrap;gap:6px;margin-bottom:20px}
.tool-tag{font-size:.72rem;font-weight:500;color:var(--text-3);background:var(--surface-2);border:1px solid var(--border);padding:3px 9px;border-radius:6px}
.tool-cta-row{display:flex;gap:10px;align-items:center}
.tool-cta-primary{flex:1;background:var(--text);color:var(--bg);padding:11px 14px;border-radius:9px;font-weight:600;font-size:.88rem;text-align:center;transition:opacity .15s,transform .15s;display:inline-flex;align-items:center;justify-content:center;gap:6px}
.tool-cta-primary:hover{opacity:.88;transform:translateY(-1px)}
.tool-cta-secondary{color:var(--accent-2);font-size:.85rem;font-weight:600;transition:gap .15s;display:inline-flex;align-items:center;gap:5px;white-space:nowrap}
.tool-cta-secondary:hover{gap:9px}
.tools-grid,.how-grid,.social-grid{grid-template-columns:repeat(2,1fr)}
.tools-grid,.social-grid{grid-template-columns:1fr}
@media(max-width:960px){.tools-grid,.how-grid,.social-grid{grid-template-columns:repeat(2,1fr)}
 .how-grid{grid-template-columns:1fr}
 .footer-inner{grid-template-columns:1fr 1fr 1fr}
 .compare-card{grid-template-columns:1fr;text-align:left}}
@media(max-width:720px){.nav-inner{flex-wrap:nowrap;gap:10px}
 .nav-links{overflow-x:auto;-webkit-overflow-scrolling:touch;scrollbar-width:none;flex-wrap:nowrap;white-space:nowrap;mask-image:linear-gradient(90deg,#000 88%,transparent)}
 .nav-links::-webkit-scrollbar{display:none}
 .nav-links a{font-size:.78rem;margin-left:12px;flex-shrink:0}
 .nav-links a.nav-cta{display:none}
 .nav-links .nav-dd{display:contents}
 .nav-links .nav-dd-toggle{display:none}
 .nav-links .nav-dd-menu{display:contents !important;position:static;background:none;border:0;box-shadow:none;padding:0;margin:0}
 .nav-links .nav-dd-menu a{padding:0;border-radius:0;font-size:.78rem;margin-left:12px;flex-shrink:0}
 .hero{padding:130px 24px 60px}
 .stats-inner{grid-template-columns:repeat(2,1fr)}
 .stat-item:nth-child(2){border-right:none}
 .stat-item:nth-child(1),.stat-item:nth-child(2){border-bottom:1px solid var(--border)}
 .tools-grid,.social-grid{grid-template-columns:1fr}
 .section{padding:70px 24px 40px}
 .how-section{padding:70px 24px;margin-top:50px}
 .footer-inner{grid-template-columns:1fr 1fr;gap:28px}
 .footer-bottom{flex-direction:column;text-align:center}
 .cta-inner{padding:44px 24px}
 .mobile-cta{display:block}
 body{padding-bottom:76px}
 .trust-band-inner{font-size:.7rem;gap:14px}}"""

PALET = "--bg:#020617;--bg-2:#0b1120;--surface:#0f172a;--surface-2:#1e293b;--border:#1e293b;--border-hi:#334155;--text:#f8fafc;--text-2:#cbd5e1;--text-3:#94a3b8;--accent:#818cf8;--accent-2:#a5b4fc;--green:#34d399;--amber:#fbbf24;--radius:16px;--radius-sm:11px;--max:1200px;--ease:cubic-bezier(.22,.68,.24,1);--shadow-card:0 1px 0 rgba(255,255,255,.035) inset,0 24px 48px -28px rgba(0,0,0,.75);--shadow-pop:0 20px 60px -18px rgba(0,0,0,.8);"

KNOP = ("filter-btn")


def filterknoppen(tools):
    """De knoppenrij uit dezelfde tools als de kaarten.

    Hardgecodeerd liep hij scheef zodra de snede veranderde: drie knoppen
    filterden naar nul kaarten en vier aanwezige categorieen hadden er geen.
    """
    kl = ("cat-btn px-6 py-2.5 rounded-full border border-slate-700/50 "
          "bg-slate-900/50 text-sm font-medium text-slate-400 hover:text-white "
          "hover:border-slate-500 transition-all duration-300 backdrop-blur-sm")
    cats = sorted({t["category"] for t in tools if t.get("category")})
    rij = [f'<button onclick="filterTools(\'All\')" data-cat="All" '
           f'class="{kl} active">All Tools</button>']
    for c in cats:
        v = html.escape(c, quote=True)
        rij.append(f'<button onclick="filterTools(\'{v}\')" data-cat="{v}" '
                   f'class="{kl}">{html.escape(c)}</button>')
    return "\n                ".join(rij)


FILTER_JS = """<script id="aibm-filter">
window.filterTools = function (c) {
  document.querySelectorAll('.cat-btn').forEach(function (b) {
    b.classList.toggle('active', b.dataset.cat === c);
  });
  document.querySelectorAll('article.tool-card').forEach(function (k) {
    k.style.display = (c === 'All' || k.dataset.category === c) ? '' : 'none';
  });
};
</script>"""

def _kaart_desc(t, grens=300):
    """Kaarttekst afklemmen op zinsgrens.

    4 aug 2026: het desc-veld uit de affiliate-database wordt hier letterlijk
    gerenderd. De mediaan is 152 tekens, maar verrijking heeft er bij zestien
    tools een alinea van gemaakt — Amplemarket stond op 2.269 en trok de hele
    grid scheef. De volledige tekst blijft in de database staan (hij komt
    nergens anders voor); alleen de kaart toont een kortere versie.

    Zoveel hele zinnen als er binnen de limiet passen. Past er geen enkele hele
    zin, dan knippen op een woordgrens met één beletselteken — maar niet als de
    knip al op interpunctie eindigt, want "wint.…" leest als een typefout.
    """
    d = (t.get("desc") or "").strip()
    if len(d) <= grens:
        return d
    kort = d[:grens]
    zinseindes = [m.end() for m in re.finditer(r"[.!?](?:\s|$)", kort)]
    if zinseindes:
        return kort[:zinseindes[-1]].strip()
    knip = kort.rsplit(" ", 1)[0].rstrip(",;:— ")
    return knip if knip.endswith((".", "!", "?")) else knip + "\u2026"



START = "<!-- TOOLS:START (auto-generated by build_cards.py — niet handmatig bewerken) -->"
END = "<!-- TOOLS:END -->"
AIBM_B2B = "https://aibuildermarketplace.com/b2b/"

CARD = """\
<article class="tool-card fade-in" data-category="{category_attr}">
 <div class="tool-card-top">
  <div class="tool-card-header">
   <div class="tool-logo" style="background:#fff;box-sizing:border-box;padding:5px">
    <img src="https://logo.clearbit.com/{domain}" alt="{name}" loading="lazy" decoding="async" style="width:100%;height:100%;object-fit:contain" onerror="this.onerror=null;this.src='https://www.google.com/s2/favicons?domain={domain}&amp;sz=64'">
   </div>
   <h3>{name}</h3>
  </div>
  <span class="tool-badge pick">{category}</span>
 </div>{alt_row}{reviews_row}
 <p class="tool-desc">{desc}</p>
 <div class="tool-cta-row">
  <a href="{link}" target="_blank" rel="sponsored noopener noreferrer" class="tool-cta-primary">Visit {name} <span aria-hidden="true">&rarr;</span></a>
 </div>
</article>"""

# rel=nofollow sinds 12 aug 2026: kruislinks naar een site van dezelfde
# eigenaar mogen lezers sturen, maar geen ranking-signaal dragen.
# (Deze kopie miste de patch die osm/build_cards.py wel kreeg.)
REVIEWS_ROW = """
                    <a href="{reviews_url}" target="_blank" rel="nofollow noopener" class="inline-flex items-center gap-1.5 text-xs text-indigo-300 hover:text-white mb-3 transition-colors"><span class="text-emerald-400">&#9679;</span> {n} in-depth review{s} &rarr;</a>"""


DIRECT_REVIEWS = {
    "Aspire": ("https://aibuildermarketplace.com/b2b/aspire-review/", 1),
    "1Password": ("https://aibuildermarketplace.com/b2b/1password-review/", 1),
    "Payoneer": ("https://aibuildermarketplace.com/b2b/payoneer-review/", 1),
    "NordVPN": ("https://aibuildermarketplace.com/b2b/nordvpn-review/", 1),
    "Apollo": ("https://aibuildermarketplace.com/b2b/apollo-review/", 1),
    "Streak": ("https://aibuildermarketplace.com/b2b/streak-review/", 1),
    "AWeber": ("https://aibuildermarketplace.com/b2b/aweber-review/", 1),
}


ALT_ROW = """\n                    <div class="text-[11px] text-slate-500 mb-3">&#8596; Alternative to <span class="text-slate-300 font-medium">{leader}</span></div>"""


def alt_row_for(t):
    r = t.get("replaces")
    return ALT_ROW.format(leader=html.escape(r)) if r else ""


def norm(name):
    return re.sub(r"[^a-z0-9]", "", name.lower())


def fetch_review_counts(root):
    """Tel data-tool-voorkomens op de live AIBM-reviewsindex; cache in reviews.json."""
    cache = root / "reviews.json"
    try:
        with urllib.request.urlopen(AIBM_B2B, timeout=20) as r:
            page = r.read().decode("utf-8", errors="replace")
        counts = {}
        for tool in re.findall(r'data-tool="([^"]+)"', page):
            counts[tool] = counts.get(tool, 0) + 1
        if counts:
            cache.write_text(json.dumps(counts, indent=1, ensure_ascii=False, sort_keys=True), encoding="utf-8")
            return counts
    except Exception as e:
        print(f"waarschuwing: AIBM-fetch mislukt ({e}); gebruik cache")
    if cache.exists():
        return json.loads(cache.read_text(encoding="utf-8"))
    return {}



SITEMAP = "https://aibuildermarketplace.com/sitemap.xml"


def fetch_review_slugs(root):
    """Welke reviewpagina's bestaan er op AIBM? Uit de sitemap, met cache.

    Waarom niet het bestandssysteem: de oude aanpak keek naar een map naast
    deze repo, en die bestaat alleen lokaal. In de GitHub Action was hij altijd
    leeg, waardoor 310 tools geen deeplink kregen en er maar 7 overbleven uit
    een handmatig lijstje.
    """
    cache = root / "review_slugs.json"
    try:
        with urllib.request.urlopen(SITEMAP, timeout=25) as r:
            xml = r.read().decode("utf-8", errors="replace")
        slugs = sorted(set(re.findall(r"/b2b/([a-z0-9-]+-review)/", xml)))
        if slugs:
            cache.write_text(json.dumps(slugs, indent=1), encoding="utf-8")
            return set(slugs)
    except Exception as e:
        print(f"waarschuwing: sitemap-fetch mislukt ({e}); gebruik cache")
    if cache.exists():
        return set(json.loads(cache.read_text(encoding="utf-8")))
    return set()

# ── De snede van deze site ────────────────────────────────────────────────
# 1 sep 2026, zelfde ingreep als op officesoftwaremarketplace: deze pagina
# toonde de hele centrale database als kaartenlijst. Zo'n mega-pagina met
# honderden sponsored links en enkele tientallen woorden per tool is de
# dunne-affiliate-vorm die AIBM in juni heeft geraakt.
#
# Marketing & Sales Software houdt de categorieen die bij zijn naam horen.
# De rest blijft op aibuildermarketplace.com staan, waar het dossier hoort.
SNEDE = {
    "Growth & Revenue",
    "Marketing",
    "SEO & Marketing",
    "Sales & CRM",
    "E-commerce",
}


def in_snede(t):
    return t.get("category") in SNEDE


EIGEN_REVIEW_ROW = (
    '<a href="{url}" class="mt-3 inline-flex items-center gap-1 text-xs '
    'font-medium text-indigo-400 hover:text-indigo-300">Read our {name} '
    'review &rarr;</a>'
)


def eigen_review(root, naam):
    """Pad naar onze eigen reviewpagina op deze site, of None."""
    slug = re.sub(r"[^a-z0-9]+", "-", naam.lower()).strip("-") + "-review"
    return f"{slug}.html" if (root / f"{slug}.html").is_file() else None


def main():
    root = Path(__file__).parent
    tools = json.loads((root / "data.json").read_text(encoding="utf-8"))
    THEME = ("Growth & Revenue", "Communication & Voice", "Marketing", "SEO & Marketing")
    tools = [t for t in tools if t["category"] in THEME]
    voor = len(tools)
    tools = [t for t in tools if in_snede(t)]
    tools.sort(key=lambda t: t["name"].lower())
    print(f"snede: {len(tools)} van {voor} tools")

    raw_counts = fetch_review_counts(root)
    counts = {norm(k): (k, v) for k, v in raw_counts.items()}

    # De reviewpagina's uit de sitemap in plaats van uit een map naast deze
    # repo — dat pad bestaat niet in de GitHub Action, waardoor hier jarenlang
    # een lege verzameling stond en vrijwel geen tool een deeplink kreeg.
    review_folders = fetch_review_slugs(root)
    aibm_b2b = root.parent / "aibuildermarketplace-main" / "b2b"
    if aibm_b2b.is_dir():
        review_folders |= {p.name for p in aibm_b2b.iterdir() if p.is_dir()}

    def _rslug(name):
        return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-") + "-review"

    # ecosysteem-UTM zodat cross-site clicks naar AIBM als 'ecosystem' attribueren
    # i.p.v. (direct)/(none) in GA4
    def _eco(u):
        return u + ("&" if "?" in u else "?") + "utm_source=marketingandsalessoftware&utm_medium=ecosystem"

    def reviews_row(t):
        # 1 sep 2026: heeft deze site zelf een review, dan wint die. De pagina op
        # AIBM is sindsdien een samenvatting die hierheen canoniekt.
        _eigen = eigen_review(root, t["name"])
        if _eigen:
            return EIGEN_REVIEW_ROW.format(url=_eigen, name=html.escape(t["name"]))
        # directe deeplink als de review als map bestaat (sterker voor SEO; werkt ook
        # vóór Victors live-index-scan), anders DIRECT_REVIEWS of de ?tool=-filter
        rs = _rslug(t["name"])
        hit = counts.get(norm(t["name"]))
        if rs in review_folders:
            n = hit[1] if hit else DIRECT_REVIEWS.get(t["name"], (None, 1))[1]
            return REVIEWS_ROW.format(reviews_url=_eco(f"https://aibuildermarketplace.com/b2b/{rs}/"),
                                      n=n, s="" if n == 1 else "s")
        direct = DIRECT_REVIEWS.get(t["name"])
        if direct:
            url, n = direct
            return REVIEWS_ROW.format(reviews_url=_eco(url), n=n, s="" if n == 1 else "s")
        if not hit:
            return ""
        aibm_name, n = hit
        url = f"{AIBM_B2B}?tool={quote(aibm_name)}"
        return REVIEWS_ROW.format(reviews_url=_eco(url), n=n, s="" if n == 1 else "s")

    matched = sum(1 for t in tools if norm(t["name"]) in counts)
    print(f"review-koppeling: {matched} van {len(tools)} tools hebben AIBM-reviews")

    cards = "\n".join(
        CARD.format(
            category_attr=html.escape(t["category"], quote=True),
            category=html.escape(t["category"]),
            domain=html.escape(t.get("domain", "example.com"), quote=True),
            name=html.escape(t["name"]),
            desc=html.escape(_kaart_desc(t)),
            link=html.escape(t["link"], quote=True),
            reviews_row=reviews_row(t),
            alt_row=alt_row_for(t),
        )
        for t in tools
    )

    index = (root / "index.html").read_text(encoding="utf-8")
    # het onaangeroerde origineel bewaren: de injectie hieronder wijzigt
    # `index`, en dan zou de vergelijking aan het eind zijn eigen
    # wijziging niet meer zien
    _origineel = index

    # kaart-CSS van AIBM, in het palet van deze site. Gemarkeerd blok, zodat een
    # herbouw hem vervangt in plaats van er nog een toe te voegen.
    _css = (f"<style id=\"aibm-kaarten\">:root{{{PALET}}}\n{KAART_CSS}</style>\n{FILTER_JS}")
    # eerst alle eerder ingespoten blokken weg, anders stapelen ze op
    for _pat in (r'<style id="aibm-kaarten">.*?</style>',
                 r'<script id="aibm-filter">.*?</script>',
                 r'<script>\s*document\.querySelectorAll\(\'\.filter-btn\'\).*?</script>'):
        index = re.sub(_pat, "", index, flags=re.S)
    index = index.replace("</head>", _css + "\n</head>", 1)

    # knoppenrij uit dezelfde tools als de kaarten
    _knoppen = filterknoppen(tools)
    # de rij bevat alleen <button>-elementen, dus dit sluit exact af
    index, _n = re.subn(
        r'(<div[^>]*id="filter-buttons">)(?:\s*<button\b.*?</button>)+(\s*</div>)',
        lambda m: m.group(1) + "\n                " + _knoppen + m.group(2),
        index, count=1, flags=re.S)
    if not _n:
        print("  let op: knoppenrij niet vervangen")
    pattern = re.compile(re.escape(START) + ".*?" + re.escape(END), re.S)
    block = f"{START}\n{cards}\n                {END}"
    if not pattern.search(index):
        raise SystemExit("Markers TOOLS:START/TOOLS:END niet gevonden in index.html")
    new_index = pattern.sub(lambda m: block, index)

    # JSON-LD ItemList synchroon houden
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
    itemlist = json.dumps(
        {
            "@context": "https://schema.org",
            "@type": "ItemList",
            "name": "Office Software Marketplace directory",
            "numberOfItems": len(tools),
            "itemListElement": items,
        },
        ensure_ascii=False,
    )
    new_index = re.sub(
        r'(<script type="application/ld\+json" id="itemlist-schema">).*?(</script>)',
        lambda m: m.group(1) + itemlist + m.group(2),
        new_index,
        flags=re.S,
    )

    if new_index != _origineel:
        (root / "index.html").write_text(new_index, encoding="utf-8")
        print(f"index.html bijgewerkt: {len(tools)} kaarten")
    else:
        print(f"geen wijzigingen ({len(tools)} kaarten)")


if __name__ == "__main__":
    main()
