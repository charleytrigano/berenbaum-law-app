import streamlit as st
import pandas as pd
from backend.dropbox_utils import load_database, save_database

st.set_page_config(page_title="Modifier dossier", page_icon="✏️", layout="wide")

st.title("✏️ Modifier un dossier existant")

# =========================================
# Chargement base
# =========================================
db = load_database()
clients = db.get("clients", [])

if not clients:
    st.warning("Aucun dossier trouvé.")
    st.stop()

df = pd.DataFrame(clients)

# =========================================
# Fonction SAFE pour les dates
# =========================================
def safe_date(value):
    """Convertit proprement en date ou None."""
    if value in ("", None, float("nan")):
        return None
    try:
        return pd.to_datetime(value).date()
    except:
        return None

# =========================================
# Sélection du dossier
# =========================================
st.subheader("📁 Sélectionner un dossier")

liste_dossiers = sorted(df["Dossier N"].unique().tolist())
selected = st.selectbox("Choisissez un numéro de dossier :", [""] + liste_dossiers)

if selected == "":
    st.stop()

dossier = df[df["Dossier N"] == selected].iloc[0].to_dict()

idx = df.index[df["Dossier N"] == selected][0]

st.markdown("---")

# =========================================
# SECTION 1 : Infos principales
# =========================================
st.subheader("📌 Informations principales")

col1, col2, col3 = st.columns(3)

with col1:
    dossier_num = st.number_input("Dossier N", value=int(dossier["Dossier N"]))
with col2:
    nom = st.text_input("Nom", value=dossier.get("Nom", ""))
with col3:
    date_creation = st.date_input(
        "Date du dossier",
        value=safe_date(dossier.get("Date"))
    )

# =========================================
# SECTION 2 : Montants
# =========================================
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
    st.number_input("Total facturé", value=float(facture), disabled=True)

# =========================================
# SECTION 3 : Acomptes
# =========================================
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

st.number_input("💼 Solde", value=float(solde), disabled=True)

# =========================================
# SECTION 4 : Dates des acomptes
# =========================================
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

# =========================================
# SECTION 5 : Statuts dossier
# =========================================
st.subheader("📌 Statuts du dossier")

colS1, colS2, colS3, colS4, colS5 = st.columns(5)

with colS1:
    envoye = st.checkbox("Dossier envoyé", value=bool(dossier.get("Dossier envoye")))
with colS2:
    accepte = st.checkbox("Dossier accepté", value=bool(dossier.get("Dossier accepte")))
with colS3:
    refuse = st.checkbox("Dossier refusé", value=bool(dossier.get("Dossier refuse")))
with colS4:
    annule = st.checkbox("Dossier annulé", value=bool(dossier.get("Dossier Annule")))
with colS5:
    rfe = st.checkbox("RFE", value=bool(dossier.get("RFE")))

# Dates statut
colDS1, colDS2, colDS3, colDS4, colDS5 = st.columns(5)

with colDS1:
    d_envoye = st.date_input("Date envoi", value=safe_date(dossier.get("Date envoi")))
with colDS2:
    d_accepte = st.date_input("Date acceptation", value=safe_date(dossier.get("Date acceptation")))
with colDS3:
    d_refuse = st.date_input("Date refus", value=safe_date(dossier.get("Date refus")))
with colDS4:
    d_annule = st.date_input("Date annulation", value=safe_date(dossier.get("Date annulation")))
with colDS5:
    d_rfe = st.date_input("Date RFE", value=safe_date(dossier.get("Date reclamation")))

# =========================================
# SECTION 6 : Escrow
# =========================================
st.subheader("💼 Escrow")

escrow = st.checkbox("Escrow actif", value=bool(dossier.get("Escrow")))

# =========================================
# ENREGISTREMENT
# =========================================
if st.button("💾 Enregistrer les modifications", type="primary"):

    updated = {
        "Dossier N": dossier_num,
        "Nom": nom,
        "Date": str(date_creation) if date_creation else "",
        "Montant honoraires (US $)": honoraires,
        "Autres frais (US $)": autres_frais,
        "Acompte 1": a1, "Date Acompte 1": str(da1) if da1 else "",
        "Acompte 2": a2, "Date Acompte 2": str(da2) if da2 else "",
        "Acompte 3": a3, "Date Acompte 3": str(da3) if da3 else "",
        "Acompte 4": a4, "Date Acompte 4": str(da4) if da4 else "",
        "Dossier envoye": float(envoye),
        "Date envoi": str(d_envoye) if d_envoye else "",
        "Dossier accepte": float(accepte),
        "Date acceptation": str(d_accepte) if d_accepte else "",
        "Dossier refuse": float(refuse),
        "Date refus": str(d_refuse) if d_refuse else "",
        "Dossier Annule": float(annule),
        "Date annulation": str(d_annule) if d_annule else "",
        "RFE": float(rfe),
        "Date reclamation": str(d_rfe) if d_rfe else "",
        "Escrow": escrow
    }

    clients[idx] = updated
    db["clients"] = clients
    save_database(db)

    st.success("✔ Dossier mis à jour avec succès")

# =========================================
# SUPPRESSION DOSSIER + HISTORIQUE
# =========================================
st.markdown("---")
st.subheader("🗑️ Suppression du dossier")

if st.button("❌ Supprimer ce dossier", type="secondary"):
    if "deleted" not in db:
        db["deleted"] = []

    db["deleted"].append(dossier)
    del clients[idx]
    db["clients"] = clients
    save_database(db)

    st.success("🔥 Dossier supprimé et envoyé dans l'historique.")
    st.stop()
