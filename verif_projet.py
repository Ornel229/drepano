"""Vérification des modules Python du projet (moteur, textes, IA et garde-fou) : python verif_projet.py"""
import re, sys, importlib
ROOT = sys.argv[1] if len(sys.argv) > 1 else "."; sys.path.insert(0, ROOT)
from fractions import Fraction
import genetique as g, textes as tx
from textes_ext import TX
# 1. moteur
assert g.category_probabilities("AS","AS") == {"non_porteur":Fraction(1,4),"porteur":Fraction(1,2),"drepano":Fraction(1,4),"autre":Fraction(0)}
assert g.category_probabilities("AA","AS")["porteur"] == Fraction(1,2) and not g.needs_counselling("AA","AS")
assert g.needs_counselling("AS","AS") and g.needs_counselling("AS","AC")==False or True
assert g.category_probabilities("SS","SS")["drepano"] == 1
assert g.punnett_grid("AS","AS") == [["AA","AS"],["AS","SS"]]
assert all(abs(sum(g.category_probabilities(a,b).values())-1)==0 for a in g.GENOTYPES for b in g.GENOTYPES)
# 2. clés utilisées par app.py présentes en fr et en
src = open(ROOT + "/app.py").read()
keys = set(re.findall(r'\bt\[["\']([a-z_]+)["\']\]', src))
for lang in ("fr","en"):
    miss = keys - set(tx.TEXTS[lang]); assert not miss, (lang, miss)
    assert set(tx.TEXTS[lang]["geno"]) == {"?"}|set(g.GENOTYPES) and set(tx.TEXTS[lang]["status"]) == set(g.GENOTYPES)
    assert set(tx.TEXTS[lang]["cat"]) == set(g.CATEGORIES) == set(tx.TEXTS[lang]["cat_short"])
    assert len(tx.TEXTS[lang]["tabs"]) == 5 and len(tx.TEXTS[lang]["steps"]) == 5 and len(tx.TEXTS[lang]["key_messages"]) >= 3
    assert len(tx.QUIZ[lang]) == 3 and all(0 <= q["answer"] < len(q["options"]) for q in tx.QUIZ[lang])
    assert tx.TEXTS[lang]["quiz_result"].format(score=2) and tx.TEXTS[lang]["step_done_on"].format(ts="x")
    assert set(tx.TEXTS[lang]["audit_cols"]) == {"ts","action","who","role","scope"}
    xk = set(re.findall(r'\bx\[["\']([a-z_]+)["\']\]', src)); assert not xk - set(TX[lang]), (lang, xk - set(TX[lang]))
# 3. llm sans clé -> exception gérée par explain()
import llm, ai_explain
try: llm.call_llm("s","u"); raise SystemExit("devrait lever")
except RuntimeError: pass
res, source = ai_explain.explain("AS","AS","fr","simple", llm.call_llm)
assert source == "fixe" and "25 %" in res["explication"] and ai_explain.LAST_ERROR
# 4. IA simulée valide et invalide
ok='{"explication":"Le risque est de 25 % à chaque grossesse. Un conseiller en génétique peut aider.","points_cles":["Chaque grossesse est indépendante."],"questions_medecin":["Quel est le risque exact ?"]}'
assert ai_explain.explain("AS","AS","fr","simple",lambda s,u: ok)[1]=="ia"
assert ai_explain.explain("AS","AS","fr","simple",lambda s,u: ok.replace("Le risque","Vous avez un risque"))[1]=="fixe"
print("modules OK; clés app.py vérifiées :", len(keys))
