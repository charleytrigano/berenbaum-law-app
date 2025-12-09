import streamlit as st
import pandas as pd
from backend.dropbox_utils import load_database, save_database
from backend.clean_json import clean_database

st.set_page_config(page_title="Modifier un dossier", page_icon="✏️", layout="wide")
st.title("✏️ Modifier un dossier")

# ---------------------------------------------------------
# 🔹 Chargement DB
# ---------------------------------------------------------
db = load_database()
clients = db.get("clients", [])

if not clients:
    st.error("Aucun dossier trouvé.")
    st.stop()

df = pd.DataFrame(clients)
DOSSIER_COL = "Dossier N"

# ---------------------------------------------------------
# 🔹 Normalisation booléens
# ---------------------------------------------------------
def normalize_bool(x):
    if isinstance(x, bool):
        return x
    if str(x).lower() in ["true", "1", "yes", "oui"]:
        return True
    return False


# ---------------------------------------------------------
# Sélection dossier
# ---------------------------------------------------------
df[DOSSIER_COL] = pd.to_numeric(df[DOSSIER_COL], errors="coerce").astype("Int64")
liste_dossiers = df[DOSSIER_COL].dropna().astype(int).sort_values().tolist()

selected = st.selectbox("Sélectionner un dossier :", liste_dossiers)

dossier = df[df[DOSSIER_COL] == selected].iloc[0].copy()

# DEBUG – état brut
st.markdown("### 🐞 DEBUG — État brut du dossier :")
st.json(dossier)

# ---------------------------------------------------------
# Importe utilitaires
# ---------------------------------------------------------
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

# ---------------------------------------------------------
# FORMULAIRE — Infos générales
# ---------------------------------------------------------
st.markdown("## 📄 Informations générales")

col1, col2, col3 = st.columns(3)
nom = col1.text_input("Nom", dossier.get("Nom", ""))
date_dossier = col2.date_input("Date du dossier", safe_date(dossier.get("Date")))
categories = col3.text_input("Catégorie", dossier.get("Categories", ""))

colA, colB = st.columns(2)
sous_categories = colA.text_input("Sous-catégorie", dossier.get("Sous-categories", ""))
visa = colB.text_input("Visa", dossier.get("Visa", ""))

colF1, colF2, colF3 = st.columns(3)
honoraires = colF1.number_input("Montant honoraires (US $)", value=to_float(dossier.get("Montant honoraires (US $)", 0)))
frais = colF2.number_input("Autres frais (US $)", value=to_float(dossier.get("Autres frais (US $)", 0)))
colF3.number_input("Total facturé", value=honoraires + frais, disabled=True)

# ---------------------------------------------------------
# ACOMPTES
# ---------------------------------------------------------
st.markdown("## 🏦 Acomptes")

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
# 🔹 MODE DE RÈGLEMENT
# ---------------------------------------------------------
st.subheader("💳 Mode de règlement")

modes = ["", "Chèque", "CB", "Virement", "Venmo"]

mode_reglement = st.selectbox(
    "Mode de paiement",
    modes,
    index=modes.index(dossier.get("mode_paiement", "")) if dossier.get("mode_paiement", "") in modes else 0
)

date_reglement = st.date_input(
    "Date du paiement",
    safe_date(dossier.get("date_paiement"))
)


# ---------------------------------------------------------
# ESCROW
# ---------------------------------------------------------
st.markdown("## 💰 Escrow")

escrow_active = st.checkbox("Escrow actif ?", value=normalize_bool(dossier.get("Escrow", False)))

# ---------------------------------------------------------
# STATUTS
# ---------------------------------------------------------
st.markdown("## 📦 Statuts du dossier")

colS1, colS2, colS3, colS4, colS5 = st.columns(5)

envoye = colS1.checkbox("Dossier envoyé", value=normalize_bool(dossier.get("Dossier_envoye", False)))
accepte = colS2.checkbox("Dossier accepté", value=normalize_bool(dossier.get("Dossier accepte", False)))
refuse = colS3.checkbox("Dossier refusé", value=normalize_bool(dossier.get("Dossier refuse", False)))
annule = colS4.checkbox("Dossier annulé", value=normalize_bool(dossier.get("Dossier Annule", False)))
rfe = colS5.checkbox("RFE", value=normalize_bool(dossier.get("RFE", False)))

colT1, colT2, colT3, colT4, colT5 = st.columns(5)
date_envoye = colT1.date_input("Date envoi", safe_date(dossier.get("Date envoi")))
date_accepte = colT2.date_input("Date acceptation", safe_date(dossier.get("Date acceptation")))
date_refuse = colT3.date_input("Date refus", safe_date(dossier.get("Date refus")))
date_annule = colT4.date_input("Date annulation", safe_date(dossier.get("Date annulation")))
date_rfe = colT5.date_input("Date RFE", safe_date(dossier.get("Date reclamation")))

# ---------------------------------------------------------
# 🔥 LOGIQUE AUTOMATIQUE ESCROW
# ---------------------------------------------------------
escrow_a_reclamer = normalize_bool(dossier.get("Escrow_a_reclamer", False))
escrow_reclame = normalize_bool(dossier.get("Escrow_reclame", False))

if envoye:
    escrow_active = False
    escrow_a_reclamer = True
    escrow_reclame = False

# ---------------------------------------------------------
# 🔥 SAUVEGARDE
# ---------------------------------------------------------
if st.button("💾 Enregistrer les modifications", type="primary"):

    idx = df[df[DOSSIER_COL] == selected].index[0]

    # Infos générales
    df.loc[idx, "Nom"] = nom
    df.loc[idx, "Date"] = str(date_dossier)
    df.loc[idx, "Categories"] = categories
    df.loc[idx, "Sous-categories"] = sous_categories
    df.loc[idx, "Visa"] = visa
    df.loc[idx, "Montant honoraires (US $)"] = honoraires
    df.loc[idx, "Autres frais (US $)"] = frais

    df.loc[idx, "Acompte 1"] = ac1
    df.loc[idx, "Acompte 2"] = ac2
    df.loc[idx, "Acompte 3"] = ac3
    df.loc[idx, "Acompte 4"] = ac4

    df.loc[idx, "Date Acompte 1"] = str(da1)
    df.loc[idx, "Date Acompte 2"] = str(da2)
    df.loc[idx, "Date Acompte 3"] = str(da3)
    df.loc[idx, "Date Acompte 4"] = str(da4)

    # Statuts
    df.loc[idx, "Dossier_envoye"] = bool(envoye)
    df.loc[idx, "Dossier accepte"] = bool(accepte)
    df.loc[idx, "Dossier refuse"] = bool(refuse)
    df.loc[idx, "Dossier Annule"] = bool(annule)
    df.loc[idx, "RFE"] = bool(rfe)

    df.loc[idx, "Date envoi"] = str(date_envoye)
    df.loc[idx, "Date acceptation"] = str(date_accepte)
    df.loc[idx, "Date refus"] = str(date_refuse)
    df.loc[idx, "Date annulation"] = str(date_annule)
    df.loc[idx, "Date reclamation"] = str(date_rfe)

    # ESCROW FINAL
    df.loc[idx, "Escrow"] = bool(escrow_active)
    df.loc[idx, "Escrow_a_reclamer"] = bool(escrow_a_reclamer)
    df.loc[idx, "Escrow_reclame"] = bool(escrow_reclame)

    # Sauvegarde JSON nettoyé
    db["clients"] = df.to_dict(orient="records")
    db = clean_database(db)
    save_database(db)

    st.success("✔ Modifications enregistrées.")
    st.rerun()
