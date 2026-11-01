# -*- coding: utf-8 -*-
"""Fabrique les pages de « Tendances de recherche en Tunisie » à partir de donnees/analyse.json (robot/analyse.py).
  python robot/construire_site.py

Pages (français à l'adresse d'origine + une vraie page arabe dans ar/, règle commune § 8 point 9) : accueil (aujourd'hui, nouveautés,
hausses inhabituelles, opportunités, catégories), semaine/, categorie/<clé>/ (17), opportunites/, mots-tapes/, historique/,
mot/<mot>/ (une page par mot vu ce mois ou récurrent), a-propos/ (« Comment fonctionne le site ? », méthode, sources) ; sitemap.xml,
robots.txt, llms.txt, manifeste. Gabarit, styles et scripts repris de la famille Concours / Outils pratiques (couleur propre : violet).
Attribution exigée par Google (étude de légalité du 01/11/2026) : « Source des données : Google Trends » sur chaque page."""
import datetime as dt, hashlib, html, json, os, re, sys

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.dirname(ICI)
sys.path.insert(0, ICI); sys.path.insert(0, os.path.join(RACINE, "tools"))
import commun as C          # noqa: E402
import categories as K      # noqa: E402
import pages_langues as PL  # noqa: E402

URL_SITE = "https://tendances.clicvia.com/"
NOM = {"fr": "Tendances de recherche en Tunisie", "ar": "اتجاهات البحث في تونس"}
COMPTEUR = "https://prix-eaux-tunisie.goatcounter.com"
FORMSPREE = "https://formspree.io"
TRENDS = "https://trends.google.com/trending?geo=TN"
CSP = ("default-src 'self'; script-src 'self' https://gc.zgo.at; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
       f"font-src 'self' https://fonts.gstatic.com; img-src 'self' data: {COMPTEUR}; connect-src 'self' {COMPTEUR} {FORMSPREE}; "
       f"form-action 'self' {FORMSPREE}; frame-src 'none'; object-src 'none'; base-uri 'self'")
E = lambda t: html.escape(str(t if t is not None else ""), quote=True)
ISO = lambda t: "⁦" + str(t) + "⁩"
MOIS_FR = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août", "septembre", "octobre", "novembre", "décembre"]
MOIS_AR = ["جانفي", "فيفري", "مارس", "أفريل", "ماي", "جوان", "جويلية", "أوت", "سبتمبر", "أكتوبر", "نوفمبر", "ديسمبر"]


def L(fr, ar):
    return f'<span data-l="fr">{fr}</span><span data-l="ar">{ar}</span>'


def dfr(d):
    return f"{d[8:10]}/{d[5:7]}/{d[:4]}" if d else ""


def insecables(t):
    """Espace insécable avant ? ! : ; (règle § 19 : le « ? » ne passe jamais seul à la ligne)."""
    return re.sub(r" ([?!:;])", " \\1", t)


def version(*fichiers):
    h = hashlib.sha1()
    for f in fichiers:
        with open(os.path.join(RACINE, f), "rb") as x:
            h.update(x.read())
    return h.hexdigest()[:8]


# ---------------------------------------------------------------- gabarit
def page(chemin, titre, description, hero, contenu, v, maj, titre_ar="", desc_ar="", jsonld="", og_type="website", indexer=True):
    racine = "../" * chemin.count("/")
    canon = URL_SITE + chemin
    hreflang = PL.liens_hreflang(URL_SITE, chemin, ["fr", "ar"])
    return f"""<!doctype html>
<html lang="fr" dir="ltr" translate="no" data-racine="{racine}" data-fixe data-chemin="{chemin}">
<head>
<meta charset="utf-8">
<meta name="google" content="notranslate">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="{CSP}">
<meta name="referrer" content="strict-origin-when-cross-origin">
<meta name="robots" content="{'noai, noimageai' if indexer else 'noindex, follow, noai, noimageai'}">
<title>{E(titre)}</title>
<meta name="description" content="{E(description)}">
<link rel="canonical" href="{canon}">
{hreflang}<link rel="icon" href="{racine}assets/logo.svg" type="image/svg+xml">
<link rel="icon" href="{racine}favicon.ico" sizes="32x32">
<link rel="apple-touch-icon" href="{racine}assets/apple-touch-icon.png">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-title" content="Tendances Tunisie">
<link rel="manifest" href="{racine}manifest.webmanifest">
<meta name="theme-color" content="#5B21B6">
<meta property="og:title" content="{E(titre.split(' | ')[0])}">
<meta property="og:description" content="{E(description)}">
<meta property="og:url" content="{canon}">
<meta property="og:image" content="{URL_SITE}assets/og-image.jpg">
<meta property="og:image:type" content="image/jpeg"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">
<meta property="og:type" content="{og_type}">
<meta property="og:locale" content="fr_FR"><meta property="og:locale:alternate" content="ar_AR">
<meta name="twitter:card" content="summary_large_image">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Figtree:wght@400;600;700;800&family=Noto+Kufi+Arabic:wght@400;600;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{racine}assets/style.css?v={v}">
{jsonld}<script src="{racine}assets/page.js?v={v}"></script>
<script src="{racine}assets/app.js?v={v}"></script>
<script src="{racine}assets/avis.js?v={v}"></script>
</head>
<body data-maj="{maj}" data-maj-texte="{dfr(maj)}" data-titre-ar="{E(titre_ar)}" data-desc-ar="{E(desc_ar)}">
<header class="entete" id="entete"></header>
<section class="hero">
  <div class="wrap">
{hero}
    <span class="maj">{L("Données lues le", "قُرئت البيانات في")}&nbsp;{ISO(dfr(maj)) if maj else '—'}</span>
  </div>
</section>
<main class="wrap chevauche">
{contenu}
</main>
<footer id="pied"><div class="wrap"><p>Source des données : <a href="https://www.google.com/trends" rel="noopener">Google Trends</a> (tendances de recherche en Tunisie) et suggestions de recherche Google · Site indépendant, non officiel · © 2026 Tendances de recherche en Tunisie — tous droits réservés.</p></div></footer>
<script data-goatcounter="{COMPTEUR}/count" async src="https://gc.zgo.at/count.js"></script>
</body>
</html>
"""


def fil(racine, fr, ar):
    return f'    <p class="fil"><a href="{racine}">{L("Accueil", "الرئيسية")}</a> › {L(fr, ar)}</p>'


def hero_simple(racine, fil_fr, fil_ar, h1_fr, h1_ar, intro_fr, intro_ar):
    return (fil(racine, fil_fr, fil_ar) + f'\n    <h1>{L(insecables(h1_fr), h1_ar)}</h1>\n'
            f'    <p class="intro une-ligne">{L(insecables(intro_fr), intro_ar)}</p>')


# ---------------------------------------------------------------- composants
def cat_nom(cle):
    c = K.PAR_CLE.get(cle) or K.PAR_CLE["autre"]
    return c[1], c[2]


def badge_cat(racine, cle):
    fr, ar = cat_nom(cle)
    return f'<a class="cat" href="{racine}categorie/{cle}/">{L(E(fr), ar)}</a>'


def quand(x):
    j = x.get("jour") or ""
    return dfr(j)


def ligne(x, racine, rang=None, opp=False):
    """Une tendance sur UNE ligne (règle § 19) : rang, mot (lien vers sa page), catégorie, volume, hausse, jour."""
    mot = E(x["mot"])
    dir_ = ' dir="rtl"' if x.get("langue") == "ar" else ' dir="ltr"'
    vol = C.palier_texte(x.get("volume")) if x.get("volume") else ""
    hausse = f'<span class="hausse">{ISO("+" + str(x["hausse"]) + " %")}</span>' if x.get("hausse") else ""
    inten = f'<span class="intention">{L("intention d’achat", "نية شراء")}</span>' if opp and x.get("intention") else ""
    return (f'<li class="tendance{" opp" if opp else ""}" data-cat="{E(x.get("categorie", "autre"))}" data-mot="{mot}">'
            + (f'<span class="rang">{rang}</span>' if rang else "")
            + f'<span class="mot"{dir_}><a href="{racine}mot/{E(x["slug"])}/">{mot}</a></span>{inten}{badge_cat(racine, x.get("categorie", "autre"))}'
            + f'<span class="nombres"><span class="vol" title="Recherches : ordre de grandeur donné par Google">{ISO(vol)}</span>{hausse}</span>'
            + f'<span class="quand">{ISO(quand(x))}</span></li>')


