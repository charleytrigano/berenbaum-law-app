import io
import hashlib
from datetime import datetime

import streamlit as st
import pandas as pd

from utils.sidebar import render_sidebar
from backend.dropbox_utils import load_database, save_database


# ---------------------------------------------------------
# CONFIG & SIDEBAR
# ---------------------------------------------------------
st.set_page_config(page_title="💰 Escrow", page_icon="💰", layout="wide")
render_sidebar()
st.title("💰 Escrow — Suivi & Transitions")


# ---------------------------------------------------------
# HELPERS
# ---------------------------------------------------------
def normalize_bool(x) -> bool:
    if isinstance(x, bool):
        return x
    if x is None:
        return False
    s = str(x).strip().lower()
    return s in ["true", "1", "1.0", "yes", "oui", "y", "vrai"]


def to_float(x) -> float:
    try:
        if x is None or x == "":
            return 0.0
        return float(x)
    except Exception:
        return 0.0


def ensure_cols(df: pd.DataFrame, cols_defaults: dict) -> pd.DataFrame:
    df = df.copy()
    for col, default in cols_defaults.items():
        if col not in df.columns:
            df[col] = default
    return df


def set_escrow_state(df: pd.DataFrame, idx, state: str) -> pd.DataFrame:
    """
    state ∈ {"actif", "a_reclamer", "reclame"}
    Règle: un dossier ne peut être que dans UN seul état à la fois.
    """
    df = df.copy()

    # reset
    df.loc[idx, "Escrow"] = False
    df.loc[idx, "Escrow_a_reclamer"] = False
    df.loc[idx, "Escrow_reclame"] = False

    if state == "actif":
        df.loc[idx, "Escrow"] = True
    elif state == "a_reclamer":
        df.loc[idx, "Escrow_a_reclamer"] = True
    elif state == "reclame":
        df.loc[idx, "Escrow_reclame"] = True

    return df


def escrow_pdf_bytes(state_label: str, df_state: pd.DataFrame, total_amount: float) -> bytes:
    """
    Génère un PDF "certifié" (timestamp + empreinte SHA256 du contenu exporté).
    Utilise reportlab (installé).
    """
    from reportlab.lib.pagesizes import letter
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

    # Empreinte de certification: dossier+nom+montant
    payload = "|".join(
        [
            f"{int(x) if pd.notna(x) else ''}::{str(n)}::{float(a):.2f}"
            for x, n, a in zip(
                df_state.get("Dossier N", []),
                df_state.get("Nom", []),
                df_state.get("Acompte 1", []),
            )
        ]
    ).encode("utf-8")

    sha = hashlib.sha256(payload).hexdigest()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=letter, rightMargin=24, leftMargin=24, topMargin=24, bottomMargin=24)
    styles = getSampleStyleSheet()

    story = []
    story.append(Paragraph("Berenbaum Law App — Export Escrow", styles["Title"]))
    story.append(Spacer(1, 8))
    story.append(Paragraph(f"<b>État :</b> {state_label}", styles["Normal"]))
    story.append(Paragraph(f"<b>Date génération :</b> {now}", styles["Normal"]))
    story.append(Paragraph(f"<b>Nombre de dossiers :</b> {len(df_state)}", styles["Normal"]))
    story.append(Paragraph(f"<b>Total (Acompte 1) :</b> ${total_amount:,.2f}", styles["Normal"]))
    story.append(Spacer(1, 10))
    story.append(Paragraph(f"<b>Empreinte SHA256 (certification) :</b><br/>{sha}", styles["Normal"]))
    story.append(Spacer(1, 14))

    table_cols = ["Dossier N", "Nom", "Date", "Categories", "Sous-categories", "Visa", "Acompte 1"]
    table_cols = [c for c in table_cols if c in df_state.columns]

    # Data table
    data = [table_cols]
    for _, r in df_state.iterrows():
        row = []
        for c in table_cols:
            v = r.get(c, "")
            if c == "Acompte 1":
                row.append(f"${to_float(v):,.2f}")
            else:
                row.append("" if pd.isna(v) else str(v))
        data.append(row)

    tbl = Table(data, repeatRows=1)
    tbl.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#222222")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 10),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#999999")),
                ("FONTSIZE", (0, 1), (-1, -1), 9),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F6F6F6")]),
            ]
        )
    )
    story.append(tbl)

    doc.build(story)
    return buf.getvalue()


# ---------------------------------------------------------
# LOAD DB
# ---------------------------------------------------------
db = load_database()
clients = db.get("clients", [])
df = pd.DataFrame(clients)

if df.empty:
    st.info("Aucun dossier trouvé.")
    st.stop()

df = ensure_cols(
    df,
    {
        "Dossier N": None,
        "Nom": "",
        "Date": "",
        "Categories": "",
        "Sous-categories": "",
        "Visa": "",
        "Acompte 1": 0.0,
        "Escrow": False,
        "Escrow_a_reclamer": False,
        "Escrow_reclame": False,
    },
)

# Normalisations
df["Dossier N"] = pd.to_numeric(df["Dossier N"], errors="coerce").astype("Int64")
df["Date"] = pd.to_datetime(df["Date"], errors="coerce").dt.date.astype(str).replace("NaT", "")
df["Acompte 1"] = df["Acompte 1"].apply(to_float)
for b in ["Escrow", "Escrow_a_reclamer", "Escrow_reclame"]:
    df[b] = df[b].apply(normalize_bool)

# ---------------------------------------------------------
# KPI (strictement alignés)
# ---------------------------------------------------------
total_actif = float(df.loc[df["Escrow"] == True, "Acompte 1"].sum())
total_areclamer = float(df.loc[df["Escrow_a_reclamer"] == True, "Acompte 1"].sum())
total_reclame = float(df.loc[df["Escrow_reclame"] == True, "Acompte 1"].sum())

