import streamlit as st
import pandas as pd
import json
from datetime import datetime

from utils.sidebar import render_sidebar
from backend.dropbox_utils import load_database, save_database

# =====================================================
# CONFIG
# =====================================================
st.set_page_config(
    page_title="💲 Tarifs par Visa",
    page_icon="💲",
    layout="wide"
)
render_sidebar()
st.title("💲 Tarifs par Visa")

# =====================================================
# LOAD DATABASE
# =====================================================
db = load_database()

tarifs = db.get("tarifs", [])
history = db.get("tarifs_history", [])
visa_ref = pd.DataFrame(db.get("visa", []))

# Liste unique des visas existants
if visa_ref.empty or "Visa" not in visa_ref.columns:
    st.error("Aucun référentiel Visa trouvé dans la base (db['visa'] est vide ou invalide).")
    st.stop()

visa_list = sorted(visa_ref["Visa"].dropna().astype(str).str.strip().unique().tolist())

# =====================================================
# OUTILS DOSSIERS (PARENTS & FILS)
# =====================================================
def parse_parent(dossier_n: str) -> str:
    s = str(dossier_n).strip()
    if not s:
        return ""
    return s.split("-", 1)[0].strip()

def parse_index(dossier_n: str) -> int:
    s = str(dossier_n).strip()
    if not s or "-" not in s:
        return 0
    suffix = s.split("-", 1)[1].strip()
    try:
        return int(suffix)
    except Exception:
        return 0

def to_float(v):
    try:
        return float(v or 0)
    except Exception:
        return 0.0

def sort_key_parent(x: str):
    s = str(x).strip()
    return (0, int(s)) if s.isdigit() else (1, s)

# =====================================================
# SÉLECTION VISA
# =====================================================
st.subheader("🎯 Sélection du Visa")

visa = st.selectbox("Visa", visa_list)

current = next((t for t in tarifs if str(t.get("Visa", "")).strip() == str(visa).strip() and bool(t.get("Actif"))), None)

col1, col2 = st.columns(2)

tarif_actuel = col1.number_input(
    "Tarif actuel (US $)",
    value=float(current.get("Tarif", 0.0)) if current else 0.0,
    step=50.0
)

date_effet = col2.date_input(
    "Date d’effet",
    value=datetime.today().date()
)

# =====================================================
# ENREGISTREMENT
# =====================================================
if st.button("💾 Enregistrer le tarif", type="primary"):

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Désactiver l’ancien tarif
    for t in tarifs:
        if str(t.get("Visa", "")).strip() == str(visa).strip() and bool(t.get("Actif")):
            t["Actif"] = False

            history.append({
                "Visa": str(visa),
                "Ancien_tarif": t.get("Tarif", 0),
                "Nouveau_tarif": float(tarif_actuel),
                "Date_effet": str(date_effet),
                "Modifie_le": now
            })

    # Ajouter le nouveau
    tarifs.append({
        "Visa": str(visa),
        "Tarif": float(tarif_actuel),
        "Date_effet": str(date_effet),
        "Actif": True
    })

    db["tarifs"] = tarifs
    db["tarifs_history"] = history
    save_database(db)

    st.success("✔ Tarif mis à jour avec historique conservé")
    st.rerun()

# =====================================================
# DOSSIERS CONCERNÉS PAR CE VISA (PARENTS & FILS)
# =====================================================
st.markdown("---")
st.subheader("📁 Dossiers concernés par ce Visa (parents & sous-dossiers)")

clients = db.get("clients", [])
df_clients = pd.DataFrame(clients).copy()

if df_clients.empty:
    st.info("Aucun dossier trouvé dans la base.")