def liste(items, racine, ident, limite=10, opp=False, vide_fr="Rien pour le moment.", vide_ar="لا شيء حاليًا."):
    if not items:
        return f'<p class="liste-vide" id="{ident}">{L(vide_fr, vide_ar)}</p>'
    return (f'<ul class="tendances" id="{ident}" data-limite="{limite}">'
            + "".join(ligne(x, racine, i + 1, opp) for i, x in enumerate(items)) + '</ul>'
            + f'<p class="liste-vide" hidden>{L("Aucune tendance ne correspond.", "لا توجد نتيجة مطابقة.")}</p>')


def filtres(racine, avec_cat=True):
    opts = "".join(f'<option value="{c}">{fr} · {ar}</option>' for c, fr, ar in K.CATEGORIES)
    sel = f'<select data-filtre-cat aria-label="Catégorie"><option value="">{E("Toutes les catégories · كل الفئات")}</option>{opts}</select>' if avec_cat else ""
    return (f'<div class="filtres">{sel}<input type="search" data-recherche placeholder="Chercher un mot · ابحث عن كلمة" aria-label="Chercher">'
            f'<span class="compte" data-compte></span></div>')


def carte(titre_fr, titre_ar, corps, ident=None, sous_fr="", sous_ar=""):
    return (f'<section class="carte"{f" id={chr(34)}{ident}{chr(34)}" if ident else ""}><h2>{L(insecables(titre_fr), titre_ar)}</h2>'
            + (f'<p class="sous">{L(insecables(sous_fr), sous_ar)}</p>' if sous_fr else "") + corps + '</section>')


def grille_categories(a, racine):
    cartes = []
    for c, fr, ar in K.CATEGORIES:
        d = a["categories"][c]
        ex = ", ".join(x["mot"] for x in d["top"][:3])
        cartes.append(f'<a class="cat-carte" href="{racine}categorie/{c}/"><b>{L(E(fr), ar)}</b>'
                      f'<span>{ISO(d["n_semaine"])} {L("cette semaine", "هذا الأسبوع")}</span><small>{E(ex) if ex else "—"}</small></a>')
    return f'<div class="cats" id="categories">{"".join(cartes)}</div>'


def barres(lignes, racine=None):
    """[(libellé fr, libellé ar, n, clé)] → barres proportionnelles."""
    if not lignes:
        return ""
    maxi = max(n for _, _, n, _ in lignes) or 1
    out = []
    for fr, ar, n, cle in lignes:
        lib = f'<a href="{racine}categorie/{cle}/">{L(E(fr), ar)}</a>' if racine and cle else L(E(fr), ar)
        out.append(f'<div class="barre"><span>{lib}</span><div class="piste"><div class="plein" style="width:{100 * n / maxi:.0f}%"></div></div><b>{ISO(n)}</b></div>')
    return '<div class="barres">' + "".join(out) + '</div>'


def frise(points):
    """[(étiquette, valeur)] → petites barres (SVG inutile : des div suffisent et restent lisibles)."""
    if not points:
        return ""
    maxi = max(v for _, v in points) or 1
    return '<div class="frise">' + "".join(f'<div class="b" style="height:{max(4, 86 * v / maxi):.0f}px" title="{E(e)} : {v}"><span>{E(e)}</span></div>' for e, v in points) + '</div>'


AVIS = """<section class="carte avis" id="avis" aria-labelledby="avis-titre">
  <h2 id="avis-titre"><span data-l="fr">Votre avis</span><span data-l="ar">رأيك يهمّنا</span></h2>
  <p class="avis-intro"><span data-l="fr">Une remarque, une erreur, une catégorie qui manque ? Écrivez-nous : chaque message est lu.</span><span data-l="ar">ملاحظة، خطأ، فئة ناقصة؟ اكتب لنا: كل رسالة تُقرأ.</span></p>
  <form id="avis-form" action="https://formspree.io/f/mwlpakqj" method="POST">
    <fieldset>
      <legend><span data-l="fr">Votre note (facultatif)</span><span data-l="ar">تقييمك (اختياري)</span></legend>
      <div class="avis-notes">
        <label><input type="radio" name="note" value="😀 Très bien"><span class="emoji" aria-hidden="true">😀</span><span class="avis-cache"><span data-l="fr">Très bien</span><span data-l="ar">ممتاز</span></span></label>
        <label><input type="radio" name="note" value="🙂 Bien"><span class="emoji" aria-hidden="true">🙂</span><span class="avis-cache"><span data-l="fr">Bien</span><span data-l="ar">جيد</span></span></label>
        <label><input type="radio" name="note" value="😐 Moyen"><span class="emoji" aria-hidden="true">😐</span><span class="avis-cache"><span data-l="fr">Moyen</span><span data-l="ar">متوسط</span></span></label>
        <label><input type="radio" name="note" value="🙁 Pas bien"><span class="emoji" aria-hidden="true">🙁</span><span class="avis-cache"><span data-l="fr">Pas bien</span><span data-l="ar">سيئ</span></span></label>
      </div>
    </fieldset>
    <label class="avis-etiquette" for="avis-message"><span data-l="fr">Votre message</span><span data-l="ar">رسالتك</span></label>
    <textarea id="avis-message" name="message" required maxlength="1000" rows="4" data-ph-fr="Ce qui vous plaît, ce qui manque, une erreur à corriger…" data-ph-ar="ما يعجبك، ما ينقص، خطأ يجب تصحيحه…"></textarea>
    <span class="avis-compte" id="avis-compte" aria-live="off">0 / 1000</span>
    <label class="avis-etiquette" for="avis-email"><span data-l="fr">Votre e-mail (obligatoire, pour vous répondre)</span><span data-l="ar">بريدك الإلكتروني (إجباري، للرد عليك)</span></label>
    <input type="email" id="avis-email" name="email" autocomplete="email" required maxlength="200" data-ph-fr="nom@example.com" data-ph-ar="nom@example.com">
    <input type="hidden" name="site" value="Tendances de recherche en Tunisie">
    <input type="hidden" name="page" value="">
    <input type="hidden" name="_subject" value="Avis — Tendances de recherche en Tunisie">
    <input type="text" name="_gotcha" class="avis-piege" tabindex="-1" autocomplete="off" aria-hidden="true">
    <div class="avis-actions">
      <button type="submit" class="avis-envoyer"><span data-l="fr">Envoyer</span><span data-l="ar">إرسال</span></button>
      <span id="avis-status" role="status" aria-live="polite"></span>
    </div>
    <p class="avis-mention"><span data-l="fr">Votre avis est envoyé au créateur du site (service Formspree). Rien n&#39;est envoyé sans clic sur « Envoyer ».</span><span data-l="ar">يُرسل رأيك إلى صاحب الموقع (خدمة ⁨Formspree⁩). لا يُرسل أي شيء دون الضغط على «إرسال».</span></p>
  </form>
</section>"""


def source_bloc():
    return (f'<p class="google-lien">{L("Source des données : <a href=https://www.google.com/trends rel=noopener target=_blank>Google Trends</a> (Tunisie) — volumes par paliers, ordre de grandeur donné par Google.", "مصدر البيانات: <a href=https://www.google.com/trends rel=noopener target=_blank>Google Trends</a> (تونس) — أحجام تقديرية حسب غوغل.")}</p>')


