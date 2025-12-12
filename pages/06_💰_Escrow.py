import streamlit as st
import pandas as pd
import io
from datetime import date

from utils.sidebar import render_sidebar
from backend.dropbox_utils import load_database, save_database


# =========================================================
# CONFIG + SIDEBAR
# =========================================================
st.set_page_config(page_title="💰 Escrow", page_icon="💰", layout="wide")
render_sidebar()
st.title("💰 Gestion des Escrows")


# =========================================================
# HELPERS
# =========================================================
REQUIRED_COLS = [
    "Dossier N", "Nom", "Date",
    "Acompte 1",
    "Escrow", "Escrow_a_reclamer", "Escrow_reclame",
    "Date envoi", "Date reclamation",
]

def normalize_bool(v) -> bool:
    if isinstance(v, bool):
        return v
    if v is None:
        return False
    s = str(v).strip().lower()
    return s in ["true", "1", "1.0", "yes", "oui", "y", "vrai"]

def to_float(v) -> float:
    try:
        if v in ["None", None, ""]:
            return 0.0
        return float(v)
    except Exception:
        return 0.0

def to_date_str(v) -> str:
    """Retourne une date ISO 'YYYY-MM-DD' ou ''."""
    if v in [None, "", "None"]:
        return ""
    try:
        d = pd.to_datetime(v, errors="coerce")
        if pd.isna(d):
            return ""
        return d.date().isoformat()
    except Exception:
        return ""

def ensure_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    for c in REQUIRED_COLS:
        if c not in df.columns:
            # defaults
            if c in ["Escrow", "Escrow_a_reclamer", "Escrow_reclame"]:
                df[c] = False
            elif c == "Acompte 1":
                df[c] = 0.0
            else:
                df[c] = ""
    # types
    df["Escrow"] = df["Escrow"].apply(normalize_bool)
    df["Escrow_a_reclamer"] = df["Escrow_a_reclamer"].apply(normalize_bool)
    df["Escrow_reclame"] = df["Escrow_reclame"].apply(normalize_bool)

    df["Acompte 1"] = df["Acompte 1"].apply(to_float)

    # normaliser dossier N
    df["Dossier N"] = pd.to_numeric(df["Dossier N"], errors="coerce").astype("Int64")

    # dates en string ISO pour éviter Timestamp dans JSON
    df["Date"] = df["Date"].apply(to_date_str)
    df["Date envoi"] = df["Date envoi"].apply(to_date_str)
    df["Date reclamation"] = df["Date reclamation"].apply(to_date_str)

    return df

def escrow_amount(row) -> float:
    # Règle confirmée : le montant escrow = Acompte 1 uniquement
    return float(row.get("Acompte 1", 0) or 0)

def compute_age_days(row) -> int:
    """
    Ancienneté (jours) pour 'Escrow à réclamer' :
    - on prend Date envoi si dispo, sinon Date du dossier.
    """
    base = row.get("Date envoi", "") or row.get("Date", "")
    if not base:
        return 0
    try:
        d = pd.to_datetime(base, errors="coerce")
        if pd.isna(d):
            return 0
        return int((pd.Timestamp.today().date() - d.date()).days)
    except Exception:
        return 0

def set_state_exclusive(df: pd.DataFrame, idx, state: str) -> pd.DataFrame:
    """
    state in {"actif","a_reclamer","reclame"}
    Machine d'état exclusive.
    """
    df = df.copy()

    if state == "actif":
        df.loc[idx, "Escrow"] = True
        df.loc[idx, "Escrow_a_reclamer"] = False
        df.loc[idx, "Escrow_reclame"] = False

    elif state == "a_reclamer":
        df.loc[idx, "Escrow"] = False
        df.loc[idx, "Escrow_a_reclamer"] = True
        df.loc[idx, "Escrow_reclame"] = False

    elif state == "reclame":
        df.loc[idx, "Escrow"] = False
        df.loc[idx, "Escrow_a_reclamer"] = False
        df.loc[idx, "Escrow_reclame"] = True
        df.loc[idx, "Date reclamation"] = date.today().isoformat()

    return df

def export_csv_bytes(df_export: pd.DataFrame) -> bytes:
    buff = io.StringIO()
    df_export.to_csv(buff, index=False)
    return buff.getvalue().encode("utf-8")


# =========================================================
# LOAD DB
# =========================================================
db = load_database()
clients = db.get("clients", [])
df = pd.DataFrame(clients)