else:
    # Sécurisation colonnes attendues
    for col in ["Dossier N", "Nom", "Date", "Visa", "Montant honoraires (US $)"]:
        if col not in df_clients.columns:
            df_clients[col] = ""

    # Normalisation
    df_clients["Visa"] = df_clients["Visa"].astype(str).fillna("").str.strip()
    df_clients["Dossier N"] = df_clients["Dossier N"].astype(str).fillna("").str.strip()
    df_clients["Nom"] = df_clients["Nom"].astype(str).fillna("").str.strip()
    df_clients["Date_sort"] = pd.to_datetime(df_clients["Date"], errors="coerce")
    df_clients["Montant_honoraires_num"] = df_clients["Montant honoraires (US $)"].apply(to_float)

    # Hiérarchie parent/fils
    df_clients["Dossier Parent"] = df_clients["Dossier N"].apply(parse_parent)
    df_clients["Dossier Index"] = df_clients["Dossier N"].apply(parse_index)
    df_clients["Type"] = df_clients["Dossier Index"].apply(lambda x: "Parent" if int(x) == 0 else "Fils")

    # Filtre sur le visa sélectionné
    df_v = df_clients[df_clients["Visa"] == str(visa)].copy()

    if df_v.empty:
        st.info("Aucun dossier ne correspond à ce Visa.")
    else:
        # Option d'affichage groupé (parents d'abord, puis fils)
        colA, colB, colC = st.columns([1, 1, 2])
        show_only_fils = colA.checkbox("Afficher uniquement les sous-dossiers (xxxxx-1, xxxxx-2...)", value=False)
        show_grouped = colB.checkbox("Trier par parent puis index", value=True)
        search = colC.text_input("Recherche (Dossier N ou Nom)", value="").strip().lower()

        if show_only_fils:
            df_v = df_v[df_v["Dossier Index"] > 0].copy()

        if search:
            mask = (
                df_v["Dossier N"].astype(str).str.lower().str.contains(search, na=False)
                | df_v["Nom"].astype(str).str.lower().str.contains(search, na=False)
            )
            df_v = df_v[mask].copy()

        # Tri
        df_v["Parent_num"] = pd.to_numeric(df_v["Dossier Parent"], errors="coerce")
        if show_grouped:
            df_v = df_v.sort_values(
                ["Parent_num", "Dossier Parent", "Dossier Index", "Date_sort", "Dossier N"],
                ascending=[True, True, True, False, True],
            )
        else:
            df_v = df_v.sort_values(["Date_sort", "Dossier N"], ascending=[False, True])

        # Tableau affiché
        table = df_v[[
            "Dossier Parent",
            "Dossier Index",
            "Dossier N",
            "Type",
            "Nom",
            "Date",
            "Montant_honoraires_num",
        ]].rename(columns={
            "Montant_honoraires_num": "Montant honoraires (US $)"
        })

        st.dataframe(table, use_container_width=True, hide_index=True)

        # Totaux utiles
        total_dossiers = len(table)
        total_honoraires = float(table["Montant honoraires (US $)"].sum()) if "Montant honoraires (US $)" in table.columns else 0.0

        st.info(
            f"Total dossiers : {total_dossiers} | "
            f"Total honoraires : ${total_honoraires:,.2f}"
        )

        # Bonus: petit récap parents / fils
        nb_parents = int((df_v["Dossier Index"] == 0).sum())
        nb_fils = int((df_v["Dossier Index"] > 0).sum())
        st.caption(f"Répartition : {nb_parents} parent(s) | {nb_fils} sous-dossier(s).")

# =====================================================
# HISTORIQUE
# =====================================================
st.markdown("---")
st.subheader("🕓 Historique des tarifs")

hist_df = pd.DataFrame([h for h in history if str(h.get("Visa", "")).strip() == str(visa).strip()])

if hist_df.empty:
    st.info("Aucun historique pour ce visa.")
else:
    # Tri robuste
    if "Modifie_le" in hist_df.columns:
        hist_df["Modifie_le_sort"] = pd.to_datetime(hist_df["Modifie_le"], errors="coerce")
        hist_df = hist_df.sort_values("Modifie_le_sort", ascending=False).drop(columns=["Modifie_le_sort"], errors="ignore")

    st.dataframe(hist_df, use_container_width=True)