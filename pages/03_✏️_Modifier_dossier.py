import streamlit as st
import pandas as pd

from utils.sidebar import render_sidebar
from backend.dropbox_utils import load_database, save_database
from utils.status_utils import normalize_bool

# ---------------------------------------------------------
# CONFIG
# ---------------------------------------------------------
st.set_page_config(page_title="✏️ Modifier un dossier", page_icon="✏️", layout="wide")
render_sidebar()
st.title("✏️ Modifier un dossier")

# ---------------------------------------------------------
# LOAD DATABASE
# ---------------------------------------------------------
db = load_database()
clients = db.get("clients", [])

if not clients:
    st.error("Aucun dossier trouvé.")
    st.stop()

df = pd.DataFrame(clients)

# Toujours travailler en STRING pour Dossier N (xxxx, xxxx-1)
df["Dossier N"] = df["Dossier N"].astype(str)

# ---------------------------------------------------------
# SELECT DOSSIER
# ---------------------------------------------------------
selected = st.selectbox(
    "Sélectionner un dossier",
    sorted(df["Dossier N"].unique())
)

row = df[df["Dossier N"] == selected].iloc[0].copy()
idx = df[df["Dossier N"] == selected].index[0]

# ---------------------------------------------------------
# HELPERS
# ---------------------------------------------------------
def safe_date(v):
    try:
        d = pd.to_datetime(v, errors="coerce")
        return None if pd.isna(d) else d.date()
    except:
        return None

def safe_float(v):
    try:
        return float(v)
    except:
        return 0.0

# ---------------------------------------------------------
# INFORMATIONS GÉNÉRALES
# ---------------------------------------------------------
st.subheader(f"📄 Dossier {selected}")

c1, c2, c3 = st.columns(3)
nom = c1.text_input("Nom", row.get("Nom", ""))
date_dossier = c2.date_input("Date", safe_date(row.get("Date")))
visa = c3.text_input("Visa", row.get("Visa", ""))

c4, c5 = st.columns(2)
categorie = c4.text_input("Catégorie", row.get("Categories", ""))
sous_cat = c5.text_input("Sous-catégorie", row.get("Sous-categories", ""))

# ---------------------------------------------------------
# FACTURATION
# ---------------------------------------------------------
st.subheader("💰 Facturation")

f1, f2, f3 = st.columns(3)
hon = f1.number_input(
    "Montant honoraires (US $)",
    value=safe_float(row.get("Montant honoraires (US $)", 0))
)
frais = f2.number_input(
    "Autres frais (US $)",
    value=safe_float(row.get("Autres frais (US $)", 0))
)
f3.number_input("Total facturé", hon + frais, disabled=True)

# ---------------------------------------------------------
# ACOMPTES COMPLETS (montant + date + mode)
# ---------------------------------------------------------
st.subheader("🏦 Paiements")

modes = ["", "Chèque", "CB", "Virement", "Venmo"]
total_encaisse = 0.0

for i in range(1, 5):
    st.markdown(f"### Acompte {i}")
    a1, a2, a3 = st.columns(3)

    montant = a1.number_input(
        f"Montant Acompte {i}",
        value=safe_float(row.get(f"Acompte {i}", 0)),
        key=f"a{i}"
    )

    date_paiement = a2.date_input(
        f"Date Acompte {i}",
        value=safe_date(row.get(f"Date Acompte {i}")),
        key=f"d{i}"
    )

    mode = a3.selectbox(
        f"Mode Acompte {i}",
        modes,
        index=modes.index(row.get(f"Mode Acompte {i}", ""))
        if row.get(f"Mode Acompte {i}", "") in modes else 0,
        key=f"m{i}"
    )

    df.loc[idx, f"Acompte {i}"] = montant
    df.loc[idx, f"Date Acompte {i}"] = str(date_paiement) if date_paiement else ""
    df.loc[idx, f"Mode Acompte {i}"] = mode

    total_encaisse += montant

solde = (hon + frais) - total_encaisse
st.info(f"💵 Total encaissé : ${total_encaisse:,.2f} — Solde dû : ${solde:,.2f}")

# ---------------------------------------------------------
# ESCROW
# ---------------------------------------------------------
st.subheader("💼 Escrow")

escrow_actif = st.checkbox(
    "Escrow actif",
    value=normalize_bool(row.get("Escrow", False))
)

escrow_reclamer = st.checkbox(
    "Escrow à réclamer",
    value=normalize_bool(row.get("Escrow_a_reclamer", False))
)

escrow_reclame = st.checkbox(
    "Escrow réclamé",
    value=normalize_bool(row.get("Escrow_reclame", False))
)

st.caption("ℹ️ Le montant en escrow correspond uniquement à **Acompte 1**")

# ---------------------------------------------------------
# STATUTS
# ---------------------------------------------------------
st.subheader("📦 Statuts du dossier")

s1, s2, s3, s4, s5 = st.columns(5)

envoye = s1.checkbox("Envoyé", normalize_bool(row.get("Dossier envoye", False)))
accepte = s2.checkbox("Accepté", normalize_bool(row.get("Dossier accepte", False)))
refuse = s3.checkbox("Refusé", normalize_bool(row.get("Dossier refuse", False)))
annule = s4.checkbox("Annulé", normalize_bool(row.get("Dossier Annule", False)))
rfe = s5.checkbox("RFE", normalize_bool(row.get("RFE", False)))

# ---------------------------------------------------------
# SAVE
# ---------------------------------------------------------
if st.button("💾 Enregistrer", type="primary"):

    df.loc[idx, "Nom"] = nom
    df.loc[idx, "Date"] = str(date_dossier)
    df.loc[idx, "Visa"] = visa
    df.loc[idx, "Categories"] = categorie
    df.loc[idx, "Sous-categories"] = sous_cat

    df.loc[idx, "Montant honoraires (US $)"] = hon
    df.loc[idx, "Autres frais (US $)"] = frais

    # Statuts
    df.loc[idx, "Dossier envoye"] = envoye
    df.loc[idx, "Dossier accepte"] = accepte
    df.loc[idx, "Dossier refuse"] = refuse
    df.loc[idx, "Dossier Annule"] = annule
    df.loc[idx, "RFE"] = rfe

    # Escrow — logique propre
    df.loc[idx, "Escrow"] = escrow_actif
    df.loc[idx, "Escrow_a_reclamer"] = escrow_reclamer and not escrow_reclame
    df.loc[idx, "Escrow_reclame"] = escrow_reclame

    db["clients"] = df.to_dict(orient="records")
    save_database(db)

    st.success("✔ Dossier mis à jour avec succès")
    st.rerun()