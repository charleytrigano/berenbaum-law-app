import streamlit as st
from utils.sidebar import render_sidebar
render_sidebar()

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
# 🔹 Normalisation booléens
# ---------------------------------------------------------
def normalize_bool(x):
    if isinstance(x, bool):
        return x
    if str(x).lower() in ["true", "1", "1.0", "yes", "oui"]:
        return True
    return False

for col in ["Dossier envoye", "Escrow", "Escrow_a_reclamer", "Escrow_reclame"]:
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
    except:
        return 0.0

def safe_date(v):
    try:
        d = pd.to_datetime(v, errors="coerce")
        return None if pd.isna(d) else d.date()
    except:
        return None


# ---------------------------------------------------------
# 🔽 LISTES Catégorie → Sous-catégorie → Visa
# ---------------------------------------------------------

all_categories = sorted([c for c in df["Categories"].dropna().unique() if c != ""])
all_sous = sorted([s for s in df["Sous-categories"].dropna().unique() if s != ""])
all_visas = sorted([v for v in df["Visa"].dropna().unique() if v != ""])

current_cat = dossier.get("Categories", "")
current_sous = dossier.get("Sous-categories", "")
current_visa = dossier.get("Visa", "")

col1, col2, col3 = st.columns(3)

# 1️⃣ Catégorie
categorie = col1.selectbox(
    "Catégorie",
    [""] + all_categories,
    index=([""] + all_categories).index(current_cat) if current_cat in all_categories else 0
)

# 2️⃣ Sous-catégories dépendantes
if categorie:
    sous_list = sorted(df[df["Categories"] == categorie]["Sous-categories"].dropna().unique())
else:
    sous_list = all_sous

sous_categorie = col2.selectbox(
    "Sous-catégorie",
    [""] + sous_list,
    index=([""] + sous_list).index(current_sous) if current_sous in sous_list else 0
)

# 3️⃣ Visa dépendant
if sous_categorie:
    visa_list = sorted(df[df["Sous-categories"] == sous_categorie]["Visa"].dropna().unique())
else:
    visa_list = all_visas

visa_choice = col3.selectbox(
    "Visa",
    [""] + visa_list,
    index=([""] + visa_list).index(current_visa) if current_visa in visa_list else 0
)


# ---------------------------------------------------------
# 🔹 Infos générales
# ---------------------------------------------------------
st.subheader(f"Dossier n° {selected}")

colA, colB = st.columns(2)
nom = colA.text_input("Nom", dossier.get("Nom", ""))
date_dossier = colB.date_input("Date", safe_date(dossier.get("Date")))

commentaire = st.text_area("📝 Commentaire", dossier.get("Commentaire", ""))


# ---------------------------------------------------------
# Facturation
# ---------------------------------------------------------
st.subheader("💵 Facturation")

colF1, colF2, colF3 = st.columns(3)

honoraires = colF1.number_input(
    "Montant honoraires (US $)",
    value=to_float(dossier.get("Montant honoraires (US $)", 0))
)
frais = colF2.number_input(
    "Autres frais (US $)",
    value=to_float(dossier.get("Autres frais (US $)", 0))
)
colF3.number_input("Total facturé", value=honoraires + frais, disabled=True)


# ---------------------------------------------------------
# Acomptes + modes + dates
# ---------------------------------------------------------
st.subheader("🏦 Acomptes et modes de règlement")

modes = ["", "Chèque", "CB", "Virement", "Venmo"]

ac_inputs, mode_inputs, date_inputs = {}, {}, {}

for i in range(1, 4 + 1):
    st.markdown(f"### Acompte {i}")
    colA, colM, colD = st.columns(3)

    ac_inputs[i] = colA.number_input(
        f"Montant Acompte {i}",
        value=to_float(dossier.get(f"Acompte {i}", 0))
    )

    mode_inputs[i] = colM.selectbox(
        f"Mode Acompte {i}",
        options=modes,
        index=modes.index(dossier.get(f"Mode Acompte {i}", ""))
        if dossier.get(f"Mode Acompte {i}", "") in modes else 0
    )

    date_inputs[i] = colD.date_input(
        f"Date Paiement {i}",
        value=safe_date(dossier.get(f"Date Paiement {i}"))
    )


