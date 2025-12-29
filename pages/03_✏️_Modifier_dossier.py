import streamlit as st
import pandas as pd
from datetime import datetime

from utils.sidebar import render_sidebar
from backend.dropbox_utils import load_database, save_database
from utils.tarif_utils import get_tarif_for_visa
from utils.status_utils import normalize_status_columns, update_status_row, normalize_bool

# ---------------------------------------------------------
# CONFIG
# ---------------------------------------------------------
st.set_page_config(page_title="✏️ Modifier un dossier", page_icon="✏️", layout="wide")
render_sidebar()
st.title("✏️ Modifier un dossier")

# ---------------------------------------------------------
# CHARGEMENT BASE
# ---------------------------------------------------------
db = load_database()
clients = db.get("clients", [])
tarifs = db.get("tarifs", [])

if not clients:
    st.error("Aucun dossier trouvé.")
    st.stop()

df = pd.DataFrame(clients)

# Normalisation statuts
df = normalize_status_columns(df)

DOSSIER_COL = "Dossier N"
df[DOSSIER_COL] = df.get(DOSSIER_COL, "").astype(str).fillna("").str.strip()

# ---------------------------------------------------------
# OUTILS
# ---------------------------------------------------------
def safe_date(v):
    try:
        d = pd.to_datetime(v, errors="coerce")
        return None if pd.isna(d) else d.date()
    except Exception:
        return None

def to_float(v):
    try:
        return float(v)
    except Exception:
        return 0.0

def norm_txt(x):
    return str(x or "").strip()

# =========================================================
# ✅ RECHERCHE DOSSIER (Nom OU Dossier N)
# =========================================================
st.subheader("🔎 Rechercher un dossier")

df["_Nom_norm"] = df.get("Nom", "").apply(norm_txt)
df["_Dossier_norm"] = df[DOSSIER_COL].apply(norm_txt)

search = st.text_input(
    "Recherche (Nom ou Dossier N)",
    value="",
    placeholder="Ex: 12904 ou LUCAS",
)

if search.strip():
    s = search.strip().lower()
    df_filtered = df[
        df["_Nom_norm"].str.lower().str.contains(s, na=False)
        | df["_Dossier_norm"].str.lower().str.contains(s, na=False)
    ].copy()
else:
    df_filtered = df.copy()

# Liste affichée : "Dossier N — Nom"
df_filtered["_label"] = df_filtered.apply(
    lambda r: f"{norm_txt(r.get('Dossier N'))} — {norm_txt(r.get('Nom'))}",
    axis=1
)

options = df_filtered["_label"].tolist()

if not options:
    st.warning("Aucun dossier ne correspond à la recherche.")
    st.stop()

selected_label = st.selectbox("Sélectionner un dossier", options)

selected = df_filtered[df_filtered["_label"] == selected_label].iloc[0][DOSSIER_COL]
row = df[df[DOSSIER_COL] == str(selected)].iloc[0]
idx = row.name

# ---------------------------------------------------------
# INFORMATIONS GÉNÉRALES
# ---------------------------------------------------------
st.markdown("---")
st.subheader(f"📄 Dossier {selected}")

c1, c2, c3 = st.columns(3)
nom = c1.text_input("Nom", row.get("Nom", ""))
date_dossier = c2.date_input("Date du dossier", safe_date(row.get("Date")))
visa = c3.text_input("Visa", row.get("Visa", ""))

c4, c5 = st.columns(2)
categorie = c4.text_input("Catégorie", row.get("Categories", ""))
sous_categorie = c5.text_input("Sous-catégorie", row.get("Sous-categories", ""))

commentaire = st.text_area("📝 Commentaire", row.get("Commentaire", ""))

# ---------------------------------------------------------
# TARIF VISA (CALCUL AUTO)
# ---------------------------------------------------------
tarif_auto = get_tarif_for_visa(
    visa,
    date_dossier,
    tarifs
)

st.subheader("💰 Facturation")

