"""Assistant de lecture des résultats de porteur (drépanocytose) - prototype Hack2Skill.

Lancer :  streamlit run app.py
Aucune donnée n'est enregistrée sur disque : tout vit dans la session du navigateur.

Organisation :
  genetique.py   moteur de scénarios (probabilités)       -> logique
  calendrier.py  risque cumulé sur plusieurs grossesses   -> logique
  arbre.py       arbre généalogique (schéma Graphviz)     -> logique
  fiche.py       fiche à apporter à la consultation       -> logique
  ai_explain.py  explication par IA + garde-fou           -> logique
  llm.py         appel au modèle d'IA                     -> logique
  textes.py / textes_ext.py  tous les textes affichés     -> textes
  app.py         interface Streamlit (ce fichier)         -> interface
"""
import csv
import io
import json
from datetime import datetime

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

import ai_explain
from ai_explain import explain
from arbre import PARENT_KEYS, build_dot, unknown_members
from calendrier import serie_risque
from fiche import build_fiche
from genetique import (CATEGORIES, GENOTYPES, category_of, category_probabilities,
                       needs_counselling, punnett_grid)
from textes import QUIZ, TEXTS
from textes_ext import TX

try:
    from llm import call_llm
except ImportError:  # si llm.py est absent : explain() utilisera le texte fixe
    def call_llm(system, user):
        raise RuntimeError("llm.py introuvable")

st.set_page_config(page_title="Résultats de porteur", page_icon="🧬", layout="centered")

OPTIONS = ["?"] + GENOTYPES
COLORS = {"non_porteur": "#d9f2d9", "porteur": "#fff3c4", "drepano": "#ffd9b3", "autre": "#e3dcf5"}
ICON_COLORS = {"non_porteur": "#7bc67b", "porteur": "#f2c94c", "drepano": "#f2994a", "autre": "#9b8bd4"}

STYLE = """
<style>
.block-container {max-width: 820px; padding-top: 2rem;}
div[data-testid="stMetric"] {background: rgba(128,128,128,0.10); padding: 12px 16px; border-radius: 14px;}
button[kind="secondary"] {border-radius: 10px;}
.stTabs [data-baseweb="tab-list"] {gap: 6px; flex-wrap: wrap;}
.stTabs [data-baseweb="tab"] {border-radius: 10px 10px 0 0; padding: 8px 12px;}
</style>
"""


# ---------- état de session ----------
def init_state():
    defaults = {"shares": [], "audit": [], "events": [], "steps": {}, "quiz_score": None}
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def now():
    return datetime.now().strftime("%d/%m/%Y %H:%M")


def log(event, detail=""):
    """Événement anonyme (jamais de nom ni de résultat)."""
    st.session_state.events.append(
        {"ts": now(), "event": event, "lang": st.session_state.get("lang", "fr"), "detail": detail}
    )


def on_step(i):
    done = st.session_state[f"step_{i}"]
    st.session_state.steps[i] = now() if done else None
    log("step", f"{i}:{'done' if done else 'undone'}")


def disp(genotype):
    return genotype.replace("T", "β")


# ---------- composants ----------
def speak_button(text, label, lang):
    code = {"fr": "fr-FR", "en": "en-US"}[lang]
    html = f"""
    <button id="b" style="padding:8px 14px;border-radius:8px;border:1px solid #888;background:#f4f4f4;font-size:15px;cursor:pointer">🔊 {label}</button>
    <script>
      document.getElementById("b").onclick = function() {{
        var u = new SpeechSynthesisUtterance({json.dumps(text, ensure_ascii=False)});
        u.lang = "{code}";
        window.speechSynthesis.cancel();
        window.speechSynthesis.speak(u);
      }};
    </script>"""
    components.html(html, height=52)


def punnett_html(g1, g2, t):
    grid = punnett_grid(g1, g2)
    rows = ["<table style='border-collapse:collapse;width:100%;text-align:center;color:#111'>"]
    rows.append("<tr><th></th>" + "".join(f"<th style='padding:6px'>{disp(b)}</th>" for b in g2) + "</tr>")
    for a, line in zip(g1, grid):
        cells = ""
        for g in line:
            cat = category_of(g)
            cells += (
                f"<td style='background:{COLORS[cat]};border:3px solid #fff;padding:10px;border-radius:10px'>"
                f"<b>{disp(g)}</b><br><span style='font-size:0.8em'>{t['cat_short'][cat]}</span></td>"
            )
        rows.append(f"<tr><th style='padding:6px'>{disp(a)}</th>{cells}</tr>")
    rows.append("</table>")
    return "".join(rows)