k1, k2, k3 = st.columns(3)
k1.metric("💼 Montant Escrow actif (Acompte 1)", f"${total_actif:,.2f}")
k2.metric("📤 Montant Escrow à réclamer (Acompte 1)", f"${total_areclamer:,.2f}")
k3.metric("✅ Montant Escrow réclamé (Acompte 1)", f"${total_reclame:,.2f}")

st.caption("Chaque dossier appartient à un seul état Escrow. Les montants Escrow = Acompte 1 uniquement.")

# ---------------------------------------------------------
# TABS
# ---------------------------------------------------------
tab_actif, tab_areclamer, tab_reclame = st.tabs(["💼 Escrow actif", "📤 Escrow à réclamer", "✅ Escrow réclamé"])

DISPLAY_COLS = [
    "Dossier N",
    "Nom",
    "Date",
    "Categories",
    "Sous-categories",
    "Visa",
    "Acompte 1",
]


def render_table_and_actions(state_key: str, state_label: str, df_state: pd.DataFrame):
    # Totaux EXACTS sous l’onglet
    total_state = float(df_state["Acompte 1"].sum()) if not df_state.empty else 0.0
    st.caption(f"Total {state_label} (Acompte 1) : ${total_state:,.2f}")

    # Export PDF certifié
    colA, colB = st.columns([1, 1])
    with colA:
        pdf = escrow_pdf_bytes(state_label, df_state, total_state)
        filename = f"escrow_{state_key}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        st.download_button(
            "📄 Exporter PDF (certifié)",
            data=pdf,
            file_name=filename,
            mime="application/pdf",
            use_container_width=True,
        )
    with colB:
        csv = df_state[DISPLAY_COLS].to_csv(index=False).encode("utf-8")
        st.download_button(
            "⬇️ Exporter CSV",
            data=csv,
            file_name=f"escrow_{state_key}.csv",
            mime="text/csv",
            use_container_width=True,
        )

    st.markdown("---")

    if df_state.empty:
        st.info("Aucun dossier dans cet état.")
        return

    # Tableau
    st.dataframe(df_state[DISPLAY_COLS], use_container_width=True, height=420)

    st.markdown("---")
    st.subheader("🔁 Actions")

    # Sélection dossier
    nums = sorted(df_state["Dossier N"].dropna().astype(int).unique())
    selected_num = st.selectbox(
        "Choisir un dossier",
        nums,
        key=f"sel_{state_key}",
    )

    if selected_num is None:
        return

    idx = df[df["Dossier N"] == selected_num].index[0]
    dossier = df.loc[idx].to_dict()
    st.write(f"**Dossier {selected_num} — {dossier.get('Nom','')}**")
    st.write(f"Montant (Acompte 1) : **${to_float(dossier.get('Acompte 1')):,.2f}**")

    # Boutons de transition (exclusifs)
    if state_key == "actif":
        c1, c2 = st.columns(2)
        with c1:
            if st.button("📤 Passer en 'Escrow à réclamer'", type="primary", key=f"to_arecl_{selected_num}"):
                df2 = set_escrow_state(df, idx, "a_reclamer")
                db["clients"] = df2.to_dict(orient="records")
                save_database(db)
                st.success("Dossier déplacé vers Escrow à réclamer.")
                st.rerun()
        with c2:
            if st.button("✅ Passer en 'Escrow réclamé'", key=f"to_reclame_{selected_num}"):
                df2 = set_escrow_state(df, idx, "reclame")
                db["clients"] = df2.to_dict(orient="records")
                save_database(db)
                st.success("Dossier déplacé vers Escrow réclamé.")
                st.rerun()

    elif state_key == "a_reclamer":
        c1, c2 = st.columns(2)
        with c1:
            if st.button("✅ Marquer comme réclamé", type="primary", key=f"mark_reclame_{selected_num}"):
                # doit DISPARAÎTRE de "à réclamer" et aller dans "réclamé"
                df2 = set_escrow_state(df, idx, "reclame")
                db["clients"] = df2.to_dict(orient="records")
                save_database(db)
                st.success("Dossier marqué comme réclamé (déplacé).")
                st.rerun()
        with c2:
            if st.button("↩️ Revenir à 'Escrow actif'", key=f"back_actif_{selected_num}"):
                df2 = set_escrow_state(df, idx, "actif")
                db["clients"] = df2.to_dict(orient="records")
                save_database(db)
                st.success("Dossier revenu en Escrow actif.")
                st.rerun()

    elif state_key == "reclame":
        if st.button("↩️ Revenir à 'Escrow à réclamer'", key=f"back_arecl_{selected_num}"):
            df2 = set_escrow_state(df, idx, "a_reclamer")
            db["clients"] = df2.to_dict(orient="records")
            save_database(db)
            st.success("Dossier revenu en Escrow à réclamer.")
            st.rerun()


# ---------------------------------------------------------
# FILTERED DATAFRAMES
# ---------------------------------------------------------
df_actif = df[df["Escrow"] == True].copy()
df_areclamer = df[df["Escrow_a_reclamer"] == True].copy()
df_reclame = df[df["Escrow_reclame"] == True].copy()

# Safety: colonnes d’affichage
for dfx in [df_actif, df_areclamer, df_reclame]:
    for c in DISPLAY_COLS:
        if c not in dfx.columns:
            dfx[c] = ""


with tab_actif:
    render_table_and_actions("actif", "Escrow actif", df_actif)

with tab_areclamer:
    render_table_and_actions("a_reclamer", "Escrow à réclamer", df_areclamer)

with tab_reclame:
    render_table_and_actions("reclame", "Escrow réclamé", df_reclame)
