# -*- coding: utf-8 -*-
"""Ce qui est commun aux robots de l'Observatoire : réseau prudent, chemins, dates, normalisation des mots.

Règles communes : un seul module réseau (User-Agent clair, pause entre deux demandes, limite de temps totale, règle § 36 : ne jamais
fatiguer les sites lus) ; fichiers écrits en UTF-8 avec fins de ligne Unix (§ 20) ; dates de Tunis (UTC+1, pas d'heure d'été)."""
import datetime as dt, json, os, re, time, unicodedata, urllib.request, urllib.error

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.dirname(ICI)
DONNEES = os.path.join(RACINE, "donnees")
UA = "ClicviaRobot/1.0 (+https://clicvia.com/; observatoire des tendances)"
PAUSE = 1.0                                   # secondes entre deux demandes au même service
TUNIS = dt.timezone(dt.timedelta(hours=1))    # la Tunisie n'a pas d'heure d'été
_dernier = {}


def maintenant():
    return dt.datetime.now(TUNIS).replace(microsecond=0)


def iso(d):
    return d.astimezone(TUNIS).strftime("%Y-%m-%dT%H:%M:%S")


def depuis_ts(ts):
    return dt.datetime.fromtimestamp(int(ts), TUNIS)


def jour(d=None):
    return (d or maintenant()).strftime("%Y-%m-%d")


def lire_json(chemin, defaut=None):
    try:
        with open(chemin, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return defaut


def ecrire_json(chemin, objet, compact=False):
    os.makedirs(os.path.dirname(chemin), exist_ok=True)
    with open(chemin, "w", encoding="utf-8", newline="\n") as f:
        json.dump(objet, f, ensure_ascii=False, indent=None if compact else 1, separators=(",", ":") if compact else None)
        f.write("\n")


def telecharger(url, donnees=None, entetes=None, delai=60, essais=3):
    """GET (ou POST si « donnees ») avec pause par hôte, 3 essais espacés ; renvoie le texte. Lève une erreur claire sinon."""
    hote = urllib.parse.urlsplit(url).hostname
    attente = PAUSE - (time.time() - _dernier.get(hote, 0))
    if attente > 0:
        time.sleep(attente)
    h = {"User-Agent": UA, "Accept-Language": "fr,ar;q=0.8"}
    h.update(entetes or {})
    derniere = None
    for k in range(essais):
        try:
            req = urllib.request.Request(url, data=donnees, headers=h, method="POST" if donnees is not None else "GET")
            with urllib.request.urlopen(req, timeout=delai) as r:
                _dernier[hote] = time.time()
                return r.read().decode("utf-8", errors="replace")
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, OSError) as e:
            derniere = e
            _dernier[hote] = time.time()
            time.sleep(3 * (k + 1))
    raise RuntimeError(f"{url.split('?')[0]} : {derniere}")


import urllib.parse  # noqa: E402  (après les fonctions : lisibilité)

ARABE = re.compile(r"[؀-ۿ]")
TASHKEEL = re.compile(r"[ً-ْٰـ]")


def langue_de(mot):
    """« ar » si le mot contient de l'arabe, sinon « fr » (le latin : français, parfois anglais ou tunisien en lettres latines)."""
    return "ar" if ARABE.search(mot or "") else "fr"


def normaliser(mot):
    """Clé de regroupement : minuscules, sans accents ni signes arabes (tashkeel), tirets et espaces unifiés."""
    m = (mot or "").strip().lower().replace("–", "-").replace("—", "-").replace("’", "'")
    m = TASHKEEL.sub("", m)
    m = m.replace("أ", "ا").replace("إ", "ا").replace("آ", "ا").replace("ة", "ه").replace("ى", "ي")
    m = "".join(c for c in unicodedata.normalize("NFD", m) if unicodedata.category(c) != "Mn")
    return re.sub(r"\s+", " ", m).strip()


def slug(mot):
    """Adresse d'une page de mot : lettres (latines ou arabes) et chiffres, le reste devient « - »."""
    s = normaliser(mot)
    s = re.sub(r"[^0-9a-z؀-ۿ]+", "-", s).strip("-")
    return s[:80] or "mot"


def palier_texte(v):
    """Volume approximatif de Google Trends (par paliers) écrit honnêtement : « 5 000+ »."""
    try:
        v = int(v)
    except (TypeError, ValueError):
        return ""
    return f"{v:,}".replace(",", " ") + "+"
