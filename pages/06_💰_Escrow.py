import streamlit as st
import pandas as pd
from backend.dropbox_utils import load_database, save_database

st.set_page_config(page_title="Escrow", page_icon="💰", layout="wide")
st.title("💰 Gestion des Escrows")

# ---------------------------------------------------------
# LOAD DATABASE
# ---------------------------------------------------------
db = load_database()
clients = db.get("clients", [])

if not clients:
    st.warning("Aucun dossier trouvé.")
    st.stop()

df = pd.DataFrame(clients)
st.markdown("### DEBUG — État réel des colonnes Escrow")
st.dataframe(df[["Dossier N", "Escrow", "Escrow_a_reclamer", "Escrow_reclame", "Dossier envoye"]])


# ---------------------------------------------------------
# NORMALISATION FINALE
# ---------------------------------------------------------
def normalize_bool(x):
    if isinstance(x, bool):
        return x
    if str(x).lower() in ["1", "true", "yes", "oui"]:
        return True
    return False

for col in ["Escrow", "Escrow_a_reclamer", "Escrow_reclame", "Dossier envoye"]:
    if col not in df.columns:
        df[col] = False
    df[col] = df[col].apply(normalize_bool)

df["Dossier N"] = pd.to_numeric(df["Dossier N"], errors="coerce").astype("Int64")

# ---------------------------------------------------------
# TABLEAUX ESCROW
# ---------------------------------------------------------
st.subheader("🟦 Escrow en cours")
escrow_cours = df[(df["Escrow"] == True) & (df["Escrow_a_reclamer"] == False)]
st.dataframe(escrow_cours, use_container_width=True)

st.subheader("🟧 Escrow à réclamer (dossier envoyé)")
escrow_reclamer = df[(df["Escrow_a_reclamer"] == True) & (df["Escrow_reclame"] == False)]
st.dataframe(escrow_reclamer, use_container_width=True)

st.subheader("🟩 Escrow réclamé")
escrow_reclame = df[df["Escrow_reclame"] == True]
st.dataframe(escrow_reclame, use_container_width=True)

# ---------------------------------------------------------
# 🔥 NOTIFICATIONS VISUELLES
# ---------------------------------------------------------
if len(escrow_reclamer) > 0:
    st.warning(f"⚠️ {len(escrow_reclamer)} dossier(s) doivent être réclamés !")

if len(escrow_cours) > 0:
    st.info(f"ℹ️ {len(escrow_cours)} dossier(s) encore en Escrow en cours.")

# ---------------------------------------------------------
# ACTION : PASSER UN DOSSIER À “RECLAMÉ”
# ---------------------------------------------------------
st.markdown("---")
st.subheader("📝 Marquer un escrow comme réclamé")

liste_reclamer = escrow_reclamer["Dossier N"].dropna().astype(int).tolist()

if len(liste_reclamer) == 0:
    st.success("Aucun dossier à réclamer.")
else:
    choix = st.selectbox("Sélectionner un dossier :", liste_reclamer)

    if st.button("Confirmer réclamation ✔"):
        df.loc[df["Dossier N"] == choix, "Escrow_a_reclamer"] = False
        df.loc[df["Dossier N"] == choix, "Escrow_reclame"] = True

        db["clients"] = df.to_dict(orient="records")
        save_database(db)

        st.success(f"✔ Escrow du dossier {choix} marqué comme réclamé.")
        st.rerun()

# ---------------------------------------------------------
# 🔍 TIMELINE ESCROW PAR DOSSIER
# ---------------------------------------------------------
st.markdown("---")
st.subheader("🕒 Historique / Timeline de l’Escrow")

liste_dossiers = df["Dossier N"].dropna().astype(int).tolist()
dossier_timeline = st.selectbox("Choisir un dossier :", liste_dossiers)

if dossier_timeline:
    d = df[df["Dossier N"] == dossier_timeline].iloc[0]

    timeline = []

    # Etat initial
    if d["Escrow"]:
        timeline.append(("Escrow en cours", "🟦"))
    if d["Dossier envoye"]:
        timeline.append(("Dossier envoyé → Escrow à réclamer", "🟧"))
    if d["Escrow_reclame"]:
        timeline.append(("Escrow réclamé", "🟩"))

    st.write("### Timeline du dossier :", dossier_timeline)
    for label, color in timeline:
        st.write(f"{color} **{label}**")

    if len(timeline) == 0:
        st.info("Aucune information d’Escrow disponible pour ce dossier.")

# ---------------------------------------------------------
# BOUTON EXPORT PDF (simple placeholder)
# ---------------------------------------------------------
st.markdown("---")
st.subheader("📄 Export PDF")

if st.button("Générer le PDF du dossier sélectionné"):
    st.info("La génération PDF sera activée dans l’étape suivante (module complet).")