# ---------------------------------------------------------------- pages
def accueil(a, v, maj):
    r = ""
    t = a["totaux"]
    premiere = t.get("premiere_lecture") or ""
    jeune = premiere and (dt.date.fromisoformat(a["jour"]) - dt.date.fromisoformat(premiere[:10])).days < 14
    hero = (f'    <h1>{L("Ce que les Tunisiens cherchent sur Google, aujourd’hui", "ماذا يبحث التونسيون على غوغل اليوم")}</h1>\n'
            f'    <p class="intro une-ligne">{L("Les recherches en forte hausse en Tunisie, en français et en arabe, mises à jour deux fois par jour.", "عمليات البحث الأكثر صعودًا في تونس، بالعربية والفرنسية، تُحيَّن مرتين في اليوم.")}</p>\n'
            f'    <div class="chiffres">'
            f'<div class="chiffre"><b>{ISO(t["aujourdhui"])}</b><span>{L("tendances aujourd’hui", "اتجاهًا اليوم")}</span></div>'
            f'<div class="chiffre"><b>{ISO(t["semaine"])}</b><span>{L("cette semaine", "هذا الأسبوع")}</span></div>'
            f'<div class="chiffre"><b>{ISO(len(a["nouveautes"]))}</b><span>{L("nouveautés (jamais vues)", "جديد (لم يُرَ من قبل)")}</span></div>'
            f'<div class="chiffre"><b>{ISO(t["mots_distincts"])}</b><span>{L("mots suivis depuis le début", "كلمة متابعة منذ البداية")}</span></div></div>')
    corps = []
    if jeune:
        corps.append(f'<p class="premiere">{L(f"Site tout neuf : nos premières lectures datent du {dfr(premiere[:10])}. L’historique se construit jour après jour ; les listes « nouveautés » et « qui redescendent » prendront tout leur sens après quelques semaines.", f"موقع جديد: أول قراءاتنا بتاريخ {dfr(premiere[:10])}. السجل يُبنى يومًا بعد يوم؛ قوائم «الجديد» و«ما يتراجع» تكتمل بعد بضعة أسابيع.")}</p>')
    corps.append(carte("Aujourd’hui : les recherches qui montent", "اليوم: عمليات البحث الصاعدة",
                       liste(a["aujourdhui"], r, "aujourdhui") + f'<p><a class="btn-second" href="{r}semaine/">{L("Voir toute la semaine →", "عرض كل الأسبوع ←")}</a></p>',
                       sous_fr="Commencées dans les dernières 24 heures, les plus fortes d’abord.", sous_ar="بدأت خلال 24 ساعة الأخيرة، الأقوى أولًا."))
    corps.append(carte("Nouveautés : jamais vues avant", "جديد: لم تُرَ من قبل",
                       liste(a["nouveautes"], r, "nouveautes", vide_fr="Aucune nouveauté depuis la dernière lecture.", vide_ar="لا جديد منذ آخر قراءة."),
                       sous_fr="Des mots que personne ne cherchait avant hier : un nouveau sujet qui commence à attirer l’attention.", sous_ar="كلمات لم يبحث عنها أحد قبل أمس: موضوع جديد يبدأ في لفت الانتباه."))
    corps.append(carte("Hausses inhabituelles", "ارتفاعات غير معتادة",
                       liste(a["hausses"], r, "hausses"),
                       sous_fr=f"Cette semaine : hausse d’au moins {a['seuils']['hausse_forte']} % ou plus de {C.palier_texte(a['seuils']['volume_fort'])[:-1]} recherches.",
                       sous_ar=f"هذا الأسبوع: ارتفاع بـ {a['seuils']['hausse_forte']}٪ على الأقل أو أكثر من {C.palier_texte(a['seuils']['volume_fort'])[:-1]} عملية بحث."))
    corps.append(carte("Opportunités pour les entrepreneurs", "فرص لأصحاب المشاريع",
                       liste(a["opportunites"][:5], r, "opportunites-apercu", limite=5, opp=True, vide_fr="Pas d’opportunité repérée cette semaine.", vide_ar="لم تُرصد فرصة هذا الأسبوع.")
                       + f'<p><a class="btn-second" href="{r}opportunites/">{L("Toutes les opportunités et la méthode →", "كل الفرص والطريقة ←")}</a></p>',
                       sous_fr="Des recherches qui montent dans un secteur utile, souvent avec une intention d’achat (prix, acheter, كراء…).",
                       sous_ar="عمليات بحث صاعدة في قطاع مفيد، غالبًا مع نية شراء (سعر، شراء، كراء…)."))
    corps.append(carte("Par catégorie", "حسب الفئة", grille_categories(a, r), ident="par-categorie",
                       sous_fr="Chaque catégorie a sa page : les tendances de la semaine et les mots que les gens tapent.", sous_ar="لكل فئة صفحتها: اتجاهات الأسبوع والكلمات التي يكتبها الناس."))
    deux = (f'<div class="deux"><div>{liste(a["retombees"][:10], r, "retombees", vide_fr="Rien ne redescend encore : il faut au moins deux semaines de lectures.", vide_ar="لا شيء يتراجع بعد: يلزم أسبوعان من القراءات على الأقل.")}</div>'
            f'<div>{liste(a["recurrents"][:10], r, "recurrents", vide_fr="Rien de récurrent encore (au moins 3 jours différents).", vide_ar="لا شيء متكرر بعد (3 أيام مختلفة على الأقل).")}</div></div>')
    corps.append(carte("Qui redescend, qui revient", "ما يتراجع وما يعود", deux,
                       sous_fr="À gauche : présents la semaine passée, absents cette semaine. À droite : vus sur au moins 3 jours différents ce mois-ci.",
                       sous_ar="يسارًا: كانت الأسبوع الماضي وغابت هذا الأسبوع. يمينًا: ظهرت في 3 أيام مختلفة على الأقل هذا الشهر."))
    corps.append(carte("Comment ça marche ?", "كيف يعمل؟",
                       '<div class="compact">'
                       f'<details><summary>{L("1. Nos robots lisent Google Trends deux fois par jour", "1. روبوتاتنا تقرأ Google Trends مرتين في اليوم")}</summary><p>{L("Les recherches en forte hausse en Tunisie (sur 24 h, 48 h et 7 jours), telles que Google les montre : mot tapé, volume approximatif, progression, recherches liées.", "عمليات البحث الأكثر صعودًا في تونس (24 ساعة، 48 ساعة، 7 أيام) كما يعرضها غوغل: الكلمة، الحجم التقديري، نسبة الصعود، البحوث المرتبطة.")}</p></details>'
                       f'<details><summary>{L("2. Nous gardons tout, jour après jour", "2. نحتفظ بكل شيء يومًا بعد يوم")}</summary><p>{L("Google ne garde que 7 jours. Nous, nous gardons chaque tendance avec sa date : c’est ainsi que naissent les nouveautés, les retours et l’historique.", "غوغل يحتفظ بـ7 أيام فقط. نحن نحتفظ بكل اتجاه مع تاريخه: هكذا تظهر المستجدات والعودة والسجل.")}</p></details>'
                       f'<details><summary>{L("3. Nous classons par catégorie et repérons les opportunités", "3. نصنّف حسب الفئة ونرصد الفرص")}</summary><p>{L("Mots-clés en français, en arabe et en tunisien, puis les catégories de Google ; une opportunité = un secteur utile + une intention d’achat ou un gros volume.", "كلمات مفتاحية بالفرنسية والعربية والتونسية، ثم فئات غوغل؛ الفرصة = قطاع مفيد + نية شراء أو حجم كبير.")}</p></details>'
                       f'</div><p><a href="{r}a-propos/">{L("Toute la méthode, les limites et les sources →", "الطريقة كاملة والحدود والمصادر ←")}</a></p>' + source_bloc(),
                       ident="comment"))
    corps.append(AVIS)
    jsonld = ('<script type="application/ld+json">\n' + json.dumps({"@context": "https://schema.org", "@graph": [
        {"@type": "WebSite", "name": NOM["fr"], "alternateName": NOM["ar"], "url": URL_SITE, "inLanguage": ["fr", "ar"],
         "description": "Ce que les Tunisiens cherchent sur Google : tendances en hausse, nouveautés, catégories, opportunités, mises à jour deux fois par jour."},
        {"@type": "Dataset", "name": "Tendances de recherche en Tunisie (relevés quotidiens)", "url": URL_SITE + "a-propos/#donnees",
         "description": "Relevés datés et catégorisés des recherches en forte hausse en Tunisie, d'après Google Trends.",
         "creator": {"@type": "Organization", "name": "Clicvia"}, "license": "https://tendances.clicvia.com/a-propos/#donnees", "isAccessibleForFree": True,
         "distribution": [{"@type": "DataDownload", "encodingFormat": "application/json", "contentUrl": URL_SITE + "donnees/analyse.json"}]}]},
        ensure_ascii=False, indent=1) + "\n</script>\n")
    titre = "Tendances de recherche en Tunisie : ce que les Tunisiens cherchent sur Google aujourd'hui"
    desc = ("Chaque jour : les mots et expressions en forte hausse dans les recherches Google en Tunisie, en français et en arabe, par catégorie, "
            "avec leur historique et les opportunités pour les entrepreneurs. Données Google Trends, mises à jour automatiquement.")
    return page("", titre, desc, hero, "\n".join(corps), v, maj, PL.ACCUEIL["ar"][0], PL.ACCUEIL["ar"][1], jsonld)


