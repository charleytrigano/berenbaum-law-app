import streamlit as st
import pandas as pd

from utils.sidebar import render_sidebar
from backend.dropbox_utils import load_database, save_database


# =========================================================
# CONFIG
# =========================================================
st.set_page_config(page_title="➕ Nouveau dossier", page_icon="➕", layout="wide")
render_sidebar()
st.title("➕ Créer un dossier")


# =========================================================
# LOAD DB
# =========================================================
db = load_database()
clients = pd.DataFrame(db.get("clients", []))

if clients.empty:
    clients = pd.DataFrame(columns=["Dossier N"])


# =========================================================
# HELPERS
# =========================================================
def normalize_dossier_n(v):
    return str(v).strip()


def extract_parent(dossier_n: str) -> str:
    if "-" in dossier_n:
        return dossier_n.split("-", 1)[0]
    return dossier_n


def next_sub_dossier(parent_id: str, df: pd.DataFrame) -> str:
    """
    Calcule automatiquement le prochain xxxxx-n
    """
    parent_id = str(parent_id)

    suffixes = []
    for v in df["Dossier N"].dropna():
        s = str(v)
        if s.startswith(parent_id + "-"):
            try:
                suffixes.append(int(s.split("-", 1)[1]))
            except Exception:
                pass

    next_idx = max(suffixes) + 1 if suffixes else 1
    return f"{parent_id}-{next_idx}"


# =========================================================
# FORMULAIRE
# =========================================================
st.subheader("📁 Type de dossier")

mode = st.radio(
    "Quel type de dossier veux-tu créer ?",
    ["🆕 Nouveau dossier principal", "📎 Sous-dossier d’un dossier existant"],
)

st.markdown("---")


# =========================================================
# DOSSIER PRINCIPAL
# =========================================================
if mode == "🆕 Nouveau dossier principal":

    dossier_n = st.text_input(
        "Dossier N (ex: 13001)",
        placeholder="Numéro principal sans suffixe",
    )

    if dossier_n:
        dossier_n = normalize_dossier_n(dossier_n)

        if dossier_n in clients["Dossier N"].astype(str).values:
            st.error("❌ Ce numéro de dossier existe déjà.")
        else:
            st.success(f"✔ Dossier principal prêt : {dossier_n}")


# =========================================================
# SOUS-DOSSIER
# =========================================================
else:
    clients["Dossier N"] = clients["Dossier N"].astype(str)
    clients["Dossier ID"] = clients["Dossier N"].apply(extract_parent)

    parents = sorted(clients["Dossier ID"].unique())

    parent = st.selectbox("Choisir le dossier parent", parents)

    if parent:
        next_id = next_sub_dossier(parent, clients)
        st.info(f"📎 Le sous-dossier sera créé automatiquement : **{next_id}**")
        dossier_n = next_id


# =========================================================
# INFOS DOSSIER
# =========================================================
st.markdown("---")
st.subheader("📝 Informations du dossier")

nom = st.text_input("Nom client")
date = st.date_input("Date")
categorie = st.text_input("Catégorie")
sous_categorie = st.text_input("Sous-catégorie")
visa = st.text_input("Visa")
honoraires = st.number_input("Montant honoraires (US $)", min_value=0.0)
frais = st.number_input("Autres frais (US $)", min_value=0.0)
commentaire = st.text_area("Commentaire")


# =========================================================
# CREATION
# =========================================================
if st.button("✅ Créer le dossier", type="primary"):

    if not dossier_n or not nom:
        st.error("❌ Dossier N et Nom sont obligatoires.")
        st.stop()

    new_row = {
        "Dossier N": dossier_n,
        "Nom": nom,
        "Date": str(date),
        "Categories": categorie,
        "Sous-categories": sous_categorie,
        "Visa": visa,
        "Montant honoraires (US $)": honoraires,
        "Autres frais (US $)": frais,
        "Acompte 1": 0.0,
        "Acompte 2": 0.0,
        "Acompte 3": 0.0,
        "Acompte 4": 0.0,
        "Escrow": False,
        "Escrow_a_reclamer": False,
        "Escrow_reclame": False,
        "Dossier envoye": False,
        "Dossier accepte": False,
        "Dossier refuse": False,
        "Dossier Annule": False,
        "RFE": False,
        "Commentaire": commentaire,
    }

    db["clients"].append(new_row)
    save_database(db)

    st.success(f"✔ Dossier **{dossier_n}** créé avec succès.")
    st.rerun()
