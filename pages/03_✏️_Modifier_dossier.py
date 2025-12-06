import streamlit as st
import pandas as pd
from backend.dropbox_utils import load_database, save_database

st.set_page_config(page_title="Modifier un dossier", page_icon="✏️", layout="wide")
st.title("✏️ Modifier un dossier")

# ---------------------------------------------------------
# 🔹 Chargement de la base
# ---------------------------------------------------------
db = load_database()
clients = db.get("clients", [])

if not clients:
    st.error("Aucun dossier trouvé dans la base Dropbox.")
    st.stop()

df = pd.DataFrame(clients)

DOSSIER_COL = "Dossier N"

# ---------------------------------------------------------
# 🔹 Helpers
# ---------------------------------------------------------
def to_float(x):
    """Convertit n’importe quoi en float sans erreur."""
    try:
        return float(x)
    except:
        return 0.0

def safe_date(value):
    """Convertit une date JSON -> datetime.date ou None."""
    try:
        v = pd.to_datetime(value, errors="coerce")
        if pd.isna(v):
            return None
        return v.date()
    except:
        return None

# ---------------------------------------------------------
# 🔹 Normalisation des numéros de dossiers
# ---------------------------------------------------------
df[DOSSIER_COL] = pd.to_numeric(df[DOSSIER_COL], errors="coerce").astype("Int64")
liste_dossiers = df[DOSSIER_COL].dropna().astype(int).sort_values().tolist()

if not liste_dossiers:
    st.error("Aucun numéro de dossier valide trouvé.")
    st.stop()

# ---------------------------------------------------------
# 🔹 Sélection du dossier
# ---------------------------------------------------------
selected_num = st.selectbox("Sélectionner un dossier :", liste_dossiers)

dossier = df[df[DOSSIER_COL] == selected_num]
if dossier.empty:
    st.error("Erreur : dossier introuvable.")
    st.stop()

dossier = dossier.iloc[0].copy()

# ---------------------------------------------------------
# 🔹 Affichage du formulaire
# ---------------------------------------------------------
st.subheader(f"Dossier n° {selected_num}")

col1, col2, col3 = st.columns(3)

with col1:
    nom = st.text_input("Nom", value=dossier.get("Nom", ""))

with col2:
    date_dossier = st.date_input("Date", value=safe_date(dossier.get("Date")))

with col3:
    categories = st.text_input("Catégories", value=dossier.get("Categories", ""))

col4, col5 = st.columns(2)

with col4:
    sous_categories = st.text_input("Sous-catégories", value=dossier.get("Sous-categories", ""))

with col5:
    visa = st.text_input("Visa", value=dossier.get("Visa", ""))

col6, col7, col8 = st.columns(3)

with col6:
    honoraires = st.number_input("Montant honoraires (US $)", value=to_float(dossier.get("Montant honoraires (US $)", 0)))

with col7:
    frais = st.number_input("Autres frais (US $)", value=to_float(dossier.get("Autres frais (US $)", 0)))

with col8:
    facture = honoraires + frais
    st.number_input("Total facturé", value=facture, disabled=True)

# ---------------------------------------------------------
# 🔹 Acomptes
# ---------------------------------------------------------
st.subheader("Acomptes")

colA1, colA2, colA3, colA4 = st.columns(4)

ac1 = colA1.number_input("Acompte 1", value=to_float(dossier.get("Acompte 1")))
ac2 = colA2.number_input("Acompte 2", value=to_float(dossier.get("Acompte 2")))
ac3 = colA3.number_input("Acompte 3", value=to_float(dossier.get("Acompte 3")))
ac4 = colA4.number_input("Acompte 4", value=to_float(dossier.get("Acompte 4")))

colD1, colD2, colD3, colD4 = st.columns(4)

da1 = colD1.date_input("Date Acompte 1", value=safe_date(dossier.get("Date Acompte 1")))
da2 = colD2.date_input("Date Acompte 2", value=safe_date(dossier.get("Date Acompte 2")))
da3 = colD3.date_input("Date Acompte 3", value=safe_date(dossier.get("Date Acompte 3")))
da4 = colD4.date_input("Date Acompte 4", value=safe_date(dossier.get("Date Acompte 4")))

# ---------------------------------------------------------
# 🔹 Statuts
# ---------------------------------------------------------
st.subheader("Statuts du dossier")

colS1, colS2, colS3, colS4, colS5 = st.columns(5)

envoye = colS1.checkbox("Dossier envoyé", bool(dossier.get("Dossier envoye", False)))
accepte = colS2.checkbox("Dossier accepté", bool(dossier.get("Dossier accepte", False)))
refuse = colS3.checkbox("Dossier refusé", bool(dossier.get("Dossier refuse", False)))
annule = colS4.checkbox("Dossier annulé", bool(dossier.get("Dossier Annule", False)))
rfe = colS5.checkbox("RFE", bool(dossier.get("RFE", False)))

colT1, colT2, colT3, colT4, colT5 = st.columns(5)

date_envoye = colT1.date_input("Date envoi", value=safe_date(dossier.get("Date envoi")))
date_accepte = colT2.date_input("Date acceptation", value=safe_date(dossier.get("Date acceptation")))
date_refuse = colT3.date_input("Date refus", value=safe_date(dossier.get("Date refus")))
date_annule = colT4.date_input("Date annulation", value=safe_date(dossier.get("Date annulation")))
date_rfe = colT5.date_input("Date RFE", value=safe_date(dossier.get("Date reclamation")))

# ---------------------------------------------------------
# 🔹 Sauvegarde
# ---------------------------------------------------------
if st.button("💾 Enregistrer"):
    idx = df[df[DOSSIER_COL] == selected_num].index[0]

    df.loc[idx, :] = {
        DOSSIER_COL: selected_num,
        "Nom": nom,
        "Date": date_dossier,
        "Categories": categories,
        "Sous-categories": sous_categories,
        "Visa": visa,
        "Montant honoraires (US $)": honoraires,
        "Autres frais (US $)": frais,
        "Acompte 1": ac1,
        "Acompte 2": ac2,
        "Acompte 3": ac3,
        "Acompte 4": ac4,
        "Date Acompte 1": da1,
        "Date Acompte 2": da2,
        "Date Acompte 3": da3,
        "Date Acompte 4": da4,
        "Dossier envoye": envoye,
        "Date envoi": date_envoye,
        "Dossier accepte": accepte,
        "Date acceptation": date_accepte,
        "Dossier refuse": refuse,
        "Date refus": date_refuse,
        "Dossier Annule": annule,
        "Date annulation": date_annule,
        "RFE": rfe,
        "Date reclamation": date_rfe,
    }

    db["clients"] = df.to_dict(orient="records")
    save_database(db)
    st.success("Dossier mis à jour ✔")
    st.experimental_rerun()

# ---------------------------------------------------------
# 🔥 SUPPRESSION
# ---------------------------------------------------------
st.markdown("---")
st.subheader("🗑️ Supprimer ce dossier")

if st.button("❌ Supprimer définitivement ce dossier"):
    df = df[df[DOSSIER_COL] != selected_num]
    db["clients"] = df.to_dict(orient="records")
    save_database(db)
    st.success(f"Dossier {selected_num} supprimé ✔")
    st.experimental_rerun()
