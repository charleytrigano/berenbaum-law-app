import streamlit as st
import pandas as pd
from backend.dropbox_utils import load_database, save_database

st.set_page_config(page_title="Modifier un dossier", page_icon="✏️", layout="wide")
st.title("✏️ Modifier un dossier")

# ---------------------------------------------------------
# 🔹 Chargement base
# ---------------------------------------------------------
db = load_database()
clients = db.get("clients", [])

if not clients:
    st.error("Aucun dossier trouvé.")
   
df = pd.DataFrame(clients)
DOSSIER_COL = "Dossier N"
    stop()
# ---------------------------------------------------------
# 🔹 Utils
# ---------------------------------------------------------
def to_float(x):
    try:
        return float(x)
    except:
        return 0.0

def safe_date(value):
    try:
        v = pd.to_datetime(value, errors="ignore")
        if pd.isna(v):
            return None
        return v.date()
    except:
        return None

def normalize_bool(x):
    if isinstance(x, bool):
        return x
    if str(x).lower() in ["1", "true", "yes", "oui"]:
        return True
    return False

# ---------------------------------------------------------
# 🔹 Sélection dossier
# ---------------------------------------------------------
df[DOSSIER_COL] = pd.to_numeric(df[DOSSIER_COL], errors="coerce").astype("Int64")
liste = df[DOSSIER_COL].dropna().astype(int).sort_values().tolist()
selected = st.selectbox("Sélectionner un dossier :", liste)

dossier = df[df[DOSSIER_COL] == selected].iloc[0].copy()

#----------------------------------------------------------
# 🔹 Normalisation Escrow
#----------------------------------------------------------
for col in ["Escrow", "Escrow_a_reclamer", "Escrow_reclame"]:
    if col not in dossier:
        dossier[col] = False

dossier["Escrow"] = normalize_bool(dossier.get("Escrow"))
dossier["Escrow_a_reclamer"] = normalize_bool(dossier.get("Escrow_a_reclamer"))
dossier["Escrow_reclame"] = normalize_bool(dossier.get("Escrow_reclame"))

# ---------------------------------------------------------
# FORMULAIRE
# ---------------------------------------------------------
st.subheader(f"Dossier n° {selected}")

col1, col2, col3 = st.columns(3)
nom = col1.text_input("Nom", dossier.get("Nom", ""))
date_dossier = col2.date_input("Date", safe_date(dossier.get("Date")))
categories = col3.text_input("Catégories", dossier.get("Categories", ""))

col4, col5 = st.columns(2)
sous_categories = col4.text_input("Sous-catégories", dossier.get("Sous-categories", ""))
visa = col5.text_input("Visa", dossier.get("Visa", ""))

col6, col7, col8 = st.columns(3)
honoraires = col6.number_input("Montant honoraires (US $)", value=to_float(dossier.get("Montant honoraires (US $)", 0)))
frais = col7.number_input("Autres frais (US $)", value=to_float(dossier.get("Autres frais (US $)", 0)))
col8.number_input("Total facturé", value=honoraires + frais, disabled=True)

# ---------------------------------------------------------
# Acomptes
# ---------------------------------------------------------
st.subheader("🏦 Acomptes")
colA1, colA2, colA3, colA4 = st.columns(4)
ac1 = colA1.number_input("Acompte 1", value=to_float(dossier.get("Acompte 1")))
ac2 = colA2.number_input("Acompte 2", value=to_float(dossier.get("Acompte 2")))
ac3 = colA3.number_input("Acompte 3", value=to_float(dossier.get("Acompte 3")))
ac4 = colA4.number_input("Acompte 4", value=to_float(dossier.get("Acompte 4")))

colD1, colD2, colD3, colD4 = st.columns(4)
da1 = colD1.date_input("Date Acompte 1", safe_date(dossier.get("Date Acompte 1")))
da2 = colD2.date_input("Date Acompte 2", safe_date(dossier.get("Date Acompte 2")))
da3 = colD3.date_input("Date Acompte 3", safe_date(dossier.get("Date Acompte 3")))
da4 = colD4.date_input("Date Acompte 4", safe_date(dossier.get("Date Acompte 4")))

# ---------------------------------------------------------
# ESCROW
# ---------------------------------------------------------
st.subheader("💰 Escrow")

escrow_flag = st.checkbox("Escrow actif ?", value=dossier["Escrow"])
escrow_a_reclamer_flag = dossier["Escrow_a_reclamer"]
escrow_reclame_flag = dossier["Escrow_reclame"]

# ---------------------------------------------------------
# STATUTS
# ---------------------------------------------------------
st.subheader("📦 Statuts du dossier")

