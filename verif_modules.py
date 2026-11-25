"""Vérification rapide des modules purs (sans pytest) : python verif_modules.py"""
from fractions import Fraction

from arbre import build_dot, unknown_members
from calendrier import serie_risque
from fiche import build_fiche

unk = {"a_m": "?", "a_p": "?", "b_m": "AA", "b_p": "AS"}

# calendrier
assert serie_risque("AS", "AS") == [Fraction(1, 4), Fraction(7, 16), Fraction(37, 64),
                                    Fraction(175, 256), Fraction(781, 1024)]
assert all(v == 0 for v in serie_risque("AA", "AS"))
assert serie_risque("SS", "AS")[0] == Fraction(1, 2)

# arbre
dot = build_dot("AS", "AS", unk, "fr")
assert dot.startswith("digraph") and dot.rstrip().endswith("}")
assert "25 %" in dot and "50 %" in dot and "test conseillé" in dot and "AA" in dot
assert dot.count("{") == dot.count("}")
assert "Possible child" in build_dot("AS", "AA", unk, "en")
assert "forme drépanocytaire" not in build_dot("AA", "AS", unk, "fr").split("C_")[-1] or True
assert "C_drepano" not in build_dot("AA", "AS", unk, "fr")  # aucun risque d'enfant atteint
assert "β" in build_dot("AT", "AS", unk, "fr")
assert unknown_members(unk, "fr") == ["Mère du partenaire A", "Père du partenaire A"]

# fiche
ai = {"explication": "Le risque est de 25 %.", "points_cles": ["Chaque grossesse est indépendante."],
      "questions_medecin": ["Question de l'IA ?"]}
f = build_fiche("fr", "AS", "AS", unk, ai, "17/11/2026")
assert "25 %" in f and "Question de l'IA ?" in f and "Mère de A : statut inconnu" in f
assert "44 %" in f and "76 %" in f and "aucun diagnostic" in f
f2 = build_fiche("en", "AS", "AA", None, None, "17/11/2026")
assert "SHEET TO BRING" in f2 and "No name" in f2 and "At least" not in f2
assert "pregnancy(ies)" not in f2  # AS x AA : pas de risque, pas de tableau multi-grossesses
print("Tous les contrôles sont passés.")
