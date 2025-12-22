import streamlit as st
import pandas as pd
from datetime import datetime

from utils.sidebar import render_sidebar
from backend.dropbox_utils import load_database, save_database

# =====================================================
# CONFIG
# =====================================================
st.set_page_config(page_title="Nouveau dossier", page_icon="➕", layout="wide")
render_sidebar()
st.title("➕ Nouveau dossier")

# ---------------------------------------------------------
# LOAD DATABASE
# ---------------------------------------------------------
db = load_database()
clients = db.get("clients", [])
visa_raw = pd.DataFrame(db.get("visa", []))

# ---------------------------------------------------------
# FILTRES SIMPLES ET ROBUSTES (VISA)
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
# NUMÉROTATION DOSSIER (support parent + sous-dossier)
# ---------------------------------------------------------
def parse_parent_and_index(dossier_n: str):
    """
    Retourne (parent:int|None, index:int|None)
    Ex:
      "12937"   -> (12937, 0)
      "12937-1" -> (12937, 1)
      "12937-2" -> (12937, 2)
    """
    if dossier_n is None:
        return None, None
    s = str(dossier_n).strip()
    if s == "":
        return None, None
    if "-" in s:
        p, i = s.split("-", 1)
        try:
            return int(float(p)), int(float(i))
        except Exception:
            return None, None
    try:
        return int(float(s)), 0
    except Exception:
        return None, None


def get_existing_parents(clients_list):
    parents = set()
    for c in clients_list:
        p, _ = parse_parent_and_index(c.get("Dossier N", ""))
        if p:
            parents.add(p)
    return sorted(parents)


def next_parent_number(clients_list):
    parents = get_existing_parents(clients_list)
    return (max(parents) + 1) if parents else 13057


def next_child_index(clients_list, parent_number: int):
    max_idx = 0
    for c in clients_list:
        p, i = parse_parent_and_index(c.get("Dossier N", ""))
        if p == parent_number and i is not None:
            if i > max_idx:
                max_idx = i
    return max_idx + 1


# =====================================================
# TYPE DE DOSSIER (Parent / Sous-dossier)
# =====================================================
st.subheader("🧭 Type de dossier")

colT1, colT2 = st.columns([2, 3])

type_dossier = colT1.radio(
    "Créer :",
    ["Dossier parent", "Sous-dossier (fils)"],
    horizontal=True
)

if type_dossier == "Dossier parent":
    parent_num = next_parent_number(clients)
    dossier_n_str = str(parent_num)
    colT2.info(
        f"Un **dossier parent** sera créé avec le numéro **{dossier_n_str}**.\n\n"
        "Pour créer des sous-dossiers, utilisez l’option « Sous-dossier (fils) »."
    )
else:
    parents = get_existing_parents(clients)
    if not parents:
        st.warning("Aucun dossier parent existant. Créez d’abord un dossier parent.")
        st.stop()

    parent_selected = colT2.selectbox("Choisir le dossier parent", parents)
    child_idx = next_child_index(clients, int(parent_selected))
    dossier_n_str = f"{int(parent_selected)}-{child_idx}"
    colT2.info(
        f"Un **sous-dossier** sera créé avec le numéro **{dossier_n_str}** "
        f"(prochain index disponible pour le parent **{int(parent_selected)}**)."
    )

# =====================================================
# FORMULAIRE
# =====================================================
st.subheader("📄 Informations dossier")

col1, col2, col3 = st.columns(3)
col1.text_input("Dossier N", value=dossier_n_str, disabled=True)
nom = col2.text_input("Nom")
date_dossier = col3.date_input("Date de création")

# ---------------- CATEGORIES & VISA ----------------------
st.subheader("🧩 Catégorisation")

colA, colB, colC = st.columns(3)

# Catégories
if not visa_raw.empty and "Categories" in visa_raw.columns:
    cat_list = ["Choisir..."] + sorted(visa_raw["Categories"].dropna().unique().tolist())
else:
    cat_list = ["Choisir..."]

categorie = colA.selectbox("Catégorie", cat_list)

# Sous-catégories
if categorie != "Choisir...":
    souscats = ["Choisir..."] + get_souscats(visa_raw, categorie)
else:
    souscats = ["Choisir..."]

sous_categorie = colB.selectbox("Sous-catégorie", souscats)

# Visa
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

# ---------------- PAIEMENTS ------------------------------
st.subheader("🏦 Paiements (Acompte 1 uniquement)")

colP1, colP2, colP3 = st.columns(3)

a1 = colP1.number_input("Acompte 1", min_value=0.0, step=50.0)

modes = ["", "Chèque", "CB", "Virement", "Venmo"]
mode_a1 = colP2.selectbox("Mode de règlement (Acompte 1)", modes)

date_a1 = colP3.date_input("Date paiement (Acompte 1)", value=None)

# Affichage solde (en se basant sur acompte 1 uniquement ici)
solde = (montant_hon + autres_frais) - a1
st.info(f"💵 Solde restant : **${solde:,.2f}**")

# Escrow + commentaire (inchangés)
escrow = st.checkbox("Mettre en Escrow")
commentaire = st.text_area("📝 Commentaire", "")

# =====================================================
# ENREGISTREMENT
# =====================================================
if st.button("💾 Enregistrer le dossier", type="primary"):

    if nom.strip() == "":
        st.error("❌ Le nom du client est obligatoire.")
        st.stop()

    if categorie == "Choisir..." or sous_categorie == "Choisir..." or visa == "Choisir...":
        st.error("❌ Veuillez sélectionner Catégorie, Sous-catégorie et Visa.")
        st.stop()

    # Sécurité : éviter doublon Dossier N
    existing_ids = set(str(c.get("Dossier N", "")).strip() for c in clients)
    if dossier_n_str in existing_ids:
        st.error(f"❌ Le numéro de dossier **{dossier_n_str}** existe déjà.")
        st.stop()

    # Date paiement acompte 1 en string (compatible JSON)
    date_a1_str = ""
    try:
        if date_a1:
            date_a1_str = str(date_a1)
    except Exception:
        date_a1_str = ""

    new_entry = {
        "Dossier N": dossier_n_str,  # support parent / fils (ex: 12937-1)
        "Nom": nom,
        "Date": str(date_dossier),

        "Categories": categorie,
        "Sous-categories": sous_categorie,
        "Visa": visa,

        "Montant honoraires (US $)": montant_hon,
        "Autres frais (US $)": autres_frais,

        # Acompte 1 + compléments demandés
        "Acompte 1": a1,
        "Date Acompte 1": date_a1_str,
        "Mode Acompte 1": mode_a1,

        # Acomptes 2/3/4 non affichés ici (mais présents, comme avant)
        "Acompte 2": 0.0,
        "Acompte 3": 0.0,
        "Acompte 4": 0.0,
        "Date Acompte 2": "",
        "Date Acompte 3": "",
        "Date Acompte 4": "",
        "Mode Acompte 2": "",
        "Mode Acompte 3": "",
        "Mode Acompte 4": "",

        # ESCROW EN 3 ÉTATS
        "Escrow": bool(escrow),
        "Escrow_a_reclamer": False,
        "Escrow_reclame": False,

        # STATUTS (inchangés)
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

    st.success(f"✔ Dossier **{dossier_n_str}** enregistré avec succès !")
    st.rerun()
