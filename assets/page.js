/* Tendances de recherche en Tunisie — repris de Concours (clicvia) : langue, en-tête et pied de page communs, partage, anti-copie, service worker */
// Trois langues depuis le 03/11/2026 (demande d'Ahmed) : fr (adresse d'origine), ar/ et en/ ; n'accepter que ces trois codes.
(function () {
  const html = document.documentElement;
  const racine = html.dataset.racine || "";
  const LANGUES = ["fr", "ar", "en"];
  const valide = l => LANGUES.includes(l || "") ? l : null;
  let langue = "fr";
  try { langue = valide(localStorage.getItem("langue")) || (navigator.language || "").startsWith("ar") && "ar" || "fr"; } catch (e) {}
  const demande = valide(new URLSearchParams(location.search).get("lang"));
  if (demande) langue = demande;

  window.T = (fr, ar, en) => html.lang === "ar" ? ar : html.lang === "en" ? (en === undefined ? fr : en) : fr;
  // Nombres et dates isolés dans un texte arabe (U+2066 … U+2069)
  window.iso = t => "⁦" + t + "⁩";

  const NOMS = { fr: ["Fr", "Français"], ar: ["ع", "العربية"], en: ["En", "English"] };
  function cadre() {
    const rp = html.dataset.racinePages !== undefined ? html.dataset.racinePages : racine;   // liens vers les pages : dans la langue
    const e = document.getElementById("entete");
    if (e) e.innerHTML = `
      <div class="wrap">
        <a class="logo" href="${rp || "./"}">
          <img class="logo-mark" src="${racine}assets/logo.svg" alt="" width="34" height="34">
          <span class="logo-nom">${T("Tendances Tunisie", "اتجاهات تونس", "Trends Tunisia")}
            <small>${T("ce que les Tunisiens cherchent sur Google", "ماذا يبحث التونسيون على غوغل", "what Tunisians search on Google")}</small></span>
        </a>
        <div class="entete-boutons">
          <a class="entete-pro" href="${rp}opportunites/">${T("Opportunités", "الفرص", "Opportunities")}</a>
          <button class="partager" type="button" aria-label="${T("Partager cette page", "شارك هذه الصفحة", "Share this page")}" title="${T("Partager", "شارك", "Share")}"><svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><path d="M8.6 13.5l6.8 4M15.4 6.5l-6.8 4"/></svg></button>
          ${LANGUES.filter(l => l !== html.lang).map(l => `<button class="langue" type="button" data-l="${l}" aria-label="${NOMS[l][1]}" title="${NOMS[l][1]}">${NOMS[l][0]}</button>`).join("")}
        </div>
      </div>`;
    const p = document.getElementById("pied");
    const maj = document.body.dataset.majTexte || "";
    if (p) p.innerHTML = `
      <div class="wrap">
        <div class="pied-logo"><img src="${racine}assets/logo.svg" alt="" width="24" height="24"> ${T("Tendances de recherche en Tunisie", "اتجاهات البحث في تونس", "Search trends in Tunisia")}</div>
        <nav>
          <a href="${rp || "./"}">${T("Aujourd'hui", "اليوم", "Today")}</a>
          <a href="${rp}semaine/">${T("Cette semaine", "هذا الأسبوع", "This week")}</a>
          <a href="${rp}opportunites/">${T("Opportunités", "الفرص", "Opportunities")}</a>
          <a href="${rp}mots-tapes/">${T("Mots tapés", "الكلمات المكتوبة", "Typed words")}</a>
          <a href="${rp}historique/">${T("Historique", "السجل", "History")}</a>
          <a href="${rp}a-propos/">${T("Comment fonctionne le site ?", "كيف يعمل الموقع؟", "How does the site work?")}</a>
          <a href="${rp}#avis">${T("Votre avis", "رأيك", "Your feedback")}</a>
          <a href="https://clicvia.com/" rel="noopener" target="_blank">${T("Tous nos services", "كل خدماتنا", "All our services")}</a>
        </nav>
        <p>${T(`Source des données : <a href="https://trends.google.com/trending?geo=TN" rel="noopener" target="_blank">Google Trends</a> (tendances de recherche en Tunisie) et suggestions de recherche Google. Les volumes sont des ordres de grandeur donnés par Google, pas des nombres exacts.`,
               `مصدر البيانات: <a href="https://trends.google.com/trending?geo=TN" rel="noopener" target="_blank">Google Trends</a> (اتجاهات البحث في تونس) واقتراحات بحث غوغل. الأحجام تقديرية كما يعطيها غوغل، وليست أرقامًا دقيقة.`,
               `Data source: <a href="https://trends.google.com/trending?geo=TN" rel="noopener" target="_blank">Google Trends</a> (search trends in Tunisia) and Google search suggestions. Volumes are orders of magnitude given by Google, not exact numbers.`)}</p>
        ${maj ? `<p>${T("Dernière lecture de la source : ", "آخر قراءة للمصدر: ", "Last reading of the source: ")}${iso(maj)}</p>` : ""}
        <p>${T("Site indépendant, non officiel, sans lien avec Google. Les marques citées appartiennent à leurs propriétaires.",
               "موقع مستقل وغير رسمي، لا علاقة له بغوغل. العلامات المذكورة ملك لأصحابها.",
               "Independent, unofficial site, unrelated to Google. Brands mentioned belong to their owners.")}</p>
        <p>© 2026 ${T("Tendances de recherche en Tunisie — tous droits réservés.", "اتجاهات البحث في تونس — جميع الحقوق محفوظة.", "Search trends in Tunisia — all rights reserved.")}</p>
      </div>`;
    document.querySelectorAll(".langue").forEach(b =>
      b.addEventListener("click", () => appliquer(b.getAttribute("data-l") || "fr", true)));
    // bouton Partager (demande d'Ahmed) : menu de partage du téléphone, sinon WhatsApp avec le lien de la page
    document.querySelectorAll(".partager").forEach(b => b.addEventListener("click", async () => {
      const url = location.href.split("#")[0].replace(/[?&]lang=(fr|ar|en)/, ""), titre = document.title.split(" | ")[0];
      try { if (window.goatcounter && window.goatcounter.count) window.goatcounter.count({ path: "partage" + location.pathname.replace(/^\/tendances-tunisie\//, "/"), title: "Partage", event: true }); } catch (e) {}
      return window.partagerLien();
    }));
  }

  // UNE ADRESSE PAR LANGUE (règle commune § 8, point 9) : la page française (adresse d'origine) contient les trois langues ; la page
  // arabe (ar/) et la page anglaise (en/), attribut data-fixe, ne contiennent que la leur. Choisir une autre langue OUVRE son adresse ;
  // un ancien lien « ?lang=ar » et un choix déjà fait mènent à la bonne adresse. Jamais de changement d'après la langue du téléphone seule.
  const BASE = /\.github\.io$/.test(location.hostname) ? "/tendances-tunisie/" : "/";
  const ici0 = location.pathname.replace(/index\.html$/, "");
  const adresseDe = l => BASE + (l === "fr" ? "" : l + "/") + (html.dataset.chemin || "");
  const FIXE = html.dataset.fixe !== undefined && html.dataset.chemin !== undefined;
  const aller = (l, remplacer) => {
    const q = new URLSearchParams(location.search); q.delete("lang");
    const u = adresseDe(l) + (q.toString() ? "?" + q : "") + location.hash;
    if (window.allerVers) return window.allerVers(u);
    if (remplacer) location.replace(u); else location.assign(u);
  };
  function appliquer(l, clic) {
    if (FIXE && l !== html.lang && (clic || ici0 === adresseDe(html.lang))) {
      try { localStorage.setItem("langue", l); } catch (e) {}
      return aller(l, !clic);
    }
    html.lang = l; html.dir = l === "ar" ? "rtl" : "ltr";
    try { localStorage.setItem("langue", l); } catch (e) {}
    cadre();
    document.dispatchEvent(new Event("langue"));
  }
  window.appliquerLangue = l => appliquer(l, true);
  document.addEventListener("DOMContentLoaded", () => {
    if (FIXE) {
      let choisie = null; try { choisie = localStorage.getItem("langue"); } catch (e) {}
      const voulue = demande || valide(choisie);
      if (voulue && voulue !== html.lang) return aller(voulue, true);
      return appliquer(html.lang);
    }
    appliquer(langue);
  });


  // ---- Protection légère contre la copie (sans gêner les visiteurs) -------------------------
  // 1) Pas d'affichage dans le cadre (iframe) d'un autre site.
  try {
    if (window.top !== window.self && window.top.location.hostname !== location.hostname) window.top.location = location.href;
  } catch (e) { try { window.top.location = location.href; } catch (e2) {} }
  // 2) Images et photos : ni clic droit ni glisser-déposer.
  const estImage = t => t && t.closest && t.closest("img, svg, .hero-photo, .carte-tn");
  document.addEventListener("contextmenu", e => { if (estImage(e.target) && !e.target.closest("a, input, textarea")) e.preventDefault(); });
  document.addEventListener("dragstart", e => { if (estImage(e.target)) e.preventDefault(); });
  // 3) Texte copié depuis une carte : on ajoute la source et la mention « tous droits réservés ».
  document.addEventListener("copy", e => {
    const sel = window.getSelection ? String(window.getSelection()) : "";
    const n = window.getSelection && window.getSelection().anchorNode;
    const el = n && (n.nodeType === 1 ? n : n.parentElement);
    if (!sel || !el || !el.closest || !el.closest(".tendance, .liste, main") || el.closest("input, textarea")) return;
    if (!e.clipboardData) return;
    e.clipboardData.setData("text/plain", sel + "\n\nSource : " + location.href.split("#")[0] + " — © Tendances de recherche en Tunisie, tous droits réservés.");
    e.preventDefault();
  });
})();

/* Installation sur le téléphone : service worker PRUDENT (sw.js : réseau d'abord pour les pages et les données).
   Seulement en https (jamais en file: pendant les tests locaux). */
if ("serviceWorker" in navigator && location.protocol === "https:") {
  window.addEventListener("load", () => {
    try { navigator.serviceWorker.register(BASE_SITE + "sw.js", { scope: BASE_SITE }).catch(() => {}); } catch (e) { /* rien : le site marche sans */ }
  });
}

/* >>> vidéo de présentation : page video/ partagée par le bouton « Partager » (outil vidéos d'Ahmed) */
/* Adresse du site (11 octobre 2026) : concours.clicvia.com (racine « / ») ; l'ancienne adresse ah6259.github.io/alerte-concours-tunisie/ redirige
   vers elle. BASE_SITE = dossier du site selon l'adresse ; GoatCounter garde le préfixe /alerte-concours-tunisie (compteur commun). */
var BASE_SITE = /\.github\.io$/.test(location.hostname) ? "/tendances-tunisie/" : "/";
window.goatcounter = window.goatcounter || {};
window.goatcounter.path = function (p) { return BASE_SITE === "/" ? "/tendances-tunisie" + p : p; };
window.VIDEO_SITE = {"base": BASE_SITE, "defaut": "fr", "video": false, "nom": {"fr": "Tendances de recherche en Tunisie", "ar": "اتجاهات البحث في تونس", "en": "Search trends in Tunisia"}};
/* « video": false » (25/10/2026) : la page video/ n'existe pas encore -> aucun lien « Vidéo de présentation » et le bouton
   « Partager » partage la page en cours. Le jour où la vidéo est faite : retirer « "video": false » (pas de vidéo = pas de lien). */
/* Bouton « Partager » (demande d'Ahmed, octobre 2026) : partage un LIEN vers la page vidéo du site (qui montre la vidéo
   de présentation, avec un gros bouton « Ouvrir le site ») + l'adresse du site dans le texte. WhatsApp et Facebook
   affichent l'aperçu de la page vidéo (grande image, vidéo lisible sur Facebook). Menu de partage du téléphone, sinon WhatsApp.
   Espace professionnels des annuaires : page « video-pro/ ». Réglages : window.VIDEO_SITE (juste au-dessus). */
(function () {
  var S = window.VIDEO_SITE, ORIGINE = S.base === "/" ? "https://tendances.clicvia.com" : "https://ah6259.github.io";
  function langue() { return document.documentElement.lang || S.defaut; }
  function M(o) { return o[langue()] || o[S.defaut] || o.fr; }
  // page vidéo à partager (et page du site correspondante) selon la page où l'on est
  window.pageVideo = function () {
    var chemin = location.pathname, pro = false;
    for (var i = 0; i < (S.pro || []).length; i++) if (chemin.indexOf(S.base + S.pro[i]) === 0) pro = true;
    var l = langue(), q = l !== S.defaut ? "?lang=" + l : "";
    return { page: ORIGINE + S.base + (pro ? "video-pro/" : "video/") + q, site: ORIGINE + S.base + (pro ? S.site_pro : "") + q + (pro ? (S.ancre_pro || "") : ""),
             titre: M(pro ? S.titre_pro : S.nom) };
  };
  window.partagerLien = function (titre, site) {
    var v = window.pageVideo(), t = titre || v.titre, texte;
    if (site) v.site = site;
    if (S.video === false) {
      t = titre || document.title.split(" | ")[0] || v.titre;
      v.page = site || (location.origin + location.pathname).replace(/index\.html$/, "");
      texte = t;
    } else {
      texte = t + "\n" + M({ fr: "Le site : ", ar: "الموقع: ", en: "The website: " }) + v.site + "\n" + M({ fr: "Regardez la vidéo :", ar: "شاهد الفيديو:", en: "Watch the video:" });
    }
    function whatsapp() { window.open("https://wa.me/?text=" + encodeURIComponent(texte + " " + v.page), "_blank", "noopener"); return "whatsapp"; }
    if (navigator.share) {
      return navigator.share({ title: t, text: texte, url: v.page }).then(function () { return "lien"; }, function (e) {
        return e && e.name === "AbortError" ? "annule" : whatsapp();
      });
    }
    return Promise.resolve(whatsapp());
  };
  // page vidéo : textes dans la langue de la page (data-vfr / data-var / data-ven), vidéo de la langue (data-src-fr…)
  function traduire() {
    var l = langue();
    var el = document.querySelectorAll("[data-vfr]");
    for (var i = 0; i < el.length; i++) { var t = el[i].getAttribute("data-v" + l) || el[i].getAttribute("data-v" + S.defaut); if (t && el[i].textContent !== t) el[i].textContent = t; }
    var v = document.querySelector(".video-lecteur");
    if (v) {
      var s = v.getAttribute("data-src-" + l) || v.getAttribute("data-src-defaut") || v.getAttribute("src");
      if (!v.getAttribute("data-src-defaut")) v.setAttribute("data-src-defaut", v.getAttribute("src"));
      if (v.getAttribute("src") !== s) v.setAttribute("src", s);
      if (!v.getAttribute("data-poster-defaut")) v.setAttribute("data-poster-defaut", v.getAttribute("poster"));
      var po = v.getAttribute("data-poster-" + l) || v.getAttribute("data-poster-defaut");
      if (v.getAttribute("poster") !== po) v.setAttribute("poster", po);
    }
    // lien discret « Vidéo de présentation » en bas de l'accueil et de À propos -> la page vidéo
    var p = location.pathname.replace(/index\.html$/, "");
    if (S.video === false) { var ancien = document.getElementById("lien-video"); if (ancien) ancien.remove(); }
    else if (p === S.base || p === S.base + "a-propos/") {
      var b = document.getElementById("lien-video");
      if (!b) {
        b = document.createElement("p"); b.id = "lien-video"; b.className = "lien-video"; b.appendChild(document.createElement("a"));
        var m = document.querySelector("main"); if (m) m.insertAdjacentElement("afterend", b); else document.body.appendChild(b);
      }
      b.firstChild.href = S.base + "video/" + (l !== S.defaut ? "?lang=" + l : "");
      b.firstChild.textContent = M({ fr: "Vidéo de présentation", ar: "الفيديو التقديمي", en: "Presentation video" });
    }
  }
  document.addEventListener("click", function (e) {
    var b = e.target && e.target.closest && e.target.closest("[data-partager-video]");
    if (!b) return;
    e.preventDefault();
    try { if (window.goatcounter && window.goatcounter.count) window.goatcounter.count({ path: "partage" + location.pathname.replace(S.base, "/"), title: "Partage", event: true }); } catch (x) {}
    window.partagerLien();
  });
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", function () { setTimeout(traduire, 0); }); else setTimeout(traduire, 0);
  document.addEventListener("langue", function () { setTimeout(traduire, 0); });
  try { new MutationObserver(function () { setTimeout(traduire, 0); }).observe(document.documentElement, { attributes: true, attributeFilter: ["lang"] }); } catch (x) {}
})();
/* <<< vidéo de présentation */
