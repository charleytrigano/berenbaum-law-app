import streamlit as st
from utils.sidebar import render_sidebar
render_sidebar()
import pandas as pd
from backend.dropbox_utils import load_database, save_database

st.set_page_config(page_title="Nouveau dossier", page_icon="➕", layout="wide")
st.title("➕ Nouveau dossier")

# ---------------------------------------------------------
# LOAD DATABASE
# ---------------------------------------------------------
db = load_database()
clients = db.get("clients", [])
visa_raw = pd.DataFrame(db.get("visa", []))

# ---------------------------------------------------------
# FILTRES SIMPLES ET ROBUSTES
# ---------------------------------------------------------
def get_souscats(df, categorie):
    if df.empty or "Categories" not in df.columns or "Sous-categories" not in df.columns:
        return []
    return sorted(
        df[df["Categories"] == categorie]["Sous-categories"]
        .dropna()
        .unique()
        .tolist()
    )

def get_visas(df, souscat):
    if df.empty or "Sous-categories" not in df.columns or "Visa" not in df.columns:
        return []
    return sorted(
        df[df["Sous-categories"] == souscat]["Visa"]
        .dropna()
        .unique()
        .tolist()
    )

# ---------------------------------------------------------
# NUMÉRO DOSSIER
# ---------------------------------------------------------
def nouveau_numero():
    nums = []
    for item in clients:
        try:
            # On ignore les formats "12937-1" ici
            n_raw = str(item.get("Dossier N", "")).strip()
            if n_raw == "":
                continue
            # Si c'est un sous-dossier, on prend la partie avant "-"
            n_main = n_raw.split("-")[0]
            n = int(float(n_main))
            if n > 0:
                nums.append(n)
        except Exception:
            pass
    return max(nums) + 1 if nums else 13057

new_id = nouveau_numero()

# ---------------------------------------------------------
# FORMULAIRE
# ---------------------------------------------------------
st.subheader("📄 Informations dossier")

col1, col2, col3 = st.columns(3)
col1.text_input("Dossier N", value=str(new_id), disabled=True)
nom = col2.text_input("Nom")
date_dossier = col3.date_input("Date de création")

# ---------------- CATEGORIES & VISA ----------------------
st.subheader("🧩 Catégorisation")

colA, colB, colC = st.columns(3)

cat_list = ["Choisir..."]
if not visa_raw.empty and "Categories" in visa_raw.columns:
    cat_list += sorted(visa_raw["Categories"].dropna().unique().tolist())

categorie = colA.selectbox("Catégorie", cat_list)

if categorie != "Choisir...":
    souscats = ["Choisir..."] + get_souscats(visa_raw, categorie)
else:
    souscats = ["Choisir..."]

sous_categorie = colB.selectbox("Sous-catégorie", souscats)

if sous_categorie != "Choisir...":
    visa_list = ["Choisir..."] + get_visas(visa_raw, sous_categorie)
else:
    visa_list = ["Choisir..."]

visa = colC.selectbox("Visa", visa_list)

# ---------------- FINANCES ------------------------------
st.subheader("💰 Facturation")

colF1, colF2, colF3 = st.columns(3)
montant_hon = colF1.number_input("Montant honoraires (US $)", min_value=0.0, step=50.0)
autres_frais = colF2.number_input("Autres frais (US $)", min_value=0.0, step=10.0)
colF3.number_input("Total facturé", value=montant_hon + autres_frais, disabled=True)

# ---------------- ACOMPTE 1 UNIQUEMENT -------------------
st.subheader("🏦 Paiement – Acompte 1")

modes = ["", "Chèque", "CB", "Virement", "Venmo"]

colP1, colP2, colP3 = st.columns(3)
a1 = colP1.number_input("Acompte 1", min_value=0.0, step=50.0)
mode_a1 = colP2.selectbox("Mode de règlement (Acompte 1)", modes, index=0)
date_a1 = colP3.date_input("Date paiement (Acompte 1)")

# Acompte 2/3/4 : invisibles ici, mais conservés dans la base (NE RIEN CASSER)
a2, a3, a4 = 0.0, 0.0, 0.0

solde = (montant_hon + autres_frais) - (a1 + a2 + a3 + a4)
st.info(f"💵 Solde restant : **${solde:,.2f}**")

escrow = st.checkbox("Mettre en Escrow (Acompte 1 uniquement)")
commentaire = st.text_area("📝 Commentaire", "")

# ---------------------------------------------------------
# ENREGISTREMENT
# ---------------------------------------------------------
if st.button("💾 Enregistrer le dossier", type="primary"):

    if nom.strip() == "":
        st.error("❌ Le nom du client est obligatoire.")
        st.stop()

    if categorie == "Choisir..." or sous_categorie == "Choisir..." or visa == "Choisir...":
        st.error("❌ Veuillez sélectionner Catégorie, Sous-catégorie et Visa.")
        st.stop()

    new_entry = {
        "Dossier N": str(new_id),  # on garde string pour compatibilité future (sous-dossiers)
        "Nom": nom,
        "Date": str(date_dossier),

        "Categories": categorie,
        "Sous-categories": sous_categorie,
        "Visa": visa,

        "Montant honoraires (US $)": float(montant_hon),
        "Autres frais (US $)": float(autres_frais),

        # ACOMPTES
        "Acompte 1": float(a1),
        "Acompte 2": float(a2),
        "Acompte 3": float(a3),
        "Acompte 4": float(a4),

        # Dates JSON historiques
        "Date Acompte 1": str(date_a1) if date_a1 else "",
        "Date Acompte 2": "",
        "Date Acompte 3": "",
        "Date Acompte 4": "",

        # Compat Modifier_dossier (tu l’utilises déjà)
        "Mode Acompte 1": mode_a1,
        "Mode Acompte 2": "",
        "Mode Acompte 3": "",
        "Mode Acompte 4": "",
        "Date Paiement 1": str(date_a1) if date_a1 else "",
        "Date Paiement 2": "",
        "Date Paiement 3": "",
        "Date Paiement 4": "",

        # Champ legacy conservé (pour ne rien casser)
        "mode de paiement": mode_a1,

        # ESCROW EN 3 ÉTATS
        "Escrow": bool(escrow),
        "Escrow_a_reclamer": False,
        "Escrow_reclame": False,

        # STATUTS (bool)
        "Dossier envoye": False,
        "Dossier accepte": False,
        "Dossier refuse": False,
        "Dossier Annule": False,
        "RFE": False,

        "Date envoi": "",
        "Date acceptation": "",
        "Date refus": "",
        "Date annulation": "",
        "Date reclamation": "",

        "Commentaire": commentaire,
    }

    clients.append(new_entry)
    db["clients"] = clients
    save_database(db)

    st.success(f"✔ Dossier **{new_entry['Dossier N']}** enregistré avec succès !")
    st.rerun()