def page_semaine(a, v, maj):
    r = "../"
    hero = hero_simple(r, "Cette semaine", "هذا الأسبوع", "Toutes les tendances de la semaine", "كل اتجاهات الأسبوع",
                       f"{a['totaux']['semaine']} recherches en hausse sur 7 jours, à filtrer par catégorie ou par mot.", f"{a['totaux']['semaine']} عملية بحث صاعدة خلال 7 أيام، يمكن تصفيتها حسب الفئة أو الكلمة.")
    corps = carte("Les 7 derniers jours", "الأيام السبعة الأخيرة",
                  f'<div data-zone-filtre>{filtres(r)}{liste(a["semaine"], r, "semaine", limite=25)}</div>' + source_bloc(),
                  sous_fr="Triées par volume puis par progression. Un mot peut apparaître plusieurs fois s’il est reparti à la hausse un autre jour.",
                  sous_ar="مرتبة حسب الحجم ثم نسبة الصعود. قد تتكرر الكلمة إن عادت للصعود في يوم آخر.")
    return page("semaine/", "Tendances de recherche de la semaine en Tunisie | " + NOM["fr"], f"Les {a['totaux']['semaine']} recherches Google en forte hausse en Tunisie ces 7 derniers jours, par catégorie, avec volume et progression.",
                hero, corps, v, maj, "اتجاهات البحث لهذا الأسبوع في تونس | " + NOM["ar"], f"{a['totaux']['semaine']} عملية بحث صاعدة في تونس خلال 7 أيام، حسب الفئة، مع الحجم ونسبة الصعود.")


def page_categorie(a, cle, v, maj):
    r = "../../"
    fr, ar = cat_nom(cle)
    d = a["categories"][cle]
    mots = (a.get("mots") or {}).get("par_categorie", {}).get(cle, [])
    hero = hero_simple(r, fr, ar, f"{fr} : les recherches qui montent en Tunisie", f"{ar}: عمليات البحث الصاعدة في تونس",
                       f"{d['n_semaine']} tendances cette semaine, {d['n_mois']} ce mois-ci.", f"{d['n_semaine']} اتجاهًا هذا الأسبوع، {d['n_mois']} هذا الشهر.")
    corps = carte("Cette semaine", "هذا الأسبوع", f'<div data-zone-filtre>{filtres(r, avec_cat=False)}{liste(d["top"], r, "cat-semaine", limite=15, vide_fr="Aucune tendance dans cette catégorie cette semaine.", vide_ar="لا اتجاه في هذه الفئة هذا الأسبوع.")}</div>')
    if mots:
        corps += carte("Ce que les gens tapent dans cette catégorie", "ما يكتبه الناس في هذه الفئة",
                       '<div class="etiquettes">' + "".join(f'<span dir="{"rtl" if m["langue"] == "ar" else "ltr"}">{E(m["mot"])}</span>' for m in mots[:40]) + '</div>'
                       + f'<p><a href="{r}mots-tapes/">{L("Tous les mots tapés →", "كل الكلمات المكتوبة ←")}</a></p>',
                       sous_fr="D’après les suggestions de recherche Google en Tunisie (relevé hebdomadaire).", sous_ar="حسب اقتراحات بحث غوغل في تونس (رصد أسبوعي).")
    corps += carte("Autres catégories", "فئات أخرى", '<div class="etiquettes">' + "".join(f'<a href="{r}categorie/{c}/">{L(E(f), a_)}</a>' for c, f, a_ in K.CATEGORIES if c != cle) + '</div>') + source_bloc()
    return page(f"categorie/{cle}/", f"{fr} : tendances de recherche en Tunisie | {NOM['fr']}",
                f"Les recherches Google en hausse en Tunisie dans la catégorie {fr.lower()} : {d['n_semaine']} cette semaine, avec volume, progression et mots tapés.",
                hero, corps, v, maj, f"{ar}: اتجاهات البحث في تونس | {NOM['ar']}", f"عمليات البحث الصاعدة في تونس في فئة {ar}: {d['n_semaine']} هذا الأسبوع، مع الحجم ونسبة الصعود والكلمات المكتوبة.")


def page_opportunites(a, v, maj):
    r = "../"
    hero = hero_simple(r, "Opportunités", "الفرص", "Opportunités commerciales repérées dans les recherches", "فرص تجارية مرصودة في عمليات البحث",
                       "Ce que les Tunisiens commencent à chercher, et qui peut devenir un produit, un service ou un site.", "ما بدأ التونسيون يبحثون عنه، وقد يصبح منتجًا أو خدمة أو موقعًا.")
    expl = (f'<div class="explication">{L("<b>Comment on les repère :</b> une recherche en hausse dans un secteur utile (immobilier, automobile, emploi, éducation, tourisme, santé, commerce, technologie, énergie, argent) <b>et</b> une intention (prix, acheter, louer, كراء, شراء, formation…) ou un gros volume. Ce sont des signaux, pas des certitudes : vérifiez toujours sur le terrain.", "<b>كيف نرصدها:</b> بحث صاعد في قطاع مفيد (عقارات، سيارات، شغل، تعليم، سياحة، صحة، تجارة، تكنولوجيا، طاقة، مال) <b>مع</b> نية (سعر، شراء، كراء، تكوين…) أو حجم كبير. هذه إشارات لا يقين: تثبّت دائمًا على أرض الواقع.")}</div>')
    corps = carte("Cette semaine", "هذا الأسبوع", expl + f'<div data-zone-filtre>{filtres(r)}{liste(a["opportunites"], r, "opportunites", limite=15, opp=True, vide_fr="Pas d’opportunité repérée cette semaine : les listes se remplissent avec le temps.", vide_ar="لم تُرصد فرصة هذا الأسبوع: تمتلئ القوائم مع الوقت.")}</div>')
    corps += carte("Idées de sites et de services", "أفكار مواقع وخدمات",
                   f'<p>{L("Un mot qui revient plusieurs semaines de suite dans « Opportunités » mérite une page dédiée sur un site, une offre ou une formation. Les mots tapés par catégorie (page « Mots tapés ») donnent les expressions exactes à employer.", "الكلمة التي تتكرر عدة أسابيع في «الفرص» تستحق صفحة خاصة في موقع أو عرضًا أو تكوينًا. صفحة «الكلمات المكتوبة» تعطي العبارات الدقيقة التي يجب استعمالها.")}</p>'
                   f'<p><a class="btn-second" href="{r}mots-tapes/">{L("Voir les mots tapés →", "عرض الكلمات المكتوبة ←")}</a></p>') + source_bloc()
    return page("opportunites/", "Opportunités commerciales dans les recherches Google en Tunisie | " + NOM["fr"],
                "Les recherches en hausse qui révèlent un besoin ou une intention d'achat en Tunisie : produits, services et idées de sites, repérés chaque semaine.",
                hero, corps, v, maj, "فرص تجارية في عمليات بحث غوغل في تونس | " + NOM["ar"], "عمليات البحث الصاعدة التي تكشف حاجة أو نية شراء في تونس: منتجات وخدمات وأفكار مواقع، تُرصد كل أسبوع.")


