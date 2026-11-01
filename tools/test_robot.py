# -*- coding: utf-8 -*-
"""Tests du robot (sans réseau) : python tools/test_robot.py
Décodage des réponses enregistrées (tools/exemples/), normalisation, catégories, fusion dans la mémoire, analyse sur des données inventées."""
import datetime as dt, json, os, sys

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.dirname(ICI)
sys.path.insert(0, os.path.join(RACINE, "robot"))
import commun as C          # noqa: E402
import categories as K      # noqa: E402
import collecte as R        # noqa: E402
import analyse as A         # noqa: E402

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
ok = ko = 0


def check(nom, cond):
    global ok, ko
    if cond:
        ok += 1
    else:
        ko += 1; print("ÉCHEC " + nom)


# ---- 1. décodage du service « tendances du moment » (réponse enregistrée le 01/11/2026)
brut = open(os.path.join(ICI, "exemples", "tendances-du-moment-168h.txt"), encoding="utf-8").read()
lus = R.analyser_batch(brut)
check("tendances du moment : au moins 100 lignes décodées sur 7 jours", len(lus) >= 100)
check("chaque ligne a un mot, un début, un volume et des codes", all(x["mot"] and x["debut"] and x["volume"] for x in lus) and any(x["codes"] for x in lus))
check("mots en arabe ET en français présents", any(C.langue_de(x["mot"]) == "ar" for x in lus) and any(C.langue_de(x["mot"]) == "fr" for x in lus))
check("une réponse « rien » de Google = liste vide, pas une erreur", R.analyser_batch('[["wrb.fr","i0OFE",null,null,null,[3],"generic"]]') == [])
try:
    R.analyser_batch("<html>panne</html>"); check("un format inconnu lève une erreur", False)
except RuntimeError:
    check("un format inconnu lève une erreur", True)
# ---- 2. flux RSS enregistré
rss = open(os.path.join(ICI, "exemples", "rss.xml"), encoding="utf-8").read()
import re
items = re.findall(r"<item>(.*?)</item>", rss, re.S)
check("RSS d'exemple : 10 tendances", len(items) == 10)
# ---- 3. normalisation et adresses
check("normaliser : accents, majuscules, tirets", C.normaliser("Classement FC Barcelone – Deportivo Alavés") == "classement fc barcelone - deportivo alaves")
check("normaliser : arabe (tashkeel, alef, ta marbouta)", C.normaliser("أمطارٌ متفرقة") == "امطار متفرقه")
check("slug : latin", C.slug("Ballon d'Or 2026") == "ballon-d-or-2026")
check("slug : arabe gardé", C.slug("سرقة") == "سرقه")
check("palier : « 5 000+ »", C.palier_texte(5000) == "5 000+" and C.palier_texte(None) == "")
check("langue : arabe / français", C.langue_de("سرقة") == "ar" and C.langue_de("huile") == "fr")
# ---- 4. catégories (mots-clés avant codes Google)
for mot, codes, attendu in [("كراء شقة سوسة", [], "immobilier"), ("prix voiture neuve", [1], "automobile"), ("journal officiel de la république tunisienne", [9, 10], "administration"),
                            ("panneau solaire prix tunisie", [], "energie"), ("concours finances 2026", [], "emploi"), ("classement fc barcelone", [17], "sport"),
                            ("أمطار متفرقة", [20], "meteo"), ("inconnu xyz", [], "autre"), ("inconnu xyz", [16], "commerce"), ("resultat bac 2026", [], "education")]:
    check(f"catégorie de « {mot} » = {attendu}", K.categorie(C.normaliser(mot), codes) == attendu)
