import streamlit as st
import os
import json
from backend.dropbox_utils import load_database

st.set_page_config(page_title="🔍 Diagnostic Secrets", page_icon="🕵️", layout="wide")

st.title("🕵️ Diagnostic complet — Secrets, Chemins & JSON utilisés")


# -----------------------------------------------------------
# 1️⃣ Localisation réelle du fichier secrets.toml
# -----------------------------------------------------------
st.header("📌 Emplacement réel du fichier secrets.toml chargé")
try:
    secrets_path = st.secrets._file_path
    st.code(secrets_path)
except:
    st.error("Impossible de récupérer l’emplacement de secrets.toml (mais il a été chargé).")


# -----------------------------------------------------------
# 2️⃣ Contenu exact de st.secrets
# -----------------------------------------------------------
st.header("📦 Contenu exact de st.secrets (ce que Streamlit utilise VRAIMENT)")
st.json(dict(st.secrets))


# -----------------------------------------------------------
# 3️⃣ Extraction du chemin JSON utilisé par l’app
# -----------------------------------------------------------
st.header("📁 Chemin JSON interprété par l’application")

if "paths" in st.secrets:
    paths = st.secrets["paths"]

    # Cas 1 : paths est un dict (correct)
    if isinstance(paths, dict):
        json_path = paths.get("DROPBOX_JSON", "❌ NON TROUVÉ")
        st.success(f"JSON utilisé (dict OK) : {json_path}")

    # Cas 2 : paths est une chaîne → MAUVAIS format
    elif isinstance(paths, str):
        st.error("❌ PROBLÈME : la section [paths] est chargée comme une CHAÎNE, pas un dictionnaire !")
        st.warning("Cela signifie que ton secrets.toml est MAL FORMATÉ. Streamlit ne peut pas lire les chemins.")
        st.code(paths)

        # Tentative de réparer la chaîne
        try:
            repaired = eval(paths)
            st.success("🔧 Conversion automatique réussie :")
            st.json(repaired)
        except:
            st.error("❌ Impossible de convertir la chaîne en dictionnaire.")

else:
    st.error("❌ Aucun bloc [paths] trouvé dans st.secrets.")


# -----------------------------------------------------------
# 4️⃣ Test : lecture réelle du JSON depuis Dropbox
# -----------------------------------------------------------
st.header("🧪 Test de lecture réelle du JSON Dropbox")

try:
    db = load_database()
    st.success("Lecture JSON Dropbox OK ✔️")
    st.json(db)
except Exception as e:
    st.error("❌ Erreur lors du chargement de la base JSON :")
    st.exception(e)
