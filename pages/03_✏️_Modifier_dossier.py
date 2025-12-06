import streamlit as st
import pandas as pd
from backend.dropbox_utils import load_database, save_database

st.set_page_config(page_title="Modifier dossier", page_icon="✏️", layout="wide")

st.title("✏️ Modifier un dossier existant")

# =====================================
# FONCTION : Trouver la colonne Dossier N
# =====================================
def find_dossier_column(df):
    candidates = [
        "Dossier N", "Dossier N ", "DossierN",
        "Numéro dossier", "Numero dossier", "numero",
        "N dossier"
    ]
    for c in df.columns:
        if c in candidates:
            return c
    # fallback : première colonne numérique
    for c in df.columns:
        if pd.api.types.is_numeric_dtype(df[c]):
            return c
    return None

# =====================================
# FONCTION : Convertir date proprement
# =====================================
def safe_date(value):
    if value in ("", None) or pd.isna(value):
        return None
    try:
        return pd.to_datetime(value).date()
    except:
        return None

# =====================================
# LOAD DATABASE
# =====================================
db = load_database()
clients = db.get("clients", [])

if not clients:
    st.warning("Aucun dossier trouvé.")
    st.stop()

df = pd.DataFrame(clients)

# Trouver colonne du numéro de dossier
DOSSIER_COL = find_dossier_column(df)

if DOSSIER_COL is None:
    st.error("❌ Impossible d’identifier la colonne du numéro de dossier.")
    st.stop()

# =====================================
# SELECTION DOSSIER
# =====================================
st.subheader("📁 Sélectionner un dossier")

liste_dossiers = sorted(df[DOSSIER_COL].dropna().unique().tolist())
selected = st.selectbox("Choisissez un numéro de dossier :", [""] + liste_dossiers)

if selected == "":
    st.stop()

dossier = df[df[DOSSIER_COL] == selected].iloc[0].to_dict()
idx = df.index[df[DOSSIER_COL] == selected][0]

st.markdown("---")

# =====================================
# INFOS PRINCIPALES
# =====================================
st.subheader("📌 Informations principales")

col1, col2, col3 = st.columns(3)

with col1:
    dossier_num = st.number_input("Dossier N", value=int(selected))

with col2:
    nom = st.text_input("Nom", value=dossier.get("Nom", ""))

with col3:
    date_creation = st.date_input(
        "Date du dossier",
        value=safe_date(dossier.get("Date"))
    )

# =====================================
# MONTANTS
# =====================================
st.subheader("💵 Montants")

col1, col2, col3 = st.columns(3)

with col1:
    honoraires = st.number_input(
        "Montant honoraires (US $)",
        value=float(dossier.get("Montant honoraires (US $)", 0))
    )

with col2:
    autres_frais = st.number_input(
        "Autres frais (US $)",
        value=float(dossier.get("Autres frais (US $)", 0))
    )

with col3:
    facture = honoraires + autres_frais
    st.number_input("Total facturé", value=facture, disabled=True)

# =====================================
# ACOMPTES
# =====================================
st.subheader("💰 Acomptes")

colA1, colA2, colA3, colA4 = st.columns(4)

with colA1:
    a1 = st.number_input("Acompte 1", value=float(dossier.get("Acompte 1", 0)))
with colA2:
    a2 = st.number_input("Acompte 2", value=float(dossier.get("Acompte 2", 0)))
with colA3:
    a3 = st.number_input("Acompte 3", value=float(dossier.get("Acompte 3", 0)))
with colA4:
    a4 = st.number_input("Acompte 4", value=float(dossier.get("Acompte 4", 0)))

solde = facture - (a1 + a2 + a3 + a4)
st.number_input("Solde", value=float(solde), disabled=True)

# =====================================
# DATES ACOMPTES
# =====================================
st.subheader("📅 Dates des acomptes")

colD1, colD2, colD3, colD4 = st.columns(4)

with colD1:
    da1 = st.date_input("Date Acompte 1", value=safe_date(dossier.get("Date Acompte 1")))
with colD2:
    da2 = st.date_input("Date Acompte 2", value=safe_date(dossier.get("Date Acompte 2")))
with colD3:
    da3 = st.date_input("Date Acompte 3", value=safe_date(dossier.get("Date Acompte 3")))
with colD4:
    da4 = st.date_input("Date Acompte 4", value=safe_date(dossier.get("Date Acompte 4")))

# =====================================
# STATUTS DOSSIER
# =====================================
st.subheader("📌 Statuts du dossier")

colS1, colS2, colS3, colS4, colS5 = st.columns(5)

envoye = colS1.checkbox("Dossier envoyé", bool(dossier.get("Dossier envoye")))
accepte = colS2.checkbox("Dossier accepté", bool(dossier.get("Dossier accepte")))
refuse = colS3.checkbox("Dossier refusé", bool(dossier.get("Dossier refuse")))
annule = colS4.checkbox("Dossier annulé", bool(dossier.get("Dossier Annule")))
rfe = colS5.checkbox("RFE", bool(dossier.get("RFE")))

# =====================================
# ENREGISTREMENT
# =====================================
if st.button("💾 Enregistrer les modifications", type="primary"):

    updated = dossier.copy()
    updated[DOSSIER_COL] = dossier_num
    updated["Nom"] = nom
    updated["Date"] = str(date_creation) if date_creation else ""

    updated["Montant honoraires (US $)"] = honoraires
    updated["Autres frais (US $)"] = autres_frais

    updated["Acompte 1"] = a1
    updated["Acompte 2"] = a2
    updated["Acompte 3"] = a3
    updated["Acompte 4"] = a4

    updated["Date Acompte 1"] = str(da1) if da1 else ""
    updated["Date Acompte 2"] = str(da2) if da2 else ""
    updated["Date Acompte 3"] = str(da3) if da3 else ""
    updated["Date Acompte 4"] = str(da4) if da4 else ""

    updated["Dossier envoye"] = float(envoye)
    updated["Dossier accepte"] = float(accepte)
    updated["Dossier refuse"] = float(refuse)
    updated["Dossier Annule"] = float(annule)
    updated["RFE"] = float(rfe)

    clients[idx] = updated
    db["clients"] = clients
    save_database(db)

    st.success("✔ Dossier mis à jour avec succès")

# =====================================
# SUPPRESSION DOSSIER + HISTORIQUE
# =====================================
st.markdown("---")
st.subheader("🗑️ Suppression du dossier")

if st.button("❌ Supprimer ce dossier"):
    if "deleted" not in db:
        db["deleted"] = []

    db["deleted"].append(dossier)
    clients.pop(idx)
    db["clients"] = clients
    save_database(db)

    st.success("🔥 Dossier supprimé et ajouté à l’historique.")
    st.stop()