def page_mots(a, v, maj):
    r = "../"
    m = a.get("mots") or {}
    hero = hero_simple(r, "Mots tapés", "الكلمات المكتوبة", "Les mots que les Tunisiens tapent vraiment", "الكلمات التي يكتبها التونسيون فعلًا",
                       f"{m.get('total', 0)} expressions relevées d’après les suggestions de recherche Google, mises à jour chaque semaine.", f"{m.get('total', 0)} عبارة مرصودة حسب اقتراحات بحث غوغل، تُحيَّن كل أسبوع.")
    def etiq(lst):
        return '<div class="etiquettes">' + "".join(f'<span dir="{"rtl" if x["langue"] == "ar" else "ltr"}">{E(x["mot"])}</span>' for x in lst) + '</div>' if lst else f'<p class="liste-vide">{L("Rien pour le moment.", "لا شيء حاليًا.")}</p>'
    corps = (f'<div class="explication">{L("Quand on commence à taper un mot, Google propose les expressions que les gens de Tunisie tapent le plus. Nous relevons ces propositions chaque semaine pour des centaines de débuts de mots, en français et en arabe, et nous gardons la date d’apparition et de disparition de chaque expression.", "عندما نبدأ بكتابة كلمة، يقترح غوغل العبارات التي يكتبها الناس في تونس أكثر. نرصد هذه الاقتراحات كل أسبوع لمئات بدايات الكلمات، بالفرنسية والعربية، ونحتفظ بتاريخ ظهور واختفاء كل عبارة.")}</div>')
    corps += carte("Nouvelles expressions cette semaine", "عبارات جديدة هذا الأسبوع", etiq(m.get("nouveaux", [])),
                   sous_fr="Jamais proposées par Google avant cette semaine (ou première semaine du site).", sous_ar="لم يقترحها غوغل قبل هذا الأسبوع (أو الأسبوع الأول للموقع).")
    par = m.get("par_categorie", {})
    blocs = "".join(f'<details><summary>{L(E(fr), ar)} ({len(par.get(c, []))})</summary>{etiq(par.get(c, []))}</details>' for c, fr, ar in K.CATEGORIES if par.get(c))
    corps += carte("Par catégorie", "حسب الفئة", f'<div class="compact">{blocs}</div>' if blocs else f'<p class="liste-vide">{L("Premier relevé en cours.", "الرصد الأول جارٍ.")}</p>')
    corps += carte("Expressions qui ont disparu", "عبارات اختفت", etiq(m.get("disparus", [])),
                   sous_fr="Proposées avant, plus proposées au dernier relevé : l’intérêt est retombé.", sous_ar="كانت مقترحة ولم تعد كذلك في آخر رصد: تراجع الاهتمام.") + source_bloc()
    return page("mots-tapes/", "Les mots que les Tunisiens tapent sur Google | " + NOM["fr"],
                "Les expressions réellement tapées sur Google en Tunisie, d'après les suggestions de recherche : nouvelles expressions, par catégorie, expressions disparues.",
                hero, corps, v, maj, "الكلمات التي يكتبها التونسيون على غوغل | " + NOM["ar"], "العبارات المكتوبة فعلًا على غوغل في تونس حسب اقتراحات البحث: عبارات جديدة، حسب الفئة، وعبارات اختفت.")


def page_historique(a, memoire, v, maj):
    r = "../"
    hero = hero_simple(r, "Historique", "السجل", "L’historique des tendances, semaine après semaine", "سجل الاتجاهات أسبوعًا بعد أسبوع",
                       "Google ne garde que 7 jours ; ici, tout est gardé depuis la première lecture.", "غوغل يحتفظ بـ7 أيام فقط؛ هنا يُحفظ كل شيء منذ أول قراءة.")
    # tendances par jour (30 derniers jours)
    par_jour = {}
    for t in memoire["tendances"].values():
        j = (t.get("debut") or t["vu_premier"])[:10]
        par_jour[j] = par_jour.get(j, 0) + 1
    jours = sorted(par_jour)[-30:]
    corps = carte("Tendances par jour", "الاتجاهات حسب اليوم", frise([(j[8:10] + "/" + j[5:7], par_jour[j]) for j in jours]),
                  sous_fr="Nombre de recherches entrées en forte hausse chaque jour (30 derniers jours).", sous_ar="عدد عمليات البحث التي دخلت في صعود قوي كل يوم (30 يومًا الأخيرة).")
    sem = a["historique"]["semaines"]
    blocs = []
    for k, b in list(sem.items())[:12]:
        d = dt.date.fromisoformat(k)
        titre_fr = f"Semaine du {d.strftime('%d/%m/%Y')}"; titre_ar = f"أسبوع {d.strftime('%d/%m/%Y')}"
        cats = [(cat_nom(c["cle"])[0], cat_nom(c["cle"])[1], c["n"], c["cle"]) for c in b["categories"][:6]]
        blocs.append(f'<details open><summary>{L(titre_fr, titre_ar)} — {ISO(b["n"])} {L("tendances", "اتجاهًا")}</summary>{barres(cats, r)}{liste(b["top"], r, "sem-" + k, limite=5)}</details>')
    corps += carte("Par semaine", "حسب الأسبوع", '<div class="compact">' + "".join(blocs) + '</div>')
    mois = a["historique"]["mois"]
    blocs = []
    for k, b in list(mois.items())[:12]:
        y, m = k.split("-")
        cats = [(cat_nom(c["cle"])[0], cat_nom(c["cle"])[1], c["n"], c["cle"]) for c in b["categories"][:6]]
        blocs.append(f'<details><summary>{L(MOIS_FR[int(m) - 1].capitalize() + " " + y, MOIS_AR[int(m) - 1] + " " + y)} — {ISO(b["n"])} {L("tendances", "اتجاهًا")}</summary>{barres(cats, r)}{liste(b["top"], r, "mois-" + k, limite=5)}</details>')
    corps += carte("Par mois", "حسب الشهر", '<div class="compact">' + "".join(blocs) + '</div>') + source_bloc()
    return page("historique/", "Historique des tendances de recherche en Tunisie | " + NOM["fr"],
                "Semaine après semaine, mois après mois : le nombre de recherches en hausse en Tunisie, les catégories dominantes et les mots les plus forts, gardés depuis la première lecture.",
                hero, corps, v, maj, "سجل اتجاهات البحث في تونس | " + NOM["ar"], "أسبوعًا بعد أسبوع وشهرًا بعد شهر: عدد عمليات البحث الصاعدة في تونس والفئات الغالبة وأقوى الكلمات، محفوظة منذ أول قراءة.")