def icons_html(probs, n=20):
    """20 pastilles colorées : une illustration simple d'une probabilité."""
    squares = []
    for cat in CATEGORIES:
        squares += [cat] * int(round(float(probs[cat]) * n))
    dots = "".join(
        f"<div style='width:30px;height:30px;border-radius:9px;background:{ICON_COLORS[c]}'></div>"
        for c in squares)
    return f"<div style='display:flex;flex-wrap:wrap;gap:6px;max-width:420px;margin:6px 0'>{dots}</div>"


def events_csv():
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=["ts", "event", "lang", "detail"])
    writer.writeheader()
    writer.writerows(st.session_state.events)
    return buf.getvalue()


# ---------- application ----------
init_state()
st.markdown(STYLE, unsafe_allow_html=True)

lang = st.radio("Langue / Language", ["fr", "en"], horizontal=True, key="lang",
                format_func=lambda k: TEXTS[k]["lang_name"])
t = TEXTS[lang]
x = TX[lang]

# Barre latérale : confidentialité, effacement, mode développeur
st.sidebar.markdown(f"**{x['privacy_title']}**\n\n{x['privacy_body']}")
if st.sidebar.button(x["erase"]):
    st.session_state.clear()
    st.rerun()
debug = st.sidebar.checkbox(x["dev_mode"], value=False)

st.caption(x["banner"])

g1 = st.session_state.get("sel1", "?")
g2 = st.session_state.get("sel2", "?")
both_known = g1 != "?" and g2 != "?"
parents = {k: st.session_state.get(f"par_{k}", "?") for k in PARENT_KEYS}
cached_ai = st.session_state.get("ai_result")
ai_now = cached_ai[0][0] if cached_ai and cached_ai[1] == (g1, g2, lang) else None

# Progression du parcours
progress_flags = [both_known, ai_now is not None, st.session_state.quiz_score is not None,
                  any(st.session_state.steps.values())]
st.progress(sum(progress_flags) / len(progress_flags), text=x["progress"])

tl = t["tabs"]
tab_home, tab_res, tab_exp, tab_fam, tab_cal, tab_share, tab_next = st.tabs(
    [tl[0], tl[1], tl[2], x["tab_family"], x["tab_calendar"], tl[3], tl[4]])

# 1. Accueil
with tab_home:
    st.title(t["title"])
    st.caption(t["subtitle"])
    st.info(t["disclaimer"])
    st.markdown(t["welcome_body"])

# 2. Résultats
with tab_res:
    st.header(t["res_title"])
    st.caption(t["res_help"])
    col_a, col_b = st.columns(2)
    with col_a:
        st.selectbox(t["partner_a"], OPTIONS, key="sel1", format_func=lambda g: t["geno"][g])
    with col_b:
        st.selectbox(t["partner_b"], OPTIONS, key="sel2", format_func=lambda g: t["geno"][g])

