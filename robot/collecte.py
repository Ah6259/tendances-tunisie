# -*- coding: utf-8 -*-
"""Robot de collecte des tendances de recherche en Tunisie (Google Trends), 2 passages par jour sur GitHub.

Sources (étude de faisabilité du 01/11/2026, « observatoire tendances/etude de faisabilite 2026-11-01.md ») :
1. Service « Tendances du moment » de trends.google.com (la même demande que la page https://trends.google.com/trending?geo=TN) :
   périodes 4 h, 24 h, 48 h et 7 jours ; chaque tendance = mot tapé, début, fin, volume par paliers, % de hausse, recherches liées,
   codes de catégorie. Non documenté par Google : son format peut changer, d'où le secours ci-dessous.
2. Flux RSS officiel https://trends.google.com/trending/rss?geo=TN (10 tendances, trafic approximatif, date).
Aucun contournement de protection (pas de cookie de session, pas de faux navigateur) : décision du 01/11/2026.

Ce que le robot garde (donnees/tendances.json) : CHAQUE tendance vue, avec sa première et sa dernière lecture, son volume maximal,
sa plus forte hausse, ses recherches liées, ses catégories Google et la nôtre. Google ne garde que 7 jours : l'historique, c'est ce
fichier. Chaque passage est aussi gardé tel quel (donnees/releves/AAAA-MM-JJ_HH.json, 60 jours) pour vérification.
Panne : les données de la veille restent ; donnees/etat.json note le dernier succès de chaque source (règle § 46 : rouge après 2 jours,
contrôlé par tools/sources_en_panne.py).
  python robot/collecte.py            (lit les sources, met à jour les fichiers)
  python robot/collecte.py --local    (ne lit rien : refait seulement les calculs à partir des fichiers)"""
import datetime as dt, html, json, os, re, sys, time, urllib.parse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import commun as C          # noqa: E402
import categories as K      # noqa: E402

FICHIER = os.path.join(C.DONNEES, "tendances.json")
ETAT = os.path.join(C.DONNEES, "etat.json")
RELEVES = os.path.join(C.DONNEES, "releves")
PERIODES = (4, 24, 48, 168)
GARDER_RELEVES_JOURS = 60
LIMITE_TOTALE = 8 * 60       # secondes : un robot de relevé a une limite de temps totale (règle § 39)


# ---------------------------------------------------------------- lecture des sources
def tendances_du_moment(heures, langue="fr"):
    """Liste brute du service « Tendances du moment » pour la Tunisie sur « heures » (4, 24, 48 ou 168)."""
    req = json.dumps([[["i0OFE", json.dumps([None, None, "TN", 0, langue, heures, 1]), None, "generic"]]])
    corps = urllib.parse.urlencode({"f.req": req}).encode()
    texte = C.telecharger("https://trends.google.com/_/TrendsUi/data/batchexecute?rpcids=i0OFE&hl=" + langue, donnees=corps,
                          entetes={"Content-Type": "application/x-www-form-urlencoded;charset=UTF-8"})
    return analyser_batch(texte)


def analyser_batch(texte):
    """Décode la réponse (enveloppe « )]}' » + JSON imbriqué) ; renvoie une liste de dictionnaires propres."""
    m = re.search(r'\[\["wrb\.fr","i0OFE","(.*?)",null,null,null,"generic"\]', texte, re.S)
    if not m:
        if re.search(r'\["wrb\.fr","i0OFE",null', texte):
            return []                                   # Google répond « rien » (période ou lieu sans tendances)
        raise RuntimeError("format inattendu du service Tendances du moment")
    interne = json.loads(json.loads('"' + m.group(1) + '"'))
    lignes = interne[1] if len(interne) > 1 and isinstance(interne[1], list) else []
    sortie = []
    for r in lignes:
        if not isinstance(r, list) or len(r) < 9 or not isinstance(r[0], str):
            continue
        debut = r[3][0] if isinstance(r[3], list) and r[3] else (r[3] if isinstance(r[3], (int, float)) else None)
        fin = r[4][0] if isinstance(r[4], list) and r[4] else (r[4] if isinstance(r[4], (int, float)) else None)
        sortie.append({"mot": r[0].strip(), "debut": int(debut) if debut else None, "fin": int(fin) if fin else None,
                       "volume": int(r[6]) if isinstance(r[6], (int, float)) else None,
                       "hausse": int(r[8]) if isinstance(r[8], (int, float)) else None,
                       "liees": [x for x in (r[9] or []) if isinstance(x, str)][:10] if len(r) > 9 else [],
                       "codes": [int(x) for x in (r[10] or []) if isinstance(x, int)] if len(r) > 10 and isinstance(r[10], list) else []})
    return sortie


