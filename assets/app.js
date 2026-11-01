/* Tendances de recherche en Tunisie — listes : filtre par catégorie, recherche dans la page, « Voir les N autres » (règle § 19 :
   10 lignes par défaut), tri. Aucun script en ligne (CSP). */
(function () {
  var html = document.documentElement;
  var T = function (fr, ar) { return html.lang === "ar" ? ar : fr; };
  var norm = function (s) { return String(s || "").toLowerCase().normalize("NFD").replace(/[̀-ًͯ-ْ]/g, "").replace(/\s+/g, " ").trim(); };

  // « Voir les N autres » : chaque liste [data-limite] montre d'abord 10 lignes
  function limiter(liste) {
    var n = parseInt(liste.getAttribute("data-limite") || "10", 10);
    var lignes = Array.prototype.filter.call(liste.children, function (li) { return !li.classList.contains("cachee-filtre"); });
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
  }

  function filtrer(zone) {
    var cat = zone.querySelector("[data-filtre-cat]"), q = zone.querySelector("[data-recherche]");
    var vc = cat ? cat.value : "", vq = q ? norm(q.value) : "";
    zone.querySelectorAll("ul[data-limite]").forEach(function (liste) {
      var visibles = 0;
      Array.prototype.forEach.call(liste.children, function (li) {
        var ok = (!vc || li.getAttribute("data-cat") === vc) && (!vq || norm(li.getAttribute("data-mot") + " " + li.textContent).indexOf(vq) >= 0);
        li.classList.toggle("cachee-filtre", !ok); if (ok) visibles++;
      });
      liste.removeAttribute("data-ouverte"); limiter(liste);
      var vide = liste.parentNode.querySelector(".liste-vide");
      if (vide) vide.hidden = visibles > 0;
    });
    var compte = zone.querySelector("[data-compte]");
    if (compte) {
      var n = zone.querySelectorAll("ul[data-limite] > li:not(.cachee-filtre)").length;
      compte.textContent = T(n + " résultat" + (n > 1 ? "s" : ""), n + " نتيجة");
    }
  }

  function brancher() {
    document.querySelectorAll("ul[data-limite]").forEach(limiter);
    document.querySelectorAll("[data-zone-filtre]").forEach(function (zone) {
      if (zone.getAttribute("data-branche")) return;
      zone.setAttribute("data-branche", "1");
      zone.querySelectorAll("[data-filtre-cat], [data-recherche]").forEach(function (c) {
        c.addEventListener(c.tagName === "SELECT" ? "change" : "input", function () { filtrer(zone); });
      });
      // choix de catégorie venu de l'adresse (#cat=immobilier)
      var m = location.hash.match(/cat=([a-z]+)/);
      var sel = zone.querySelector("[data-filtre-cat]");
      if (m && sel) { sel.value = m[1]; }
      filtrer(zone);
    });
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", brancher); else brancher();
  document.addEventListener("langue", function () { document.querySelectorAll("ul[data-limite]").forEach(limiter); document.querySelectorAll("[data-zone-filtre]").forEach(filtrer); });
})();
