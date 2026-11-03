# Tendances de recherche en Tunisie (tendances-tunisie)

Fichier lu par Claude Code au début de chaque session. **Dépôt PUBLIC : rien de personnel ni de secret, jamais le nom d'un
concurrent.** Répondre à Ahmed **en français**, simplement. Règles communes à tous les sites d'Ahmed : `../../regles communes a tous
les sites.md` (dépôt privé projets-ahmed) ; étude et brief : `../etude de faisabilite 2026-11-01.md`, `../brief d'Ahmed 2026-11-01.md`,
`../etude concurrence et legalite 2026-11-01.md`.

## AVANT TOUT : récupérer le travail fait ailleurs
Ahmed travaille depuis le PC ET depuis son téléphone. Toujours `git pull --rebase --autostash` avant de modifier ; commit + push à la fin.

## Ce que fait le site (décisions d'Ahmed du 01/11/2026 : « puisque c'est faisable, fais tout »)
Observatoire de ce que les Tunisiens cherchent sur Google : recherches en forte hausse (24 h, 7 j), nouveautés (jamais vues),
hausses inhabituelles, qui redescend / qui revient, 17 catégories (les 10 demandées par Ahmed + sport, divertissement, météo,
politique, finance, religion, autre), opportunités commerciales, mots tapés (suggestions Google), historique construit jour après
jour (Google ne garde que 7 jours), une page par mot. Français + arabe + **anglais** (03/11/2026, demande d'Ahmed, exception à la règle
« site Tunisie = fr + ar »), **une adresse par langue** (`ar/`, `en/`). Tout automatique.
Adresse : https://tendances.clicvia.com/ (sous-domaine Cloudflare d'Ahmed, CNAME → ah6259.github.io).

## Sources (étude de légalité du 01/11/2026 — attribution « Source des données : Google Trends » sur chaque page)
- **Tendances du moment** : `trends.google.com/_/TrendsUi/data/batchexecute` (rpc `i0OFE`, la demande de la page publique
  trends.google.com/trending?geo=TN), périodes 4/24/48/168 h ; robot identifié, SANS cookie, sans imitation de navigateur
  (toute méthode « cookie » pour l'API explore est REFUSÉE : contournement anti-robot). Non documenté : format peut changer.
- **RSS officiel** `trends.google.com/trending/rss?geo=TN` (secours, 10 tendances).
- **Suggestions** `suggestqueries.google.com/complete/search?client=firefox&gl=tn` (vrais mots tapés), 1 fois par semaine.
- Pas de régions pour la Tunisie, pas de palmarès absolu, volumes par paliers (jamais additionnés). API officielle Google Trends
  (alpha, candidature) = seule voie vers l'indice 0-100 et 5 ans d'historique : décision d'Ahmed.

## Fichiers
- `robot/commun.py` (réseau prudent : User-Agent, pause 1 s, 3 essais ; dates de Tunis ; normalisation ; slug), `robot/categories.py`
  (17 catégories ; mots-clés FR/AR/tunisien AVANT les codes Google ; `INTENTION` = intention d'achat ; carnet des mots sans catégorie
  `donnees/carnet-categories.json`, règle § 40), `robot/collecte.py` (2×/jour ; mémoire `donnees/tendances.json` = toute tendance vue,
  clé mot normalisé + heure de début ; relevés bruts `donnees/releves/` 60 jours ; `donnees/etat.json` = dernier succès par source),
  `robot/mots.py` (hebdo, `donnees/mots.json` : apparu / vu / meilleur rang), `robot/analyse.py` (→ `donnees/analyse.json`, données
  ouvertes), `robot/construire_site.py` (pages FR, puis AR et EN par `tools/pages_langues.py` copié de Mosquées en version 3 langues) ;
  `robot/anglais.py` = dictionnaire des textes anglais (clé = texte français EXACT) : un texte français sans anglais ARRÊTE la
  construction (« texte(s) sans anglais ») — les textes avec des nombres ont leur anglais en 3e argument de `L()`.
- **Masquage (01/11/2026, Ahmed : « la plupart des recherches sont liées au football »)** : catégorie `football` séparée de `sport`
  (robot/categories.py) ; barre « Masquer » (assets/app.js, clé localStorage `tendances-masquer`, défaut `["football"]`, boutons football /
  sport / divertissement / politique), rangs renumérotés, jamais masqué sur la page de sa catégorie (`body[data-categorie]`) ; tests jsdom.
- Pages : accueil, `semaine/`, `opportunites/`, `mots-tapes/`, `historique/`, `a-propos/` (« Comment fonctionne le site ? », liste
  `FONCTIONS` : toute fonction visible nouvelle = une ligne + son test), `categorie/<clé>/`, `mot/<slug>/` (mots vus ce mois ou
  récurrents ; les anciens dossiers sont retirés à la construction).
- `assets/` : style.css (famille Concours, couleur violet #5B21B6), page.js (en-tête, pied, langue par adresse, partage, anti-copie,
  service worker), app.js (filtres, recherche, « Voir les N autres »), avis.js (Formspree mwlpakqj, e-mail obligatoire), logo.svg, og-image.jpg.
- Robots : `maj.yml` (7h40 et 19h40 : collecte → données enregistrées tout de suite → analyse → pages → tests → pages enregistrées →
  sources en panne), `mots.yml` (dimanche 4h15), `tests.yml` (à chaque envoi : test_robot, test_site, visiteur simulé), gendarme des tests.
- Tests : `python tools/test_robot.py` (42), `node tools/test_site.mjs` (jsdom), `node tools/test_navigateur.mjs` (scripts chargés dans
  <head> comme Chrome : toute erreur JS = rouge ; leçon du 01/11), `python tools/visiteur_simule.py`.
  Construire : `python robot/collecte.py` (réseau) ou `--local`, `python robot/analyse.py`, `python robot/construire_site.py`.
  Envoyer : `bash "../../outils envoi/envoyer_si_vert.sh" "$PWD" "message" "python robot/analyse.py && python robot/construire_site.py" "python tools/test_robot.py" "node tools/test_site.mjs"`.

## Décisions en attente d'Ahmed
- Candidature à l'API officielle Google Trends (formulaire public, compte Google d'Ahmed).
- Partie payante (règle commune § 11 : gratuit + payant dès le départ) : rien de payant en v1 ; idées : rapport mensuel par
  catégorie, alertes « nouveau mot dans ma catégorie » par e-mail/Telegram, accès aux données détaillées. À décider.
- Régions (gouvernorats) : impossible avec Google Trends pour la Tunisie ; seule l'API officielle (sous-régions) pourrait l'ouvrir.
