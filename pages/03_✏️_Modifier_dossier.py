import streamlit as st
import pandas as pd
from backend.dropbox_utils import load_database, save_database

st.set_page_config(page_title="Modifier dossier", page_icon="✏️", layout="wide")
st.title("✏️ Modifier un dossier")

# ---------------------------------------------------------
# LOAD DATABASE
# ---------------------------------------------------------
db = load_database()
clients = db.get("clients", [])
deleted = db.get("deleted", [])  # historique des suppressions

if not clients:
    st.warning("Aucun dossier n’est disponible.")
    st.stop()

df = pd.DataFrame(clients)

# ---------------------------------------------------------
# CHOIX DU DOSSIER
# ---------------------------------------------------------
st.subheader("🔍 Sélection du dossier")
dossier_id = st.selectbox("Sélectionner un dossier", df["Dossier N"].tolist())

dossier = next(d for d in clients if d["Dossier N"] == dossier_id)

# ---------------------------------------------------------
# NORMALISATION POUR ÉVITER LES ERREURS
# ---------------------------------------------------------
def num(v): 
    try: return float(v)
    except: return 0.0

def date_or_none(v):
    try: return pd.to_datetime(v).date()
    except: return None

# ---------------------------------------------------------
# FORMULAIRE
# ---------------------------------------------------------
st.markdown("---")
st.subheader("📝 Informations générales")

col1, col2, col3 = st.columns(3)
with col1:
    st.write(f"**Dossier N :** {dossier['Dossier N']}")
with col2:
    nom = st.text_input("Nom", dossier.get("Nom", ""))
with col3:
    date = st.date_input("Date", value=date_or_none(dossier.get("Date")))

# ---------------------------------------------------------
# FINANCIER
# ---------------------------------------------------------
st.markdown("---")
st.subheader("💵 Informations financières")

colH1, colH2, colH3 = st.columns(3)
with colH1:
    honoraires = st.number_input("Montant honoraires (US $)", value=num(dossier.get("Montant honoraires (US $)")))
with colH2:
    autres = st.number_input("Autres frais (US $)", value=num(dossier.get("Autres frais (US $)")))
with colH3:
    total = honoraires + autres
    st.number_input("Total facturé", value=total, disabled=True)

st.subheader("💰 Acomptes")

colA1, colA2, colA3, colA4 = st.columns(4)
with colA1:
    a1 = st.number_input("Acompte 1", value=num(dossier.get("Acompte 1")))
with colA2:
    a2 = st.number_input("Acompte 2", value=num(dossier.get("Acompte 2")))
with colA3:
    a3 = st.number_input("Acompte 3", value=num(dossier.get("Acompte 3")))
with colA4:
    a4 = st.number_input("Acompte 4", value=num(dossier.get("Acompte 4")))

encaissé = a1 + a2 + a3 + a4
solde = total - encaissé

st.metric("Solde restant", f"${solde:,.2f}")

# Dates des acomptes
colD1, colD2, colD3, colD4 = st.columns(4)
with colD1:
    da1 = st.date_input("Date Acompte 1", value=date_or_none(dossier.get("Date Acompte 1")))
with colD2:
    da2 = st.date_input("Date Acompte 2", value=date_or_none(dossier.get("Date Acompte 2")))
with colD3:
    da3 = st.date_input("Date Acompte 3", value=date_or_none(dossier.get("Date Acompte 3")))
with colD4:
    da4 = st.date_input("Date Acompte 4", value=date_or_none(dossier.get("Date Acompte 4")))

# ---------------------------------------------------------
# STATUTS DU DOSSIER
# ---------------------------------------------------------
st.markdown("---")
st.subheader("📌 Statuts du dossier")

colS1, colS2, colS3, colS4, colS5 = st.columns(5)

with colS1:
    envoye = st.checkbox("Dossier envoyé", bool(dossier.get("Dossier envoye")))
with colS2:
    accepte = st.checkbox("Dossier accepté", bool(dossier.get("Dossier accepte")))
with colS3:
    refuse = st.checkbox("Dossier refusé", bool(dossier.get("Dossier refuse")))
with colS4:
    annule = st.checkbox("Dossier annulé", bool(dossier.get("Dossier Annule")))
with colS5:
    rfe = st.checkbox("RFE", bool(dossier.get("RFE")))

colSD1, colSD2, colSD3, colSD4, colSD5 = st.columns(5)

with colSD1:
    date_envoye = st.date_input("Date envoi", value=date_or_none(dossier.get("Date envoi")))
with colSD2:
    date_accepte = st.date_input("Date acceptation", value=date_or_none(dossier.get("Date acceptation")))
with colSD3:
    date_refus = st.date_input("Date refus", value=date_or_none(dossier.get("Date refus")))
with colSD4:
    date_annule = st.date_input("Date annulation", value=date_or_none(dossier.get("Date annulation")))
with colSD5:
    date_rfe = st.date_input("Date RFE", value=date_or_none(dossier.get("Date reclamation")))

# ---------------------------------------------------------
# ESCROW
# ---------------------------------------------------------
st.markdown("---")
escrow = st.checkbox("Escrow", bool(dossier.get("Escrow")))

# ---------------------------------------------------------
# BOUTON SAUVEGARDER
# ---------------------------------------------------------
if st.button("💾 Enregistrer les modifications", type="primary"):
    dossier.update({
        "Nom": nom,
        "Date": str(date),
        "Montant honoraires (US $)": honoraires,
        "Autres frais (US $)": autres,
        "Acompte 1": a1,
        "Acompte 2": a2,
        "Acompte 3": a3,
        "Acompte 4": a4,
        "Date Acompte 1": str(da1) if da1 else "",
        "Date Acompte 2": str(da2) if da2 else "",
        "Date Acompte 3": str(da3) if da3 else "",
        "Date Acompte 4": str(da4) if da4 else "",
        "Dossier envoye": float(envoye),
        "Date envoi": str(date_envoye) if date_envoye else "",
        "Dossier accepte": float(accepte),
        "Date acceptation": str(date_accepte) if date_accepte else "",
        "Dossier refuse": float(refuse),
        "Date refus": str(date_refus) if date_refus else "",
        "Dossier Annule": float(annule),
        "Date annulation": str(date_annule) if date_annule else "",
        "RFE": float(rfe),
        "Date reclamation": str(date_rfe) if date_rfe else "",
        "Escrow": escrow
    })

    save_database(db)
    st.success("✔ Dossier mis à jour avec succès !")
    st.experimental_rerun()

# ---------------------------------------------------------
# 🗑 SUPPRESSION DU DOSSIER AVEC HISTORIQUE
# ---------------------------------------------------------
st.markdown("---")
st.subheader("🗑 Suppression du dossier")

delete_confirm = st.checkbox(
    f"⚠️ Je confirme vouloir supprimer le dossier {dossier['Dossier N']} définitivement",
    key="confirm_delete"
)

if delete_confirm:
    if st.button("❌ Supprimer ce dossier", type="primary"):

        # Ajout à l’historique
        dossier["deleted_at"] = str(pd.Timestamp.now())
        deleted.append(dossier)
        db["deleted"] = deleted

        # Suppression du dossier
        db["clients"] = [d for d in clients if d["Dossier N"] != dossier["Dossier N"]]

        save_database(db)

        st.error(f"🚨 Dossier {dossier['Dossier N']} supprimé et archivé dans l’historique.")
        st.info("⏳ Rechargement...")
        st.experimental_rerun()
