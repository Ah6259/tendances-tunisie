# -*- coding: utf-8 -*-
"""Robot des « mots tapés » : les suggestions de Google (ce que Google propose quand un Tunisien commence à taper), une fois par semaine.

Source : https://suggestqueries.google.com/complete/search?client=firefox&gl=tn (testé le 01/11/2026 : 10 propositions par début de mot,
en français et en arabe). Ce ne sont pas des volumes mais de VRAIES expressions tapées en Tunisie, classées par Google selon leur
fréquence : on les garde avec leur date d'apparition et de disparition → « nouveaux mots qui apparaissent », « mots qui disparaissent ».
Amorces : lettres et syllabes FR + AR, plus des débuts de mots par catégorie (prix, كراء, شغل…). ~400 demandes, 1 par seconde (§ 36).
  python robot/mots.py            (lit Google, met à jour donnees/mots.json)"""
import datetime as dt, json, os, sys, time, urllib.parse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import commun as C          # noqa: E402
import categories as K      # noqa: E402

FICHIER = os.path.join(C.DONNEES, "mots.json")
LIMITE_TOTALE = 20 * 60

AMORCES_FR = list("abcdefghijklmnopqrstuvwxyz") + [
    "prix ", "prix de ", "acheter ", "vente ", "location ", "louer ", "appartement ", "maison ", "terrain ", "voiture ", "permis ",
    "concours ", "emploi ", "recrutement ", "salaire ", "bac ", "inscription ", "formation ", "hotel ", "vol ", "visa ", "medecin ",
    "pharmacie ", "hopital ", "iphone ", "samsung ", "ooredoo ", "orange ", "steg ", "panneau solaire ", "banque ", "credit ", "dinar ",
    "meteo ", "match ", "film ", "comment ", "combien ", "ou ", "meilleur ", "pas cher ", "tunisie ", "tunis ", "sfax ", "sousse ",
    "carrefour ", "monoprix ", "tayara ", "jumia ", "huile ", "sucre ", "lait ", "ramadan ", "aid ", "cnss ", "cnam ", "e-houwiya ",
    "journal officiel ", "resultat ", "mondial ", "coupe ", "ligue ", "pizza ", "restaurant ", "cafe ", "mariage ", "bebe ", "chat ", "chien "]
AMORCES_AR = list("ابتثجحخدذرزسشصضطظعغفقكلمنهوي") + [
    "سعر ", "اسعار ", "شراء ", "بيع ", "كراء ", "شقة ", "منزل ", "ارض ", "سيارة ", "رخصة ", "مناظرة ", "شغل ", "انتداب ", "اجر ",
    "باكالوريا ", "تسجيل ", "تكوين ", "فندق ", "طيران ", "فيزا ", "طبيب ", "صيدلية ", "مستشفى ", "هاتف ", "اوريدو ", "ستاغ ", "طاقة شمسية ",
    "بنك ", "قرض ", "دينار ", "طقس ", "مباراة ", "فيلم ", "كيفاش ", "قداش ", "وين ", "افضل ", "رخيص ", "تونس ", "صفاقس ", "سوسة ",
    "زيت ", "سكر ", "حليب ", "رمضان ", "عيد ", "نتائج ", "كاس ", "مطعم ", "قهوة ", "عرس ", "طفل ", "مرض ", "دواء ", "كهرباء ", "ماء "]


def suggestions(q, hl):
    u = "https://suggestqueries.google.com/complete/search?" + urllib.parse.urlencode({"client": "firefox", "gl": "tn", "hl": hl, "q": q})
    d = json.loads(C.telecharger(u, delai=30))
    return [x for x in (d[1] if len(d) > 1 else []) if isinstance(x, str)]


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    quand = C.maintenant()
    jour = C.jour(quand)
    d = C.lire_json(FICHIER) or {"explication": "Expressions proposées par Google en Tunisie (suggestions), avec date d'apparition et de disparition.",
                                 "mots": {}, "passages": []}
    M = d["mots"]
    vus, demandes, erreurs = set(), 0, 0
    depart = time.time()
    for amorces, hl in ((AMORCES_FR, "fr"), (AMORCES_AR, "ar")):
        for a in amorces:
            if time.time() - depart > LIMITE_TOTALE:
                print("limite de temps totale atteinte"); break
            try:
                props = suggestions(a, hl)
            except Exception as e:
                erreurs += 1
                if erreurs > 20:
                    sys.exit(f"ÉCHEC : trop d'erreurs ({e})")
                continue
            demandes += 1
            for rang, p in enumerate(props):
                n = C.normaliser(p)
                if len(n) < 2:
                    continue
                vus.add(n)
                x = M.get(n)
                if x is None:
                    x = M[n] = {"mot": p, "langue": C.langue_de(p), "apparu": jour, "vu": jour, "amorces": [], "meilleur_rang": rang + 1,
                                "categorie": K.categorie(n)}
                x["vu"] = jour
                x["meilleur_rang"] = min(x["meilleur_rang"], rang + 1)
                if a.strip() not in x["amorces"] and len(x["amorces"]) < 6:
                    x["amorces"].append(a.strip())
                x["categorie"] = K.categorie(n)
    nouveaux = [n for n, x in M.items() if x["apparu"] == jour]
    d["maj"] = C.iso(quand)
    d["passages"] = (d.get("passages") or [])[-52:] + [{"jour": jour, "demandes": demandes, "expressions": len(vus), "nouvelles": len(nouveaux)}]
    C.ecrire_json(FICHIER, d)
    print(f"{demandes} demandes, {len(vus)} expressions vues aujourd'hui, {len(nouveaux)} nouvelles, {len(M)} en mémoire")
    if demandes < 50:
        sys.exit("ÉCHEC : trop peu de demandes réussies")


if __name__ == "__main__":
    main()