def page_mot(a, pm, slugs, v, maj):
    r = "../../"
    fr, ar = cat_nom(pm["categorie"])
    mot = pm["mot"]
    ep = pm["episodes"]
    dernier = ep[0]
    intro_fr = f"Vu {pm['jours']} jour{'s' if pm['jours'] > 1 else ''} en forte hausse, jusqu’à {C.palier_texte(pm['volume_max'])} recherches ({fr.lower()})." if pm["volume_max"] else f"Vu {pm['jours']} jour{'s' if pm['jours'] > 1 else ''} en forte hausse ({fr.lower()})."
    intro_ar = f"ظهرت في {pm['jours']} يوم بصعود قوي، حتى {C.palier_texte(pm['volume_max'])} عملية بحث ({ar})." if pm["volume_max"] else f"ظهرت في {pm['jours']} يوم بصعود قوي ({ar})."
    dir_ = "rtl" if pm["langue"] == "ar" else "ltr"
    hero = (fil(r, "Mot", "كلمة") + f'\n    <h1><span dir="{dir_}">« {E(mot)} »</span> {L("dans les recherches en Tunisie", "في عمليات البحث في تونس")}</h1>\n'
            f'    <p class="intro une-ligne">{L(insecables(intro_fr), intro_ar)}</p>')
    pts = [(dfr(e["jour"])[:5], e.get("volume") or 0) for e in reversed(ep[:20])]
    lignes = "".join(f'<li class="tendance" data-cat="{E(pm["categorie"])}" data-mot="{E(mot)}"><span class="quand">{ISO(dfr(e["jour"]))}</span><span class="mot">{L("début", "البداية")} {ISO((e.get("debut") or "")[11:16])}</span>'
                     f'<span class="vol">{ISO(C.palier_texte(e["volume"]) if e.get("volume") else "")}</span>' + (f'<span class="hausse">{ISO("+" + str(e["hausse"]) + " %")}</span>' if e.get("hausse") else "") + '</li>' for e in ep)
    corps = carte("Les fois où ce mot est monté", "المرات التي صعدت فيها هذه الكلمة", frise(pts) + f'<ul class="tendances" data-limite="10">{lignes}</ul>',
                  sous_fr="Chaque ligne = une poussée de recherches repérée par Google, avec le volume approximatif et la hausse.", sous_ar="كل سطر = موجة بحث رصدها غوغل، مع الحجم التقديري ونسبة الصعود.")
    if pm["liees"]:
        et = "".join((f'<a href="{r}mot/{slugs[C.normaliser(l)]}/" dir="{"rtl" if C.langue_de(l) == "ar" else "ltr"}">{E(l)}</a>' if C.normaliser(l) in slugs else f'<span dir="{"rtl" if C.langue_de(l) == "ar" else "ltr"}">{E(l)}</span>') for l in pm["liees"])
        corps += carte("Recherches liées", "بحوث مرتبطة", f'<div class="etiquettes">{et}</div>', sous_fr="Ce que les mêmes personnes ont aussi cherché, d’après Google.", sous_ar="ما بحث عنه نفس الأشخاص أيضًا، حسب غوغل.")
    corps += carte("Catégorie et suite", "الفئة والمتابعة",
                   f'<p>{L("Catégorie :", "الفئة:")} <a href="{r}categorie/{pm["categorie"]}/">{L(E(fr), ar)}</a></p>'
                   f'<p class="google-lien"><a href="https://trends.google.com/trends/explore?geo=TN&amp;q={E(C.__dict__["urllib"].parse.quote(mot))}" rel="noopener" target="_blank">{L("Voir la courbe de ce mot sur Google Trends →", "عرض منحنى هذه الكلمة على Google Trends ←")}</a></p>') + source_bloc()
    jsonld = ('<script type="application/ld+json">\n' + json.dumps({"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Accueil", "item": URL_SITE},
        {"@type": "ListItem", "position": 2, "name": fr, "item": URL_SITE + f"categorie/{pm['categorie']}/"},
        {"@type": "ListItem", "position": 3, "name": mot, "item": URL_SITE + f"mot/{pm['slug']}/"}]}, ensure_ascii=False) + "\n</script>\n")
    return page(f"mot/{pm['slug']}/", f"« {mot} » : tendance de recherche en Tunisie | {NOM['fr']}",
                f"Le mot « {mot} » dans les recherches Google en Tunisie : {pm['jours']} jour(s) en forte hausse, jusqu'à {C.palier_texte(pm['volume_max'])} recherches, catégorie {fr.lower()}, dernière poussée le {dfr(dernier['jour'])}.",
                hero, corps, v, maj, f"«{mot}»: اتجاه بحث في تونس | {NOM['ar']}", f"كلمة «{mot}» في عمليات بحث غوغل في تونس: {pm['jours']} يوم بصعود قوي، حتى {C.palier_texte(pm['volume_max'])} عملية بحث، فئة {ar}، آخر صعود في {dfr(dernier['jour'])}.",
                jsonld, og_type="article")


# « Comment fonctionne le site ? » : chaque fonction visible a sa phrase (règle § 44) ; tools/test_site.mjs vérifie la liste FONCTIONS.
FONCTIONS = [
    ("Aujourd’hui", "اليوم", "La liste « Aujourd’hui » montre les recherches commencées dans les dernières 24 heures, les plus fortes d’abord, avec leur volume approximatif et leur progression.", "قائمة «اليوم» تعرض عمليات البحث التي بدأت خلال 24 ساعة الأخيرة، الأقوى أولًا، مع حجمها التقديري ونسبة صعودها."),
    ("Nouveautés", "الجديد", "Les « Nouveautés » sont les mots jamais vus dans nos relevés avant les dernières 24 heures : un sujet qui commence à attirer l’attention.", "«الجديد» هي الكلمات التي لم تظهر في قراءاتنا قبل 24 ساعة الأخيرة: موضوع يبدأ في لفت الانتباه."),
    ("Hausses inhabituelles", "ارتفاعات غير معتادة", "Les « Hausses inhabituelles » sont les recherches de la semaine avec une progression d’au moins 500 % ou un volume d’au moins 5 000.", "«الارتفاعات غير المعتادة» هي بحوث الأسبوع بصعود 500٪ على الأقل أو حجم 5000 على الأقل."),
    ("Opportunités", "الفرص", "La page « Opportunités » garde les recherches en hausse d’un secteur utile aux entrepreneurs qui portent une intention (prix, acheter, كراء…) ou un gros volume.", "صفحة «الفرص» تحتفظ بالبحوث الصاعدة في قطاع مفيد لأصحاب المشاريع والتي تحمل نية (سعر، شراء، كراء…) أو حجمًا كبيرًا."),
    ("Catégories", "الفئات", "Chaque tendance est rangée dans une catégorie (immobilier, automobile, emploi, éducation, tourisme, santé, commerce, technologie, administration, énergie, argent, sport, divertissement, météo, politique, religion, autre) et chaque catégorie a sa page.", "كل اتجاه يُصنّف في فئة (عقارات، سيارات، شغل، تعليم، سياحة، صحة، تجارة، تكنولوجيا، إدارة، طاقة، مال، رياضة، ترفيه، طقس، سياسة، دين، أخرى) ولكل فئة صفحتها."),
    ("Mots tapés", "الكلمات المكتوبة", "La page « Mots tapés » relève chaque semaine les expressions que Google propose aux Tunisiens quand ils commencent à taper, avec leur date d’apparition et de disparition.", "صفحة «الكلمات المكتوبة» ترصد كل أسبوع العبارات التي يقترحها غوغل للتونسيين عند بداية الكتابة، مع تاريخ ظهورها واختفائها."),
    ("Historique", "السجل", "La page « Historique » garde tout depuis la première lecture : tendances par jour, par semaine et par mois, avec les catégories dominantes.", "صفحة «السجل» تحتفظ بكل شيء منذ أول قراءة: الاتجاهات حسب اليوم والأسبوع والشهر، مع الفئات الغالبة."),
    ("Page de chaque mot", "صفحة كل كلمة", "Chaque mot a sa page : toutes les fois où il est monté, son volume, ses recherches liées, sa catégorie et un lien vers sa courbe sur Google Trends.", "لكل كلمة صفحتها: كل المرات التي صعدت فيها، حجمها، البحوث المرتبطة، فئتها، ورابط إلى منحناها على Google Trends."),
    ("Qui redescend, qui revient", "ما يتراجع وما يعود", "« Qui redescend » = présents la semaine passée, absents cette semaine ; « qui revient » = vus sur au moins 3 jours différents ce mois-ci.", "«ما يتراجع» = كانت الأسبوع الماضي وغابت هذا الأسبوع؛ «ما يعود» = ظهرت في 3 أيام مختلفة على الأقل هذا الشهر."),
    ("Filtres", "التصفية", "Les listes se filtrent par catégorie et par mot, montrent 10 lignes puis « Voir les N autres ».", "القوائم تُصفّى حسب الفئة والكلمة، وتعرض 10 أسطر ثم «عرض N الأخرى»."),
    ("Deux langues", "لغتان", "Le site existe en français et en arabe, chaque langue à sa propre adresse (bouton « ع / Fr » en haut).", "الموقع متاح بالفرنسية والعربية، ولكل لغة عنوانها الخاص (زر «ع / Fr» في الأعلى)."),
    ("Partager", "شارك", "Le bouton rond « Partager » en haut envoie le lien de la page par le menu de partage du téléphone, sinon par WhatsApp.", "الزر الدائري «شارك» في الأعلى يرسل رابط الصفحة عبر قائمة المشاركة في الهاتف، وإلا عبر واتساب."),
    ("Votre avis", "رأيك", "La section « Votre avis » en bas de l’accueil envoie votre message au créateur du site (e-mail obligatoire pour vous répondre).", "قسم «رأيك» أسفل الصفحة الرئيسية يرسل رسالتك إلى صاحب الموقع (البريد الإلكتروني إجباري للرد عليك)."),
    ("Données ouvertes", "بيانات مفتوحة", "Nos relevés sont publiés en données ouvertes (donnees/analyse.json) : nos propres relevés datés et catégorisés, avec la source citée, pas une copie de Google.", "قراءاتنا منشورة كبيانات مفتوحة (donnees/analyse.json): قراءاتنا المؤرخة والمصنفة مع ذكر المصدر، لا نسخة من غوغل."),
    ("Mise à jour automatique", "تحيين آلي", "Tout est automatique : deux lectures par jour (tendances) et une par semaine (mots tapés) par nos robots, sans intervention humaine ; la date de lecture est en haut de chaque page.", "كل شيء آلي: قراءتان في اليوم (الاتجاهات) وواحدة في الأسبوع (الكلمات المكتوبة) بروبوتاتنا دون تدخل بشري؛ تاريخ القراءة أعلى كل صفحة."),
]