def flux_rss():
    """Flux RSS officiel : [{mot, trafic, date}]."""
    texte = C.telecharger("https://trends.google.com/trending/rss?geo=TN")
    sortie = []
    for it in re.findall(r"<item>(.*?)</item>", texte, re.S):
        t = re.search(r"<title>(.*?)</title>", it, re.S)
        tr = re.search(r"<ht:approx_traffic>(.*?)</ht:approx_traffic>", it)
        d = re.search(r"<pubDate>(.*?)</pubDate>", it)
        if not t:
            continue
        mot = html.unescape(t.group(1)).strip()
        trafic = int(re.sub(r"\D", "", tr.group(1)) or 0) if tr else None
        quand = None
        if d:
            try:
                quand = int(dt.datetime.strptime(d.group(1).strip(), "%a, %d %b %Y %H:%M:%S %z").timestamp())
            except ValueError:
                pass
        sortie.append({"mot": mot, "volume": trafic, "debut": quand})
    return sortie


# ---------------------------------------------------------------- fusion dans la mémoire
def cle_de(mot, debut):
    """Une tendance = un mot + un début (à l'heure près) : le même mot qui revient une autre semaine est une autre tendance."""
    return f"{C.normaliser(mot)}|{(debut or 0) // 3600}"


def fusionner(memoire, lus, periode, quand):
    """Ajoute ou enrichit les tendances lues (période en heures ; « rss » pour le flux)."""
    T = memoire["tendances"]
    n_nouv = 0
    for x in lus:
        if not x.get("mot"):
            continue
        k = cle_de(x["mot"], x.get("debut"))
        if k not in T and periode == "rss":
            # le RSS n'a pas la même heure de début : rattacher à une tendance du même mot vue depuis moins de 36 h
            n = C.normaliser(x["mot"])
            proches = [kk for kk, t in T.items() if t["mot_norm"] == n and x.get("debut") and abs((t.get("debut_ts") or 0) - x["debut"]) < 36 * 3600]
            if proches:
                k = max(proches, key=lambda kk: T[kk].get("debut_ts") or 0)
        t = T.get(k)
        if t is None:
            n_nouv += 1
            t = T[k] = {"mot": x["mot"], "mot_norm": C.normaliser(x["mot"]), "langue": C.langue_de(x["mot"]),
                        "debut": C.iso(C.depuis_ts(x["debut"])) if x.get("debut") else None, "debut_ts": x.get("debut"),
                        "fin": None, "volume": None, "hausse": None, "liees": [], "codes": [], "categorie": "autre",
                        "vu_premier": C.iso(quand), "vu_dernier": C.iso(quand), "releves": 0, "periodes": [], "sources": []}
        t["vu_dernier"] = C.iso(quand)
        t["releves"] += 1
        if x.get("fin"):
            t["fin"] = C.iso(C.depuis_ts(x["fin"]))
        if x.get("volume") and (t["volume"] is None or x["volume"] > t["volume"]):
            t["volume"] = x["volume"]
        if x.get("hausse") and (t["hausse"] is None or x["hausse"] > t["hausse"]):
            t["hausse"] = x["hausse"]
        for l in x.get("liees") or []:
            if l not in t["liees"] and C.normaliser(l) != t["mot_norm"]:
                t["liees"].append(l)
        for c in x.get("codes") or []:
            if c not in t["codes"]:
                t["codes"].append(c)
        src = "rss" if periode == "rss" else f"{periode}h"
        if src not in t["sources"]:
            t["sources"].append(src)
        if periode != "rss" and periode not in t["periodes"]:
            t["periodes"].append(periode)
        t["categorie"] = K.categorie(t["mot_norm"], t["codes"])
    return n_nouv


