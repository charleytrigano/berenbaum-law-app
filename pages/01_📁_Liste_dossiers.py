import streamlit as st
import pandas as pd
from backend.dropbox_utils import load_database
from utils.visa_filters import clean_visa_df
from components.export_pdf import generate_pdf_from_dataframe

st.set_page_config(page_title="Liste des dossiers", page_icon="📁", layout="wide")

st.title("📁 Liste des dossiers – Analyse & Filtrage avancé")

# ---------------------------------------------------------
# LOAD DATABASE
# ---------------------------------------------------------
db = load_database()
clients = db.get("clients", [])
visa_raw = pd.DataFrame(db.get("visa", []))

if not clients:
    st.warning("Aucun dossier trouvé.")
    st.stop()

df = pd.DataFrame(clients)
visa_table = clean_visa_df(visa_raw)

# ---------------------------------------------------------
# NORMALISATIONS CLIENTS
# ---------------------------------------------------------
df["Date"] = pd.to_datetime(df.get("Date"), errors="coerce")

num_cols = [
    "Montant honoraires (US $)", "Autres frais (US $)",
    "Acompte 1", "Acompte 2", "Acompte 3", "Acompte 4"
]

for c in num_cols:
    df[c] = pd.to_numeric(df.get(c, 0), errors="coerce").fillna(0)

df["Total facturé"] = df["Montant honoraires (US $)"] + df["Autres frais (US $)"]
df["Montant encaissé"] = df["Acompte 1"] + df["Acompte 2"] + df["Acompte 3"] + df["Acompte 4"]
df["Solde"] = df["Total facturé"] - df["Montant encaissé"]
df["Année"] = df["Date"].dt.year

# ---------------------------------------------------------
# STATUT DOSSIER
# ---------------------------------------------------------
def compute_status(row):
    if str(row.get("RFE", "")).strip() not in ["", "None", "nan"]:
        return "RFE"
    if str(row.get("Date annulation", "")).strip():
        return "Annulé"
    if str(row.get("Date refus", "")).strip():
        return "Refusé"
    if str(row.get("Date acceptation", "")).strip():
        return "Accepté"
    if str(row.get("Date envoi", "")).strip():
        return "Envoyé"
    return "En cours"

df["Statut"] = df.apply(compute_status, axis=1)

# ---------------------------------------------------------
# KPI STYLE
# ---------------------------------------------------------
st.markdown("""
<style>
div[data-testid="stMetricValue"] {
    font-size: 18px !important;
}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# KPI FUNCTION
# ---------------------------------------------------------
def show_kpis(df_local):
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    c1.metric("Dossiers", len(df_local))
    c2.metric("Honoraires", f"${df_local['Montant honoraires (US $)'].sum():,.0f}")
    c3.metric("Autres frais", f"${df_local['Autres frais (US $)'].sum():,.0f}")
    c4.metric("Facturé", f"${df_local['Total facturé'].sum():,.0f}")
    c5.metric("Encaissé", f"${df_local['Montant encaissé'].sum():,.0f}")
    c6.metric("Solde", f"${df_local['Solde'].sum():,.0f}")

st.subheader("📌 Indicateurs (Filtres actifs)")
show_kpis(df)

# ---------------------------------------------------------
# FILTRES
# ---------------------------------------------------------
st.markdown("---")
st.subheader("🎛️ Filtres")

colA, colB, colC, colD, colE = st.columns(5)

# Catégories
cat_list = ["Toutes"] + sorted(visa_table["Categories"].unique())
cat = colA.selectbox("Catégorie", cat_list)

# Sous-catégories
if cat != "Toutes":
    souscat_list = ["Toutes"] + sorted(
        visa_table.loc[visa_table["Categories"] == cat]["Sous-categories"].unique()
    )
else:
    souscat_list = ["Toutes"] + sorted(visa_table["Sous-categories"].unique())

souscat = colB.selectbox("Sous-catégorie", souscat_list)

# Visa
if souscat != "Toutes":
    visa_list = ["Tous"] + sorted(
        visa_table.loc[visa_table["Sous-categories"] == souscat]["Visa"].unique()
    )
elif cat != "Toutes":
    visa_list = ["Tous"] + sorted(
        visa_table.loc[visa_table["Categories"] == cat]["Visa"].unique()
    )
else:
    visa_list = ["Tous"] + sorted(visa_table["Visa"].unique())

visa_choice = colC.selectbox("Visa", visa_list)

# Année
annees = ["Toutes"] + sorted(df["Année"].dropna().unique().tolist())
annee = colD.selectbox("Année", annees)

# Statut
status_filter = colE.selectbox(
    "Statut dossier",
    ["Tous", "En cours", "Envoyé", "Accepté", "Refusé", "Annulé", "RFE"]
)

# ---------------------------------------------------------
# APPLICATION FILTRES
# ---------------------------------------------------------
filtered = df.copy()

if cat != "Toutes":
    filtered = filtered[filtered["Categories"] == cat]

if souscat != "Toutes":
    filtered = filtered[filtered["Sous-categories"] == souscat]

if visa_choice != "Tous":
    filtered = filtered[filtered["Visa"] == visa_choice]

if annee != "Toutes":
    filtered = filtered[filtered["Année"] == annee]

if status_filter != "Tous":
    filtered = filtered[filtered["Statut"] == status_filter]

# KPI avec filtres
st.subheader("📌 Indicateurs filtrés")
show_kpis(filtered)

st.markdown("---")

# ---------------------------------------------------------
# ACTIONS : EXPORTS & MODIFICATION DOSSIER
# ---------------------------------------------------------
st.subheader("📤 Export & Actions")

colX, colY = st.columns(2)

# ---- EXPORT EXCEL ----
excel_data = filtered.to_excel(index=False, engine="openpyxl")
colX.download_button(
    label="📥 Export Excel",
    data=excel_data,
    file_name="Liste_dossiers.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
)

# ---- EXPORT PDF ----
pdf_buffer = generate_pdf_from_dataframe(filtered)
colY.download_button(
    label="📄 Export PDF",
    data=pdf_buffer,
    file_name="Liste_dossiers.pdf",
    mime="application/pdf",
)

st.markdown("---")

# ---------------------------------------------------------
# TABLEAU AVEC BOUTON "MODIFIER"
# ---------------------------------------------------------
st.subheader("📋 Dossiers filtrés")

def add_actions(df_local):
    df_out = df_local.copy()
    df_out["Action"] = ""
    for idx, row in df_out.iterrows():
        if st.button("✏️ Modifier", key=f"edit_{idx}"):
            st.session_state["edit_dossier"] = row["Dossier N"]
            st.switch_page("pages/03_✏️_Modifier_dossier.py")
    return df_out

st.dataframe(
    filtered,
    use_container_width=True,
    height=650
)
