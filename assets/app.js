/* Tendances de recherche en Tunisie — listes : filtre par catégorie, recherche dans la page, « Voir les N autres » (règle § 19 :
   10 lignes par défaut), et MASQUAGE de catégories (01/11/2026, Ahmed : « la plupart des recherches sont liées au football ; un filtre pour
   ne pas voir le football, et peut-être le sport, le cinéma et la politique »). Le football est masqué par défaut dans les classements ;
   le visiteur choisit (boutons ⚽ 🏅 🎬 🏛), son choix est gardé sur l'appareil ; une page de catégorie montre toujours sa catégorie.
   Aucun script en ligne (CSP). */
(function () {
  var html = document.documentElement;
  var T = function (fr, ar) { return html.lang === "ar" ? ar : fr; };
  var norm = function (s) { return String(s || "").toLowerCase().normalize("NFD").replace(/[̀-ًͯ-ْ]/g, "").replace(/\s+/g, " ").trim(); };

  // ---- masquage de catégories (gardé dans le navigateur ; défaut : football)
  var MASQUABLES = [["football", "⚽", "Football", "كرة القدم"], ["sport", "🏅", "Autres sports", "رياضات أخرى"],
    ["divertissement", "🎬", "Divertissement", "الترفيه"], ["politique", "🏛️", "Politique", "السياسة"]];
  var CLE = "tendances-masquer";
  function masques() {
    try { var v = localStorage.getItem(CLE); if (v !== null) return JSON.parse(v); } catch (e) {}
    return ["football"];
  }
  function garder(liste) { try { localStorage.setItem(CLE, JSON.stringify(liste)); } catch (e) {} }
  var pageCat = document.body.getAttribute("data-categorie") || "";       // page d'une catégorie : jamais masquée ici

  function appliquerMasque() {
    var m = masques();
    document.querySelectorAll("ul.tendances").forEach(function (liste) {
      Array.prototype.forEach.call(liste.children, function (li) {
        var cat = li.getAttribute("data-cat");
        li.classList.toggle("cachee-masque", !!cat && cat !== pageCat && m.indexOf(cat) >= 0);
      });
      renumeroter(liste);
    });
    document.querySelectorAll(".masquage button").forEach(function (b) {
      var actif = m.indexOf(b.getAttribute("data-cat")) >= 0;
      b.setAttribute("aria-pressed", actif ? "true" : "false");
      b.classList.toggle("actif", actif);
    });
    var n = m.length;
    document.querySelectorAll(".masquage .etat").forEach(function (e) {
      e.textContent = n ? T(n + " catégorie" + (n > 1 ? "s" : "") + " masquée" + (n > 1 ? "s" : "") + " dans les classements", "فئات مخفية من الترتيب: " + n)
        : T("Rien n’est masqué", "لا شيء مخفي");
    });
  }
  function renumeroter(liste) {
    var i = 0;
    Array.prototype.forEach.call(liste.children, function (li) {
      var r = li.querySelector(".rang");
      if (li.classList.contains("cachee-masque") || li.classList.contains("cachee-filtre")) return;
      if (r) r.textContent = ++i;
    });
  }
  function barreMasquage() {
    if (document.querySelector(".masquage") || !document.querySelector("ul.tendances")) return;
    var bar = document.createElement("div"); bar.className = "masquage";
    var lab = document.createElement("span"); lab.className = "masquage-titre"; lab.textContent = T("Masquer :", "إخفاء:"); bar.appendChild(lab);
    MASQUABLES.forEach(function (c) {
      if (c[0] === pageCat) return;
      var b = document.createElement("button"); b.type = "button"; b.setAttribute("data-cat", c[0]);
      b.textContent = c[1] + " " + T(c[2], c[3]);
      b.addEventListener("click", function () {
        var m = masques(), k = m.indexOf(c[0]);
        if (k >= 0) m.splice(k, 1); else m.push(c[0]);
        garder(m); appliquerMasque(); document.querySelectorAll("ul[data-limite]").forEach(limiter); document.querySelectorAll("[data-zone-filtre]").forEach(compter);
      });
      bar.appendChild(b);
    });
    var etat = document.createElement("span"); etat.className = "etat"; bar.appendChild(etat);
    var main = document.querySelector("main");
    if (main) main.insertBefore(bar, main.firstChild);
  }

  // « Voir les N autres » : chaque liste [data-limite] montre d'abord 10 lignes
  function limiter(liste) {
    var n = parseInt(liste.getAttribute("data-limite") || "10", 10);
    var lignes = Array.prototype.filter.call(liste.children, function (li) { return !li.classList.contains("cachee-filtre") && !li.classList.contains("cachee-masque"); });
    var bouton = liste.nextElementSibling && liste.nextElementSibling.classList.contains("voir-plus") ? liste.nextElementSibling : null;
    if (liste.getAttribute("data-ouverte")) { lignes.forEach(function (li) { li.classList.remove("cachee-limite"); }); if (bouton) bouton.hidden = true; return; }
    lignes.forEach(function (li, i) { li.classList.toggle("cachee-limite", i >= n); });
    var reste = Math.max(0, lignes.length - n);
    if (!bouton) {
      bouton = document.createElement("button"); bouton.type = "button"; bouton.className = "voir-plus";
      liste.insertAdjacentElement("afterend", bouton);
      bouton.addEventListener("click", function () { liste.setAttribute("data-ouverte", "1"); limiter(liste); });
    }
    bouton.hidden = reste === 0;
    bouton.textContent = T("Voir les " + reste + " autres", "عرض " + reste + " الأخرى");
    var vide = liste.parentNode.querySelector(".liste-vide");
    if (vide) vide.hidden = lignes.length > 0;
  }

  function compter(zone) {
    var compte = zone.querySelector("[data-compte]");
    if (compte) {
      var n = zone.querySelectorAll("ul[data-limite] > li:not(.cachee-filtre):not(.cachee-masque)").length;
      compte.textContent = T(n + " résultat" + (n > 1 ? "s" : ""), n + " نتيجة");
    }
  }
  function filtrer(zone) {
    var cat = zone.querySelector("[data-filtre-cat]"), q = zone.querySelector("[data-recherche]");
    var vc = cat ? cat.value : "", vq = q ? norm(q.value) : "";
    zone.querySelectorAll("ul[data-limite]").forEach(function (liste) {
      Array.prototype.forEach.call(liste.children, function (li) {
        var ok = (!vc || li.getAttribute("data-cat") === vc) && (!vq || norm(li.getAttribute("data-mot") + " " + li.textContent).indexOf(vq) >= 0);
        li.classList.toggle("cachee-filtre", !ok);
      });
      liste.removeAttribute("data-ouverte"); renumeroter(liste); limiter(liste);
    });
    compter(zone);
  }

  function brancher() {
    barreMasquage();
    appliquerMasque();
    document.querySelectorAll("ul[data-limite]").forEach(limiter);
    document.querySelectorAll("[data-zone-filtre]").forEach(function (zone) {
      if (zone.getAttribute("data-branche")) return;
      zone.setAttribute("data-branche", "1");
      zone.querySelectorAll("[data-filtre-cat], [data-recherche]").forEach(function (c) {
        c.addEventListener(c.tagName === "SELECT" ? "change" : "input", function () { filtrer(zone); });
      });
      var m = location.hash.match(/cat=([a-z]+)/);
      var sel = zone.querySelector("[data-filtre-cat]");
      if (m && sel) { sel.value = m[1]; }
      filtrer(zone);
    });
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", brancher); else brancher();
  document.addEventListener("langue", function () {
    var bar = document.querySelector(".masquage"); if (bar) bar.remove();
    barreMasquage(); appliquerMasque();
    document.querySelectorAll("ul[data-limite]").forEach(limiter); document.querySelectorAll("[data-zone-filtre]").forEach(compter);
  });
})();
