"""Fiche à apporter à la consultation : texte simple, sans aucun nom ni identifiant."""
from calendrier import serie_risque
from genetique import CATEGORIES, category_probabilities, needs_counselling

LABELS = {
    "fr": {"non_porteur": "enfant non porteur", "porteur": "enfant porteur (sans la maladie)",
           "drepano": "enfant avec une forme de drépanocytose",
           "autre": "autre combinaison, à voir avec un spécialiste"},
    "en": {"non_porteur": "child not a carrier", "porteur": "child who is a carrier (without the disease)",
           "drepano": "child with a form of sickle cell disease",
           "autre": "other combination, to review with a specialist"},
}

S = {
    "fr": {
        "title": "FICHE À APPORTER À LA CONSULTATION",
        "meta": "Aucun nom ni identifiant. Générée le {date}.",
        "results": "Résultats saisis", "a": "Partenaire A", "b": "Partenaire B",
        "family": "Proches (statuts saisis)", "unknown": "statut inconnu",
        "risks": "Risque estimé pour chaque grossesse",
        "multi": "Probabilité d'avoir au moins un enfant avec une forme drépanocytaire",
        "preg": "grossesse(s)",
        "counsel_yes": "Un conseil génétique est recommandé pour ce couple.",
        "counsel_no": "Aucun risque d'enfant atteint n'est calculé, mais un conseil reste possible.",
        "ai": "Explication générée par IA (relue par un garde-fou automatique)",
        "questions": "Questions à poser au professionnel de santé",
        "q": ["Quel est le risque exact pour notre couple, d'après nos résultats ?",
              "Faut-il tester d'autres membres de la famille ?",
              "Quelles options existent avant et pendant une grossesse, et où sont-elles disponibles ?",
              "Quel suivi est conseillé pour un enfant porteur ou atteint ?",
              "Où pouvons-nous faire confirmer nos résultats ?"],
        "disclaimer": "Cet outil informe : il ne pose aucun diagnostic et ne remplace pas un conseil "
                      "génétique. Seul un professionnel de santé peut interpréter votre situation.",
    },
    "en": {
        "title": "SHEET TO BRING TO YOUR CONSULTATION",
        "meta": "No name or identifier. Generated on {date}.",
        "results": "Results entered", "a": "Partner A", "b": "Partner B",
        "family": "Relatives (statuses entered)", "unknown": "status unknown",
        "risks": "Estimated risk for each pregnancy",
        "multi": "Chance of at least one child with a sickle cell form",
        "preg": "pregnancy(ies)",
        "counsel_yes": "Genetic counselling is recommended for this couple.",
        "counsel_no": "No risk of an affected child is calculated, but counselling remains possible.",
        "ai": "AI-generated explanation (checked by an automatic safeguard)",
        "questions": "Questions to ask the health professional",
        "q": ["What is the exact risk for our couple, based on our results?",
              "Should other family members be tested?",
              "What options exist before and during a pregnancy, and where are they available?",
              "What follow-up is advised for a child who is a carrier or affected?",
              "Where can we get our results confirmed?"],
        "disclaimer": "This tool informs: it makes no diagnosis and does not replace genetic counselling. "
                      "Only a health professional can interpret your situation.",
    },
}

ROLE = {
    "fr": {"a_m": "Mère de A", "a_p": "Père de A", "b_m": "Mère de B", "b_p": "Père de B"},
    "en": {"a_m": "Mother of A", "a_p": "Father of A", "b_m": "Mother of B", "b_p": "Father of B"},
}


def _disp(g):
    return g.replace("T", "β")


def build_fiche(lang, g1, g2, parents, ai, date_txt):
    """ai : dict {'explication','points_cles','questions_medecin'} ou None."""
    lang = lang if lang in S else "fr"
    s, labels, roles = S[lang], LABELS[lang], ROLE[lang]
    out = [s["title"], s["meta"].format(date=date_txt), "", s["results"],
           f"- {s['a']} : {_disp(g1)}", f"- {s['b']} : {_disp(g2)}"]
    if parents:
        out += ["", s["family"]]
        for key in ("a_m", "a_p", "b_m", "b_p"):
            g = parents.get(key, "?")
            out.append(f"- {roles[key]} : {s['unknown'] if g == '?' else _disp(g)}")
    probs = category_probabilities(g1, g2)
    out += ["", s["risks"]]
    out += [f"- {labels[c]} : {int(probs[c] * 100)} %" for c in CATEGORIES if probs[c] > 0]
    serie = serie_risque(g1, g2, 5)
    if serie[0] > 0:
        out += ["", s["multi"]]
        out += [f"- {n} {s['preg']} : {float(v) * 100:.0f} %" for n, v in enumerate(serie, 1)]
    out += ["", s["counsel_yes"] if needs_counselling(g1, g2) else s["counsel_no"]]
    if ai:
        out += ["", s["ai"], ai["explication"]]
        out += [f"- {p}" for p in ai["points_cles"]]
    out += ["", s["questions"]]
    out += [f"- {q}" for q in s["q"]]
    if ai:
        out += [f"- {q}" for q in ai["questions_medecin"] if q not in s["q"]]
    out += ["", s["disclaimer"]]
    return "\n".join(out) + "\n"
