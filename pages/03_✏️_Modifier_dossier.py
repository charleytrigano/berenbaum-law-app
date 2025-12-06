import streamlit as st
import pandas as pd
from datetime import datetime, date
from backend.dropbox_utils import load_database, save_database

st.set_page_config(page_title="Modifier un dossier", page_icon="✏️", layout="wide")
st.title("✏️ Modifier un dossier")

# ---------------------------------------------------------
# Chargement base
# ---------------------------------------------------------
db = load_database()
clients = db.get("clients", [])
historique = db.get("historique_suppressions", [])

df = pd.DataFrame(clients)

if df.empty:
    st.error("❌ Aucun dossier trouvé.")
    st.stop()

DOSSIER_COL = "Dossier N"

# ---------------------------------------------------------
# Fonction sécurisée de conversion numéro de dossier
# ---------------------------------------------------------
def safe_int(value):
    """Convertit proprement un numéro de dossier quel que soit son format."""
    try:
        return int(str(value).strip())
    except:
        return None

# Nettoyage complet des numéros
df[DOSSIER_COL] = df[DOSSIER_COL].apply(safe_int)

# Suppression des lignes invalides
df = df.dropna(subset=[DOSSIER_COL])

# ---------------------------------------------------------
# Liste triée des numéros de dossiers
# ---------------------------------------------------------
liste_dossiers = sorted(df[DOSSIER_COL].astype(int).unique().tolist())

if not liste_dossiers:
    st.error("❌ Aucun numéro de dossier valide détecté.")
    st.stop()

# Sélecteur principal
selected_num = st.selectbox("Sélectionner un dossier", liste_dossiers)

# Charger dossier sélectionné
dossier = df[df[DOSSIER_COL] == selected_num].iloc[0].copy()

# ---------------------------------------------------------
# Fonction date propre
# ---------------------------------------------------------
def clean_date(v):
    if not v:
        return None
    try:
        return pd.to_datetime(v).date()
    except:
        return None

# ---------------------------------------------------------
# Formulaire modification
# ---------------------------------------------------------
st.subheader("Informations principales")

col1, col2, col3 = st.columns(3)
nom = col1.text_input("Nom", value=dossier.get("Nom", ""))
date_dossier = col2.date_input("Date", value=clean_date(dossier.get("Date")) or date.today())

cat = col1.text_input("Catégorie", value=dossier.get("Categories", ""))
souscat = col2.text_input("Sous-catégorie", value=dossier.get("Sous-categories", ""))
visa = col3.text_input("Visa", value=dossier.get("Visa", ""))

st.subheader("💰 Finances")

colA, colB, colC = st.columns(3)
honoraires = colA.number_input("Honoraires (US $)", value=float(dossier.get("Montant honoraires (US $)", 0)))
frais = colB.number_input("Autres frais (US $)", value=float(dossier.get("Autres frais (US $)", 0)))
total = honoraires + frais
colC.metric("Total facturé", f"{total:,.0f} $")

st.subheader("Acomptes")

# Acomptes & dates
def get_float(val): 
    try: return float(val)
    except: return 0.0

colA1, colA2, colA3, colA4 = st.columns(4)
a1 = colA1.number_input("Acompte 1", value=get_float(dossier.get("Acompte 1")))
a2 = colA2.number_input("Acompte 2", value=get_float(dossier.get("Acompte 2")))
a3 = colA3.number_input("Acompte 3", value=get_float(dossier.get("Acompte 3")))
a4 = colA4.number_input("Acompte 4", value=get_float(dossier.get("Acompte 4")))

colD1, colD2, colD3, colD4 = st.columns(4)
da1 = colD1.date_input("Date Acompte 1", value=clean_date(dossier.get("Date Acompte 1")))
da2 = colD2.date_input("Date Acompte 2", value=clean_date(dossier.get("Date Acompte 2")))
da3 = colD3.date_input("Date Acompte 3", value=clean_date(dossier.get("Date Acompte 3")))
da4 = colD4.date_input("Date Acompte 4", value=clean_date(dossier.get("Date Acompte 4")))

st.subheader("📌 Statuts dossier")
colS1, colS2, colS3, colS4, colS5 = st.columns(5)

envoye = colS1.checkbox("Dossier envoyé", value=bool(dossier.get("Dossier envoye", False)))
accepte = colS2.checkbox("Dossier accepté", value=bool(dossier.get("Dossier accepte", False)))
refuse = colS3.checkbox("Dossier refusé", value=bool(dossier.get("Dossier refuse", False)))
annule = colS4.checkbox("Dossier annulé", value=bool(dossier.get("Dossier Annule", False)))
rfe = colS5.checkbox("RFE", value=bool(dossier.get("RFE", False)))

st.subheader("📦 Escrow")
escrow = st.checkbox("Escrow activé", value=bool(dossier.get("Escrow", False)))

# ---------------------------------------------------------
# Sauvegarde
# ---------------------------------------------------------
if st.button("💾 Enregistrer les modifications"):
    idx = df.index[df[DOSSIER_COL] == selected_num][0]

    df.at[idx, "Nom"] = nom
    df.at[idx, "Date"] = str(date_dossier)
    df.at[idx, "Categories"] = cat
    df.at[idx, "Sous-categories"] = souscat
    df.at[idx, "Visa"] = visa

    df.at[idx, "Montant honoraires (US $)"] = honoraires
    df.at[idx, "Autres frais (US $)"] = frais

    df.at[idx, "Acompte 1"] = a1
    df.at[idx, "Acompte 2"] = a2
    df.at[idx, "Acompte 3"] = a3
    df.at[idx, "Acompte 4"] = a4

    df.at[idx, "Date Acompte 1"] = str(da1) if da1 else ""
    df.at[idx, "Date Acompte 2"] = str(da2) if da2 else ""
    df.at[idx, "Date Acompte 3"] = str(da3) if da3 else ""
    df.at[idx, "Date Acompte 4"] = str(da4) if da4 else ""

    df.at[idx, "Dossier envoye"] = envoye
    df.at[idx, "Dossier accepte"] = accepte
    df.at[idx, "Dossier refuse"] = refuse
    df.at[idx, "Dossier Annule"] = annule
    df.at[idx, "RFE"] = rfe

    df.at[idx, "Escrow"] = escrow

    db["clients"] = df.to_dict(orient="records")
    save_database(db)

    st.success("✅ Dossier mis à jour avec succès !")
    st.experimental_rerun()

# ---------------------------------------------------------
# Suppression dossier
# ---------------------------------------------------------
st.markdown("---")
st.subheader("🗑️ Supprimer ce dossier")

if st.button("❌ Supprimer définitivement"):
    deleted = dossier.copy()
    deleted["supprimé_le"] = datetime.now().isoformat()

    historique.append(deleted)
    db["historique_suppressions"] = historique

    df = df[df[DOSSIER_COL] != selected_num]
    db["clients"] = df.to_dict(orient="records")

    save_database(db)

    st.success("🚮 Dossier supprimé et archivé.")
    st.experimental_rerun()

# ---------------------------------------------------------
# Affichage historique
# ---------------------------------------------------------
st.markdown("---")
st.subheader("📜 Historique des suppressions")

if historique:
    st.dataframe(pd.DataFrame(historique))
else:
    st.info("Aucune suppression enregistrée.")