# 3. Explication
with tab_exp:
    st.header(t["exp_title"])
    for label, g in ((t["partner_a"], g1), (t["partner_b"], g2)):
        if g != "?":
            st.info(f"**{label}** : {t['status'][g]}")
    if not both_known:
        st.warning(t["exp_unknown"])
    else:
        probs = category_probabilities(g1, g2)
        st.subheader(t["punnett_title"])
        st.caption(t["punnett_caption"])
        st.markdown(punnett_html(g1, g2, t), unsafe_allow_html=True)

        lines = [t["each_pregnancy"]]
        for cat in CATEGORIES:
            if probs[cat] > 0:
                lines.append(f"{t['cat'][cat]} : {int(probs[cat] * 100)} %")
        st.markdown("**" + lines[0] + "**\n\n" + "\n".join(f"- {line}" for line in lines[1:]))

        # Pastilles : 20 grossesses
        st.markdown(f"**{x['cards_title']}**")
        st.markdown(icons_html(probs), unsafe_allow_html=True)
        legend = " &nbsp; ".join(
            f"<span style='color:{ICON_COLORS[c]}'>■</span> {t['cat'][c]} ({int(probs[c] * 100)} %)"
            for c in CATEGORIES if probs[c] > 0)
        st.markdown(legend, unsafe_allow_html=True)
        st.caption(x["cards_note"])

        st.subheader(t["key_title"])
        for message in t["key_messages"]:
            st.markdown(f"- {message}")
        st.caption(t["uncertainty"])

        speech = " ".join(lines) + ". " + " ".join(t["key_messages"][:3]) + " " + t["uncertainty"]
        speak_button(speech, t["listen"], lang)

        # --- Explication par l'IA ---
        st.divider()
        st.subheader(x["ai_title"])
        consent_ai = st.checkbox(x["ai_consent"], key="consent_ai")
        niveau = st.selectbox(x["ai_level"], x["ai_levels"], key="niveau_ai")
        if consent_ai and st.button(x["ai_button"]):
            with st.spinner("..."):
                st.session_state.ai_result = (explain(g1, g2, lang, niveau, call_llm), (g1, g2, lang))
            log("ai_explain", st.session_state.ai_result[0][1])
            st.rerun()
        cached = st.session_state.get("ai_result")
        if cached and cached[1] == (g1, g2, lang):
            res, source = cached[0]
            st.write(res["explication"])
            for p in res["points_cles"]:
                st.markdown(f"- {p}")
            st.markdown(f"**{x['ai_questions']}**")
            for q_ in res["questions_medecin"]:
                st.markdown(f"- {q_}")
            st.caption(x["ai_ok"] if source == "ia" else x["ai_fixed"])
            err = getattr(ai_explain, "LAST_ERROR", "")
            if debug and source != "ia" and err:
                st.caption(x["dev_detail"] + err)

        # --- Quiz ---
        st.divider()
        st.subheader(t["quiz_title"])
        questions = QUIZ[lang]
        answers = []
        for i, q in enumerate(questions):
            answers.append(st.radio(q["q"], q["options"], index=None, key=f"quiz_{lang}_{i}"))
        if st.button(t["quiz_check"]):
            if any(a is None for a in answers):
                st.warning(t["quiz_answer_all"])
            else:
                score = sum(1 for a, q in zip(answers, questions) if q["options"].index(a) == q["answer"])
                st.session_state.quiz_score = score
                log("quiz", f"{score}/3")
                st.success(t["quiz_result"].format(score=score))

# 4. Famille : arbre généalogique
with tab_fam:
    st.header(x["family_title"])
    st.caption(x["family_intro"])
    if not both_known:
        st.info(x["family_need"])
    else:
        keys = [("a_m", x["a_mother"]), ("a_p", x["a_father"]), ("b_m", x["b_mother"]), ("b_p", x["b_father"])]
        c1, c2 = st.columns(2)
        for i, (k, label) in enumerate(keys):
            with (c1 if i < 2 else c2):
                st.selectbox(label, OPTIONS, key=f"par_{k}", format_func=lambda g: t["geno"][g])
        parents = {k: st.session_state.get(f"par_{k}", "?") for k in PARENT_KEYS}
        st.graphviz_chart(build_dot(g1, g2, parents, lang), use_container_width=True)
        missing = unknown_members(parents, lang)
        if missing:
            st.warning(x["family_unknown"].format(who=", ".join(missing)))
        st.caption(x["family_note"])

# 5. Calendrier : risque au fil des grossesses + feuille de route
with tab_cal:
    st.header(x["calendar_title"])
    st.write(x["calendar_intro"])
    if not both_known:
        st.info(x["calendar_need"])
    else:
        serie = serie_risque(g1, g2, 5)
        pct = [float(v) * 100 for v in serie]
        if pct[0] == 0:
            st.success(x["calendar_none"])
        else:
            n = st.slider(x["calendar_slider"], 1, 5, 3, key="cal_n")
            st.metric(x["calendar_metric"], f"{pct[n - 1]:.0f} %")
            df = pd.DataFrame({x["calendar_axis"]: pct}, index=[str(i) for i in range(1, 6)])
            st.bar_chart(df, height=240)
        st.caption(x["calendar_indep"])

    st.subheader(x["timeline_title"])
    for i, (title, body) in enumerate(x["timeline"], 1):
        with st.container(border=True):
            st.markdown(f"**{i}. {title}**")
            st.write(body)