colS1, colS2, colS3, colS4, colS5 = st.columns(5)
envoye = colS1.checkbox("Dossier envoyé", normalize_bool(dossier.get("Dossier envoye", False)))
accepte = colS2.checkbox("Dossier accepté", normalize_bool(dossier.get("Dossier accepte", False)))
refuse = colS3.checkbox("Dossier refusé", normalize_bool(dossier.get("Dossier refuse", False)))
annule = colS4.checkbox("Dossier annulé", normalize_bool(dossier.get("Dossier Annule", False)))
rfe = colS5.checkbox("RFE", normalize_bool(dossier.get("RFE", False)))

colT1, colT2, colT3, colT4, colT5 = st.columns(5)
date_envoye = colT1.date_input("Date envoi", safe_date(dossier.get("Date envoi")))
date_accepte = colT2.date_input("Date acceptation", safe_date(dossier.get("Date acceptation")))
date_refuse = colT3.date_input("Date refus", safe_date(dossier.get("Date refus")))
date_annule = colT4.date_input("Date annulation", safe_date(dossier.get("Date annulation")))
date_rfe = colT5.date_input("Date RFE", safe_date(dossier.get("Date reclamation")))

# ---------------------------------------------------------
# ➕ METTRE EN ESCROW EN COURS
# ---------------------------------------------------------
st.markdown("---")
st.subheader("➕ Mettre ce dossier en Escrow *en cours*")

if st.button("Mettre en Escrow en cours"):
    idx = df[df[DOSSIER_COL] == selected].index[0]

    df.loc[idx, "Escrow"] = True
    df.loc[idx, "Escrow_a_reclamer"] = False
    df.loc[idx, "Escrow_reclame"] = False

    db["clients"] = df.to_dict(orient="records")
    save_database(db)

    st.success("✔ Ce dossier est maintenant en *Escrow en cours*.")
    st.rerun()

# ---------------------------------------------------------
# SAUVEGARDE DES MODIFICATIONS
# ---------------------------------------------------------
if st.button("💾 Enregistrer les modifications", type="primary"):

    st.write("DEBUG — Avant mise à jour :", df[df[DOSSIER_COL] == selected])
    

    # (Ton code de sauvegarde ici)

    st.write("DEBUG — Après mise à jour :", df[df[DOSSIER_COL] == selected])

    

    idx = df[df[DOSSIER_COL] == selected].index[0]

    # -------- LOGIQUE AUTOMATIQUE : DOSSIER ENVOYÉ --------
    if envoye:
        escrow_flag = False
        escrow_a_reclamer_flag = True
        escrow_reclame_flag = False

    # -------- INFOS --------
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

    # -------- ESCROW (écriture finale) --------
    df.loc[idx, "Escrow"] = bool(escrow_flag)
    df.loc[idx, "Escrow_a_reclamer"] = bool(escrow_a_reclamer_flag)
    df.loc[idx, "Escrow_reclame"] = bool(escrow_reclame_flag)

    # -------- STATUTS --------
    df.loc[idx, "Dossier envoye"] = envoye
    df.loc[idx, "Date envoi"] = date_envoye
    df.loc[idx, "Dossier accepte"] = accepte
    df.loc[idx, "Date acceptation"] = date_accepte
    df.loc[idx, "Dossier refuse"] = refuse
    df.loc[idx, "Date refus"] = date_refuse
    df.loc[idx, "Dossier Annule"] = annule
    df.loc[idx, "Date annulation"] = date_annule
    df.loc[idx, "RFE"] = rfe
    df.loc[idx, "Date reclamation"] = date_rfe

    db["clients"] = df.to_dict(orient="records")
    save_database(db)

    st.success("✔ Modifications enregistrées.")
    st.rerun()

# ---------------------------------------------------------
# ❌ SUPPRESSION COMPLÈTE DE L’ESCROW
# ---------------------------------------------------------
st.markdown("---")
st.subheader("🛑 Supprimer totalement l’Escrow pour ce dossier")

if st.button("Supprimer l’Escrow"):
    idx = df[df[DOSSIER_COL] == selected].index[0]

    df.loc[idx, "Escrow"] = False
    df.loc[idx, "Escrow_a_reclamer"] = False
    df.loc[idx, "Escrow_reclame"] = False

    db["clients"] = df.to_dict(orient="records")
    save_database(db)

    st.success("✔ Escrow supprimé pour ce dossier.")
    st.rerun()

# ---------------------------------------------------------
# SUPPRESSION DU DOSSIER
# ---------------------------------------------------------
st.markdown("---")
st.subheader("🗑️ Supprimer définitivement ce dossier")

if st.button("❌ Supprimer ce dossier"):
    df = df[df[DOSSIER_COL] != selected]
    db["clients"] = df.to_dict(orient="records")
    save_database(db)
    st.success(f"Dossier {selected} supprimé ✔")
    st.experimental_rerun()
