
import streamlit as st
import pandas as pd

from utils.sidebar import render_sidebar
from backend.dropbox_utils import load_database, save_database

# =========================================================
# CONFIG
# =========================================================
st.set_page_config(
    page_title="📂 Fiche groupe de dossiers",
    page_icon="📂",
    layout="wide"
)
render_sidebar()
st.title("📂 Fiche groupe de dossiers (Parent & Fils)")

# =========================================================
# CHARGEMENT BASE
# =========================================================
db = load_database()
clients = db.get("clients", [])

if not clients:
    st.warning("Aucun dossier trouvé.")
    st.stop()

df = pd.DataFrame(clients)

# =========================================================
# NORMALISATION Dossier Parent / Index
# =========================================================
def split_dossier(n):
    s = str(n)
    if "-" in s:
        p, i = s.split("-", 1)
        return p, int(i)
    return s, 0

df[["Dossier Parent", "Dossier Index"]] = df["Dossier N"].apply(
    lambda x: pd.Series(split_dossier(x))
)

# =========================================================
# SÉLECTION DOSSIER PARENT
# =========================================================
parents = (
    df[df["Dossier Index"] == 0]["Dossier Parent"]
    .dropna()
    .unique()
    .tolist()
)
parents = sorted(parents, key=lambda x: int(x))

selected_parent = st.selectbox(
    "📂 Sélectionner un dossier parent",
    parents
)

group = (
    df[df["Dossier Parent"] == selected_parent]
    .sort_values("Dossier Index")
    .copy()
)

parent_row = group[group["Dossier Index"] == 0].iloc[0]

# =========================================================
# SECTION A — DOSSIER PARENT
# =========================================================
st.markdown("## 🧾 Dossier parent")

col1, col2, col3 = st.columns(3)

parent_nom = col1.text_input("Nom", parent_row.get("Nom", ""))
parent_cat = col2.text_input("Catégorie", parent_row.get("Categories", ""))
parent_souscat = col3.text_input("Sous-catégorie", parent_row.get("Sous-categories", ""))

col4, col5 = st.columns(2)
parent_visa = col4.text_input("Visa (parent)", parent_row.get("Visa", ""))
parent_commentaire = col5.text_area(
    "Commentaire global",
    parent_row.get("Commentaire", ""),
    height=80
)

st.markdown("---")

# =========================================================
# SECTION B — SOUS-DOSSIERS (ÉDITION COMPLÈTE)
# =========================================================
st.markdown("## 📑 Sous-dossiers")

edited_rows = []

for _, row in group.iterrows():

    idx = row.name
    is_parent = row["Dossier Index"] == 0

    with st.container(border=True):
        st.markdown(
            f"### 📄 Dossier {row['Dossier N']}"
            + (" (Parent)" if is_parent else "")
        )

        c1, c2, c3 = st.columns(3)

        nom = c1.text_input(
            "Nom",
            row.get("Nom", ""),
            key=f"nom_{idx}"
        )

        categories = c2.text_input(
            "Catégorie",
            row.get("Categories", ""),
            key=f"cat_{idx}"
        )

        souscat = c3.text_input(
            "Sous-catégorie",
            row.get("Sous-categories", ""),
            key=f"sous_{idx}"
        )

        c4, c5 = st.columns(2)

        visa = c4.text_input(
            "Visa",
            row.get("Visa", ""),
            key=f"visa_{idx}"
        )

        commentaire = c5.text_area(
            "Commentaire",
            row.get("Commentaire", ""),
            key=f"com_{idx}",
            height=60
        )

        st.markdown("**💰 Finances**")

        f1, f2, f3, f4 = st.columns(4)

        hon = f1.number_input(
            "Honoraires",
            value=float(row.get("Montant honoraires (US $)", 0)),
            key=f"hon_{idx}"
        )

        frais = f2.number_input(
            "Autres frais",
            value=float(row.get("Autres frais (US $)", 0)),
            key=f"frais_{idx}"
        )

        a1 = f3.number_input(
            "Acompte 1",
            value=float(row.get("Acompte 1", 0)),
            key=f"a1_{idx}"
        )

        a2 = f4.number_input(
            "Acompte 2",
            value=float(row.get("Acompte 2", 0)),
            key=f"a2_{idx}"
        )

        a3, a4 = st.columns(2)
        a3 = a3.number_input(
            "Acompte 3",
            value=float(row.get("Acompte 3", 0)),
            key=f"a3_{idx}"
        )

        a4 = a4.number_input(
            "Acompte 4",
            value=float(row.get("Acompte 4", 0)),
            key=f"a4_{idx}"
        )

        escrow = st.checkbox(
            "Escrow actif",
            value=bool(row.get("Escrow", False)),
            key=f"esc_{idx}"
        )

        escrow_a = st.checkbox(
            "Escrow à réclamer",
            value=bool(row.get("Escrow_a_reclamer", False)),
            key=f"esc_a_{idx}"
        )

        escrow_r = st.checkbox(
            "Escrow réclamé",
            value=bool(row.get("Escrow_reclame", False)),
            key=f"esc_r_{idx}"
        )

        edited_rows.append({
            "index": idx,
            "Nom": nom,
            "Categories": categories,
            "Sous-categories": souscat,
            "Visa": visa,
            "Commentaire": commentaire,
            "Montant honoraires (US $)": hon,
            "Autres frais (US $)": frais,
            "Acompte 1": a1,
            "Acompte 2": a2,
            "Acompte 3": a3,
            "Acompte 4": a4,
            "Escrow": escrow,
            "Escrow_a_reclamer": escrow_a,
            "Escrow_reclame": escrow_r,
        })

# =========================================================
# SECTION C — TOTAUX GROUPE
# =========================================================
st.markdown("## 📊 Totaux consolidés")

total_facture = (
    group["Montant honoraires (US $)"].sum()
    + group["Autres frais (US $)"].sum()
)
total_encaisse = (
    group["Acompte 1"].sum()
    + group["Acompte 2"].sum()
    + group["Acompte 3"].sum()
    + group["Acompte 4"].sum()
)

st.info(
    f"""
    **Total facturé :** ${total_facture:,.2f}  
    **Total encaissé :** ${total_encaisse:,.2f}  
    **Solde global :** ${total_facture - total_encaisse:,.2f}
    """
)

# =========================================================
# SAUVEGARDE
# =========================================================
if st.button("💾 Enregistrer tout le groupe", type="primary"):

    for r in edited_rows:
        for k, v in r.items():
            if k != "index":
                df.loc[r["index"], k] = v

    db["clients"] = df.to_dict(orient="records")
    save_database(db)

    st.success("✔ Groupe de dossiers enregistré avec succès.")
    st.rerun()