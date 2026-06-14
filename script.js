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

document.addEventListener("DOMContentLoaded", () => {
    // Diepe link zoals /#Growth%20%26%20Revenue direct openen
    const fromHash = decodeURIComponent(window.location.hash.slice(1));
    filterTools(categoryInfo[fromHash] ? fromHash : 'All', false);
});

function filterTools(category, updateHash = true) {
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

    // 3. Statische kaarten tonen/verbergen
    document.querySelectorAll('#marketplace-grid .tool-card').forEach(card => {
        const show = category === 'All' || card.dataset.category === category;
        card.style.display = show ? '' : 'none';
    });

    // 4. Categorie deelbaar maken via de URL-hash
    if (updateHash) {
        history.replaceState(null, '', category === 'All' ? '#' : '#' + encodeURIComponent(category));
    }
}
