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
# CHARGEMENT BASE
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
    except Exception:
        return None


def to_float(v):
    try:
        return float(v)
    except Exception:
        return 0.0


def get_souscats(cat):
    if visa_table.empty:
        return []
    return (
        visa_table[visa_table["Categories"] == cat]["Sous-categories"]
        .dropna()
        .unique()
        .tolist()
    )


def get_visas(souscat):
    if visa_table.empty:
        return []
    return (
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
# INFORMATIONS GÉNÉRALES
# ---------------------------------------------------------
st.subheader(f"📄 Dossier {selected}")

c1, c2, c3 = st.columns(3)
nom = c1.text_input("Nom", row.get("Nom", ""))
date_dossier = c2.date_input("Date du dossier", safe_date(row.get("Date")))

# ----------------- CATEGORIES / SOUS-CATEGORIES / VISA -----------------
st.subheader("🧩 Catégorisation")

colA, colB, colC = st.columns(3)

cat_list = sorted(visa_table["Categories"].dropna().unique().tolist()) if not visa_table.empty else []
if not cat_list:
    # fallback texte si pas de table visa
    categorie = colA.text_input("Catégorie", row.get("Categories", ""))
    sous_categorie = colB.text_input("Sous-catégorie", row.get("Sous-categories", ""))
    visa = colC.text_input("Visa", row.get("Visa", ""))
else:
    # Catégorie
    current_cat = row.get("Categories", "")
    if current_cat not in cat_list and cat_list:
        current_cat = cat_list[0]

    categorie = colA.selectbox(
        "Catégorie",
        cat_list,
        index=cat_list.index(current_cat) if current_cat in cat_list else 0,
    )

    # Sous-catégorie dépendante
    souscat_list = get_souscats(categorie)
    current_sous = row.get("Sous-categories", "")
    if current_sous not in souscat_list and souscat_list:
        current_sous = souscat_list[0]

    sous_categorie = colB.selectbox(
        "Sous-catégorie",
        souscat_list,
        index=souscat_list.index(current_sous) if current_sous in souscat_list else 0,
    )

    # Visa dépendant
    visa_list = get_visas(sous_categorie)
    current_visa = row.get("Visa", "")
    if current_visa not in visa_list and visa_list:
        current_visa = visa_list[0]

    visa = colC.selectbox(
        "Visa",
        visa_list,
        index=visa_list.index(current_visa) if current_visa in visa_list else 0,
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
    step=50.0,
)

autres_frais = f2.number_input(
    "Autres frais (US $)",
    value=to_float(row.get("Autres frais (US $)", 0)),
    step=10.0,
)

total_facture = honoraires + autres_frais
st.info(f"💵 Total facturé : **${total_facture:,.2f}**")

# ---------------------------------------------------------
# ACOMPTES + DATES + MODES
# ---------------------------------------------------------
st.subheader("🏦 Paiements")

modes_reglement = ["", "Chèque", "CB", "Virement", "Venmo"]

acomptes = {}
dates_acompte = {}
modes_acompte = {}

for i in range(1, 5):
    st.markdown(f"### Acompte {i}")
    colA, colD, colM = st.columns(3)

    acomptes[i] = colA.number_input(
        f"Montant Acompte {i}",
        value=to_float(row.get(f"Acompte {i}", 0)),
        step=50.0,
    )

    dates_acompte[i] = colD.date_input(
        f"Date Acompte {i}",
        value=safe_date(row.get(f"Date Acompte {i}", "")),
    )

    current_mode = row.get(f"Mode Acompte {i}", "")
    if current_mode not in modes_reglement:
        current_mode = ""
    modes_acompte[i] = colM.selectbox(
        f"Mode Acompte {i}",
        options=modes_reglement,
        index=modes_reglement.index(current_mode),
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
    value=normalize_bool(row.get("Escrow", False)),
)

# ---------------------------------------------------------
# STATUTS + DATES
# ---------------------------------------------------------
st.subheader("📦 Statuts du dossier")

s1, s2, s3, s4, s5 = st.columns(5)

envoye = s1.checkbox("Dossier envoyé", normalize_bool(row.get("Dossier envoye")))
accepte = s2.checkbox("Dossier accepté", normalize_bool(row.get("Dossier accepte")))
refuse = s3.checkbox("Dossier refusé", normalize_bool(row.get("Dossier refuse")))
annule = s4.checkbox("Dossier annulé", normalize_bool(row.get("Dossier Annule")))
rfe = s5.checkbox("RFE", normalize_bool(row.get("RFE")))

d1, d2, d3, d4, d5 = st.columns(5)

date_envoye = d1.date_input("Date envoi", safe_date(row.get("Date envoi", "")))
date_accepte = d2.date_input(
    "Date acceptation", safe_date(row.get("Date acceptation", ""))
)
date_refuse = d3.date_input("Date refus", safe_date(row.get("Date refus", "")))
date_annule = d4.date_input(
    "Date annulation", safe_date(row.get("Date annulation", ""))
)
date_rfe = d5.date_input(
    "Date RFE", safe_date(row.get("Date reclamation", ""))
)

# ---------------------------------------------------------
# SAUVEGARDE
# ---------------------------------------------------------
if st.button("💾 Enregistrer les modifications", type="primary"):

    # Infos générales
    df.loc[idx, "Nom"] = nom
    df.loc[idx, "Date"] = str(date_dossier)
    df.loc[idx, "Visa"] = visa
    df.loc[idx, "Categories"] = categorie
    df.loc[idx, "Sous-categories"] = sous_categorie
    df.loc[idx, "Commentaire"] = commentaire

    # Facturation
    df.loc[idx, "Montant honoraires (US $)"] = honoraires
    df.loc[idx, "Autres frais (US $)"] = autres_frais

    # Acomptes + dates + modes
    for i in range(1, 5):
        df.loc[idx, f"Acompte {i}"] = acomptes[i]
        df.loc[idx, f"Date Acompte {i}"] = (
            str(dates_acompte[i]) if dates_acompte[i] else ""
        )
        df.loc[idx, f"Mode Acompte {i}"] = modes_acompte[i]

    # Statuts (via helper centralisé)
    df = update_status_row(
        df,
        idx,
        envoye=envoye,
        accepte=accepte,
        refuse=refuse,
        annule=annule,
        rfe=rfe,
    )

    # Dates des statuts
    df.loc[idx, "Date envoi"] = str(date_envoye) if date_envoye else ""
    df.loc[idx, "Date acceptation"] = str(date_accepte) if date_accepte else ""
    df.loc[idx, "Date refus"] = str(date_refuse) if date_refuse else ""
    df.loc[idx, "Date annulation"] = str(date_annule) if date_annule else ""
    df.loc[idx, "Date reclamation"] = str(date_rfe) if date_rfe else ""

    # Escrow (règle cohérente)
    if escrow_actif:
        df.loc[idx, "Escrow"] = True
        df.loc[idx, "Escrow_a_reclamer"] = False
        df.loc[idx, "Escrow_reclame"] = False
    else:
        df.loc[idx, "Escrow"] = False

    # Sauvegarde
    db["clients"] = df.to_dict(orient="records")
    save_database(db)

    st.success("✔ Dossier mis à jour avec succès")
    st.rerun()
