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
    st.stop()

df = pd.DataFrame(clients)
DOSSIER_COL = "Dossier N"

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

# ---------------------------------------------------------
# DEBUG : afficher le dossier brut
# ---------------------------------------------------------
st.write("🔍 DEBUG — Dossier brut avant modification :")
st.write(dossier)

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

# DEBUG date_dossier
st.write("🔍 DEBUG — date_dossier :", date_dossier, type(date_dossier))

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
envoye = colS1.checkbox("Dossier envoyé", normalize_bool(dossier.get("Dossier envoye", dossier.get("Dossier envoyé", False))))

st.write("🔍 DEBUG — Valeur envoyée lue :", envoye)

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
# SAUVEGARDE DES MODIFICATIONS
# ---------------------------------------------------------
if st.button("💾 Enregistrer les modifications", type="primary"):

    st.write("DEBUG — Sauvegarde en cours...")

    idx = df[df[DOSSIER_COL] == selected].index[0]

    # LOGIQUE
    if envoye:
        escrow_flag = False
        escrow_a_reclamer_flag = True

    # -----------------------------------------------------
    # CHECKPOINTS de chaque écriture df.loc
    # -----------------------------------------------------
    try:
        df.loc[idx, "Nom"] = nom
        st.write("CHECK Nom OK")
        
        df.loc[idx, "Date"] = date_dossier
        st.write("CHECK Date OK")

        df.loc[idx, "Categories"] = categories
        st.write("CHECK Categories OK")

        df.loc[idx, "Sous-categories"] = sous_categories
        st.write("CHECK Sous-cat OK")

        df.loc[idx, "Visa"] = visa
        st.write("CHECK Visa OK")

        df.loc[idx, "Montant honoraires (US $)"] = honoraires
        st.write("CHECK Hon OK")

        df.loc[idx, "Autres frais (US $)"] = frais
        st.write("CHECK Frais OK")

        df.loc[idx, "Acompte 1"] = ac1
        st.write("CHECK A1 OK")

        df.loc[idx, "Acompte 2"] = ac2
        st.write("CHECK A2 OK")

        df.loc[idx, "Acompte 3"] = ac3
        st.write("CHECK A3 OK")

        df.loc[idx, "Acompte 4"] = ac4
        st.write("CHECK A4 OK")

        df.loc[idx, "Date Acompte 1"] = da1
        st.write("CHECK DA1 OK")

        df.loc[idx, "Date Acompte 2"] = da2
        st.write("CHECK DA2 OK")

        df.loc[idx, "Date Acompte 3"] = da3
        st.write("CHECK DA3 OK")

        df.loc[idx, "Date Acompte 4"] = da4
        st.write("CHECK DA4 OK")

        # ESCROW
        df.loc[idx, "Escrow"] = bool(escrow_flag)
        st.write("CHECK Escrow OK")

        df.loc[idx, "Escrow_a_reclamer"] = bool(escrow_a_reclamer_flag)
        st.write("CHECK Escrow a réclamer OK")

        df.loc[idx, "Escrow_reclame"] = bool(escrow_reclame_flag)
        st.write("CHECK Escrow réclamé OK")

        # STATUTS
        df.loc[idx, "Dossier envoye"] = envoye
        df.loc[idx, "Dossier envoyé"] = envoye
        st.write("CHECK Dossier envoye OK")

    except Exception as e:
        st.error(f"⛔ ERREUR D'ÉCRITURE df.loc : {e}")
        st.stop()

    # -----------------------------------------------------
    # CHECKPOINT — conversion JSON
    # -----------------------------------------------------
    db["clients"] = df.to_dict(orient="records")
    st.write("CHECKPOINT JSON OK")

    # -----------------------------------------------------
    # CHECKPOINT — sauvegarde Dropbox
    # -----------------------------------------------------
    try:
        save_database(db)
        st.write("DEBUG — SAUVEGARDE OK")
    except Exception as e:
        st.error(f"⛔ ERREUR DE SAUVEGARDE : {e}")
        st.stop()

    st.write("DEBUG — Dernière ligne atteinte ✔")
    st.success("✔ Modifications enregistrées.")
    st.rerun()
