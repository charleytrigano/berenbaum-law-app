import streamlit as st
import pandas as pd
from backend.dropbox_utils import load_database, save_database

st.set_page_config(page_title="Modifier un dossier", page_icon="✏️", layout="wide")
st.title("✏️ Modifier un dossier")

db = load_database()
clients = db.get("clients", [])

if not clients:
    st.error("Aucun dossier trouvé dans la base Dropbox.")
    st.stop()

df = pd.DataFrame(clients)
DOSSIER_COL = "Dossier N"

def to_float(x):
    try:
        return float(x)
    except:
        return 0.0

def safe_date(value):
    try:
        v = pd.to_datetime(value, errors="coerce")
        if pd.isna(v):
            return None
        return v.date()
    except:
        return None

df[DOSSIER_COL] = pd.to_numeric(df[DOSSIER_COL], errors="coerce").astype("Int64")
liste_dossiers = df[DOSSIER_COL].dropna().astype(int).sort_values().tolist()

selected_num = st.selectbox("Sélectionner un dossier :", liste_dossiers)
dossier = df[df[DOSSIER_COL] == selected_num].iloc[0].copy()

# ---------------------------------------------------------
# FORMULAIRE
# ---------------------------------------------------------
st.subheader(f"Dossier n° {selected_num}")

col1, col2, col3 = st.columns(3)
nom = col1.text_input("Nom", value=dossier.get("Nom", ""))
date_dossier = col2.date_input("Date", value=safe_date(dossier.get("Date")))
categories = col3.text_input("Catégories", value=dossier.get("Categories", ""))

col4, col5 = st.columns(2)
sous_categories = col4.text_input("Sous-catégories", value=dossier.get("Sous-categories", ""))
visa = col5.text_input("Visa", value=dossier.get("Visa", ""))

col6, col7, col8 = st.columns(3)
honoraires = col6.number_input("Montant honoraires (US $)", value=to_float(dossier.get("Montant honoraires (US $)", 0)))
frais = col7.number_input("Autres frais (US $)", value=to_float(dossier.get("Autres frais (US $)", 0)))
col8.number_input("Total facturé", value=honoraires + frais, disabled=True)

# Acomptes
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

# Escrow
dossier["Escrow"] = st.checkbox("Escrow ?", value=bool(dossier.get("Escrow", False)))

# ---------------------------------------------------------
# SAUVEGARDE
# ---------------------------------------------------------
if st.button("💾 Enregistrer"):

    idx = df[df[DOSSIER_COL] == selected_num].index[0]

    if "Escrow" not in df.columns:
        df["Escrow"] = False

    df.loc[idx, "Nom"] = nom
    df.loc[idx, "Date"] = date_dossier
    df.loc[idx, "Categories"] = categories
    df.loc[idx, "Sous-categories"] = sous_categories
    df.loc[idx, "Visa"] = visa
    df.loc[idx, "Montant honoraires (US $)"] = honoraires
    df.loc[idx, "Autres frais (US $)"] = frais
    df.loc[idx, "Acompte 1"] = ac1
    df.loc[idx, "Acompte 2"] = ac2
    df.loc[idx, "Acompte 3"] = ac3
    df.loc[idx, "Acompte 4"] = ac4
    df.loc[idx, "Date Acompte 1"] = da1
    df.loc[idx, "Date Acompte 2"] = da2
    df.loc[idx, "Date Acompte 3"] = da3
    df.loc[idx, "Date Acompte 4"] = da4

    df.loc[idx, "Escrow"] = bool(dossier["Escrow"])

    db["clients"] = df.to_dict(orient="records")
    save_database(db)

    st.success("Dossier mis à jour ✔")
    st.rerun()
