// De toolkaarten staan statisch in index.html (gegenereerd door build_cards.py
// vanuit data.json — gesynchroniseerd met de centrale affiliate-database via
// GitHub Actions). Dit script filtert alleen nog de bestaande DOM: geen
// runtime-fetch meer nodig, dus de site werkt ook zonder JavaScript en is
// volledig indexeerbaar.

// Vlotte, menselijke omschrijvingen per categorie afgestemd op Marketing & Sales
const categoryInfo = {
    'All': {
        title: "Explore All Tools",
        desc: "The complete arsenal. From inbound marketing automation to AI sales reps, explore every piece of high-intent software we've verified to scale your revenue."
    },
    'Growth & Revenue': {
        title: "Growth & Revenue",
        desc: "The engines of your business. Discover powerful platforms for automated outreach, lead generation, CRM, and scalable marketing campaigns."
    },
    'Communication & Voice': {
        title: "Communication & Voice",
        desc: "Connect clearly and close faster. Explore modern solutions for business VoIP, smart call routing, and autonomous AI voice assistants."
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
