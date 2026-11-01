# -*- coding: utf-8 -*-
"""Règle commune § 46 / § 15.7 : une source en panne depuis plus de 2 jours = robot ROUGE (GitHub prévient Ahmed), les données
de la veille restent en ligne. Lit donnees/etat.json (dernier succès de chaque source, écrit par robot/collecte.py).
  python tools/sources_en_panne.py"""
import datetime as dt, json, os, sys

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LIMITE_JOURS = 2
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
try:
    etat = json.load(open(os.path.join(RACINE, "donnees", "etat.json"), encoding="utf-8"))
except (OSError, ValueError):
    sys.exit("ÉCHEC : donnees/etat.json illisible (le robot de collecte n'a jamais tourné ?)")
maintenant = dt.datetime.now(dt.timezone(dt.timedelta(hours=1)))
echecs = []
for nom in ("24h", "168h", "rss"):          # 4 h et 48 h sont des compléments : leur absence n'est pas une panne
    s = etat.get("sources", {}).get(nom)
    if not s:
        echecs.append(f"{nom} : jamais lue"); continue
    d = dt.datetime.strptime(s["dernier_succes"], "%Y-%m-%dT%H:%M:%S").replace(tzinfo=maintenant.tzinfo)
    age = (maintenant - d).total_seconds() / 86400
    if age > LIMITE_JOURS:
        echecs.append(f"{nom} : dernier succès le {s['dernier_succes'][:10]} ({age:.1f} jours)")
    else:
        print(f"OK  {nom} : dernier succès le {s['dernier_succes']}")
if echecs:
    sys.exit("ÉCHEC — source en panne depuis plus de 2 jours : " + " ; ".join(echecs) + " — " + " ; ".join(etat.get("erreurs") or []))
print("Toutes les sources ont répondu depuis moins de 2 jours.")