if df.empty:
    st.info("Aucun dossier en base.")
    st.stop()

df = ensure_columns(df)

# Alerte automatique si escrow à réclamer
count_reclamer = int(df["Escrow_a_reclamer"].sum())
if count_reclamer > 0:
    st.warning(f"⚠️ {count_reclamer} dossier(s) en Escrow à réclamer.")


# =========================================================
# KPI GLOBAL
# =========================================================
total_actif = df.loc[df["Escrow"], "Acompte 1"].sum()
total_a_reclamer = df.loc[df["Escrow_a_reclamer"], "Acompte 1"].sum()
total_reclame = df.loc[df["Escrow_reclame"], "Acompte 1"].sum()

k1, k2, k3, k4 = st.columns(4)
k1.metric("Escrow actif", f"{int(df['Escrow'].sum())}")
k2.metric("Escrow à réclamer", f"{int(df['Escrow_a_reclamer'].sum())}")
k3.metric("Escrow réclamé", f"{int(df['Escrow_reclame'].sum())}")
k4.metric("Montant total Escrow (Acompte 1)", f"${total_actif + total_a_reclamer + total_reclame:,.2f}")


# =========================================================
# TABS
# =========================================================
tab_actif, tab_reclamer, tab_reclame = st.tabs([
    "💼 Escrow actif",
    "📤 Escrow à réclamer",
    "✅ Escrow réclamé",
])

# =========================================================
# TAB 1 — ACTIF
# =========================================================
with tab_actif:
    st.subheader("💼 Dossiers en Escrow actif")
    df_actif = df[df["Escrow"] == True].copy()
    df_actif["Montant Escrow (Acompte 1)"] = df_actif.apply(escrow_amount, axis=1)

    total = float(df_actif["Montant Escrow (Acompte 1)"].sum()) if not df_actif.empty else 0.0
    st.caption(f"Total Escrow actif (Acompte 1) : **${total:,.2f}**")

    if df_actif.empty:
        st.info("Aucun dossier en Escrow actif.")
    else:
        for idx, row in df_actif.sort_values("Dossier N").iterrows():
            dnum = int(row["Dossier N"]) if pd.notna(row["Dossier N"]) else "?"
            montant = float(row["Montant Escrow (Acompte 1)"] or 0)

            with st.container(border=True):
                c1, c2, c3, c4 = st.columns([2, 4, 2, 2])
                c1.markdown(f"**Dossier**: {dnum}")
                c2.markdown(f"**Nom**: {row.get('Nom','')}")
                c3.markdown(f"**Acompte 1**: ${montant:,.2f}")
                c4.markdown(f"**Date**: {row.get('Date','')}")

                b1, b2 = st.columns([1, 5])
                if b1.button("📤 Passer à réclamer", key=f"to_reclamer_actif_{dnum}"):
                    df2 = set_state_exclusive(df, idx, "a_reclamer")
                    db["clients"] = df2.to_dict(orient="records")
                    save_database(db)
                    st.success("✔ Déplacé vers Escrow à réclamer.")
                    st.rerun()

        # Export CSV
        export_cols = ["Dossier N", "Nom", "Date", "Acompte 1", "Montant Escrow (Acompte 1)"]
        csv_bytes = export_csv_bytes(df_actif[export_cols])
        st.download_button(
            "⬇️ Export CSV (Escrow actif)",
            data=csv_bytes,
            file_name="escrow_actif.csv",
            mime="text/csv",
            key="csv_actif",
        )


