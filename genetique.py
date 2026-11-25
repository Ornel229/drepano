"""Moteur de scénarios génétiques (logique pure, sans Streamlit).

Quatre variantes du gène de l'hémoglobine :
  A = normal, S = drépanocytaire, C = hémoglobine C, T = bêta-thalassémie (affichée « β »).
Chaque parent transmet l'une de ses deux lettres avec une probabilité de 1/2 :
les quatre cases du carré de Punnett sont donc équiprobables.
Les probabilités sont des Fraction (calculs exacts, pas d'arrondi flottant).
"""
from fractions import Fraction

GENOTYPES = ["AA", "AS", "AC", "AT", "SS", "SC", "ST", "CC", "CT", "TT"]
CATEGORIES = ["non_porteur", "porteur", "drepano", "autre"]

_ORDER = "ASCT"
_DREPANO = {"SS", "SC", "ST"}


def normalize(genotype):
    """Écrit un génotype dans l'ordre A, S, C, T (« SA » devient « AS »)."""
    return "".join(sorted(genotype, key=_ORDER.index))


def category_of(genotype):
    """Catégorie d'un génotype d'enfant ou de parent."""
    g = normalize(genotype)
    if g == "AA":
        return "non_porteur"
    if "A" in g:
        return "porteur"      # AS, AC, AT : porteur, sans la maladie
    if g in _DREPANO:
        return "drepano"      # SS, SC, ST : forme drépanocytaire
    return "autre"            # CC, CT, TT : à voir avec un spécialiste


def punnett_grid(g1, g2):
    """Carré de Punnett : une ligne par lettre de g1, une colonne par lettre de g2."""
    return [[normalize(a + b) for b in g2] for a in g1]


def category_probabilities(g1, g2):
    """Probabilité (Fraction) de chaque catégorie pour un enfant de ce couple."""
    probs = {c: Fraction(0) for c in CATEGORIES}
    for row in punnett_grid(g1, g2):
        for g in row:
            probs[category_of(g)] += Fraction(1, 4)
    return probs


def needs_counselling(g1, g2):
    """Vrai si un enfant avec une forme drépanocytaire ou une autre combinaison est possible."""
    probs = category_probabilities(g1, g2)
    return probs["drepano"] > 0 or probs["autre"] > 0
