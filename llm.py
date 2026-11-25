"""Appel au modèle d'IA : call_llm(system, user) -> str (texte brut de la réponse).

ai_explain.explain() gère les erreurs : si cette fonction lève une exception ou si la
réponse est refusée par le garde-fou, l'application affiche le texte fixe.

Configuration (variables d'environnement ou secrets Streamlit) :
  ANTHROPIC_API_KEY   clé d'API (obligatoire pour activer l'IA)
  LLM_MODEL           modèle à utiliser (défaut : claude-haiku-5-5)
Cette version utilise l'API Anthropic. Pour un autre fournisseur, ne changez que le corps de call_llm.
"""
import os

import requests

API_URL = "https://api.anthropic.com/v1/messages"
DEFAULT_MODEL = "claude-haiku-5-5"


def _setting(name, default=""):
    value = os.environ.get(name)
    if value:
        return value
    try:  # secrets Streamlit (.streamlit/secrets.toml), si disponibles
        import streamlit as st
        return str(st.secrets.get(name, default))
    except Exception:
        return default


def call_llm(system, user):
    key = _setting("ANTHROPIC_API_KEY")
    if not key:
        raise RuntimeError("ANTHROPIC_API_KEY manquante : l'IA est désactivée.")
    response = requests.post(
        API_URL,
        headers={"x-api-key": key, "anthropic-version": "2023-06-01", "content-type": "application/json"},
        json={"model": _setting("LLM_MODEL", DEFAULT_MODEL), "max_tokens": 700, "temperature": 0.2,
              "system": system, "messages": [{"role": "user", "content": user}]},
        timeout=30,
    )
    response.raise_for_status()
    return "".join(block.get("text", "") for block in response.json().get("content", []))
