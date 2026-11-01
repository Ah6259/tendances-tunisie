// Test du site Tendances de recherche en Tunisie (après « python robot/construire_site.py ») :
//   npm install --no-save --no-package-lock jsdom ; node tools/test_site.mjs
// Minimums, jamais des nombres exacts (le robot qui ajoute ne doit jamais être bloqué).
import { readFileSync, existsSync, readdirSync } from "fs";
import { join, dirname } from "path";
import { fileURLToPath } from "url";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const lire = f => readFileSync(join(root, f), "utf8");
let ok = 0, ko = 0;
const check = (nom, cond) => { if (cond) ok++; else { ko++; console.log("ÉCHEC " + nom); } };
const SITE = "https://tendances.clicvia.com/";

const A = JSON.parse(lire("donnees/analyse.json"));
const M = JSON.parse(lire("donnees/tendances.json"));
const CATS = ["immobilier", "automobile", "emploi", "education", "tourisme", "sante", "commerce", "technologie", "administration", "energie", "finance", "football", "sport", "divertissement", "meteo", "politique", "religion", "autre"];
const fixes = ["", "semaine/", "opportunites/", "mots-tapes/", "historique/", "a-propos/", ...CATS.map(c => `categorie/${c}/`)];
const mots = readdirSync(join(root, "mot")).map(m => `mot/${m}/`);
const pages = [...fixes, ...mots];

// ---- 1. données
check("données : au moins 50 tendances en mémoire, chacune avec mot, catégorie, première et dernière lecture", Object.keys(M.tendances).length >= 50
  && Object.values(M.tendances).every(t => t.mot && t.categorie && t.vu_premier && t.vu_dernier));
check("données : l'analyse a une date, des listes et les 17 catégories", A.maj && Array.isArray(A.aujourdhui) && Array.isArray(A.semaine) && CATS.every(c => A.categories[c]));
check("données : chaque tendance de la semaine a un volume ou une hausse (jamais vide)", A.semaine.every(x => x.volume || x.hausse));
check("données : au moins 20 pages de mots", A.pages_mots.length >= 20 && mots.length >= 20);

// ---- 2. toutes les pages : FR + AR, en-tête, sécurité, propre
for (const p of pages) {
  const fr = p + "index.html", ar = "ar/" + p + "index.html";
  check(`${p || "accueil"} : existe en français et en arabe`, existsSync(join(root, fr)) && existsSync(join(root, ar)));
  if (!existsSync(join(root, fr)) || !existsSync(join(root, ar))) continue;
  const h = lire(fr), ha = lire(ar);
  const propre = x => /<title>[^<]{10,}<\/title>/.test(x) && /name="description" content="[^"]{30,}"/.test(x) && x.includes('http-equiv="Content-Security-Policy"')
    && /content="(noindex, follow, )?noai, noimageai"/.test(x) && !/undefined|NaN|\[object|None\b/.test(x.replace(/"@type"|lastmod/g, ""))
    && !/<script>(?!\s*$)/.test(x.replace(/<script type="application\/ld\+json">[\s\S]*?<\/script>/g, "")) && (x.match(/<h1[ >]/g) || []).length === 1
    && x.includes("Source des données") && x.includes("google.com/trends");
  check(`${p || "accueil"} : titre, description, CSP, noai, un seul h1, source Google Trends citée, aucun trou`, propre(h) && propre(ha));
  check(`${p || "accueil"} : adresse officielle + hreflang fr/ar/x-default identiques sur les 2 versions`,
    h.includes(`<link rel="canonical" href="${SITE}${p}">`) && ha.includes(`<link rel="canonical" href="${SITE}ar/${p}">`)
    && [`hreflang="fr" href="${SITE}${p}"`, `hreflang="ar" href="${SITE}ar/${p}"`, `hreflang="x-default" href="${SITE}${p}"`].every(l => h.includes(l) && ha.includes(l)));
  check(`${p || "accueil"} : page française bilingue (data-l), page arabe lang=ar dir=rtl sans texte français caché`,
    h.includes('<html lang="fr"') && h.includes('data-l="ar"') && ha.includes('<html lang="ar" dir="rtl"') && !ha.includes('data-l="fr"') && ha.includes('data-fixe'));
  check(`${p || "accueil"} : scripts du site seulement (page.js, app.js, avis.js), ?v= identique`,
    ["page.js", "app.js", "avis.js"].every(s => h.includes(`assets/${s}?v=`)) && new Set([...h.matchAll(/\?v=([0-9a-f]{8})/g)].map(m => m[1])).size === 1);
}
check("version ?v= identique sur toutes les pages (règle § 21)", new Set(pages.map(p => (lire(p + "index.html").match(/\?v=([0-9a-f]{8})/) || [])[1])).size === 1);

