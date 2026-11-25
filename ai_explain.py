"""Couche IA explicable : le LLM explique, il ne calcule jamais.

Il reçoit uniquement des pourcentages (aucun nom, aucun génotype). Sa réponse est
validée (JSON + garde-fou de formulation) ; en cas d'échec, un texte fixe est utilisé.
"""
import json
import re

from genetique import category_probabilities, needs_counselling

LANGS = {"fr": "français", "en": "English"}

SYSTEM_PROMPT = """Tu expliques à un couple, en {langue} et en langage simple (niveau : {niveau}),
des probabilités d'hérédité liées à la drépanocytose. Règles :
- Tu n'inventes ni ne modifies aucun chiffre : utilise seulement ceux fournis.
- Tu parles de risque ("le risque est de 25 % à chaque grossesse"), jamais de certitude.
- Tu ne poses aucun diagnostic, ne parles d'aucun traitement et ne recommandes aucun choix familial.
- Tu rappelles que seul un conseiller en génétique ou un spécialiste peut interpréter la situation.
- Tu précises que chaque grossesse est indépendante des précédentes.
Réponds UNIQUEMENT par un objet JSON, sans Markdown, de la forme :
{{"explication": "...", "points_cles": ["...", "..."], "questions_medecin": ["...", "..."]}}"""

FORBIDDEN = [
    r"\bvous avez\b", r"\bvotre enfant (aura|sera|est)\b", r"\bvous êtes (atteint|malade|porteur)",
    r"\bvous allez avoir\b", r"\btraitement\b",
    r"\byou have\b", r"\byour child (will|is)\b", r"\byou are (affected|sick)\b", r"\btreatment\b",
]
REQUIRED_ANY = ["conseiller en génétique", "spécialiste", "hématologue",
                "genetic counsellor", "genetic counselor", "specialist"]
KEYS = {"explication": str, "points_cles": list, "questions_medecin": list}

LABELS = {
    "fr": {"non_porteur": "enfant non porteur", "porteur": "enfant porteur (sans la maladie)",
           "drepano": "enfant avec une forme de drépanocytose",
           "autre": "autre combinaison, à voir avec un spécialiste"},
    "en": {"non_porteur": "child not a carrier", "porteur": "child who is a carrier (without the disease)",
           "drepano": "child with a form of sickle cell disease",
           "autre": "other combination, to review with a specialist"},
}


def build_payload(g1, g2):
    """Données minimales envoyées au LLM : pourcentages par catégorie, rien d'autre."""
    probs = category_probabilities(g1, g2)
    return {
        "risque_par_grossesse_en_pourcent": {c: int(p * 100) for c, p in probs.items() if p > 0},
        "conseil_genetique_recommande": needs_counselling(g1, g2),
    }


def validate(raw):
    """Retourne le dict validé, ou None si la réponse est inutilisable ou non conforme."""
    try:
        data = json.loads(re.sub(r"^```(?:json)?|```$", "", raw.strip(), flags=re.M).strip())
    except (ValueError, AttributeError):
        return None
    if not isinstance(data, dict) or any(not isinstance(data.get(k), t) for k, t in KEYS.items()):
        return None
    text = " ".join([data["explication"], *map(str, data["points_cles"]),
                     *map(str, data["questions_medecin"])]).lower()
    if any(re.search(p, text) for p in FORBIDDEN):
        return None
    if not any(r in text for r in REQUIRED_ANY):
        return None
    return data


def fallback(g1, g2, lang):
    """Texte fixe, sûr, utilisé si l'IA est indisponible ou refusée par le garde-fou."""
    labels = LABELS["en" if lang == "en" else "fr"]
    probs = {c: int(p * 100) for c, p in category_probabilities(g1, g2).items() if p > 0}
    detail = ", ".join(f"{labels[c]} : {p} %" for c, p in probs.items())
    if lang == "en":
        return {"explication": f"For each pregnancy, the estimated risks are: {detail}. "
                               "Only a genetic counsellor or a specialist can interpret your situation.",
                "points_cles": ["Each pregnancy is independent of the previous ones."],
                "questions_medecin": ["What are our options and where can we get tested?"]}
    return {"explication": f"Pour chaque grossesse, les risques estimés sont : {detail}. "
                           "Seul un conseiller en génétique ou un spécialiste peut interpréter votre situation.",
            "points_cles": ["Chaque grossesse est indépendante des précédentes."],
            "questions_medecin": ["Quelles sont nos options et où faire les tests ?"]}


LAST_ERROR = ""


def explain(g1, g2, lang, niveau, call_llm, tries=2):
    """call_llm(system: str, user: str) -> str.

    Retourne (résultat, source) avec source = 'ia' ou 'fixe'.
    """
    global LAST_ERROR
    LAST_ERROR = ""
    system = SYSTEM_PROMPT.format(langue=LANGS[lang], niveau=niveau)
    user = json.dumps(build_payload(g1, g2), ensure_ascii=False)
    for _ in range(tries):
        try:
            raw = call_llm(system, user)
        except Exception as e:
            LAST_ERROR = f"Appel à l'IA impossible : {type(e).__name__}: {e}"
            continue
        data = validate(raw)
        if data:
            return data, "ia"
        LAST_ERROR = "Réponse refusée par le garde-fou. Début : " + raw[:300].replace("\n", " ")
    return fallback(g1, g2, lang), "fixe"
