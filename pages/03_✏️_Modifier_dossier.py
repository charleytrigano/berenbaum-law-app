# pages/03_✏️_Modifier_dossier.py
import streamlit as st
import pandas as pd
from datetime import datetime

from utils.sidebar import render_sidebar
from backend.dropbox_utils import load_database, save_database
from utils.tarif_utils import get_tarif_for_visa
from utils.status_utils import normalize_status_columns, update_status_row, normalize_bool

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
tarifs = db.get("tarifs", [])
visa_ref = pd.DataFrame(db.get("visa", []))

if not clients:
    st.error("Aucun dossier trouvé.")
    st.stop()

df = pd.DataFrame(clients)

# Normalisation statuts
df = normalize_status_columns(df)

DOSSIER_COL = "Dossier N"
df[DOSSIER_COL] = df[DOSSIER_COL].astype(str)

# ---------------------------------------------------------
# HELPERS
# ---------------------------------------------------------
def safe_date(v):
    try:
        d = pd.to_datetime(v, errors="coerce")
        return None if pd.isna(d) else d.date()
    except Exception:
        return None

def date_to_str(d):
    if d is None:
        return ""
    try:
        return str(d)
    except Exception:
        return ""

def to_float(v):
    try:
        return float(v)
    except Exception:
        return 0.0

def to_text(v):
    return "" if v is None else str(v)