def page_a_propos(a, v, maj):
    r = "../"
    hero = hero_simple(r, "Comment fonctionne le site ?", "كيف يعمل الموقع؟", "Comment fonctionne le site ?", "كيف يعمل الموقع؟",
                       "Ce que le site fait, d’où viennent les chiffres, ce qu’ils veulent dire et ce qu’ils ne disent pas.", "ما يفعله الموقع، من أين تأتي الأرقام، ماذا تعني وماذا لا تقول.")
    fonctions = "".join(f'<details><summary>{L(E(f), fa)}</summary><p>{L(E(d), da)}</p></details>' for f, fa, d, da in FONCTIONS)
    corps = carte("Ce que fait le site", "ما يفعله الموقع", f'<div class="compact" id="fonctions">{fonctions}</div>')
    corps += carte("D’où viennent les chiffres", "من أين تأتي الأرقام",
                   f'<p>{L("<b>Google Trends, Tunisie</b> : la liste des recherches en forte hausse (4 h, 24 h, 48 h et 7 jours), lue deux fois par jour, exactement comme la page publique <a href=https://trends.google.com/trending?geo=TN rel=noopener target=_blank>trends.google.com/trending?geo=TN</a>, et son flux RSS officiel en secours. <b>Suggestions de recherche Google</b> (Tunisie) : les expressions proposées quand on commence à taper, relevées chaque semaine.", "<b>Google Trends، تونس</b>: قائمة عمليات البحث الأكثر صعودًا (4 س، 24 س، 48 س، 7 أيام)، تُقرأ مرتين في اليوم، تمامًا كالصفحة العمومية <a href=https://trends.google.com/trending?geo=TN rel=noopener target=_blank>trends.google.com/trending?geo=TN</a>، وخلاصتها RSS الرسمية كاحتياط. <b>اقتراحات بحث غوغل</b> (تونس): العبارات المقترحة عند بداية الكتابة، تُرصد كل أسبوع.")}</p>'
                   f'<p>{L("Nous lisons ces pages avec un robot identifié, sans contourner aucune protection, et nous citons la source sur chaque page comme Google le demande : <b>Source des données : Google Trends</b>.", "نقرأ هذه الصفحات بروبوت معرَّف، دون تجاوز أي حماية، ونذكر المصدر في كل صفحة كما يطلب غوغل: <b>مصدر البيانات: Google Trends</b>.")}</p>')
    corps += carte("Ce que les chiffres veulent dire (et ne disent pas)", "ماذا تعني الأرقام (وماذا لا تقول)",
                   f'<ul><li>{L("<b>Volume</b> : un ordre de grandeur donné par Google par paliers (200+, 1 000+, 5 000+…), jamais un nombre exact. On ne l’additionne pas entre mots.", "<b>الحجم</b>: تقدير يعطيه غوغل بدرجات (200+، 1000+، 5000+…)، وليس رقمًا دقيقًا. لا نجمعه بين الكلمات.")}</li>'
                   f'<li>{L("<b>Progression</b> : la hausse en % calculée par Google sur la période (plafonnée à 1 000 %).", "<b>نسبة الصعود</b>: الارتفاع بالنسبة المئوية كما يحسبه غوغل على الفترة (بحد أقصى 1000٪).")}</li>'
                   f'<li>{L("<b>Seulement les hausses</b> : Google Trends montre ce qui monte, pas le palmarès absolu (« facebook » ou « youtube » n’apparaissent jamais : trop stables).", "<b>الصعود فقط</b>: يعرض Google Trends ما يرتفع، لا الترتيب المطلق («facebook» أو «youtube» لا تظهر أبدًا: مستقرة جدًا).")}</li>'
                   f'<li>{L("<b>Pas de régions</b> : Google ne donne pas de tendances par gouvernorat pour la Tunisie.", "<b>لا جهات</b>: لا يعطي غوغل اتجاهات حسب الولاية لتونس.")}</li>'
                   f'<li>{L("<b>Deux tendances se comparent</b> seulement sur la même période et la même date de lecture.", "<b>يُقارَن اتجاهان</b> فقط على نفس الفترة ونفس تاريخ القراءة.")}</li>'
                   f'<li>{L("<b>Catégories</b> : décidées par nos mots-clés (français, arabe, tunisien) puis par les catégories de Google ; un mot mal rangé peut nous être signalé (« Votre avis »).", "<b>الفئات</b>: تُحدَّد بكلماتنا المفتاحية (فرنسية، عربية، تونسية) ثم بفئات غوغل؛ يمكن إبلاغنا بكلمة مصنفة خطأ («رأيك»).")}</li></ul>')
    corps += carte("Données ouvertes", "بيانات مفتوحة",
                   f'<p id="donnees">{L("Nos relevés sont réutilisables librement avec la mention « Tendances de recherche en Tunisie (tendances.clicvia.com), d’après Google Trends » : <a href=../donnees/analyse.json>donnees/analyse.json</a> (l’analyse du jour) et <a href=../donnees/tendances.json>donnees/tendances.json</a> (toutes les tendances vues, datées et catégorisées). Ce sont nos relevés, pas une copie des services de Google.", "قراءاتنا قابلة لإعادة الاستعمال بحرية مع ذكر «اتجاهات البحث في تونس (tendances.clicvia.com)، حسب Google Trends»: <a href=../donnees/analyse.json>donnees/analyse.json</a> (تحليل اليوم) و<a href=../donnees/tendances.json>donnees/tendances.json</a> (كل الاتجاهات المرصودة، مؤرخة ومصنفة). هذه قراءاتنا لا نسخة من خدمات غوغل.")}</p>')
    corps += carte("Qui est derrière ce site", "من وراء هذا الموقع",
                   f'<p>{L("Un site indépendant de la famille <a href=https://clicvia.com/ rel=noopener target=_blank>Clicvia</a> (services gratuits pour la Tunisie), sans lien avec Google. Il est entièrement automatique. Les marques citées dans les tendances appartiennent à leurs propriétaires.", "موقع مستقل من عائلة <a href=https://clicvia.com/ rel=noopener target=_blank>Clicvia</a> (خدمات مجانية لتونس)، لا علاقة له بغوغل. وهو آلي بالكامل. العلامات المذكورة في الاتجاهات ملك لأصحابها.")}</p>'
                   f'<p><a class="btn-second" href="{r}#avis">{L("Nous écrire (« Votre avis ») →", "راسلنا («رأيك») ←")}</a></p>')
    jsonld = ('<script type="application/ld+json">\n' + json.dumps({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": "D'où viennent les chiffres de Tendances de recherche en Tunisie ?", "acceptedAnswer": {"@type": "Answer", "text": "De Google Trends (recherches en forte hausse en Tunisie, lues deux fois par jour) et des suggestions de recherche Google (relevées chaque semaine). Source des données : Google Trends."}},
        {"@type": "Question", "name": "Les volumes sont-ils des nombres exacts ?", "acceptedAnswer": {"@type": "Answer", "text": "Non : Google donne un ordre de grandeur par paliers (200+, 1 000+, 5 000+…). Nous les affichons tels quels, jamais additionnés."}},
        {"@type": "Question", "name": "Pourquoi les recherches les plus courantes (facebook, youtube) n'apparaissent-elles pas ?", "acceptedAnswer": {"@type": "Answer", "text": "Google Trends montre les recherches qui montent, pas le palmarès absolu : les mots très stables n'y figurent jamais."}},
        {"@type": "Question", "name": "Y a-t-il des tendances par gouvernorat ?", "acceptedAnswer": {"@type": "Answer", "text": "Pas pour le moment : Google ne publie pas de tendances régionales pour la Tunisie."}}]}, ensure_ascii=False, indent=1) + "\n</script>\n")
    return page("a-propos/", "Comment fonctionne le site ? Méthode, sources et limites | " + NOM["fr"],
                "Comment Tendances de recherche en Tunisie lit Google Trends deux fois par jour, garde l'historique, classe par catégorie et repère les opportunités ; ce que les volumes veulent dire et leurs limites.",
                hero, corps, v, maj, "كيف يعمل الموقع؟ الطريقة والمصادر والحدود | " + NOM["ar"], "كيف يقرأ الموقع Google Trends مرتين في اليوم، ويحفظ السجل، ويصنف حسب الفئة، ويرصد الفرص؛ ماذا تعني الأحجام وما حدودها.", jsonld)


