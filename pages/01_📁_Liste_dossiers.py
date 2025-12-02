import streamlit as st
import pandas as pd
import io
import pandas as pd
from components.export_pdf import generate_pdf_from_dataframe

from backend.dropbox_utils import load_database

st.set_page_config(page_title="Liste des dossiers", page_icon="📁", layout="wide")

st.title("📁 Liste des dossiers")
st.write("Visualisation, recherche et analyse filtrée des dossiers clients.")

# --------------------------------------------------------
# Charger la base
# --------------------------------------------------------
db = load_database()
clients = db.get("clients", [])
visa_table = db.get("visa", [])

if not clients:
    st.warning("Aucun dossier trouvé.")
    st.stop()

# Convertir en DataFrame
df = pd.DataFrame(clients)

# Normaliser colonnes financières
for col in [
    "Montant honoraires (US $)",
    "Autres frais (US $)",
    "Acompte 1",
    "Acompte 2",
    "Acompte 3",
    "Acompte 4"
]:
    if col not in df.columns:
        df[col] = 0
    df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

# Totaux
df["Total facturé"] = df["Montant honoraires (US $)"] + df["Autres frais (US $)"]
df["Montant encaissé"] = (
    df["Acompte 1"] + df["Acompte 2"] + df["Acompte 3"] + df["Acompte 4"]
)
df["Solde"] = df["Total facturé"] - df["Montant encaissé"]

# --------------------------------------------------------
# KPI
# --------------------------------------------------------
st.subheader("📌 Indicateurs")

c1, c2, c3, c4, c5, c6 = st.columns(6)

c1.metric("Total", len(df))
c2.metric("Total facturé", f"${df['Total facturé'].sum():,.2f}")
c3.metric("Honoraires", f"${df['Montant honoraires (US $)'].sum():,.2f}")
c4.metric("Autres frais", f"${df['Autres frais (US $)'].sum():,.2f}")
c5.metric("Montant encaissé", f"${df['Montant encaissé'].sum():,.2f}")
c6.metric("Solde", f"${df['Solde'].sum():,.2f}")

st.markdown("---")

# --------------------------------------------------------
# Filtres (version simple pour l'instant)
# --------------------------------------------------------
st.subheader("🎛️ Filtres")

cat = st.selectbox("Catégorie", ["Toutes"] + sorted(df["Catégories"].dropna().unique()))
souscat = st.selectbox("Sous-catégorie", ["Toutes"] + sorted(df["Sous-catégories"].dropna().unique()))
visa = st.selectbox("Visa", ["Tous"] + sorted(df["Visa"].dropna().unique()))

# Application
filtered = df.copy()

if cat != "Toutes":
    filtered = filtered[filtered["Catégories"] == cat]

if souscat != "Toutes":
    filtered = filtered[filtered["Sous-catégories"] == souscat]

if visa != "Tous":
    filtered = filtered[filtered["Visa"] == visa]

# --------------------------------------------------------
# TABLEAU
# --------------------------------------------------------
st.subheader("📋 Dossiers")

colonnes = [
    "Dossier N",
    "Nom",
    "Catégories",
    "Sous-catégories",
    "Visa",
    "Montant honoraires (US $)",
    "Autres frais (US $)",
    "Total facturé",
    "Montant encaissé",
    "Solde",
    "Date"
]
colonnes = [c for c in colonnes if c in filtered.columns]

st.dataframe(filtered[colonnes], use_container_width=True, height=600)

from components.export_pdf import generate_pdf_from_dataframe

st.markdown("### 📤 Export")

col_exp1, col_exp2, col_exp3 = st.columns(3)

# Export CSV
csv = filtered.to_csv(index=False).encode("utf-8")
col_exp1.download_button(
    "📄 Export CSV",
    csv,
    "dossiers.csv",
    "text/csv"
)

# Export Excel
excel_buffer = io.BytesIO()
with pd.ExcelWriter(excel_buffer, engine="xlsxwriter") as writer:
    filtered.to_excel(writer, index=False, sheet_name="Dossiers")
col_exp2.download_button(
    "📘 Export Excel",
    excel_buffer.getvalue(),
    "dossiers.xlsx"
)

# Export PDF minimal
pdf_buffer = generate_pdf_from_dataframe(filtered, title="Liste des dossiers filtrés")
col_exp3.download_button(
    "📕 Export PDF",
    pdf_buffer,
    "dossiers.pdf",
    "application/pdf"
)