def get_souscats(df_visa, categorie):
    if df_visa.empty or "Categories" not in df_visa.columns or "Sous-categories" not in df_visa.columns:
        return []
    return sorted(
        df_visa[df_visa["Categories"] == categorie]["Sous-categories"]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

def get_visas(df_visa, categorie, souscat):
    if df_visa.empty or "Categories" not in df_visa.columns or "Sous-categories" not in df_visa.columns or "Visa" not in df_visa.columns:
        return []
    return sorted(
        df_visa[(df_visa["Categories"] == categorie) & (df_visa["Sous-categories"] == souscat)]["Visa"]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

# ---------------------------------------------------------
# SÉLECTION DOSSIER (avec recherche Nom ou Dossier N)
# ---------------------------------------------------------
st.subheader("🔎 Recherche dossier")

search = st.text_input("Rechercher par Dossier N ou Nom", value="").strip().lower()

df_search = df.copy()
df_search["Nom"] = df_search.get("Nom", "").astype(str)
df_search["_label"] = df_search[DOSSIER_COL].astype(str) + " — " + df_search["Nom"].astype(str)

if search:
    mask = df_search[DOSSIER_COL].astype(str).str.lower().str.contains(search) | df_search["Nom"].astype(str).str.lower().str.contains(search)
    df_search = df_search[mask]

liste_labels = df_search["_label"].dropna().astype(str).unique().tolist()
liste_labels = sorted(liste_labels)

if not liste_labels:
    st.warning("Aucun dossier ne correspond à la recherche.")
    st.stop()

selected_label = st.selectbox("Sélectionner un dossier", liste_labels)
selected = selected_label.split(" — ", 1)[0].strip()

row = df[df[DOSSIER_COL] == selected].iloc[0]
idx = row.name

# ---------------------------------------------------------
# INFORMATIONS GÉNÉRALES
# ---------------------------------------------------------
st.subheader(f"📄 Dossier {selected}")

c1, c2, c3 = st.columns(3)
nom = c1.text_input("Nom", row.get("Nom", ""))
date_dossier = c2.date_input("Date du dossier", safe_date(row.get("Date")))
# Visa (sera alimenté par selectbox plus bas)
visa_current = to_text(row.get("Visa", ""))

# ---------------------------------------------------------
# CATÉGORISATION (selectbox réactivés)
# ---------------------------------------------------------
st.subheader("🧩 Catégorisation")

visa_ref = visa_ref.copy()
for col in ["Categories", "Sous-categories", "Visa"]:
    if col in visa_ref.columns:
        visa_ref[col] = visa_ref[col].astype(str)

cat_list = ["Choisir..."]
if not visa_ref.empty and "Categories" in visa_ref.columns:
    cat_list += sorted(visa_ref["Categories"].dropna().astype(str).unique().tolist())

current_cat = to_text(row.get("Categories", ""))
if current_cat and current_cat not in cat_list:
    cat_list.append(current_cat)
cat_list = ["Choisir..."] + sorted([c for c in cat_list if c != "Choisir..."])

colA, colB, colC = st.columns(3)
categorie = colA.selectbox(
    "Catégorie",
    options=cat_list,
    index=(cat_list.index(current_cat) if current_cat in cat_list else 0),
)

souscats = ["Choisir..."]
if categorie != "Choisir...":
    souscats += get_souscats(visa_ref, categorie)

current_souscat = to_text(row.get("Sous-categories", ""))
if current_souscat and current_souscat not in souscats:
    souscats.append(current_souscat)
souscats = ["Choisir..."] + sorted([s for s in souscats if s != "Choisir..."])

sous_categorie = colB.selectbox(
    "Sous-catégorie",
    options=souscats,
    index=(souscats.index(current_souscat) if current_souscat in souscats else 0),
)

visa_list = ["Choisir..."]
if categorie != "Choisir..." and sous_categorie != "Choisir...":
    visa_list += get_visas(visa_ref, categorie, sous_categorie)

# IMPORTANT : le visa peut être différent même si cat/sous-cat ne matchent pas (compat)
if visa_current and visa_current not in visa_list:
    visa_list.append(visa_current)
visa_list = ["Choisir..."] + sorted([v for v in visa_list if v != "Choisir..."])

visa = colC.selectbox(
    "Visa",
    options=visa_list,
    index=(visa_list.index(visa_current) if visa_current in visa_list else 0),
)

commentaire = st.text_area("📝 Commentaire", row.get("Commentaire", ""))

# ---------------------------------------------------------
# FACTURATION (Montant honoraires à la place de “Tarif visa appliqué”)
# ---------------------------------------------------------
st.subheader("💰 Facturation")

f1, f2, f3 = st.columns(3)

montant_honoraires = f1.number_input(
    "Montant honoraires (US $)",
    value=to_float(row.get("Montant honoraires (US $)", 0)),
    step=50.0
)

autres_frais = f2.number_input(
    "Autres frais (US $)",
    value=to_float(row.get("Autres frais (US $)", 0)),
    step=10.0
)

total_facture = montant_honoraires + autres_frais
f3.number_input("Total facturé", value=float(total_facture), disabled=True)

# ---------------------------------------------------------
# ACOMPTES + DATES + MODES (AJOUT SANS CASSER)
# ---------------------------------------------------------
st.subheader("🏦 Paiements (Acomptes)")

modes = ["", "Chèque", "CB", "Virement", "Venmo"]

acomptes = {}
dates_ac = {}
modes_ac = {}

for i in range(1, 5):
    st.markdown(f"### Acompte {i}")
    colM1, colM2, colM3 = st.columns(3)

    # Montant
    acomptes[i] = colM1.number_input(
        f"Montant Acompte {i}",
        value=to_float(row.get(f"Acompte {i}", 0)),
        step=50.0,
        key=f"ac_montant_{i}_{selected}",
    )

    # Date de paiement (colonne attendue: "Date Acompte i")
    dates_ac[i] = colM2.date_input(
        f"Date Acompte {i}",
        value=safe_date(row.get(f"Date Acompte {i}", "")),
        key=f"ac_date_{i}_{selected}",
    )

    # Mode de règlement (priorité à "Mode Acompte i", sinon fallback sur "mode de paiement")
    current_mode = to_text(row.get(f"Mode Acompte {i}", ""))
    if not current_mode and i == 1:
        current_mode = to_text(row.get("mode de paiement", ""))

    idx_mode = modes.index(current_mode) if current_mode in modes else 0
    modes_ac[i] = colM3.selectbox(
        f"Mode Acompte {i}",
        options=modes,
        index=idx_mode,
        key=f"ac_mode_{i}_{selected}",
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
# STATUTS + DATES (AJOUT SANS CASSER)
# ---------------------------------------------------------
st.subheader("📦 Statuts du dossier")

s1, s2, s3, s4, s5 = st.columns(5)
envoye = s1.checkbox("Dossier envoyé", normalize_bool(row.get("Dossier envoye")))
accepte = s2.checkbox("Dossier accepté", normalize_bool(row.get("Dossier accepte")))
refuse = s3.checkbox("Dossier refusé", normalize_bool(row.get("Dossier refuse")))
annule = s4.checkbox("Dossier annulé", normalize_bool(row.get("Dossier Annule")))
rfe = s5.checkbox("RFE", normalize_bool(row.get("RFE")))

d1, d2, d3, d4, d5 = st.columns(5)
date_envoye = d1.date_input("Date dossier envoyé", safe_date(row.get("Date envoi")))
date_accepte = d2.date_input("Date dossier accepté", safe_date(row.get("Date acceptation")))
date_refuse = d3.date_input("Date dossier refusé", safe_date(row.get("Date refus")))
date_annule = d4.date_input("Date dossier annulé", safe_date(row.get("Date annulation")))
date_rfe = d5.date_input("Date RFE", safe_date(row.get("Date reclamation")))

# ---------------------------------------------------------
# SAUVEGARDE
# ---------------------------------------------------------
if st.button("💾 Enregistrer les modifications", type="primary"):

    # Infos générales
    df.loc[idx, "Nom"] = nom
    df.loc[idx, "Date"] = str(date_dossier)
    df.loc[idx, "Categories"] = "" if categorie == "Choisir..." else categorie
    df.loc[idx, "Sous-categories"] = "" if sous_categorie == "Choisir..." else sous_categorie
    df.loc[idx, "Visa"] = "" if visa == "Choisir..." else visa
    df.loc[idx, "Commentaire"] = commentaire

    # Facturation
    df.loc[idx, "Montant honoraires (US $)"] = float(montant_honoraires)
    df.loc[idx, "Autres frais (US $)"] = float(autres_frais)

    # Acomptes + dates + modes (AJOUT)
    for i in range(1, 5):
        df.loc[idx, f"Acompte {i}"] = float(acomptes[i])

        # Date
        df.loc[idx, f"Date Acompte {i}"] = date_to_str(dates_ac[i])

        # Mode par acompte
        df.loc[idx, f"Mode Acompte {i}"] = modes_ac[i]

    # Compat: garde aussi le champ historique "mode de paiement" (lié à Acompte 1)
    df.loc[idx, "mode de paiement"] = modes_ac[1]

    # Statuts (centralisé)
    df = update_status_row(
        df,
        idx,
        envoye=envoye,
        accepte=accepte,
        refuse=refuse,
        annule=annule,
        rfe=rfe,
    )

    # Dates statuts (AJOUT)
    df.loc[idx, "Date envoi"] = date_to_str(date_envoye)
    df.loc[idx, "Date acceptation"] = date_to_str(date_accepte)
    df.loc[idx, "Date refus"] = date_to_str(date_refuse)
    df.loc[idx, "Date annulation"] = date_to_str(date_annule)
    df.loc[idx, "Date reclamation"] = date_to_str(date_rfe)

    # Escrow (règle claire)
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