# ---------------------------------------------------------
# Escrow
# ---------------------------------------------------------
st.subheader("💰 Escrow")
escrow_flag = st.checkbox("Escrow actif ?", value=normalize_bool(dossier.get("Escrow", False)))


# ---------------------------------------------------------
# Statuts
# ---------------------------------------------------------
st.subheader("📦 Statuts du dossier")

colS1, colS2, colS3, colS4, colS5 = st.columns(5)

envoye = colS1.checkbox("Dossier envoyé", normalize_bool(dossier.get("Dossier envoye", False)))
accepte = colS2.checkbox("Dossier accepté", normalize_bool(dossier.get("Dossier accepte", False)))
refuse = colS3.checkbox("Dossier refusé", normalize_bool(dossier.get("Dossier refuse", False)))
annule = colS4.checkbox("Dossier annulé", normalize_bool(dossier.get("Dossier Annule", False)))
rfe = colS5.checkbox("RFE", normalize_bool(dossier.get("RFE", False)))

colD1, colD2, colD3, colD4, colD5 = st.columns(5)
date_envoye = colD1.date_input("Date envoi", safe_date(dossier.get("Date envoi")))
date_accepte = colD2.date_input("Date acceptation", safe_date(dossier.get("Date acceptation")))
date_refuse = colD3.date_input("Date refus", safe_date(dossier.get("Date refus")))
date_annule = colD4.date_input("Date annulation", safe_date(dossier.get("Date annulation")))
date_rfe = colD5.date_input("Date RFE", safe_date(dossier.get("Date reclamation")))


# ---------------------------------------------------------
# Sauvegarde
# ---------------------------------------------------------
if st.button("💾 Enregistrer les modifications", type="primary"):

    idx = df[df[DOSSIER_COL] == selected].index[0]

    # Infos générales
    df.loc[idx, "Nom"] = nom
    df.loc[idx, "Date"] = date_dossier
    df.loc[idx, "Commentaire"] = commentaire

    df.loc[idx, "Categories"] = categorie
    df.loc[idx, "Sous-categories"] = sous_categorie
    df.loc[idx, "Visa"] = visa_choice

    df.loc[idx, "Montant honoraires (US $)"] = honoraires
    df.loc[idx, "Autres frais (US $)"] = frais

    # Acomptes
    for i in range(1, 5):
        df.loc[idx, f"Acompte {i}"] = ac_inputs[i]
        df.loc[idx, f"Mode Acompte {i}"] = mode_inputs[i]
        df.loc[idx, f"Date Paiement {i}"] = date_inputs[i]

    # Statuts
    df.loc[idx, "Dossier envoye"] = bool(envoye)
    df.loc[idx, "Dossier accepte"] = bool(accepte)
    df.loc[idx, "Dossier refuse"] = bool(refuse)
    df.loc[idx, "Dossier Annule"] = bool(annule)
    df.loc[idx, "RFE"] = bool(rfe)

    df.loc[idx, "Date envoi"] = date_envoye
    df.loc[idx, "Date acceptation"] = date_accepte
    df.loc[idx, "Date refus"] = date_refuse
    df.loc[idx, "Date annulation"] = date_annule
    df.loc[idx, "Date reclamation"] = date_rfe

    # Escrow
    if envoye:
        df.loc[idx, "Escrow"] = False
        df.loc[idx, "Escrow_a_reclamer"] = True
        df.loc[idx, "Escrow_reclame"] = False
    else:
        df.loc[idx, "Escrow"] = bool(escrow_flag)

    # SAVE
    db["clients"] = df.to_dict(orient="records")
    save_database(db)

    st.success("✔ Dossier mis à jour avec succès !")
    st.rerun()
