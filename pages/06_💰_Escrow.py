import streamlit as st
import pandas as pd

from utils.sidebar import render_sidebar
from backend.dropbox_utils import load_database, save_database

# ---------------------------------------------------------
# CONFIG PAGE
# ---------------------------------------------------------
st.set_page_config(page_title="💰 Escrow", page_icon="💰", layout="wide")
render_sidebar()
st.title("💰 Gestion des Escrows")

# ---------------------------------------------------------
# HELPERS
# ---------------------------------------------------------
def normalize_bool(x):
    if isinstance(x, bool):
        return x
    if x is None:
        return False
    s = str(x).strip().lower()
    return s in ["true", "1", "1.0", "yes", "oui", "y", "vrai"]

def to_float(x):
    try:
        return float(x)
    except Exception:
        return 0.0

def safe_date(v):
    try:
        d = pd.to_datetime(v, errors="coerce")
        return None if pd.isna(d) else d.date()
    except Exception:
        return None

# ---------------------------------------------------------
# CHARGEMENT BASE
# ---------------------------------------------------------
db = load_database()
clients = db.get("clients", [])
df = pd.DataFrame(clients)

if df.empty:
    st.info("Aucun dossier trouvé.")
    st.stop()

# ---------------------------------------------------------
# NORMALISATION COLONNES
# ---------------------------------------------------------
# Colonnes booléennes attendues
for col in ["Escrow", "Escrow_a_reclamer", "Escrow_reclame"]:
    if col not in df.columns:
        df[col] = False
    df[col] = df[col].apply(normalize_bool)

# Acompte 1 = montant escrow (règle métier)
if "Acompte 1" not in df.columns:
    df["Acompte 1"] = 0.0
df["Acompte 1"] = df["Acompte 1"].apply(to_float)

# Dates (pour ancienneté)
if "Date" in df.columns:
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
else:
    df["Date"] = pd.NaT

# Montant Escrow à chaque étape = Acompte 1 uniquement si Escrow actif
df["Montant Escrow"] = df.apply(lambda r: r["Acompte 1"] if r["Escrow"] else 0.0, axis=1)

# ---------------------------------------------------------
# KPI GLOBAUX (sur base Montant Escrow)
# ---------------------------------------------------------
total_escrow = df.loc[df["Escrow"] == True, "Montant Escrow"].sum()

# Pour être "à réclamer" / "réclamé" : on exige Escrow True sinon montant 0
df_a_reclamer = df[(df["Escrow"] == True) & (df["Escrow_a_reclamer"] == True)].copy()
df_reclame = df[(df["Escrow"] == True) & (df["Escrow_reclame"] == True)].copy()

total_a_reclamer = df_a_reclamer["Montant Escrow"].sum()
total_reclame = df_reclame["Montant Escrow"].sum()

col1, col2, col3 = st.columns(3)
col1.metric("💼 Escrow actif", f"${total_escrow:,.2f}")
col2.metric("⏳ Escrow à réclamer", f"${total_a_reclamer:,.2f}")
col3.metric("✅ Escrow réclamé", f"${total_reclame:,.2f}")

# Alerte automatique
if total_a_reclamer > 0:
    st.warning(
        f"⚠️ {len(df_a_reclamer)} dossier(s) en escrow à réclamer "
        f"pour un total de ${total_a_reclamer:,.2f}."
    )

st.divider()

# ---------------------------------------------------------
# SECTION 1 — ESCROW ACTIFS
# ---------------------------------------------------------
st.subheader("💼 Escrows actifs (Montant = Acompte 1)")

df_active = df[df["Escrow"] == True].copy()
df_active_display = df_active[[
    "Dossier N", "Nom", "Date", "Acompte 1", "Montant Escrow",
    "Escrow_a_reclamer", "Escrow_reclame"
]].copy()

st.dataframe(df_active_display, use_container_width=True)

st.divider()

# ---------------------------------------------------------
# SECTION 2 — ESCROW À RÉCLAMER + BOUTON → RÉCLAMÉ
# ---------------------------------------------------------
st.subheader("⏳ Escrows à réclamer (avec ancienneté)")

if df_a_reclamer.empty:
    st.success("✔ Aucun escrow en attente de réclamation.")
else:
    df_a_reclamer["Ancienneté (jours)"] = (pd.Timestamp.today() - df_a_reclamer["Date"]).dt.days

    # Affichage + actions
    for i, row in df_a_reclamer.sort_values("Ancienneté (jours)", ascending=False).iterrows():
        dnum = row.get("Dossier N", "")
        nom = row.get("Nom", "")
        date_dossier = safe_date(row.get("Date"))
        montant = row.get("Montant Escrow", 0.0)
        age = row.get("Ancienneté (jours)", 0)

        with st.container(border=True):
            c1, c2, c3, c4, c5 = st.columns([1.1, 2.2, 1.4, 1.4, 1.4])

            c1.markdown(f"**#{int(dnum) if pd.notna(dnum) else ''}**")
            c2.markdown(f"**{nom}**")
            c3.markdown(f"📅 {date_dossier if date_dossier else '—'}")
            c4.markdown(f"💵 **${montant:,.2f}**")
            c5.markdown(f"⏱️ **{int(age) if pd.notna(age) else 0} j**")

            # Bouton action : passer à réclamé
            if st.button(
                "✅ Marquer comme réclamé",
                key=f"btn_reclame_{int(dnum) if pd.notna(dnum) else i}",
                type="primary",
                use_container_width=True
            ):
                # Update dans df
                idx = df.index[i]  # index original (i vient de df_a_reclamer qui garde index df)
                df.loc[idx, "Escrow_reclame"] = True
                df.loc[idx, "Escrow_a_reclamer"] = False

                # (Optionnel) si tu veux garder Escrow actif même après réclamation, on ne touche pas "Escrow"
                # df.loc[idx, "Escrow"] = True

                # Recalcul Montant Escrow (reste Acompte 1 si Escrow True)
                df.loc[idx, "Montant Escrow"] = df.loc[idx, "Acompte 1"] if df.loc[idx, "Escrow"] else 0.0

                # Sauvegarde JSON
                db["clients"] = df.drop(columns=["Montant Escrow"], errors="ignore").to_dict(orient="records")
                save_database(db)

                st.success("✔ Escrow marqué comme réclamé. Le dossier a été retiré de 'à réclamer'.")
                st.rerun()

    # Export CSV de la liste "à réclamer"
    csv = df_a_reclamer.to_csv(index=False).encode("utf-8")
    st.download_button(
        "⬇️ Export Escrows à réclamer (CSV)",
        csv,
        "escrow_a_reclamer.csv",
        "text/csv",
    )

st.divider()

# ---------------------------------------------------------
# SECTION 3 — ESCROW RÉCLAMÉS
# ---------------------------------------------------------
st.subheader("✅ Escrows réclamés")

if df_reclame.empty:
    st.info("Aucun escrow réclamé pour le moment.")
else:
    df_reclame_display = df_reclame[[
        "Dossier N", "Nom", "Date", "Acompte 1", "Montant Escrow"
    ]].copy()
    st.dataframe(df_reclame_display, use_container_width=True)

    csv_done = df_reclame.to_csv(index=False).encode("utf-8")
    st.download_button(
        "⬇️ Export Escrows réclamés (CSV)",
        csv_done,
        "escrow_reclame.csv",
        "text/csv",
    )

# ---------------------------------------------------------
# FIN
# ---------------------------------------------------------
st.caption("Règle métier : Montant Escrow = Acompte 1 uniquement si Escrow actif.")