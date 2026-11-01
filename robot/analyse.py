# -*- coding: utf-8 -*-
"""Analyse des tendances (étape 4 du projet) : à partir de donnees/tendances.json et donnees/mots.json, calcule ce que montre le site
et l'écrit dans donnees/analyse.json (lu aussi par les assistants IA et les curieux : données ouvertes).

Règles de normalisation (étude du 01/11/2026, § 4) : volumes = paliers approximatifs (« 5 000+ »), jamais additionnés entre mots ;
une hausse en % vaut pour la période de Google ; deux tendances ne se comparent que sur la même période.
Ce qu'on calcule :
- aujourd'hui (24 h) et cette semaine (7 j) : les tendances vues, triées par volume puis hausse ;
- NOUVEAUTÉS : mots jamais vus avant les dernières 24 h (sur toute la mémoire) ;
- HAUSSES INHABITUELLES : hausse ≥ 500 % ou volume ≥ 5 000 ;
- QUI REDESCENDENT : mots présents la semaine passée, absents cette semaine ;
- RÉCURRENTS : mots vus sur au moins 3 jours différents ;
- par CATÉGORIE : effectifs et têtes de liste ;
- OPPORTUNITÉS : tendances d'une catégorie utile aux entrepreneurs, avec une intention (prix, acheter, كراء…) ou un gros volume ;
- HISTORIQUE : par semaine et par mois (effectifs, têtes de liste) ;
- MOTS TAPÉS : expressions nouvelles de la semaine et expressions disparues (suggestions Google).
  python robot/analyse.py [--aujourdhui AAAA-MM-JJTHH:MM]"""
import datetime as dt, os, sys
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import commun as C          # noqa: E402
import categories as K      # noqa: E402

SORTIE = os.path.join(C.DONNEES, "analyse.json")
HAUSSE_FORTE, VOLUME_FORT = 500, 5000
MAX_LISTE = 60


def d_iso(s):
    return dt.datetime.strptime(s, "%Y-%m-%dT%H:%M:%S").replace(tzinfo=C.TUNIS)


def resume(t):
    """Ce qu'une page a besoin de savoir d'une tendance (compact)."""
    return {"mot": t["mot"], "slug": C.slug(t["mot"]), "langue": t["langue"], "categorie": t["categorie"], "volume": t.get("volume"),
            "hausse": t.get("hausse"), "debut": t.get("debut"), "fin": t.get("fin"), "liees": t.get("liees", [])[:5],
            "jour": (t.get("debut") or t["vu_premier"])[:10]}


def tri(lst):
    return sorted(lst, key=lambda x: (-(x.get("volume") or 0), -(x.get("hausse") or 0), x["mot"]))


