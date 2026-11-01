# -*- coding: utf-8 -*-
"""Catégories de l'Observatoire : celles demandées par Ahmed (immobilier, automobile, emploi, tourisme, santé, commerce, technologie,
éducation, administration, énergie) + sport, divertissement, météo, politique, finance, religion, autre.

Une tendance est classée d'abord par des MOTS-CLÉS (français, arabe, tunisien en lettres latines), sinon par les codes de catégorie
de Google Trends (vérifiés sur les données du 01/11/2026 : 1 autos, 2 beauté/mode, 3 affaires/finance, 4 divertissement,
5 alimentation, 6 jeux, 7 santé, 8 loisirs, 9 emploi/éducation, 10 lois/administration, 11 autre, 13 animaux, 14 politique,
15 sciences, 16 achats, 17 sport, 18 technologie, 19 voyages, 20 climat), sinon « autre ».
Règle commune § 40 : les mots qui restent en « autre » sont comptés ; quand un même mot inconnu revient souvent, il est signalé dans
le carnet des catégories (donnees/carnet-categories.json) pour qu'on lui donne une catégorie."""
import re

CATEGORIES = [
    ("immobilier", "Immobilier", "العقارات"),
    ("automobile", "Automobile", "السيارات"),
    ("emploi", "Emploi et concours", "الشغل والمناظرات"),
    ("education", "Éducation", "التعليم"),
    ("tourisme", "Tourisme et voyages", "السياحة والسفر"),
    ("sante", "Santé", "الصحة"),
    ("commerce", "Commerce et consommation", "التجارة والاستهلاك"),
    ("technologie", "Technologie", "التكنولوجيا"),
    ("administration", "Administration et démarches", "الإدارة والإجراءات"),
    ("energie", "Énergie", "الطاقة"),
    ("finance", "Argent et banques", "المال والبنوك"),
    ("football", "Football", "كرة القدم"),
    ("sport", "Autres sports", "رياضات أخرى"),
    ("divertissement", "Divertissement et médias", "الترفيه والإعلام"),
    ("meteo", "Météo", "الطقس"),
    ("politique", "Politique et actualité", "السياسة والأخبار"),
    ("religion", "Religion et fêtes", "الدين والأعياد"),
    ("autre", "Autre", "أخرى"),
]
PAR_CLE = {c[0]: c for c in CATEGORIES}
# catégories « utiles aux entrepreneurs » : seules celles-ci donnent des opportunités commerciales
COMMERCIALES = {"immobilier", "automobile", "emploi", "education", "tourisme", "sante", "commerce", "technologie", "energie", "finance"}

GOOGLE = {1: "automobile", 2: "commerce", 3: "finance", 4: "divertissement", 5: "commerce", 6: "divertissement", 7: "sante",
          8: "divertissement", 9: "education", 10: "administration", 11: "autre", 13: "autre", 14: "politique", 15: "technologie",
          16: "commerce", 17: "sport", 18: "technologie", 19: "tourisme", 20: "meteo"}