f1, f2, f3 = st.columns(3)

tarif_applique = f1.number_input(
    "Montant honoraires (US $)",
    value=to_float(row.get("Montant honoraires (US $)", tarif_auto)),
    step=50.0
)

tarif_modifie = f2.checkbox(
    "Tarif modifié manuellement",
    value=bool(row.get("Tarif modifie manuellement", False))
)

autres_frais = f3.number_input(
    "Autres frais (US $)",
    value=to_float(row.get("Autres frais (US $)", 0)),
    step=10.0
)

total_facture = tarif_applique + autres_frais
st.info(f"💵 Total facturé : **${total_facture:,.2f}**")

# ---------------------------------------------------------
# ACOMPTES
# ---------------------------------------------------------
st.subheader("🏦 Paiements")

ac_cols = st.columns(4)
acomptes = {}

for i in range(1, 5):
    acomptes[i] = ac_cols[i - 1].number_input(
        f"Acompte {i}",
        value=to_float(row.get(f"Acompte {i}", 0)),
        step=50.0
    )

total_encaisse = sum(acomptes.values())
solde = total_facture - total_encaisse

st.success(f"💰 Total encaissé : ${total_encaisse:,.2f}")
st.warning(f"📉 Solde dû : ${solde:,.2f}")

# ---------------------------------------------------------
# ESCROW
# ---------------------------------------------------------
st.subheader("💼 Escrow")

escrow_actif = st.checkbox(
    "Escrow actif",
    value=normalize_bool(row.get("Escrow", False))
)

# ---------------------------------------------------------
# STATUTS
# ---------------------------------------------------------
st.subheader("📦 Statuts du dossier")

s1, s2, s3, s4, s5 = st.columns(5)

envoye = s1.checkbox("Dossier envoyé", normalize_bool(row.get("Dossier envoye")))
accepte = s2.checkbox("Dossier accepté", normalize_bool(row.get("Dossier accepte")))
refuse = s3.checkbox("Dossier refusé", normalize_bool(row.get("Dossier refuse")))
annule = s4.checkbox("Dossier annulé", normalize_bool(row.get("Dossier Annule")))
rfe = s5.checkbox("RFE", normalize_bool(row.get("RFE")))

# ---------------------------------------------------------
# SAUVEGARDE
# ---------------------------------------------------------
if st.button("💾 Enregistrer les modifications", type="primary"):

    # Infos générales
    df.loc[idx, "Nom"] = nom
    df.loc[idx, "Date"] = str(date_dossier)
    df.loc[idx, "Visa"] = visa
    df.loc[idx, "Categories"] = categorie
    df.loc[idx, "Sous-categories"] = sous_categorie
    df.loc[idx, "Commentaire"] = commentaire

    # Facturation
    df.loc[idx, "Tarif modifie manuellement"] = bool(tarif_modifie)
    df.loc[idx, "Montant honoraires (US $)"] = float(tarif_applique or 0)
    df.loc[idx, "Autres frais (US $)"] = float(autres_frais or 0)

    # Acomptes
    for i in range(1, 5):
        df.loc[idx, f"Acompte {i}"] = float(acomptes[i] or 0)

    # Statuts (centralisé)
    df = update_status_row(
        df,
        idx,
        envoye=envoye,
        accepte=accepte,
        refuse=refuse,
        annule=annule,
        rfe=rfe,
    )

    # Escrow (règle claire)
    if escrow_actif:
        df.loc[idx, "Escrow"] = True
        df.loc[idx, "Escrow_a_reclamer"] = False
        df.loc[idx, "Escrow_reclame"] = False
    else:
        df.loc[idx, "Escrow"] = False

    # Sauvegarde
    db["clients"] = df.drop(columns=[c for c in ["_Nom_norm", "_Dossier_norm", "_label"] if c in df.columns], errors="ignore").to_dict(orient="records")
    save_database(db)

    st.success("✔ Dossier mis à jour avec succès")
    st.rerun()