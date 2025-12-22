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
df[DOSSIER_COL] = df[DOSSIER_COL].astype(str)

# ---------------------------------------------------------
# HELPERS (AJOUTS SANS CASSER)
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


def get_existing_parents(df_clients: pd.DataFrame):
    parents = set()
    if df_clients.empty or "Dossier N" not in df_clients.columns:
        return []
    for v in df_clients["Dossier N"].astype(str).tolist():
        p, _ = parse_parent_and_index(v)
        if p:
            parents.add(p)
    return sorted(parents)


def get_souscats(visa_df: pd.DataFrame, categorie: str):
    if visa_df.empty or "Categories" not in visa_df.columns or "Sous-categories" not in visa_df.columns:
        return []
    return sorted(
        visa_df[visa_df["Categories"] == categorie]["Sous-categories"]
        .dropna()
        .unique()
        .tolist()
    )


def get_visas(visa_df: pd.DataFrame, souscat: str):
    # IMPORTANT: visa doit dépendre de Sous-categories
    if visa_df.empty or "Sous-categories" not in visa_df.columns or "Visa" not in visa_df.columns:
        return []
    return sorted(
        visa_df[visa_df["Sous-categories"] == souscat]["Visa"]
        .dropna()
        .unique()
        .tolist()
    )


# Référence Visa pour dropdowns (sans casser si absent)
visa_ref = pd.DataFrame(db.get("visa", []))

# ---------------------------------------------------------
# SÉLECTION DOSSIER
# ---------------------------------------------------------
liste = sorted(df[DOSSIER_COL].unique())
selected = st.selectbox("Sélectionner un dossier", liste)

row = df[df[DOSSIER_COL] == selected].iloc[0]
idx = row.name

# =========================================================
# AJOUT: TYPE DOSSIER (PARENT / FILS) + DOSSIER PARENT
# (sans casser : si l'utilisateur ne touche pas, on reconstruit à partir de Dossier N)
# =========================================================
st.subheader("🧭 Type de dossier (Parent / Fils)")

p_current, i_current = parse_parent_and_index(selected)
is_child_current = (i_current is not None and i_current > 0)

colTD1, colTD2 = st.columns([2, 3])
type_dossier = colTD1.radio(
    "Ce dossier est :",
    ["Dossier parent", "Sous-dossier (fils)"],
    index=1 if is_child_current else 0,
    horizontal=True,
)

parents_list = get_existing_parents(df)

# Valeur par défaut dossier parent
default_parent = p_current if p_current else (parents_list[0] if parents_list else None)

if type_dossier == "Sous-dossier (fils)":
    if not parents_list:
        colTD2.warning("Aucun dossier parent existant. Créez d’abord un dossier parent.")
        dossier_parent_selected = None
    else:
        dossier_parent_selected = colTD2.selectbox(
            "Dossier parent",
            parents_list,
            index=parents_list.index(default_parent) if default_parent in parents_list else 0,
        )
else:
    dossier_parent_selected = None
    colTD2.info("Un dossier parent n’a pas de dossier parent associé.")

# ---------------------------------------------------------
# INFORMATIONS GÉNÉRALES (inchangé sauf catégories/visa maintenant liés)
# ---------------------------------------------------------
st.subheader(f"📄 Dossier {selected}")

c1, c2, c3 = st.columns(3)
nom = c1.text_input("Nom", row.get("Nom", ""))
date_dossier = c2.date_input("Date du dossier", safe_date(row.get("Date")))

# ---------------------------------------------------------
# CATEGORIE / SOUS-CATEGORIE / VISA LIÉS
# - AVANT: text_input
# - AJOUT demandé: Visa doit dépendre de sous-catégorie
# - On ne casse pas : si visa_ref vide, on retombe sur text_input comme avant.
# ---------------------------------------------------------
st.subheader("🧩 Catégorisation")

if visa_ref.empty or not {"Categories", "Sous-categories", "Visa"}.issubset(set(visa_ref.columns)):
    # Fallback strict: comportement historique (pas de casse)
    st.info("Référentiel Visa indisponible : saisie manuelle conservée.")
    ccat1, ccat2, ccat3 = st.columns(3)
    categorie = ccat1.text_input("Catégorie", row.get("Categories", ""))
    sous_categorie = ccat2.text_input("Sous-catégorie", row.get("Sous-categories", ""))
    visa = ccat3.text_input("Visa", row.get("Visa", ""))
else:
    ccat1, ccat2, ccat3 = st.columns(3)

    cat_list = [""] + sorted(visa_ref["Categories"].dropna().unique().tolist())
    current_cat = row.get("Categories", "") or ""
    if current_cat not in cat_list:
        cat_list = [current_cat] + cat_list  # permet de garder une valeur existante non référencée
    categorie = ccat1.selectbox("Catégorie", cat_list, index=cat_list.index(current_cat))

    sous_list = [""] + get_souscats(visa_ref, categorie) if categorie else [""]
    current_sous = row.get("Sous-categories", "") or ""
    if current_sous not in sous_list:
        sous_list = [current_sous] + sous_list
    sous_categorie = ccat2.selectbox("Sous-catégorie", sous_list, index=sous_list.index(current_sous))

    visa_list = [""] + get_visas(visa_ref, sous_categorie) if sous_categorie else [""]
    current_visa = row.get("Visa", "") or ""
    if current_visa not in visa_list:
        visa_list = [current_visa] + visa_list
    visa = ccat3.selectbox("Visa", visa_list, index=visa_list.index(current_visa))