# ---------------------------------------------------------------- fichiers annexes
ROBOTS = """# Assistants IA qui répondent à une question en citant leur source : bienvenus (référencement sur les IA, 13/10/2026)
User-agent: OAI-SearchBot
User-agent: ChatGPT-User
User-agent: PerplexityBot
User-agent: Perplexity-User
User-agent: Claude-SearchBot
User-agent: Claude-User
User-agent: MistralAI-User
User-agent: DuckAssistBot
Allow: /

User-agent: Googlebot
Allow: /

User-agent: Bingbot
Allow: /

""" + "".join(f"User-agent: {b}\nDisallow: /\n\n" for b in ["GPTBot", "CCBot", "ClaudeBot", "Claude-Web", "anthropic-ai", "Google-Extended", "Bytespider", "Amazonbot", "Applebot-Extended", "Meta-ExternalAgent", "FacebookBot", "Diffbot", "Omgilibot", "cohere-ai", "ImagesiftBot", "HTTrack", "WebCopier", "WebZIP", "Offline Explorer", "SiteSnagger"]) + f"""User-agent: *
Allow: /

Sitemap: {URL_SITE}sitemap.xml
"""


def ecrire(chemin, texte):
    p = os.path.join(RACINE, chemin)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8", newline="\n") as f:
        f.write(texte)


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    a = C.lire_json(os.path.join(C.DONNEES, "analyse.json"))
    memoire = C.lire_json(os.path.join(C.DONNEES, "tendances.json"))
    if not a or not memoire:
        sys.exit("ÉCHEC : donnees/analyse.json ou tendances.json absent (lancer collecte.py puis analyse.py)")
    v = version("assets/style.css", "assets/page.js", "assets/app.js", "assets/avis.js", "robot/construire_site.py")
    maj = a["maj"][:10]
    slugs = {pm["mot_norm"]: pm["slug"] for pm in a["pages_mots"]}
    pages = {"": accueil(a, v, maj), "semaine/": page_semaine(a, v, maj), "opportunites/": page_opportunites(a, v, maj),
             "mots-tapes/": page_mots(a, v, maj), "historique/": page_historique(a, memoire, v, maj), "a-propos/": page_a_propos(a, v, maj)}
    for c, _, _ in K.CATEGORIES:
        pages[f"categorie/{c}/"] = page_categorie(a, c, v, maj)
    dates = {}
    for pm in a["pages_mots"]:
        pages[f"mot/{pm['slug']}/"] = page_mot(a, pm, slugs, v, maj)
        dates[f"mot/{pm['slug']}/"] = pm["episodes"][0]["jour"]
    # pages de mots devenues vieilles : retirées (le sitemap fait foi)
    dossier_mots = os.path.join(RACINE, "mot")
    if os.path.isdir(dossier_mots):
        for d in os.listdir(dossier_mots):
            if f"mot/{d}/" not in pages:
                for sous in (os.path.join(dossier_mots, d), os.path.join(RACINE, "ar", "mot", d)):
                    if os.path.isdir(sous):
                        for f in os.listdir(sous):
                            os.remove(os.path.join(sous, f))
                        os.rmdir(sous)
    trad = {}
    manques = 0
    for chemin, h in pages.items():
        ecrire(chemin + "index.html", h)
        titre_ar = re.search(r'data-titre-ar="([^"]*)"', h).group(1)
        desc_ar = re.search(r'data-desc-ar="([^"]*)"', h).group(1)
        h_ar, manque = PL.variante(h, URL_SITE, chemin, "ar", ["fr", "ar"], trad, meta=(html.unescape(titre_ar), html.unescape(desc_ar), None))
        manques += manque
        ecrire("ar/" + chemin + "index.html", h_ar)
    # sitemap (lastmod VRAI : date des données pour les pages vivantes, date du dernier épisode pour un mot)
    lignes = []
    for chemin in pages:
        lm = dates.get(chemin, maj)
        for l in ("fr", "ar"):
            lignes.append(f'<url><loc>{PL.adresse(URL_SITE, chemin, l)}</loc><lastmod>{lm}</lastmod>'
                          + "".join(f'<xhtml:link rel="alternate" hreflang="{x}" href="{PL.adresse(URL_SITE, chemin, x)}"/>' for x in ("fr", "ar"))
                          + f'<xhtml:link rel="alternate" hreflang="x-default" href="{PL.adresse(URL_SITE, chemin, "fr")}"/></url>')
    ecrire("sitemap.xml", '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n' + "\n".join(lignes) + "\n</urlset>\n")
    ecrire("robots.txt", ROBOTS)
    ecrire("manifest.webmanifest", json.dumps({"id": "/", "name": NOM["fr"], "short_name": "Tendances TN", "description": "Ce que les Tunisiens cherchent sur Google, chaque jour.",
                                               "start_url": "./", "scope": "./", "display": "standalone", "lang": "fr", "dir": "auto", "theme_color": "#5B21B6", "background_color": "#F3F6F9",
                                               "icons": [{"src": "assets/icons/icon-192.png", "sizes": "192x192", "type": "image/png"}, {"src": "assets/icons/icon-512.png", "sizes": "512x512", "type": "image/png"},
                                                         {"src": "assets/icons/icon-maskable-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"}]}, ensure_ascii=False, indent=2) + "\n")
    ecrire("llms.txt", f"""# Tendances de recherche en Tunisie

> Ce que les Tunisiens cherchent sur Google : recherches en forte hausse (24 h, 7 jours), nouveautés, catégories, opportunités pour les entrepreneurs, historique construit jour après jour. Français et arabe (une adresse par langue : /ar/). Adresse : {URL_SITE}

Source des données : Google Trends (Tunisie) et suggestions de recherche Google ; lecture automatique deux fois par jour. Volumes = ordres de grandeur par paliers, jamais exacts.

## Pages
- [Aujourd'hui]({URL_SITE}) : recherches commencées dans les 24 dernières heures, nouveautés, hausses inhabituelles, opportunités, catégories.
- [Cette semaine]({URL_SITE}semaine/) : toutes les tendances des 7 derniers jours, filtrables.
- [Opportunités]({URL_SITE}opportunites/) : recherches en hausse qui révèlent un besoin ou une intention d'achat.
- [Mots tapés]({URL_SITE}mots-tapes/) : expressions réellement tapées (suggestions Google), nouvelles et disparues.
- [Historique]({URL_SITE}historique/) : par jour, semaine et mois.
- [Catégories]({URL_SITE}categorie/immobilier/) : une page par catégorie (immobilier, automobile, emploi, education, tourisme, sante, commerce, technologie, administration, energie, finance, sport, divertissement, meteo, politique, religion, autre).
- [Comment fonctionne le site ?]({URL_SITE}a-propos/) : méthode, limites, sources.

## Données ouvertes
- {URL_SITE}donnees/analyse.json : l'analyse du jour (JSON) ; {URL_SITE}donnees/tendances.json : toutes les tendances vues. Réutilisation libre avec la mention « Tendances de recherche en Tunisie (tendances.clicvia.com), d'après Google Trends ».

## À savoir
- Site indépendant, non officiel, sans lien avec Google. Pour citer : le nom du site et le lien de la page.
""")
    print(f"site : {len(pages)} pages françaises + {len(pages)} pages arabes ({len(a['pages_mots'])} pages de mots), version {v}"
          + (f" — {manques} textes sans traduction" if manques else ""))


if __name__ == "__main__":
    main()