# =========================================================
# TAB 2 — A RÉCLAMER
# =========================================================
with tab_reclamer:
    st.subheader("📤 Dossiers en Escrow à réclamer")
    df_reclamer = df[df["Escrow_a_reclamer"] == True].copy()
    df_reclamer["Montant Escrow (Acompte 1)"] = df_reclamer.apply(escrow_amount, axis=1)
    df_reclamer["Ancienneté (jours)"] = df_reclamer.apply(compute_age_days, axis=1)

    total = float(df_reclamer["Montant Escrow (Acompte 1)"].sum()) if not df_reclamer.empty else 0.0
    st.caption(f"Total Escrow à réclamer (Acompte 1) : **${total:,.2f}**")

    if not df_reclamer.empty:
        max_age = int(df_reclamer["Ancienneté (jours)"].max())
        st.info(f"Ancienneté max des escrows non réclamés : **{max_age} jours**")

    if df_reclamer.empty:
        st.info("Aucun dossier en Escrow à réclamer.")
    else:
        df_reclamer = df_reclamer.sort_values(["Ancienneté (jours)", "Dossier N"], ascending=[False, True])

        for idx, row in df_reclamer.iterrows():
            dnum = int(row["Dossier N"]) if pd.notna(row["Dossier N"]) else "?"
            montant = float(row["Montant Escrow (Acompte 1)"] or 0)
            age = int(row["Ancienneté (jours)"] or 0)

            with st.container(border=True):
                c1, c2, c3, c4, c5 = st.columns([2, 4, 2, 2, 2])
                c1.markdown(f"**Dossier**: {dnum}")
                c2.markdown(f"**Nom**: {row.get('Nom','')}")
                c3.markdown(f"**Acompte 1**: ${montant:,.2f}")
                c4.markdown(f"**Ancienneté**: {age} j")
                c5.markdown(f"**Date envoi**: {row.get('Date envoi','') or '—'}")

                b1, b2, b3 = st.columns([1.4, 1.4, 5])
                if b1.button("✅ Marquer réclamé", key=f"mark_reclame_{dnum}"):
                    df2 = set_state_exclusive(df, idx, "reclame")
                    db["clients"] = df2.to_dict(orient="records")
                    save_database(db)
                    st.success("✔ Marqué comme réclamé (déplacé vers Escrow réclamé).")
                    st.rerun()

                if b2.button("↩️ Revenir actif", key=f"back_actif_{dnum}"):
                    df2 = set_state_exclusive(df, idx, "actif")
                    db["clients"] = df2.to_dict(orient="records")
                    save_database(db)
                    st.success("✔ Repassé en Escrow actif.")
                    st.rerun()

        # Export CSV
        export_cols = ["Dossier N", "Nom", "Date", "Date envoi", "Acompte 1", "Montant Escrow (Acompte 1)", "Ancienneté (jours)"]
        csv_bytes = export_csv_bytes(df_reclamer[export_cols])
        st.download_button(
            "⬇️ Export CSV (Escrow à réclamer)",
            data=csv_bytes,
            file_name="escrow_a_reclamer.csv",
            mime="text/csv",
            key="csv_reclamer",
        )


# =========================================================
# TAB 3 — RÉCLAMÉ
# =========================================================
with tab_reclame:
    st.subheader("✅ Dossiers en Escrow réclamé")
    df_reclame = df[df["Escrow_reclame"] == True].copy()
    df_reclame["Montant Escrow (Acompte 1)"] = df_reclame.apply(escrow_amount, axis=1)

    total = float(df_reclame["Montant Escrow (Acompte 1)"].sum()) if not df_reclame.empty else 0.0
    st.caption(f"Total Escrow réclamé (Acompte 1) : **${total:,.2f}**")

    if df_reclame.empty:
        st.info("Aucun dossier en Escrow réclamé.")
    else:
        df_reclame = df_reclame.sort_values(["Date reclamation", "Dossier N"], ascending=[False, True])

        for idx, row in df_reclame.iterrows():
            dnum = int(row["Dossier N"]) if pd.notna(row["Dossier N"]) else "?"
            montant = float(row["Montant Escrow (Acompte 1)"] or 0)

            with st.container(border=True):
                c1, c2, c3, c4 = st.columns([2, 4, 2, 2])
                c1.markdown(f"**Dossier**: {dnum}")
                c2.markdown(f"**Nom**: {row.get('Nom','')}")
                c3.markdown(f"**Acompte 1**: ${montant:,.2f}")
                c4.markdown(f"**Date réclamation**: {row.get('Date reclamation','') or '—'}")

                b1, b2 = st.columns([1.4, 5])
                if b1.button("↩️ Revenir à réclamer", key=f"back_reclamer_{dnum}"):
                    df2 = set_state_exclusive(df, idx, "a_reclamer")
                    db["clients"] = df2.to_dict(orient="records")
                    save_database(db)
                    st.success("✔ Repassé en Escrow à réclamer.")
                    st.rerun()

        # Export CSV
        export_cols = ["Dossier N", "Nom", "Date", "Date reclamation", "Acompte 1", "Montant Escrow (Acompte 1)"]
        csv_bytes = export_csv_bytes(df_reclame[export_cols])
        st.download_button(
            "⬇️ Export CSV (Escrow réclamé)",
            data=csv_bytes,
            file_name="escrow_reclame.csv",
            mime="text/csv",
            key="csv_reclame",
        )
