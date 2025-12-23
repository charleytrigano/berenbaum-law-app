import streamlit as st
import pandas as pd
from datetime import datetime
from io import BytesIO

from utils.sidebar import render_sidebar
from backend.dropbox_utils import load_database

# ---------------------------------------------------------
# CONFIG PAGE
# ---------------------------------------------------------
st.set_page_config(
    page_title="📤 Export JSON → Excel",
    page_icon="📤",
    layout="wide",
)
render_sidebar()
st.title("📤 Export JSON → Excel multi-feuilles")

st.markdown("""
Cette page permet d’exporter la base JSON (Dropbox) au format **Excel (.xlsx)**  
avec **plusieurs feuilles** : Clients, Visa, Tarifs, Escrow, Compta, etc.

L’export est **horodaté** et ne contient **aucune signature**.
""")

# ---------------------------------------------------------
# CHARGEMENT BASE
# ---------------------------------------------------------
db = load_database()

# Helpers pour construire les feuilles
def as_df(data):
    if not data:
        return pd.DataFrame()
    if isinstance(data, dict):
        return pd.DataFrame([data])
    return pd.DataFrame(data)

sheets = {}

# Feuille Clients
sheets["Clients"] = as_df(db.get("clients", []))

# Feuille Visa (référentiel)
sheets["Visa"] = as_df(db.get("visa", []))

# Feuille Tarifs et historique de tarifs si présents
sheets["Tarifs"] = as_df(db.get("tarifs", []))
sheets["Tarifs_history"] = as_df(db.get("tarifs_history", []))

# Feuille Escrow (si vous en avez une structure dédiée)
sheets["Escrow"] = as_df(db.get("escrow", []))

# Feuille Compta (si existante)
sheets["Compta"] = as_df(db.get("compta", []))

# Historique générique (si existant)
sheets["History"] = as_df(db.get("history", []))

# Ne garder que les feuilles non vides
sheets = {
    name: df for name, df in sheets.items()
    if not df.empty
}

if not sheets:
    st.error("Aucune donnée exploitable trouvée dans la base JSON.")
    st.stop()

# ---------------------------------------------------------
# RÉCAP DES DONNÉES
# ---------------------------------------------------------
st.subheader("📊 Aperçu des feuilles disponibles")

recap_rows = []
for name, df in sheets.items():
    recap_rows.append({
        "Feuille": name,
        "Nombre de lignes": len(df),
        "Nombre de colonnes": len(df.columns),
    })

recap_df = pd.DataFrame(recap_rows)
st.dataframe(recap_df, use_container_width=True)

# ---------------------------------------------------------
# CHOIX DES FEUILLES À EXPORTER
# ---------------------------------------------------------
st.subheader("📄 Sélection des feuilles à inclure dans l’Excel")

all_sheet_names = list(sheets.keys())
selected_sheets = st.multiselect(
    "Choisissez les feuilles à exporter :",
    options=all_sheet_names,
    default=all_sheet_names,
)

if not selected_sheets:
    st.warning("Sélectionnez au moins une feuille pour pouvoir exporter.")
    st.stop()

# ---------------------------------------------------------
# GÉNÉRATION FICHIER EXCEL HORODATÉ
# ---------------------------------------------------------
st.subheader("⬇️ Export Excel")

st.markdown("""
L’export produit un fichier Excel avec :
- une feuille par type de données sélectionné,
- un nom de fichier horodaté, par exemple :  
  `export_berenbaum_20251223_1542.xlsx`
""")

if st.button("📥 Générer le fichier Excel", type="primary"):
    # Horodatage pour le nom du fichier
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    filename = f"export_berenbaum_{timestamp}.xlsx"

    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
        for name in selected_sheets:
            df_sheet = sheets[name]

            # Excel limite les noms d’onglets à 31 caractères
            sheet_name = name[:31]

            df_sheet.to_excel(
                writer,
                index=False,
                sheet_name=sheet_name,
            )

        # Pas de signature, pas de méta-feuille spéciale

    buffer.seek(0)

    st.download_button(
        label=f"⬇️ Télécharger {filename}",
        data=buffer.getvalue(),
        file_name=filename,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

    st.success("✔ Fichier Excel généré. Vous pouvez le télécharger ci-dessus.")
