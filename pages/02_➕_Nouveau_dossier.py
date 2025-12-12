import streamlit as st
import pandas as pd
from utils.sidebar import render_sidebar
from backend.dropbox_utils import load_database, save_database

# ---------------------------------------------------------
# CONFIG
# ---------------------------------------------------------
st.set_page_config(page_title="➕ Nouveau dossier", page_icon="➕", layout="wide")
render_sidebar()
st.title("➕ Nouveau dossier")

# ---------------------------------------------------------
# LOAD DB
# ---------------------------------------------------------
db = load_database()
clients = db.get("clients", [])
visa_raw = pd.DataFrame(db.get("visa", []))

# ---------------------------------------------------------
# NUMÉRO DOSSIER (support xxxxx-1, xxxxx-2)
# ---------------------------------------------------------
def next_dossier_number():
    nums = []
    for c in clients:
        try:
            base = str(c.get("Dossier N")).split("-")[0]
            nums.append(int(base))
        except:
            pass
    return max(nums) + 1 if nums else 13000

base_id = next_dossier_number()

st.subheader("📄 Identification")

colI1, colI2 = st.columns(2)
parent_id = colI1.text_input("Dossier parent", value=str(base_id))
suffix = colI2.text_input("Suffixe (ex: -1, -2)", value="")

dossier_id = f"{parent_id}{suffix}"

# ---------------------------------------------------------
# INFOS CLIENT
# ---------------------------------------------------------
st.subheader("👤 Client")

col1, col2, col3 = st.columns(3)
nom = col1.text_input("Nom")
date_dossier = col2.date_input("Date de création")
visa_cat = col3.selectbox(
    "Catégorie",
    [""] + sorted(visa_raw["Categories"].dropna().unique().tolist())
)

souscats = (
    visa_raw[visa_raw["Categories"] == visa_cat]["Sous-categories"]
    .dropna().unique().tolist()
    if visa_cat else []
)

sous_categorie = st.selectbox("Sous-catégorie", [""] + souscats)

visas = (
    visa_raw[visa_raw["Sous-categories"] == sous_categorie]["Visa"]
    .dropna().unique().tolist()
    if sous_categorie else []
)

visa = st.selectbox("Visa", [""] + visas)

# ---------------------------------------------------------
# FACTURATION
# ---------------------------------------------------------
st.subheader("💰 Facturation")

colF1, colF2, colF3 = st.columns(3)
hon = colF1.number_input("Montant honoraires (US $)", 0.0)
frais = colF2.number_input("Autres frais (US $)", 0.0)
colF3.number_input("Total facturé", hon + frais, disabled=True)

# ---------------------------------------------------------
# ACOMPTES COMPLETS
# ---------------------------------------------------------
st.subheader("🏦 Paiements")

modes = ["", "Chèque", "CB", "Virement", "Venmo"]

acomptes = {}
for i in range(1, 5):
    st.markdown(f"### Acompte {i}")
    c1, c2, c3 = st.columns(3)
    acomptes[f"Acompte {i}"] = c1.number_input(f"Montant Acompte {i}", 0.0)
    acomptes[f"Date Acompte {i}"] = c2.date_input(
        f"Date Acompte {i}", value=None
    )
    acomptes[f"Mode Acompte {i}"] = c3.selectbox(
        f"Mode Acompte {i}", modes, key=f"mode_{i}"
    )

# ---------------------------------------------------------
# ESCROW
# ---------------------------------------------------------
escrow = st.checkbox("Mettre le dossier en Escrow")

commentaire = st.text_area("📝 Commentaire")

# ---------------------------------------------------------
# SAVE
# ---------------------------------------------------------
if st.button("💾 Enregistrer le dossier", type="primary"):

    if not nom.strip():
        st.error("Nom obligatoire")
        st.stop()

    entry = {
        "Dossier N": dossier_id,
        "Nom": nom,
        "Date": str(date_dossier),
        "Categories": visa_cat,
        "Sous-categories": sous_categorie,
        "Visa": visa,
        "Montant honoraires (US $)": hon,
        "Autres frais (US $)": frais,
        "Escrow": bool(escrow),
        "Escrow_a_reclamer": False,
        "Escrow_reclame": False,
        "Dossier envoye": False,
        "Dossier accepte": False,
        "Dossier refuse": False,
        "Dossier Annule": False,
        "RFE": False,
        "Commentaire": commentaire,
    }

    for k, v in acomptes.items():
        if "Date" in k and v:
            entry[k] = str(v)
        else:
            entry[k] = v or ""

    clients.append(entry)
    db["clients"] = clients
    save_database(db)

    st.success(f"✔ Dossier {dossier_id} créé")
    st.balloons()