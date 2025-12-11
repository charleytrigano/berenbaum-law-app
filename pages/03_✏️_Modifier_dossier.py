import streamlit as st
import pandas as pd

from utils.sidebar import render_sidebar
from backend.dropbox_utils import load_database, save_database
from utils.status_utils import normalize_bool   # <-- SEULE IMPORTATION OK

# ---------------------------------------------------------
# CONFIG & SIDEBAR
# ---------------------------------------------------------
st.set_page_config(page_title="Modifier un dossier", page_icon="✏️", layout="wide")
render_sidebar()
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
# 🔹 Normalisation des colonnes de statuts
# (on ne fusionne plus rien, on garantit juste leur présence)
# ---------------------------------------------------------
expected_cols = [
    "Dossier envoye",
    "Dossier accepte",
    "Dossier refuse",
    "Dossier Annule",
    "RFE",
    "Escrow",
    "Escrow_a_reclamer",
    "Escrow_reclame",
]

for col in expected_cols:
    if col not in df.columns:
        df[col] = False
    df[col] = df[col].apply(normalize_bool)

# ---------------------------------------------------------
# 🔹 Sélection dossier
# ---------------------------------------------------------
df[DOSSIER_COL] = pd.to_numeric(df[DOSSIER_COL], errors="coerce")
liste = sorted(df[DOSSIER_COL].dropna().astype(int).unique())

selected = st.selectbox("Sélectionner un dossier", liste)
dossier = df[df[DOSSIER_COL] == selected].iloc[0].copy()

# ---------------------------------------------------------
# Utils
# ---------------------------------------------------------
def to_float(x):
    try:
        return float(x)
    except Exception:
        return 0.0

def safe_date(v):
    try:
        d = pd.to_datetime(v, errors="coerce")
        return None if pd.isna(d) else d.date()
    except Exception:
        return None

# ---------------------------------------------------------
# FORMULAIRE — Infos générales
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

commentaire = st.text_area("📝 Commentaire", dossier.get("Commentaire", ""))

# ---------------------------------------------------------
# 🏦 Acomptes + Modes + Dates
# ---------------------------------------------------------
st.subheader("🏦 Acomptes et modes de règlement")

modes = ["", "Chèque", "CB", "Virement", "Venmo"]

ac_inputs = {}
mode_inputs = {}
date_inputs = {}

for i in range(1, 5):
    st.markdown(f"### Acompte {i}")
    colA, colM, colD = st.columns(3)
    ac_inputs[i] = colA.number_input(f"Montant Acompte {i}", value=to_float(dossier.get(f"Acompte {i}", 0)))
    mode_inputs[i] = colM.selectbox(
        f"Mode Acompte {i}", 
        options=modes,
        index=modes.index(dossier.get(f"Mode Acompte {i}", "")) if dossier.get(f"Mode Acompte {i}", "") in modes else 0,
    )
    date_inputs[i] = colD.date_input(
        f"Date Paiement {i}",
        value=safe_date(dossier.get(f"Date Paiement {i}"))
    )

# ---------------------------------------------------------
# 💰 Escrow
# ---------------------------------------------------------
st.subheader("💰 Escrow")
escrow_flag = st.checkbox("Escrow actif ?", value=normalize_bool(dossier.get("Escrow", False)))

# ---------------------------------------------------------
# 📦 Statuts
# ---------------------------------------------------------
st.subheader("📦 Statuts du dossier")

colS1, colS2, colS3, colS4, colS5 = st.columns(5)

envoye = colS1.checkbox("Dossier envoyé", normalize_bool(dossier.get("Dossier envoye")))
accepte = colS2.checkbox("Dossier accepté", normalize_bool(dossier.get("Dossier accepte")))
refuse = colS3.checkbox("Dossier refusé", normalize_bool(dossier.get("Dossier refuse")))
annule = colS4.checkbox("Dossier annulé", normalize_bool(dossier.get("Dossier Annule")))
rfe = colS5.checkbox("RFE", normalize_bool(dossier.get("RFE")))

colT1, colT2, colT3, colT4, colT5 = st.columns(5)
date_envoye = colT1.date_input("Date envoi", safe_date(dossier.get("Date envoi")))
date_accepte = colT2.date_input("Date acceptation", safe_date(dossier.get("Date acceptation")))
date_refuse = colT3.date_input("Date refus", safe_date(dossier.get("Date refus")))
date_annule = colT4.date_input("Date annulation", safe_date(dossier.get("Date annulation")))
date_rfe = colT5.date_input("Date RFE", safe_date(dossier.get("Date reclamation")))

# ---------------------------------------------------------
# 🔥 SAUVEGARDE DES MODIFICATIONS
# ---------------------------------------------------------
if st.button("💾 Enregistrer les modifications", type="primary"):
    idx = df[df[DOSSIER_COL] == selected].index[0]

    # Infos générales
    df.loc[idx, "Nom"] = nom
    df.loc[idx, "Date"] = date_dossier
    df.loc[idx, "Categories"] = categories
    df.loc[idx, "Sous-categories"] = sous_categories
    df.loc[idx, "Visa"] = visa
    df.loc[idx, "Montant honoraires (US $)"] = honoraires
    df.loc[idx, "Autres frais (US $)"] = frais
    df.loc[idx, "Commentaire"] = commentaire

    # Acomptes
    for i in range(1, 5):
        df.loc[idx, f"Acompte {i}"] = ac_inputs[i]
        df.loc[idx, f"Mode Acompte {i}"] = mode_inputs[i]
        df.loc[idx, f"Date Paiement {i}"] = date_inputs[i]

    # ➤ STATUTS — PATCH **GARANTI FONCTIONNEL**
    df.loc[idx, "Dossier envoye"] = bool(envoye)
    df.loc[idx, "Dossier accepte"] = bool(accepte)
    df.loc[idx, "Dossier refuse"] = bool(refuse)
    df.loc[idx, "Dossier Annule"] = bool(annule)
    df.loc[idx, "RFE"] = bool(rfe)

    # Dates
    df.loc[idx, "Date envoi"] = date_envoye
    df.loc[idx, "Date acceptation"] = date_accepte
    df.loc[idx, "Date refus"] = date_refuse
    df.loc[idx, "Date annulation"] = date_annule
    df.loc[idx, "Date reclamation"] = date_rfe

    # ➤ ESCROW LOGIQUE
    if envoye:
        df.loc[idx, "Escrow"] = False
        df.loc[idx, "Escrow_a_reclamer"] = True
        df.loc[idx, "Escrow_reclame"] = False
    else:
        df.loc[idx, "Escrow"] = bool(escrow_flag)

    # Sauvegarde
    db["clients"] = df.to_dict(orient="records")
    save_database(db)

    st.success("✔ Dossier mis à jour avec succès.")
    st.rerun()