commentaire = st.text_area("📝 Commentaire", row.get("Commentaire", ""))

# ---------------------------------------------------------
# TARIF VISA
# ---------------------------------------------------------
tarif_auto = get_tarif_for_visa(
    visa,
    date_dossier,
    tarifs
)

st.subheader("💰 Facturation")

f1, f2, f3 = st.columns(3)

tarif_applique = f1.number_input(
    "Tarif Visa appliqué",
    value=to_float(row.get("Tarif visa applique", tarif_auto)),
    step=50.0
)

tarif_modifie = f2.checkbox(
    "Tarif modifié manuellement",
    value=row.get("Tarif modifie manuellement", False)
)

autres_frais = f3.number_input(
    "Autres frais",
    value=to_float(row.get("Autres frais (US $)", 0)),
    step=10.0
)

total_facture = tarif_applique + autres_frais
st.info(f"💵 Total facturé : **${total_facture:,.2f}**")

# ---------------------------------------------------------
# ACOMPTES + (AJOUT) DATE + MODE SOUS CHAQUE ACOMPTE
# (sans casser: on ne change pas les champs existants, on ajoute Mode Acompte i / Date Paiement i + compat Date Acompte i)
# ---------------------------------------------------------
st.subheader("🏦 Paiements")

modes = ["", "Chèque", "CB", "Virement", "Venmo"]

acomptes = {}
modes_ac = {}
dates_ac = {}

for i in range(1, 5):
    st.markdown(f"### Acompte {i}")
    p1, p2, p3 = st.columns(3)

    acomptes[i] = p1.number_input(
        f"Montant Acompte {i}",
        value=to_float(row.get(f"Acompte {i}", 0)),
        step=50.0,
        key=f"ac_{i}_{selected}",
    )

    # Mode: on lit d'abord "Mode Acompte i" puis fallback "mode de paiement" uniquement pour acompte 1 si présent
    default_mode = row.get(f"Mode Acompte {i}", "")
    if i == 1 and (not default_mode):
        default_mode = row.get("mode de paiement", "") or ""
    if default_mode not in modes:
        default_mode = ""

    modes_ac[i] = p2.selectbox(
        f"Mode de règlement (Acompte {i})",
        options=modes,
        index=modes.index(default_mode),
        key=f"mode_{i}_{selected}",
    )

    # Date: on lit "Date Paiement i" puis fallback "Date Acompte i"
    default_date = row.get(f"Date Paiement {i}", None)
    if not default_date:
        default_date = row.get(f"Date Acompte {i}", None)

    dates_ac[i] = p3.date_input(
        f"Date paiement (Acompte {i})",
        value=safe_date(default_date),
        key=f"date_{i}_{selected}",
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

    # Catégorisation (liée)
    df.loc[idx, "Visa"] = visa
    df.loc[idx, "Categories"] = categorie
    df.loc[idx, "Sous-categories"] = sous_categorie

    df.loc[idx, "Commentaire"] = commentaire

    # Facturation
    df.loc[idx, "Tarif visa applique"] = tarif_applique
    df.loc[idx, "Tarif modifie manuellement"] = bool(tarif_modifie)
    df.loc[idx, "Montant honoraires (US $)"] = tarif_applique
    df.loc[idx, "Autres frais (US $)"] = autres_frais

    # Acomptes (existants + AJOUTS date/mode)
    for i in range(1, 5):
        df.loc[idx, f"Acompte {i}"] = acomptes[i]

        # AJOUT: mode + date paiement (conservation)
        df.loc[idx, f"Mode Acompte {i}"] = modes_ac[i]

        # Date -> string compatible JSON
        date_str = ""
        try:
            if dates_ac[i]:
                date_str = str(dates_ac[i])
        except Exception:
            date_str = ""
        df.loc[idx, f"Date Paiement {i}"] = date_str

        # Compat: remplir aussi "Date Acompte i" si existe déjà dans votre JSON (sans casser)
        if f"Date Acompte {i}" in df.columns:
            df.loc[idx, f"Date Acompte {i}"] = date_str

        # Compat: pour acompte 1, garder "mode de paiement" si vous l’utilisez encore
        if i == 1 and "mode de paiement" in df.columns:
            df.loc[idx, "mode de paiement"] = modes_ac[i]

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

    # AJOUT: persistance parent/fils dans le JSON (sans toucher Dossier N)
    # - Dossier Type: "parent" / "fils"
    # - Dossier Parent: numéro parent (string) si fils, sinon ""
    if type_dossier == "Sous-dossier (fils)" and dossier_parent_selected is not None:
        df.loc[idx, "Dossier Type"] = "fils"
        df.loc[idx, "Dossier Parent"] = str(int(dossier_parent_selected))
    else:
        df.loc[idx, "Dossier Type"] = "parent"
        df.loc[idx, "Dossier Parent"] = ""

    # Sauvegarde
    db["clients"] = df.to_dict(orient="records")
    save_database(db)

    st.success("✔ Dossier mis à jour avec succès")
    st.rerun()
