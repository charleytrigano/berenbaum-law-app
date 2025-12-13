import streamlit as st
import pandas as pd
from datetime import date

from utils.sidebar import render_sidebar
from backend.dropbox_utils import load_database, save_database
from utils.tarif_utils import get_tarif_for_visa

# ---------------------------------------------------------
st.set_page_config(page_title="➕ Nouveau dossier", page_icon="➕", layout="wide")
render_sidebar()
st.title("➕ Nouveau dossier")

# ---------------------------------------------------------
db = load_database()
clients = db.get("clients", [])
tarifs = db.get("tarifs", [])
visa_df = pd.DataFrame(db.get("visa", []))

# ---------------------------------------------------------
def next_dossier_num():
    nums = []
    for c in clients:
        try:
            nums.append(int(str(c.get("Dossier N")).split("-")[0]))
        except:
            pass
    return max(nums) + 1 if nums else 13000

dossier_n = next_dossier_num()

# ---------------------------------------------------------
st.subheader("📄 Informations générales")

c1, c2, c3 = st.columns(3)
c1.text_input("Dossier N", value=str(dossier_n), disabled=True)
nom = c2.text_input("Nom")
date_dossier = c3.date_input("Date du dossier", value=date.today())

# ---------------------------------------------------------
st.subheader("🧩 Catégorisation")

cat = st.selectbox("Catégorie", sorted(visa_df["Categories"].dropna().unique()))
sous = st.selectbox(
    "Sous-catégorie",
    sorted(visa_df[visa_df["Categories"] == cat]["Sous-categories"].dropna().unique())
)
visa = st.selectbox(
    "Visa",
    sorted(visa_df[visa_df["Sous-categories"] == sous]["Visa"].dropna().unique())
)

# ---------------------------------------------------------
# TARIF VISA
# ---------------------------------------------------------
tarif_auto = get_tarif_for_visa(visa, date_dossier, tarifs)

st.subheader("💰 Facturation")

colT1, colT2 = st.columns(2)
tarif_applique = colT1.number_input(
    "Tarif Visa appliqué (modifiable)",
    value=float(tarif_auto),
    step=50.0
)

tarif_modifie = colT2.checkbox(
    "Tarif modifié manuellement",
    value=(tarif_applique != tarif_auto)
)

autres_frais = st.number_input("Autres frais", 0.0, step=10.0)
total = tarif_applique + autres_frais
st.info(f"💵 Total facturé : **${total:,.2f}**")

# ---------------------------------------------------------
commentaire = st.text_area("📝 Commentaire")

# ---------------------------------------------------------
if st.button("💾 Enregistrer le dossier", type="primary"):

    new = {
        "Dossier N": dossier_n,
        "Nom": nom,
        "Date": str(date_dossier),
        "Categories": cat,
        "Sous-categories": sous,
        "Visa": visa,

        "Tarif visa applique": tarif_applique,
        "Tarif modifie manuellement": bool(tarif_modifie),

        "Montant honoraires (US $)": tarif_applique,
        "Autres frais (US $)": autres_frais,

        "Acompte 1": 0,
        "Acompte 2": 0,
        "Acompte 3": 0,
        "Acompte 4": 0,

        "Escrow": False,
        "Escrow_a_reclamer": False,
        "Escrow_reclame": False,

        "Dossier envoye": False,
        "Dossier accepte": False,
        "Dossier refuse": False,
        "Dossier Annule": False,
        "RFE": False,

        "Commentaire": commentaire,
    }

    clients.append(new)
    db["clients"] = clients
    save_database(db)

    st.success("✔ Dossier créé avec succès")
    st.balloons()