def recalculer(memoire):
    """Catégories recalculées (les mots-clés évoluent) + carnet des mots inconnus (règle § 40)."""
    inconnus = {}
    for t in memoire["tendances"].values():
        t["categorie"] = K.categorie(t["mot_norm"], t.get("codes", []))
        if t["categorie"] == "autre":
            x = inconnus.setdefault(t["mot_norm"], {"mot": t["mot"], "fois": 0, "volume": 0})
            x["fois"] += 1
            x["volume"] = max(x["volume"], t.get("volume") or 0)
    carnet = sorted(inconnus.values(), key=lambda x: (-x["fois"], -x["volume"]))[:200]
    C.ecrire_json(os.path.join(C.DONNEES, "carnet-categories.json"),
                  {"maj": C.jour(), "explication": "Mots restés sans catégorie (à classer dans robot/categories.py quand ils reviennent).",
                   "mots": carnet})


def menage_releves(quand):
    limite = (quand - dt.timedelta(days=GARDER_RELEVES_JOURS)).strftime("%Y-%m-%d")
    if os.path.isdir(RELEVES):
        for f in os.listdir(RELEVES):
            if f.endswith(".json") and f[:10] < limite:
                os.remove(os.path.join(RELEVES, f))


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    quand = C.maintenant()
    memoire = C.lire_json(FICHIER) or {"explication": "Toutes les tendances de recherche vues en Tunisie (Google Trends), avec première et dernière lecture.",
                                        "tendances": {}}
    etat = C.lire_json(ETAT) or {"sources": {}}
    if "--local" in sys.argv:
        recalculer(memoire); memoire["maj"] = C.iso(quand); C.ecrire_json(FICHIER, memoire)
        print(f"recalcul local : {len(memoire['tendances'])} tendances en mémoire"); return
    depart = time.time()
    releve = {"quand": C.iso(quand), "sources": {}}
    erreurs = []
    for h in PERIODES:
        if time.time() - depart > LIMITE_TOTALE:
            erreurs.append(f"{h}h : limite de temps totale atteinte"); continue
        try:
            lus = tendances_du_moment(h)
            releve["sources"][f"{h}h"] = lus
            n = fusionner(memoire, lus, h, quand)
            etat["sources"][f"{h}h"] = {"dernier_succes": C.iso(quand), "n": len(lus)}
            print(f"{h:>3} h : {len(lus)} tendances lues, {n} nouvelles")
        except Exception as e:
            erreurs.append(f"{h}h : {e}"); print(f"{h:>3} h : ÉCHEC — {e}")
    try:
        lus = flux_rss()
        releve["sources"]["rss"] = lus
        n = fusionner(memoire, lus, "rss", quand)
        etat["sources"]["rss"] = {"dernier_succes": C.iso(quand), "n": len(lus)}
        print(f"RSS   : {len(lus)} tendances lues, {n} nouvelles")
    except Exception as e:
        erreurs.append(f"rss : {e}"); print(f"RSS   : ÉCHEC — {e}")
    if any(releve["sources"].values()):
        memoire["maj"] = C.iso(quand)
        recalculer(memoire)
        C.ecrire_json(FICHIER, memoire)
        C.ecrire_json(os.path.join(RELEVES, quand.strftime("%Y-%m-%d_%H") + ".json"), releve, compact=True)
        menage_releves(quand)
    etat["derniere_tentative"] = C.iso(quand)
    etat["erreurs"] = erreurs
    C.ecrire_json(ETAT, etat)
    print(f"mémoire : {len(memoire['tendances'])} tendances au total")
    if erreurs and not any(releve["sources"].values()):
        sys.exit("ÉCHEC : aucune source lue — " + " ; ".join(erreurs))


if __name__ == "__main__":
    main()
