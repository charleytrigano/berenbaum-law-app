import streamlit as st
import pandas as pd
from datetime import datetime

from utils.sidebar import render_sidebar
from backend.dropbox_utils import load_database, save_database
from utils.tarif_utils import get_tarif_for_visa
from utils.status_utils import (
    normalize_status_columns,
    update_status_row,
    normalize_bool,
)

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
visa_table = pd.DataFrame(db.get("visa", []))
tarifs = db.get("tarifs", [])

if not clients:
    st.error("Aucun dossier trouvé.")
    st.stop()

df = pd.DataFrame(clients)
df = normalize_status_columns(df)

DOSSIER_COL = "Dossier N"
df[DOSSIER_COL] = df[DOSSIER_COL].astype(str)

# ---------------------------------------------------------
# UTILS
# ---------------------------------------------------------
def safe_date(v):
    try:
        d = pd.to_datetime(v, errors="coerce")
        return None if pd.isna(d) else d.date()
    except:
        return None

def to_float(v):
    try:
        return float(v)
    except:
        return 0.0

def get_souscats(cat):
    return sorted(
        visa_table[visa_table["Categories"] == cat]["Sous-categories"]
        .dropna()
        .unique()
        .tolist()
    )

def get_visas(souscat):
    return sorted(
        visa_table[visa_table["Sous-categories"] == souscat]["Visa"]
        .dropna()
        .unique()
        .tolist()
    )

# ---------------------------------------------------------
# SÉLECTION DOSSIER
# ---------------------------------------------------------
liste = sorted(df[DOSSIER_COL].unique())
selected = st.selectbox("Sélectionner un dossier", liste)

row = df[df[DOSSIER_COL] == selected].iloc[0]
idx = row.name

# ---------------------------------------------------------
# INFOS GÉNÉRALES
# ---------------------------------------------------------
st.subheader(f"📄 Dossier {selected}")

c1, c2, c3 = st.columns(3)
nom = c1.text_input("Nom", row.get("Nom", ""))
date_dossier = c2.date_input("Date du dossier", safe_date(row.get("Date")))

# ----------------- CATEGORIES / SOUS-CATEGORIES / VISA -----------------
st.subheader("🧩 Catégorisation")

colA, colB, colC = st.columns(3)

cat_list = sorted(visa_table["Categories"].dropna().unique().tolist())
categorie = colA.selectbox(
    "Catégorie",
    cat_list,
    index=cat_list.index(row.get("Categories")) if row.get("Categories") in cat_list else 0
)

souscat_list = get_souscats(categorie)
sous_categorie = colB.selectbox(
    "Sous-catégorie",
    souscat_list,
    index=souscat_list.index(row.get("Sous-categories")) if row.get("Sous-categories") in souscat_list else 0
)

visa_list = get_visas(sous_categorie)
visa = colC.selectbox(
    "Visa",
    visa_list,
    index=visa_list.index(row.get("Visa")) if row.get("Visa") in visa_list else 0
)

commentaire = st.text_area("📝 Commentaire", row.get("Commentaire", ""))

# ---------------------------------------------------------
# FACTURATION
# ---------------------------------------------------------
tarif_auto = get_tarif_for_visa(visa, date_dossier, tarifs)

st.subheader("💰 Facturation")

f1, f2 = st.columns(2)

honoraires = f1.number_input(
    "Montant honoraires (US $)",
    value=to_float(row.get("Montant honoraires (US $)", tarif_auto)),
    step=50.0
)

autres_frais = f2.number_input(
    "Autres frais (US $)",
    value=to_float(row.get("Autres frais (US $)", 0)),
    step=10.0
)

total_facture = honoraires + autres_frais
st.info(f"💵 Total facturé : **${total_facture:,.2f}**")

# ---------------------------------------------------------
# ACOMPTES
# ---------------------------------------------------------
st.subheader("🏦 Paiements")

ac_cols = st.columns(4)
acomptes = {}

for i in range(1, 5):
    acomptes[i] = ac_cols[i-1].number_input(
        f"Acompte {i}",
        value=to_float(row.get(f"Acompte {i}", 0)),
        step=50.0
    )

total_encaisse = sum(acomptes.values())
solde = total_facture - total_encaisse

st.success(f"💰 Total encaissé : ${total_encaisse:,.2f}")
st.warning(f"📉 Solde dû : ${solde:,.2f}")

# ---------------------------------------------------------
# ESCROW
# ---------------------------------------------------------
st.subheader("💼 Escrow")

escrow_actif = st.checkbox(
    "Escrow actif",
    value=normalize_bool(row.get("Escrow", False))
)

# ---------------------------------------------------------
# STATUTS
# ---------------------------------------------------------
st.subheader("📦 Statuts du dossier")

s1, s2, s3, s4, s5 = st.columns(5)

envoye = s1.checkbox("Dossier envoyé", normalize_bool(row.get("Dossier envoye")))
accepte = s2.checkbox("Dossier accepté", normalize_bool(row.get("Dossier accepte")))
refuse = s3.checkbox("Dossier refusé", normalize_bool(row.get("Dossier refuse")))
annule = s4.checkbox("Dossier annulé", normalize_bool(row.get("Dossier Annule")))
rfe = s5.checkbox("RFE", normalize_bool(row.get("RFE")))

# ---------------------------------------------------------
# SAUVEGARDE
# ---------------------------------------------------------
if st.button("💾 Enregistrer les modifications", type="primary"):

    df.loc[idx, "Nom"] = nom
    df.loc[idx, "Date"] = str(date_dossier)
    df.loc[idx, "Categories"] = categorie
    df.loc[idx, "Sous-categories"] = sous_categorie
    df.loc[idx, "Visa"] = visa
    df.loc[idx, "Commentaire"] = commentaire

    df.loc[idx, "Montant honoraires (US $)"] = honoraires
    df.loc[idx, "Autres frais (US $)"] = autres_frais

    for i in range(1, 5):
        df.loc[idx, f"Acompte {i}"] = acomptes[i]

    df = update_status_row(
        df,
        idx,
        envoye=envoye,
        accepte=accepte,
        refuse=refuse,
        annule=annule,
        rfe=rfe,
    )

    if escrow_actif:
        df.loc[idx, "Escrow"] = True
        df.loc[idx, "Escrow_a_reclamer"] = False
        df.loc[idx, "Escrow_reclame"] = False
    else:
        df.loc[idx, "Escrow"] = False

    db["clients"] = df.to_dict(orient="records")
    save_database(db)

    st.success("✔ Dossier mis à jour avec succès")
    st.rerun()
