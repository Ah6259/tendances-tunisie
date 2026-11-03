// Test « comme un vrai navigateur » (01/11/2026) : les scripts du site sont chargés dans <head>, AVANT le corps de la page.
// Le 01/11, app.js lisait document.body au chargement : aucune erreur dans les tests jsdom habituels (scripts lancés après la page),
// mais tout le script plantait en ligne (plus de barre « Masquer », plus de « Voir les N autres »). Ici, la page est chargée avec ses
// scripts EN LIGNE, exactement comme Chrome le fait : la moindre erreur JavaScript = test rouge.
//   npm install --no-save --no-package-lock jsdom ; node tools/test_navigateur.mjs
import { readFileSync } from "fs";
import { join, dirname } from "path";
import { fileURLToPath } from "url";
const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const lire = f => readFileSync(join(root, f), "utf8");
const { JSDOM } = await import("jsdom");
let ok = 0, ko = 0;
const check = (nom, cond) => { if (cond) ok++; else { ko++; console.log("ÉCHEC " + nom); } };
const PAGES = ["index.html", "semaine/index.html", "categorie/football/index.html", "ar/index.html", "en/index.html", "en/semaine/index.html", "a-propos/index.html"];
for (const p of PAGES) {
  const base = "../".repeat(p.split("/").length - 1);
  const html = lire(p).replace(/<script src="([^"]+\.js)\?v=[0-9a-f]+"><\/script>/g, (m, src) => {
    const chemin = src.replace(/^(\.\.\/)+/, "").replace(/^assets\//, "assets/");
    return "<script>" + lire(chemin.startsWith("assets/") ? chemin : "assets/" + chemin.split("assets/").pop()) + "</script>";
  });
  const erreurs = [];
  const dom = new JSDOM(html, { runScripts: "dangerously", pretendToBeVisual: true, url: "https://tendances.clicvia.com/" + p.replace(/index\.html$/, "") });
  dom.window.addEventListener("error", e => erreurs.push(e.message));
  dom.window.allerVers = () => {};
  await new Promise(r => setTimeout(r, 250));
  const d = dom.window.document;
  check(`${p} : aucune erreur JavaScript au chargement${erreurs.length ? " — " + erreurs[0] : ""}`, erreurs.length === 0);
  check(`${p} : en-tête et pied fabriqués, listes repliées (Voir les N autres) quand elles dépassent 10`,
    d.querySelector("#entete .logo") && d.querySelector("#pied nav") && [...d.querySelectorAll("ul[data-limite]")].every(u => u.querySelectorAll("li:not(.cachee-limite):not(.cachee-masque):not(.cachee-filtre)").length <= parseInt(u.getAttribute("data-limite"), 10)));
  if (p === "index.html") check("accueil : barre « Masquer » présente et football masqué", d.querySelector(".masquage") && [...d.querySelectorAll('li[data-cat="football"]')].every(li => li.classList.contains("cachee-masque")));
  if (p === "categorie/football/index.html") check("catégorie football : ses lignes restent visibles", [...d.querySelectorAll('li[data-cat="football"]')].every(li => !li.classList.contains("cachee-masque")));
  if (p === "en/index.html") check("accueil anglais : en-tête « Trends Tunisia », barre « Hide: », bouton « Show N more » en anglais", d.querySelector("#entete .logo-nom").textContent.includes("Trends Tunisia") && d.querySelector(".masquage").textContent.includes("Hide:") && [...d.querySelectorAll(".voir-plus")].every(b => /^Show \d+ more$/.test(b.textContent)));
}
console.log(`${ok} vérifications réussies, ${ko} échec(s)`);
process.exit(ko ? 1 : 0);