check("intention commerciale : prix / كراء oui, match non", K.intention_commerciale("prix iphone") and K.intention_commerciale("كراء شقه") and not K.intention_commerciale("match barca"))
# ---- 5. fusion : deux lectures du même mot = une tendance ; le RSS se rattache
mem = {"tendances": {}}
quand = dt.datetime(2026, 11, 1, 10, 0, tzinfo=C.TUNIS)
n1 = R.fusionner(mem, lus, 168, quand)
n2 = R.fusionner(mem, lus, 24, quand + dt.timedelta(hours=1))
check("fusion : 1re lecture crée, 2e lecture n'ajoute rien", n1 == len(lus) and n2 == 0)
t = next(iter(mem["tendances"].values()))
check("fusion : releves=2, vu_dernier avancé, source 168h et 24h", t["releves"] == 2 and t["vu_dernier"].startswith("2026-11-01T11") and set(t["sources"]) == {"168h", "24h"})
rss_lus = [{"mot": lus[0]["mot"], "volume": 99999, "debut": lus[0]["debut"] + 3600}]
R.fusionner(mem, rss_lus, "rss", quand)
check("fusion : le RSS se rattache à la tendance du même mot (volume max gardé)", mem["tendances"][R.cle_de(lus[0]["mot"], lus[0]["debut"])]["volume"] == 99999)
# ---- 6. analyse sur des données inventées : nouveautés, retombées, récurrents, opportunités, pages de mots
def tend(mot, jours_avant, volume=1000, hausse=500, codes=()):
    d = quand - dt.timedelta(days=jours_avant)
    return {"mot": mot, "mot_norm": C.normaliser(mot), "langue": C.langue_de(mot), "debut": C.iso(d), "debut_ts": int(d.timestamp()), "fin": None,
            "volume": volume, "hausse": hausse, "liees": [], "codes": list(codes), "categorie": K.categorie(C.normaliser(mot), codes),
            "vu_premier": C.iso(d), "vu_dernier": C.iso(d), "releves": 1, "periodes": [24], "sources": ["24h"]}
T = [tend("prix panneau solaire", 0, 2000, 900), tend("match test", 0, 500, 300, [17]), tend("vieux sujet", 10, 1000, 600),
     tend("record", 0, 200, 100), tend("record", 3, 200, 100), tend("record", 6, 200, 100), tend("كراء شقة", 1.5, 1000, 1000)]
mots = {"mots": {"x": {"mot": "x neuf", "langue": "fr", "apparu": C.jour(quand), "vu": C.jour(quand), "meilleur_rang": 1, "categorie": "autre", "amorces": []}},
        "passages": [{"jour": C.jour(quand)}]}
a = A.analyser({"tendances": {f"{i}": t for i, t in enumerate(T)}}, mots, quand)
check("analyse : aujourd'hui = les tendances commencées depuis 24 h", {x["mot"] for x in a["aujourdhui"]} == {"prix panneau solaire", "match test", "record"})
check("analyse : nouveauté = jamais vu avant (record vu il y a 6 j n'en est pas une)", {x["mot"] for x in a["nouveautes"]} == {"prix panneau solaire", "match test"})
check("analyse : retombée = la semaine passée, pas cette semaine", [x["mot"] for x in a["retombees"]] == ["vieux sujet"])
check("analyse : récurrent = 3 jours différents", [x["mot"] for x in a["recurrents"]] == ["record"] and a["recurrents"][0]["jours"] == 3)
check("analyse : opportunités = énergie avec intention + immobilier avec intention, pas le sport", {x["mot"] for x in a["opportunites"]} == {"prix panneau solaire", "كراء شقة"})
check("analyse : hausses fortes (semaine) = hausse ≥ 500 % ou volume ≥ 5 000", {x["mot"] for x in a["hausses"]} == {"prix panneau solaire", "كراء شقة"})
check("analyse : page de mot « record » avec 3 épisodes", any(p["mot"] == "record" and len(p["episodes"]) == 3 for p in a["pages_mots"]))
check("analyse : mots tapés nouveaux repris", a["mots"]["nouveaux"] and a["mots"]["nouveaux"][0]["mot"] == "x neuf")
check("analyse : toutes les catégories présentes", set(a["categories"]) == {c for c, _, _ in K.CATEGORIES})
# ---- 7. fins de ligne Unix dans les fichiers écrits par le robot (règle § 20)
for f in ("donnees/tendances.json", "donnees/analyse.json", "index.html", "sitemap.xml", "robots.txt"):
    p = os.path.join(RACINE, f)
    if os.path.exists(p):
        check(f"{f} : fins de ligne LF", b"\r\n" not in open(p, "rb").read())

print(f"{ok} vérifications réussies, {ko} échec(s)")
sys.exit(1 if ko else 0)