# 6. Partage
with tab_share:
    st.header(t["share_title"])
    st.write(t["share_intro"])
    with st.form("share_form", clear_on_submit=True):
        name = st.text_input(t["share_name"], help=t["share_name_help"])
        role = st.selectbox(t["share_role"], list(t["roles"]), format_func=lambda k: t["roles"][k])
        scope = st.multiselect(t["share_scope"], list(t["scopes"]), format_func=lambda k: t["scopes"][k])
        consent = st.checkbox(t["share_consent"])
        submitted = st.form_submit_button(t["share_add"])
    if submitted:
        if not (name.strip() and scope and consent):
            st.error(t["share_missing"])
        else:
            scope_txt = ", ".join(t["scopes"][s] for s in scope)
            st.session_state.shares.append(
                {"who": name.strip(), "role": role, "scope": scope_txt, "active": True})
            st.session_state.audit.append(
                {"ts": now(), "action": "granted", "who": name.strip(), "role": role, "scope": scope_txt})
            log("share_granted", role)
            st.rerun()

    st.subheader(t["share_active"])
    active = [(i, s) for i, s in enumerate(st.session_state.shares) if s["active"]]
    if not active:
        st.caption(t["share_none"])
    for i, s in active:
        c1, c2 = st.columns([3, 2])
        c1.markdown(f"**{s['who']}** ({t['roles'][s['role']]})  \n{s['scope']}")
        if c2.button(t["share_revoke"], key=f"revoke_{i}"):
            s["active"] = False
            st.session_state.audit.append(
                {"ts": now(), "action": "revoked", "who": s["who"], "role": s["role"], "scope": s["scope"]})
            log("share_revoked", s["role"])
            st.rerun()

    if st.session_state.audit:
        st.subheader(t["audit_title"])
        cols = t["audit_cols"]
        rows = [
            {cols["ts"]: a["ts"], cols["action"]: t["audit_actions"][a["action"]], cols["who"]: a["who"],
             cols["role"]: t["roles"][a["role"]], cols["scope"]: a["scope"]}
            for a in st.session_state.audit
        ]
        st.dataframe(rows, use_container_width=True, hide_index=True)

# 7. Suite
with tab_next:
    st.header(t["next_title"])
    if not both_known:
        st.info(t["counsel_wait"])
        counselling = False
    else:
        counselling = needs_counselling(g1, g2)
        (st.warning if counselling else st.success)(t["counsel_yes"] if counselling else t["counsel_no"])

    # --- Voie de référence vers un spécialiste ---
    st.subheader(x["refer_title"])
    st.info(x["refer_body"])
    with st.expander(x["refer_questions_title"]):
        for q_ in x["refer_questions"]:
            st.markdown(f"- {q_}")
    st.caption(x["refer_directory"])

    # --- Fiche à apporter à la consultation ---
    st.subheader(x["fiche_title"])
    st.write(x["fiche_intro"])
    if both_known:
        st.download_button(x["fiche_button"], build_fiche(lang, g1, g2, parents, ai_now, now()),
                           file_name="fiche_consultation.txt", mime="text/plain")
    else:
        st.caption(x["fiche_need"])
    st.divider()

    for i, label in enumerate(t["steps"]):
        if i == 0:
            st.markdown(("✅ " if both_known else "⬜ ") + label)
        elif i == 2:
            st.markdown(("✅ " if counselling else "⬜ ") + label)
        else:
            st.checkbox(label, key=f"step_{i}", on_change=on_step, args=(i,))
            ts = st.session_state.steps.get(i)
            if ts:
                st.caption(t["step_done_on"].format(ts=ts))

    st.divider()
    st.subheader(t["indicators_title"])
    steps_done = sum(1 for v in st.session_state.steps.values() if v) + int(both_known) + int(counselling)
    shares_active = sum(1 for s in st.session_state.shares if s["active"])
    quiz = st.session_state.quiz_score
    m1, m2, m3 = st.columns(3)
    m1.metric(t["ind_quiz"], f"{quiz}/3" if quiz is not None else "-")
    m2.metric(t["ind_steps"], f"{steps_done}/{len(t['steps'])}")
    m3.metric(t["ind_shares"], shares_active)
    st.download_button(t["ind_export"], events_csv(), file_name="indicateurs_anonymes.csv", mime="text/csv")
    st.caption(t["ind_note"])
