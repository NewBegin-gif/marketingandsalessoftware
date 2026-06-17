// De toolkaarten staan statisch in index.html (gegenereerd door build_cards.py
// vanuit data.json — gesynchroniseerd met de centrale affiliate-database via
// GitHub Actions). Dit script filtert alleen nog de bestaande DOM: geen
// runtime-fetch meer nodig, dus de site werkt ook zonder JavaScript en is
// volledig indexeerbaar.

// Vlotte, menselijke omschrijvingen per categorie
const categoryInfo = {
    'All': {
        title: "Explore All Tools",
        desc: "Browsing the full collection. From accounting platforms to AI-driven design tools, explore every piece of software we've handpicked to scale your business."
    },
    'Financial Operations': {
        title: "Financial Operations",
        desc: "Keep your numbers straight and your cash flowing. Dive into top-tier tools for accounting, automated payroll, tax compliance, and seamless invoicing."
    },
    'Growth & Revenue': {
        title: "Growth & Revenue",
        desc: "The engines that drive your business forward. Discover powerful platforms for marketing automation, sales outreach, CRM, and social media management."
    },
    'Operations & Workflow': {
        title: "Operations & Workflow",
        desc: "Keep the chaos at bay. We've highlighted the best software for project management, team collaboration, document creation, and building solid SOPs."
    },
    'Communication & Voice': {
        title: "Communication & Voice",
        desc: "Connect clearly and professionally. Explore modern solutions for business VoIP, smart call centers, live chat, and autonomous AI voice assistants."
    },
    'IT & Productivity': {
        title: "IT & Productivity",
        desc: "The silent backbone of your daily operations. Equip your team with essential tools for cybersecurity, cloud storage, web hosting, and advanced AI infrastructure."
    }
};

// Zoek × categorie: substring-match op naam (h3) + beschrijving (p) + categorie.
let _cat = 'All', _q = '', _bundle = null;
const BUNDLES = {
 outbound:{label:'Cold Outreach Machine',desc:'Find, enrich and close leads at scale.',tools:['Clay','Reply.io','Close','Salesmessage']},
 content:{label:'Content & Social',desc:'Create and schedule across every channel.',tools:['Later','SocialBee','AdCreative.ai','Beehiiv']},
 emailcrm:{label:'Email & CRM',desc:'Capture, nurture and convert from one place.',tools:['Brevo','ActiveCampaign','folk','Nutshell']}
};
function _cardName(card){return ((card.querySelector('h3')||{}).innerText||'').trim();}
function _cardMatch(card) {
    const base = _bundle ? (BUNDLES[_bundle].tools.indexOf(_cardName(card)) >= 0)
                         : (_cat === 'All' || card.dataset.category === _cat);
    if (!base) return false;
    if (!_q) return true;
    const txt = (((card.querySelector('h3') || {}).innerText || '') + ' ' +
                 ((card.querySelector('p') || {}).innerText || '') + ' ' +
                 (card.dataset.category || '')).toLowerCase();
    return txt.indexOf(_q) >= 0;
}
function selectBundle(key){
    _bundle = (_bundle === key) ? null : key;
    if (_bundle) _cat = 'All';
    document.querySelectorAll('.cat-btn').forEach(b => b.classList.toggle('active', !_bundle && b.innerText === 'All Tools'));
    document.querySelectorAll('.bundle-btn').forEach(b => {
        const on = !!_bundle && b.dataset.bundle === _bundle;
        b.classList.toggle('bg-indigo-600', on); b.classList.toggle('text-white', on); b.classList.toggle('border-indigo-500', on);
    });
    const info = _bundle ? BUNDLES[_bundle] : categoryInfo['All'];
    const t = document.getElementById('category-title'), d = document.getElementById('category-desc');
    if (t) t.innerText = info.label || info.title;
    if (d) d.innerText = info.desc;
    applyGrid();
    if (typeof gtag === 'function') gtag('event', 'bundle_select', { bundle: _bundle || 'cleared' });
}
function applyGrid() {
    const grid = document.getElementById('marketplace-grid');
    if (!grid) return;
    let total = 0;
    grid.querySelectorAll('.tool-card').forEach(card => {
        const ok = _cardMatch(card);
        card.style.display = ok ? '' : 'none';
        if (ok) total++;
    });
    let nr = document.getElementById('osm-no-results');
    if (!nr) {
        nr = document.createElement('div');
        nr.id = 'osm-no-results';
        nr.className = 'col-span-full text-center text-slate-500 py-8';
        nr.textContent = 'No tools match your search.';
        grid.appendChild(nr);
    }
    nr.style.display = total ? 'none' : '';
}
function searchTools(q) { _q = (q || '').trim().toLowerCase(); applyGrid(); }

document.addEventListener("DOMContentLoaded", () => {
    // Diepe link zoals /#Growth%20%26%20Revenue direct openen
    const fromHash = decodeURIComponent(window.location.hash.slice(1));
    filterTools(categoryInfo[fromHash] ? fromHash : 'All', false);
});

function filterTools(category, updateHash = true) {
    _bundle = null;
    document.querySelectorAll('.bundle-btn').forEach(b => b.classList.remove('bg-indigo-600','text-white','border-indigo-500'));
    // 1. Actieve knop bijwerken
    document.querySelectorAll('.cat-btn').forEach(btn => {
        if (btn.innerText === category || (category === 'All' && btn.innerText === 'All Tools')) {
            btn.classList.add('active');
        } else {
            btn.classList.remove('active');
        }
    });

    // 2. Dynamische infokaart bijwerken
    const cardElement = document.getElementById('category-info-card');
    const titleElement = document.getElementById('category-title');
    const descElement = document.getElementById('category-desc');

    cardElement.style.opacity = 0;
    setTimeout(() => {
        const info = categoryInfo[category] || categoryInfo['All'];
        titleElement.innerText = info.title;
        descElement.innerText = info.desc;
        cardElement.style.opacity = 1;
    }, 150);

    // 3. Categorie-state + grid toepassen (zoekterm × categorie)
    _cat = category;
    applyGrid();

    // 4. Categorie deelbaar maken via de URL-hash
    if (updateHash) {
        history.replaceState(null, '', category === 'All' ? '#' : '#' + encodeURIComponent(category));
    }
}