def analyser(memoire, mots, maintenant):
    T = list(memoire["tendances"].values())
    for t in T:
        t["_debut"] = d_iso(t["debut"]) if t.get("debut") else d_iso(t["vu_premier"])
        t["_vu"] = d_iso(t["vu_dernier"])
    il_y_a = lambda h: maintenant - dt.timedelta(hours=h)
    jour24 = [t for t in T if t["_debut"] >= il_y_a(24)]        # « aujourd'hui » = commencé dans les 24 h (liste 24 h de Google)
    sem = [t for t in T if t["_debut"] >= il_y_a(168)]
    sem_prec = [t for t in T if il_y_a(336) <= t["_debut"] < il_y_a(168)]
    mois = [t for t in T if t["_debut"] >= il_y_a(24 * 30)]
    # première apparition de chaque mot (toute la mémoire)
    premiere = {}
    for t in sorted(T, key=lambda t: t["_debut"]):
        premiere.setdefault(t["mot_norm"], t["_debut"])
    nouveautes = [t for t in jour24 if premiere[t["mot_norm"]] >= il_y_a(24)]
    hausses = [t for t in sem if (t.get("hausse") or 0) >= HAUSSE_FORTE or (t.get("volume") or 0) >= VOLUME_FORT]
    mots_sem = {t["mot_norm"] for t in sem}
    retombees = {}
    for t in sem_prec:
        if t["mot_norm"] not in mots_sem:
            retombees.setdefault(t["mot_norm"], t)
    jours_par_mot = defaultdict(set)
    for t in T:
        jours_par_mot[t["mot_norm"]].add(t["_debut"].strftime("%Y-%m-%d"))
    recurrents = {}
    for t in sorted(mois, key=lambda t: -(t.get("volume") or 0)):
        if len(jours_par_mot[t["mot_norm"]]) >= 3 and t["mot_norm"] not in recurrents:
            recurrents[t["mot_norm"]] = dict(resume(t), jours=len(jours_par_mot[t["mot_norm"]]))
    par_cat = {}
    for c, fr, ar in K.CATEGORIES:
        lst = tri([resume(t) for t in sem if t["categorie"] == c])
        lst24 = [x for x in lst if x["jour"] >= C.jour(il_y_a(24))]
        par_cat[c] = {"fr": fr, "ar": ar, "n_semaine": len(lst), "n_mois": sum(1 for t in mois if t["categorie"] == c),
                      "top": lst[:MAX_LISTE], "top24": lst24[:10]}
    opportunites = []
    for t in sem:
        if t["categorie"] in K.COMMERCIALES and (K.intention_commerciale(t["mot_norm"]) or (t.get("volume") or 0) >= 2000):
            x = resume(t); x["intention"] = K.intention_commerciale(t["mot_norm"])
            x["score"] = (t.get("volume") or 100) * (2 if x["intention"] else 1) * (1 + (t.get("hausse") or 0) / 1000)
            opportunites.append(x)
    opportunites.sort(key=lambda x: -x["score"])
    # historique : semaines (lundi) et mois
    semaines, moisH = defaultdict(list), defaultdict(list)
    for t in T:
        d = t["_debut"]
        semaines[(d - dt.timedelta(days=d.weekday())).strftime("%Y-%m-%d")].append(t)
        moisH[d.strftime("%Y-%m")].append(t)
    def bloc(lst):
        cats = Counter(t["categorie"] for t in lst)
        return {"n": len(lst), "top": tri([resume(t) for t in lst])[:10],
                "categories": [{"cle": c, "n": n} for c, n in cats.most_common()]}
    historique = {"semaines": {k: bloc(v) for k, v in sorted(semaines.items(), reverse=True)[:26]},
                  "mois": {k: bloc(v) for k, v in sorted(moisH.items(), reverse=True)[:24]}}
    # mots tapés (suggestions)
    M = (mots or {}).get("mots", {})
    jour7 = C.jour(il_y_a(168))
    mots_nouveaux = sorted((x for x in M.values() if x["apparu"] >= jour7), key=lambda x: (x["meilleur_rang"], x["mot"]))
    dernier_passage = max((p["jour"] for p in (mots or {}).get("passages", [])), default=None)
    mots_disparus = sorted((x for x in M.values() if dernier_passage and x["vu"] < dernier_passage and x["vu"] >= C.jour(il_y_a(24 * 60))),
                           key=lambda x: x["vu"], reverse=True)
    mots_par_cat = defaultdict(list)
    for x in M.values():
        if x["vu"] == dernier_passage:
            mots_par_cat[x["categorie"]].append(x)
    for c in mots_par_cat:
        mots_par_cat[c].sort(key=lambda x: (x["meilleur_rang"], x["mot"]))
    # pages par mot : un mot = toutes ses tendances (épisodes), pour les mots vus ce mois ou récurrents
    par_mot = defaultdict(list)
    for t in T:
        par_mot[t["mot_norm"]].append(t)
    pages_mots = []
    for n, lst in par_mot.items():
        lst.sort(key=lambda t: t["_debut"], reverse=True)
        if lst[0]["_debut"] < il_y_a(24 * 30) and len(lst) < 3:
            continue
        pages_mots.append({"mot": lst[0]["mot"], "mot_norm": n, "slug": C.slug(lst[0]["mot"]), "langue": lst[0]["langue"],
                           "categorie": lst[0]["categorie"], "episodes": [resume(t) for t in lst][:30],
                           "jours": len(jours_par_mot[n]), "volume_max": max((t.get("volume") or 0) for t in lst),
                           "liees": sorted({l for t in lst for l in t.get("liees", [])})[:12]})
    pages_mots.sort(key=lambda x: (-x["volume_max"], x["mot"]))
    return {
        "maj": C.iso(maintenant), "jour": C.jour(maintenant),
        "totaux": {"tendances": len(T), "mots_distincts": len(par_mot), "aujourdhui": len(jour24), "semaine": len(sem), "mois": len(mois),
                   "expressions_tapees": len(M), "premiere_lecture": min((t["vu_premier"] for t in T), default=None)},
        "aujourdhui": tri([resume(t) for t in jour24])[:MAX_LISTE],
        "semaine": tri([resume(t) for t in sem])[:200],
        "nouveautes": tri([resume(t) for t in nouveautes])[:MAX_LISTE],
        "hausses": sorted([resume(t) for t in hausses], key=lambda x: (-(x["hausse"] or 0), -(x["volume"] or 0)))[:MAX_LISTE],
        "retombees": tri([resume(t) for t in retombees.values()])[:MAX_LISTE],
        "recurrents": list(recurrents.values())[:MAX_LISTE],
        "categories": par_cat,
        "opportunites": opportunites[:MAX_LISTE],
        "historique": historique,
        "mots": {"passage": dernier_passage, "nouveaux": [{"mot": x["mot"], "langue": x["langue"], "categorie": x["categorie"], "apparu": x["apparu"]} for x in mots_nouveaux[:150]],
                 "disparus": [{"mot": x["mot"], "langue": x["langue"], "vu": x["vu"]} for x in mots_disparus[:80]],
                 "par_categorie": {c: [{"mot": x["mot"], "langue": x["langue"]} for x in v[:40]] for c, v in mots_par_cat.items()},
                 "total": len(M)},
        "pages_mots": pages_mots[:1500],
        "seuils": {"hausse_forte": HAUSSE_FORTE, "volume_fort": VOLUME_FORT},
    }


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    quand = C.maintenant()
    if "--aujourdhui" in sys.argv:
        quand = dt.datetime.strptime(sys.argv[sys.argv.index("--aujourdhui") + 1], "%Y-%m-%dT%H:%M").replace(tzinfo=C.TUNIS)
    memoire = C.lire_json(os.path.join(C.DONNEES, "tendances.json"))
    if not memoire or not memoire.get("tendances"):
        sys.exit("ÉCHEC : donnees/tendances.json vide (lancer robot/collecte.py d'abord)")
    a = analyser(memoire, C.lire_json(os.path.join(C.DONNEES, "mots.json")), quand)
    C.ecrire_json(SORTIE, a)
    print(f"analyse : {a['totaux']['aujourdhui']} aujourd'hui, {a['totaux']['semaine']} cette semaine, {len(a['nouveautes'])} nouveautés, "
          f"{len(a['hausses'])} hausses fortes, {len(a['opportunites'])} opportunités, {len(a['pages_mots'])} pages de mots")


if __name__ == "__main__":
    main()