// ---- 3. accueil
const acc = lire("index.html");
check("accueil : chiffres (aujourd'hui, semaine, nouveautés, mots suivis)", (acc.match(/class="chiffre"/g) || []).length >= 4);
check("accueil : listes Aujourd'hui, Nouveautés, Hausses, Opportunités (aperçu), Qui redescend / revient", ["aujourdhui", "nouveautes", "hausses", "opportunites-apercu", "retombees", "recurrents"].every(i => acc.includes(`id="${i}"`)));
check("accueil : grille des 17 catégories, chacune vers sa page", CATS.every(c => acc.includes(`href="categorie/${c}/"`)) && acc.includes('id="categories"'));
check("accueil : chaque ligne = mot (lien vers sa page), catégorie, nombres ; limite de 10 lignes", /<li class="tendance" data-cat="[a-z]+" data-mot="[^"]+"><span class="rang">1<\/span><span class="mot" dir="(ltr|rtl)"><a href="mot\/[^"]+\/">/.test(acc) && acc.includes('data-limite="10"'));
check("accueil : « Comment ça marche » compact (details) + lien vers À propos", acc.includes('id="comment"') && acc.includes('href="a-propos/"'));
check("accueil : section Votre avis (e-mail obligatoire, Formspree mwlpakqj, champs site et page, piège)", acc.includes('id="avis-form"') && acc.includes("formspree.io/f/mwlpakqj")
  && /name="email"[^>]*required/.test(acc) && acc.includes('name="site" value="Tendances de recherche en Tunisie"') && acc.includes('name="page"') && acc.includes('name="_gotcha"'));
check("accueil : JSON-LD WebSite + Dataset (données ouvertes)", acc.includes('"@type": "WebSite"') && acc.includes('"@type": "Dataset"') && acc.includes("donnees/analyse.json"));
check("accueil : aperçu de partage JPEG 1200×630 présent", acc.includes("assets/og-image.jpg") && existsSync(join(root, "assets/og-image.jpg")) && acc.includes('og:image:width" content="1200"'));
check("accueil : site tout neuf expliqué OU plus de 14 jours de relevés", acc.includes('class="premiere"') || (new Date(A.jour) - new Date(A.totaux.premiere_lecture.slice(0, 10))) / 864e5 >= 14);

