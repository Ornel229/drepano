"""Calendrier de reproduction : risque cumulé sur plusieurs grossesses (logique pure, sans Streamlit)."""
from genetique import category_probabilities


def serie_risque(g1, g2, n_max=5):
    """Liste de n_max Fractions : probabilité d'avoir AU MOINS un enfant avec une forme
    drépanocytaire sur 1, 2, ..., n_max grossesses. Chaque grossesse est indépendante."""
    p = category_probabilities(g1, g2)["drepano"]
    return [1 - (1 - p) ** n for n in range(1, n_max + 1)]