# mots-clés : (expression régulière sur le mot normalisé, catégorie). L'ordre compte : la première qui correspond gagne.
MOTS = [
    (r"\b(appartement|maison|villa|terrain|studio|loyer|immobili|duplex|s\+[1-4]|promoteur)\b|كراء شق|شقه|شقق|منزل|عقار|ارض للبيع|فيلا|دار للبيع|كراء منازل", "immobilier"),
    (r"\b(voiture|auto-?ecole|permis|vignette|visite technique|leasing auto|carburant|essence|gasoil|diesel|pneu|moto|camion)\b|سياره|سيارات|رخصه سياقه|معلوم الجولان|بنزين|كازوال", "automobile"),
    (r"\b(concours|recrutement|emploi|offre d'emploi|stage|aneti|cnss|cnrps|salaire|smig|grève|greve|chomage|travail)\b|مناظره|مناظرات|انتداب|شغل|خدمه|اجر|اضراب|توظيف|عمل", "emploi"),
    (r"\b(bac|baccalaur|universit|faculte|inscription|orientation|resultat|examen|ecole|lycee|master|bourse d'etude|cours|formation|iset|isetcom)\b|باكالوريا|جامعه|كليه|نتائج|امتحان|مدرسه|معهد|توجيه|تسجيل|دروس|تكوين", "education"),
    (r"\b(hotel|vol|billet|aeroport|tunisair|nouvelair|visa|voyage|omra|hajj|croisiere|ferry|ctn|plage|djerba|tourisme)\b|فندق|طيران|رحله|تاشيره|فيزا|عمره|سفر|شاطئ", "tourisme"),
    (r"\b(hopital|medecin|docteur|pharmacie|clinique|grippe|vaccin|covid|cancer|dentiste|maladie|urgence|cnam|medicament)\b|مستشفى|طبيب|دواء|صيدليه|مرض|لقاح|كورونا|كنام|صحه", "sante"),
    (r"\b(iphone|samsung|android|ios|telephone|smartphone|pc|ordinateur|internet|wifi|4g|5g|ooredoo|orange|telecom|topnet|facebook|instagram|tiktok|whatsapp|youtube|chatgpt|ia|intelligence artificielle|application|jeu video|playstation|xbox|binance|crypto|bitcoin)\b|هاتف|انترنت|تطبيق|اوريدو|اورنج|اتصالات|فايسبوك|تيك توك|ذكاء اصطناعي", "technologie"),
    (r"\b(journal officiel|jort|ministere|municipalite|commune|gouvernorat|carte d'identite|passeport|cin|e-?houwiya|elections?|permis de construire|tribunal|justice|loi|decret|impot|declaration|douane|tunisie telecom|poste tunisienne|la poste)\b|الرائد الرسمي|وزاره|بلديه|ولايه|بطاقه تعريف|جواز سفر|هويه|محكمه|قانون|مرسوم|ضريبه|جباي|ديوانه|البريد", "administration"),
    (r"\b(steg|electricite|coupure|gaz|bouteille de gaz|panneau solaire|solaire|photovolta|petrole|energie|eau|sonede)\b|كهرباء|ستاغ|انقطاع|غاز|قاروره|طاقه شمسيه|شمسي|بترول|ماء|صوناد", "energie"),
    (r"\b(banque|biat|attijari|stb|bna|amen bank|zitouna|credit|pret|dinar|euro|dollar|change|bourse|assurance|d17|flouci|argent|inflation|bct)\b|بنك|قرض|دينار|اورو|دولار|صرف|بورصه|تامين|فلوس|تضخم", "finance"),
    (r"\b(prix|promo|promotion|solde|boutique|magasin|carrefour|monoprix|geant|aziza|mg|jumia|tayara|achat|vente|acheter|huile|sucre|lait|viande|pain|legume|aid el|mouton)\b|سعر|اسعار|ثمن|بيع|شراء|تخفيض|عرض|مغازه|زيت|سكر|حليب|لحم|خبز|خضر|علوش", "commerce"),
    (r"\b(match|classement|ligue|championnat|coupe|club|stade|equipe nationale|joueur|football|foot|buteur|transfert|mercato|barca|real|psg|milan|inter|bayern|liverpool|city|arsenal|chelsea|juventus|dortmund|atletico|esperance|etoile|css|ca|est|eas|usm|ballon d'or|ol|om|can|fifa|uefa|mondial|derby|penalty|gardien|entraineur|fc|united|tottenham|napoli|roma|ajax|benfica|porto|zamalek|ahly|wydad|raja|alaves|levante|brighton|bologne|getafe|villarreal|sevilla|betis|lazio|monaco|marseille|lille|lyon|rennes|nice|lens|st etienne|bastia|sfaxien|bizertin|us monastir|gabesien|olympique beja|stade tunisien|ca bizertin|club africain|kompany|mbappe|yamal|ronaldo|messi|haaland|salah|vinicius|bellingham)\b|مباراه|ترتيب|رابطه|بطوله|كاس|نادي|ملعب|منتخب|لاعب|كره القدم|الترجي|النجم|الافريقي|الصفاقسي|برشلونه|ريال|مبابي|رونالدو|ميسي|هدف|حارس|مدرب|انتقالات", "football"),
    (r"\b(basket|handball|hand|tennis|volley|natation|athletisme|marathon|boxe|mma|ufc|judo|karate|cyclisme|tour de france|formule 1|f1|moto gp|golf|rugby|jeux olympiques|jo|escrime|halterophilie|petanque)\b|كره السله|كره اليد|تنس|سباحه|العاب القوى|ملاكمه|جودو|كاراتيه|دراجات|فورمولا|رقبي|الالعاب الاولمبيه", "sport"),
    (r"\b(film|serie|episode|saison|musique|chanson|concert|festival|cinema|netflix|tv|chaine|emission|acteur|chanteur|halloween|celebrite|star|miss)\b|فيلم|مسلسل|حلقه|موسم|اغنيه|حفل|مهرجان|سينما|قناه|برنامج|ممثل|مغني|نجم", "divertissement"),
    (r"\b(meteo|temps|pluie|pluies|orage|neige|canicule|vent|temperature|inondation|seisme|tremblement)\b|طقس|امطار|مطر|عاصفه|ثلج|حراره|رياح|فيضان|زلزال", "meteo"),
    (r"\b(president|parlement|gouvernement|ministre|election|vote|manifestation|guerre|israel|gaza|palestine|france|algerie|libye|usa|onu|crise)\b|رئيس|برلمان|حكومه|وزير|انتخابات|تصويت|مظاهره|حرب|اسرائيل|غزه|فلسطين|فرنسا|الجزائر|ليبيا|ازمه", "politique"),
    (r"\b(ramadan|aid|eid|mouled|achoura|priere|mosquee|coran|hijri|moharram|jeune|fete)\b|رمضان|عيد|مولد|عاشوراء|صلاه|مسجد|قران|هجري|محرم|صيام", "religion"),
]
_MOTS = [(re.compile(r), c) for r, c in MOTS]


def categorie(mot_norm, codes_google=()):
    """Catégorie de l'Observatoire pour un mot normalisé, d'après les mots-clés puis les codes Google."""
    for r, c in _MOTS:
        if r.search(mot_norm):
            return c
    for code in codes_google or []:
        c = GOOGLE.get(code)
        if c and c != "autre":
            return c
    return "autre"


# marqueurs d'une intention d'achat ou de besoin (opportunité commerciale)
INTENTION = re.compile(r"\b(prix|tarif|acheter|achat|vente|vendre|louer|location|promo|devis|formation|cours|livraison|reparation|occasion|pas cher|meilleur|comparatif|avis|ouvrir|creer|comment)\b"
                       r"|سعر|اسعار|ثمن|شراء|بيع|للبيع|كراء|للكراء|عرض|تخفيض|تكوين|دوره|توصيل|اصلاح|مستعمل|رخيص|افضل|كيفاش|كيف")


def intention_commerciale(mot_norm):
    return bool(INTENTION.search(mot_norm))