// ---- 4. pages spéciales
const sem = lire("semaine/index.html");
check("semaine : filtre catégorie + recherche + compte + liste limitée", sem.includes("data-filtre-cat") && sem.includes("data-recherche") && sem.includes("data-compte") && sem.includes('id="semaine"'));
check("semaine : les 17 catégories dans le filtre", CATS.every(c => sem.includes(`<option value="${c}">`)));
const opp = lire("opportunites/index.html");
check("opportunités : méthode expliquée + liste (ou texte « pas d'opportunité ») + lien mots tapés", opp.includes("Comment on les repère") && (opp.includes('id="opportunites"') || opp.includes("Pas d’opportunité")) && opp.includes('href="../mots-tapes/"'));
const mt = lire("mots-tapes/index.html");
check("mots tapés : explication + 3 sections (nouvelles, par catégorie, disparues)", mt.includes("suggestions") && mt.includes("Nouvelles expressions") && mt.includes("Par catégorie") && mt.includes("Expressions qui ont disparu"));
const hist = lire("historique/index.html");
check("historique : frise par jour + semaines + mois", hist.includes('class="frise"') && hist.includes("Par semaine") && hist.includes("Par mois") && hist.includes('class="barre"'));
for (const c of CATS) {
  const h = lire(`categorie/${c}/index.html`);
  check(`catégorie ${c} : h1 propre, liste ou texte vide, liens vers les autres catégories`, /<h1>/.test(h) && (h.includes('id="cat-semaine"')) && CATS.filter(x => x !== c).every(x => h.includes(`categorie/${x}/`)));
}
// pages de mots
for (const pm of A.pages_mots.slice(0, 30)) {
  const h = lire(`mot/${pm.slug}/index.html`).replace(/&#x27;|&#39;/g, "'");
  check(`mot « ${pm.mot} » : titre avec le mot, épisodes, catégorie, lien Google Trends, fil d'Ariane JSON-LD`,
    h.includes(`« ${pm.mot.replace(/&/g, "&amp;")} »`) && h.includes("Les fois où ce mot est monté") && h.includes(`categorie/${pm.categorie}/`) && h.includes("trends.google.com/trends/explore?geo=TN") && h.includes('"BreadcrumbList"'));
}
check("mots : aucune page orpheline (chaque dossier mot/ est dans l'analyse)", mots.every(m => A.pages_mots.some(pm => `mot/${pm.slug}/` === m)));

// ---- 5. « Comment fonctionne le site ? » (règle § 44) : chaque fonction visible est expliquée en FR et en AR
const ap = lire("a-propos/index.html"), apa = lire("ar/a-propos/index.html");
const FONCTIONS = [
  ["liste Aujourd'hui", acc.includes('id="aujourdhui"'), /Aujourd’hui.*24 heures/, /اليوم.*24 ساعة/],
  ["Nouveautés", acc.includes('id="nouveautes"'), /Nouveautés.*jamais vus/, /الجديد.*لم تظهر/],
  ["Hausses inhabituelles", acc.includes('id="hausses"'), /Hausses inhabituelles.*500/, /ارتفاعات غير معتادة.*500/],
  ["Opportunités", existsSync(join(root, "opportunites/index.html")), /Opportunités.*intention/, /الفرص.*نية/],
  ["Catégories", acc.includes('id="categories"'), /catégorie \(immobilier/, /فئة \(عقارات/],
  ["Mots tapés", existsSync(join(root, "mots-tapes/index.html")), /Mots tapés.*suggestions|Mots tapés.*propose/, /الكلمات المكتوبة.*يقترحها/],
  ["Historique", existsSync(join(root, "historique/index.html")), /Historique.*par jour, par semaine et par mois/, /السجل.*اليوم والأسبوع والشهر/],
  ["page de chaque mot", mots.length > 0, /Chaque mot a sa page/, /لكل كلمة صفحتها/],
  ["Qui redescend / revient", acc.includes('id="retombees"'), /Qui redescend.*3 jours/, /ما يتراجع.*3 أيام/],
  ["filtres et Voir les N autres", sem.includes("data-filtre-cat"), /filtrent par catégorie.*Voir les N autres/, /تُصفّى حسب الفئة/],
  ["masquer le football", lire("assets/app.js").includes("tendances-masquer"), /Masquer.*football par défaut/, /إخفاء.*كرة القدم افتراضيًا/],
  ["deux langues", existsSync(join(root, "ar/index.html")), /français et en arabe.*adresse/, /بالفرنسية والعربية.*عنوانها/],
  ["bouton Partager", lire("assets/page.js").includes("partagerLien"), /bouton rond « Partager »/, /الزر الدائري «شارك»/],
  ["Votre avis", acc.includes('id="avis-form"'), /Votre avis.*e-mail obligatoire/, /رأيك.*البريد الإلكتروني إجباري/],
  ["données ouvertes", existsSync(join(root, "donnees/analyse.json")), /données ouvertes.*analyse\.json/, /بيانات مفتوحة.*analyse\.json/],
  ["mise à jour automatique", existsSync(join(root, ".github/workflows/maj.yml")), /deux lectures par jour.*une par semaine/, /قراءتان في اليوم.*واحدة في الأسبوع/],
];
const manque = [];
for (const [nom, sur, fr, ar] of FONCTIONS) if (sur && !(fr.test(ap.replace(/&#39;|&#x27;/g, "’")) && ar.test(apa))) manque.push(nom);
check(`À propos : chaque fonction du site expliquée en FR et AR (${FONCTIONS.length} fonctions)` + (manque.length ? " — manque : " + manque.join(", ") : ""), manque.length === 0);
check("À propos : méthode, limites, données ouvertes, FAQ JSON-LD", ap.includes("D’où viennent les chiffres") && ap.includes("ne disent pas") && ap.includes('id="donnees"') && ap.includes('"FAQPage"'));

// ---- 6. fichiers de visibilité et de sécurité (règle § 8, consigne sécurité)
const plan = lire("sitemap.xml"), robots = lire("robots.txt");
check("sitemap : toutes les pages FR et AR, avec lastmod, hreflang, aucune adresse étrangère", pages.every(p => plan.includes(`<loc>${SITE}${p}</loc>`) && plan.includes(`<loc>${SITE}ar/${p}</loc>`))
  && /<lastmod>\d{4}-\d{2}-\d{2}<\/lastmod>/.test(plan) && [...plan.matchAll(/<loc>([^<]+)<\/loc>/g)].every(m => m[1].startsWith(SITE)) && !plan.includes("ah6259.github.io"));
check("robots.txt : moteurs autorisés, robots d'IA d'entraînement refusés, assistants qui citent autorisés, Sitemap", robots.includes("User-agent: Googlebot\nAllow: /") && robots.includes("User-agent: GPTBot\nDisallow: /")
  && robots.includes("User-agent: ClaudeBot\nDisallow: /") && robots.includes("OAI-SearchBot") && robots.includes(`Sitemap: ${SITE}sitemap.xml`));
check("llms.txt, manifeste, service worker, clé IndexNow, licence, favicon, icônes", ["llms.txt", "manifest.webmanifest", "sw.js", "377f054ba9c5ed40d6796adc8d87d1e8.txt", "LICENSE", "favicon.ico", "assets/icons/icon-192.png", "assets/icons/icon-512.png", "assets/icons/icon-maskable-512.png", "assets/apple-touch-icon.png"].every(f => existsSync(join(root, f))));
check("aucun lien vers une ancienne adresse ni vers un concurrent", !pages.some(p => /ah6259\.github\.io|semrush|similarweb|exploding/i.test(lire(p + "index.html"))));
check("lien « Tous nos services » vers clicvia.com dans le pied (page.js)", lire("assets/page.js").includes('https://clicvia.com/'));
check("aucun secret dans le dépôt", !/ghp_[A-Za-z0-9]{20,}|github_pat_|[0-9]{8,10}:[A-Za-z0-9_-]{30,}|EAA[A-Za-z0-9]{40,}/.test(pages.map(p => lire(p + "index.html")).join("") + lire("robot/collecte.py") + lire("robot/mots.py")));
check("manifeste : id, icônes maskable, couleur du thème", (() => { const m = JSON.parse(lire("manifest.webmanifest")); return m.id && m.icons.some(i => i.purpose === "maskable") && m.theme_color === "#5B21B6"; })());

// ---- 7. avec jsdom : en-tête, pied, langue, listes « Voir les N autres », filtre
let JSDOM = null;
try { ({ JSDOM } = await import("jsdom")); } catch (e) { console.log("(jsdom absent : tests navigateur sautés)"); }
if (JSDOM) {
  const ouvrir = async (f, url) => {
    const dom = new JSDOM(lire(f), { url: url || SITE + f.replace(/index\.html$/, ""), runScripts: "outside-only", pretendToBeVisual: true });
    dom.window.allerVers = u => { dom.window.__alle = u; };
    for (const s of ["assets/page.js", "assets/app.js", "assets/avis.js"]) dom.window.eval(lire(s));
    dom.window.document.dispatchEvent(new dom.window.Event("DOMContentLoaded"));
    await new Promise(r => setTimeout(r, 30));
    return dom.window;
  };
  const w = await ouvrir("index.html");
  const d = w.document;
  // masquage (01/11/2026, Ahmed) : football caché par défaut, rangs renumérotés, bouton pour le remontrer ; page de catégorie jamais masquée
  const footAcc = d.querySelectorAll('ul.tendances > li[data-cat="football"]');
  check("jsdom : barre « Masquer » présente, football masqué par défaut dans les classements", d.querySelector(".masquage button[data-cat=football][aria-pressed=true]") && [...footAcc].every(li => li.classList.contains("cachee-masque")));
  check("jsdom : les rangs visibles recommencent à 1 sans trou", (() => { const r = [...d.querySelectorAll("#semaine > li:not(.cachee-masque) .rang, #aujourdhui > li:not(.cachee-masque) .rang")].slice(0, 5).map(x => +x.textContent); return r.length === 0 || r[0] === 1; })());
  d.querySelector(".masquage button[data-cat=football]").click();
  check("jsdom : un clic remontre le football et garde le choix", d.querySelector(".masquage button[data-cat=football][aria-pressed=false]") && [...footAcc].every(li => !li.classList.contains("cachee-masque")) && w.localStorage.getItem("tendances-masquer") === "[]");
  w.localStorage.removeItem("tendances-masquer");
  const wf = await ouvrir("categorie/football/index.html");
  check("jsdom : la page de la catégorie Football montre ses lignes malgré le masquage par défaut", wf.document.body.getAttribute("data-categorie") === "football" && [...wf.document.querySelectorAll('ul.tendances > li[data-cat="football"]')].every(li => !li.classList.contains("cachee-masque")));
  check("jsdom : en-tête avec logo, bouton Partager, bouton de langue, lien Opportunités", d.querySelector("#entete .logo") && d.querySelector("#entete .partager") && d.querySelector("#entete .langue") && d.querySelector('#entete a[href$="opportunites/"]'));
  check("jsdom : pied de page avec les rubriques et « Tous nos services »", d.querySelectorAll("#pied nav a").length >= 7 && d.querySelector('#pied a[href="https://clicvia.com/"]'));
  check("jsdom : liste Aujourd'hui limitée à 10 + bouton « Voir les N autres »", d.querySelectorAll("#aujourdhui > li:not(.cachee-limite)").length <= 10 && (d.querySelector("#aujourdhui + .voir-plus") || d.querySelectorAll("#aujourdhui > li").length <= 10));
  d.querySelector("#entete .langue").click();
  check("jsdom : le bouton de langue sur la page française OUVRE l'adresse arabe", w.__alle === "/ar/");
  const wa = await ouvrir("ar/index.html");
  check("jsdom : page arabe : lang=ar, en-tête en arabe, bouton « Fr » ouvre la page française", wa.document.documentElement.lang === "ar" && wa.document.querySelector("#entete .logo-nom").textContent.includes("اتجاهات")
    && (wa.document.querySelector("#entete .langue").click(), wa.__alle === "/"));
  const ws = await ouvrir("semaine/index.html");
  const sel = ws.document.querySelector("[data-filtre-cat]");
  sel.value = "sport"; sel.dispatchEvent(new ws.window.Event("change"));
  const vis = [...ws.document.querySelectorAll("#semaine > li:not(.cachee-filtre)")];
  check("jsdom : le filtre « sport » ne laisse que des lignes sport (ou aucune)", vis.every(li => li.getAttribute("data-cat") === "sport"));
  const q = ws.document.querySelector("[data-recherche]");
  q.value = "zzzz-introuvable"; q.dispatchEvent(new ws.window.Event("input"));
  check("jsdom : une recherche sans résultat montre le texte « Aucune tendance »", ws.document.querySelectorAll("#semaine > li:not(.cachee-filtre)").length === 0 && !ws.document.querySelector("#semaine ~ .liste-vide").hidden);
  // sabotage du test lui-même (règle : un test doit sonner) : une page sans CSP doit être vue
  check("sabotage : une page sans CSP serait refusée", !(/http-equiv="Content-Security-Policy"/.test(acc.replace('http-equiv="Content-Security-Policy"', ""))));
}

console.log(`${ok} vérifications réussies, ${ko} échec(s)`);
process.exit(ko ? 1 : 0);
