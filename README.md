# Tendances de recherche en Tunisie

Ce que les Tunisiens cherchent sur Google, chaque jour : recherches en forte hausse, nouveautés, catégories, opportunités pour
les entrepreneurs, mots réellement tapés, historique construit jour après jour. Français et arabe. https://tendances.clicvia.com/

Source des données : Google Trends (Tunisie) et suggestions de recherche Google. Site indépendant, non officiel, sans lien avec Google.

## Plan de continuité (le site vit seul)
- `maj.yml` : deux fois par jour, lit Google Trends, enregistre les données, refait les pages, teste, publie (GitHub Pages).
- `mots.yml` : chaque dimanche, relève les suggestions Google.
- `tests.yml` : à chaque envoi, tests du robot, du site et visiteur simulé.
- Une source en panne plus de 2 jours = robot rouge (e-mail GitHub), les données de la veille restent en ligne.
- Données ouvertes : `donnees/analyse.json` (analyse du jour), `donnees/tendances.json` (toutes les tendances vues) — nos relevés datés
  et catégorisés, réutilisables avec la mention « Tendances de recherche en Tunisie (tendances.clicvia.com), d'après Google Trends ».

## Construire sur un PC
```
python robot/collecte.py          # lit Google (ou --local pour ne rien lire)
python robot/analyse.py
python robot/construire_site.py
python tools/test_robot.py ; npm install --no-save --no-package-lock jsdom ; node tools/test_site.mjs
```
© 2026 — tous droits réservés (voir LICENSE).
