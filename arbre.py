"""Arbre généalogique : génère un schéma DOT (Graphviz) à partir des statuts saisis.

Logique pure (aucune dépendance à Streamlit). Les noms ne sont jamais utilisés :
seulement des rôles (« Mère du partenaire A ») et des statuts.
"""
from genetique import CATEGORIES, category_of, category_probabilities

FILL = {"non_porteur": "#d9f2d9", "porteur": "#fff3c4", "drepano": "#ffd9b3",
        "autre": "#e3dcf5", "inconnu": "#e6e6e6"}

SHORT = {
    "fr": {"non_porteur": "non porteur", "porteur": "porteur", "drepano": "forme drépanocytaire",
           "autre": "autre combinaison"},
    "en": {"non_porteur": "not a carrier", "porteur": "carrier", "drepano": "sickle cell form",
           "autre": "other combination"},
}

ROLES = {
    "fr": {"a_m": "Mère du partenaire A", "a_p": "Père du partenaire A",
           "b_m": "Mère du partenaire B", "b_p": "Père du partenaire B"},
    "en": {"a_m": "Mother of partner A", "a_p": "Father of partner A",
           "b_m": "Mother of partner B", "b_p": "Father of partner B"},
}

TXT = {
    "fr": {"partner_a": "Partenaire A", "partner_b": "Partenaire B",
           "unknown": "statut inconnu\\n(test conseillé)", "child": "Enfant possible"},
    "en": {"partner_a": "Partner A", "partner_b": "Partner B",
           "unknown": "status unknown\\n(testing advised)", "child": "Possible child"},
}

PARENT_KEYS = ("a_m", "a_p", "b_m", "b_p")


def disp(genotype):
    return genotype.replace("T", "β")


def _fill(genotype):
    return FILL["inconnu"] if genotype == "?" else FILL[category_of(genotype)]


def _node(node_id, label, fill):
    return f'{node_id} [label="{label}", fillcolor="{fill}"];'


def unknown_members(parents, lang="fr"):
    """Rôles dont le statut est inconnu (pour proposer un test)."""
    roles = ROLES.get(lang, ROLES["fr"])
    return [roles[k] for k in PARENT_KEYS if parents.get(k, "?") == "?"]


def build_dot(g1, g2, parents, lang="fr"):
    lang = lang if lang in TXT else "fr"
    tx, short, roles = TXT[lang], SHORT[lang], ROLES[lang]
    lines = [
        "digraph G {",
        'rankdir=TB; bgcolor="transparent"; nodesep=0.35; ranksep=0.6;',
        'node [shape=box, style="rounded,filled", fontname="Helvetica", fontsize=11, '
        'fontcolor="#111111", color="#9aa0a6", margin="0.15,0.08"];',
        'edge [color="#9aa0a6"];',
    ]
    for key in PARENT_KEYS:
        g = parents.get(key, "?")
        label = f"{roles[key]}\\n" + (tx["unknown"] if g == "?" else f"{disp(g)}\\n{short[category_of(g)]}")
        lines.append(_node(f"P_{key}", label, _fill(g)))
    lines.append(_node("A", f"{tx['partner_a']}\\n{disp(g1)}\\n{short[category_of(g1)]}", _fill(g1)))
    lines.append(_node("B", f"{tx['partner_b']}\\n{disp(g2)}\\n{short[category_of(g2)]}", _fill(g2)))
    lines += ["P_a_m -> A;", "P_a_p -> A;", "P_b_m -> B;", "P_b_p -> B;",
              "{rank=same; A; B;}",
              'U [shape=point, width=0.08, label=""];',
              "A -> U [dir=none];", "B -> U [dir=none];"]
    probs = category_probabilities(g1, g2)
    for cat in CATEGORIES:
        if probs[cat] > 0:
            pct = int(probs[cat] * 100)
            lines.append(_node(f"C_{cat}", f"{tx['child']}\\n{short[cat]}\\n{pct} %", FILL[cat]))
            lines.append(f"U -> C_{cat};")
    lines.append("}")
    return "\n".join(lines)
