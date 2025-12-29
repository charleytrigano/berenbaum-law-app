import streamlit as st
import pandas as pd

from utils.sidebar import render_sidebar
from backend.dropbox_utils import load_database, save_database

# =====================================================
# CONFIG
# =====================================================
st.set_page_config(page_title="🛂 Visa", page_icon="🛂", layout="wide")
render_sidebar()
st.title("🛂 Référentiel Visa (Création / Modification)")

# =====================================================
# LOAD DB
# =====================================================
db = load_database()
visa_list = db.get("visa", [])

if not isinstance(visa_list, list):
    visa_list = []

df = pd.DataFrame(visa_list)

# Harmonisation colonnes minimales attendues
for col in ["Categories", "Sous-categories", "Visa"]:
    if col not in df.columns:
        df[col] = ""

df = df.fillna("")

# =====================================================
# OUTILS
# =====================================================
def normalize_text(v):
    return str(v or "").strip()

def make_key(row):
    # clé stable pour retrouver une ligne
    return (
        normalize_text(row.get("Categories", "")),
        normalize_text(row.get("Sous-categories", "")),
        normalize_text(row.get("Visa", "")),
    )

def rebuild_db_from_df(df_in):
    out = df_in.copy()
    out = out.fillna("")
    db["visa"] = out.to_dict(orient="records")
    save_database(db)

# =====================================================
# VUE TABLE
# =====================================================
st.subheader("📋 Table des visas (référence)")

cols_show = [c for c in ["Categories", "Sous-categories", "Visa"] if c in df.columns]
st.dataframe(df[cols_show].sort_values(cols_show), use_container_width=True, height=360)

st.markdown("---")

# =====================================================
# MODE : MODIFIER / AJOUTER
# =====================================================
cA, cB = st.columns([2, 1])

with cA:
    st.subheader("✏️ Modifier un visa existant")

    if df.empty:
        st.info("Aucun visa dans la base. Utilise l’encart 'Ajouter' pour en créer.")
    else:
        # Liste de sélection lisible
        df["_label"] = df.apply(
            lambda r: f"{normalize_text(r['Visa'])}  |  {normalize_text(r['Categories'])} → {normalize_text(r['Sous-categories'])}",
            axis=1,
        )
        labels = df["_label"].tolist()
        selected_label = st.selectbox("Sélectionner un visa", labels)

        row_sel = df[df["_label"] == selected_label].iloc[0].to_dict()
        old_key = make_key(row_sel)

        with st.form("edit_visa_form"):
            e1, e2, e3 = st.columns(3)
            new_cat = e1.text_input("Catégorie", value=normalize_text(row_sel.get("Categories", "")))
            new_sous = e2.text_input("Sous-catégorie", value=normalize_text(row_sel.get("Sous-categories", "")))
            new_visa = e3.text_input("Visa", value=normalize_text(row_sel.get("Visa", "")))

            # Si tu as d’autres colonnes dans visa.xlsx/json (ex: Prix, Notes), elles resteront intactes
            submitted = st.form_submit_button("💾 Enregistrer la modification", type="primary")

        if submitted:
            new_cat = normalize_text(new_cat)
            new_sous = normalize_text(new_sous)
            new_visa = normalize_text(new_visa)

            if not new_cat or not new_sous or not new_visa:
                st.error("❌ Catégorie, Sous-catégorie et Visa sont obligatoires.")
                st.stop()

            # Mise à jour de la ligne (on modifie uniquement ces 3 champs)
            # On repère la ligne par l’ancienne clé.
            mask = (
                (df["Categories"].apply(normalize_text) == old_key[0]) &
                (df["Sous-categories"].apply(normalize_text) == old_key[1]) &
                (df["Visa"].apply(normalize_text) == old_key[2])
            )

            if mask.sum() == 0:
                st.error("❌ Impossible de retrouver la ligne à modifier (conflit de clé).")
                st.stop()

            # Vérifie collision (si on renomme vers un visa déjà existant)
            new_key = (new_cat, new_sous, new_visa)
            collision = (
                (df["Categories"].apply(normalize_text) == new_key[0]) &
                (df["Sous-categories"].apply(normalize_text) == new_key[1]) &
                (df["Visa"].apply(normalize_text) == new_key[2])
            )
            # Collision autorisée uniquement si on reste sur la même ligne
            if collision.sum() > 0 and new_key != old_key:
                st.error("❌ Ce visa existe déjà (doublon).")
                st.stop()

            df.loc[mask, "Categories"] = new_cat
            df.loc[mask, "Sous-categories"] = new_sous
            df.loc[mask, "Visa"] = new_visa

            # Nettoyage colonne label avant sauvegarde
            df2 = df.drop(columns=[c for c in ["_label"] if c in df.columns], errors="ignore")
            rebuild_db_from_df(df2)

            st.success("✔ Visa modifié et sauvegardé.")
            st.rerun()

with cB:
    st.subheader("➕ Ajouter / 🗑 Supprimer")

    st.markdown("### ➕ Ajouter un visa")
    with st.form("add_visa_form"):
        a1 = st.text_input("Catégorie (nouveau)")
        a2 = st.text_input("Sous-catégorie (nouveau)")
        a3 = st.text_input("Visa (nouveau)")
        add_ok = st.form_submit_button("➕ Ajouter", type="primary")

    if add_ok:
        a1 = normalize_text(a1)
        a2 = normalize_text(a2)
        a3 = normalize_text(a3)

        if not a1 or not a2 or not a3:
            st.error("❌ Catégorie, Sous-catégorie et Visa sont obligatoires.")
            st.stop()

        exists = (
            (df["Categories"].apply(normalize_text) == a1) &
            (df["Sous-categories"].apply(normalize_text) == a2) &
            (df["Visa"].apply(normalize_text) == a3)
        )
        if exists.any():
            st.error("❌ Ce visa existe déjà.")
            st.stop()

        new_row = {"Categories": a1, "Sous-categories": a2, "Visa": a3}
        df2 = df.drop(columns=[c for c in ["_label"] if c in df.columns], errors="ignore").copy()
        df2 = pd.concat([df2, pd.DataFrame([new_row])], ignore_index=True)
        rebuild_db_from_df(df2)

        st.success("✔ Visa ajouté.")
        st.rerun()

    st.markdown("---")
    st.markdown("### 🗑 Supprimer un visa")

    if df.empty:
        st.info("Aucun visa à supprimer.")
    else:
        # reconstruction labels si besoin
        tmp = df.drop(columns=[c for c in ["_label"] if c in df.columns], errors="ignore").copy()
        tmp["_label2"] = tmp.apply(
            lambda r: f"{normalize_text(r['Visa'])}  |  {normalize_text(r['Categories'])} → {normalize_text(r['Sous-categories'])}",
            axis=1,
        )
        del_label = st.selectbox("Sélectionner à supprimer", tmp["_label2"].tolist(), key="del_select")

        if st.button("🗑 Supprimer définitivement", type="secondary"):
            row_del = tmp[tmp["_label2"] == del_label].iloc[0].to_dict()
            key_del = make_key(row_del)

            mask_del = (
                (tmp["Categories"].apply(normalize_text) == key_del[0]) &
                (tmp["Sous-categories"].apply(normalize_text) == key_del[1]) &
                (tmp["Visa"].apply(normalize_text) == key_del[2])
            )

            df2 = tmp.loc[~mask_del].drop(columns=["_label2"], errors="ignore").copy()
            rebuild_db_from_df(df2)

            st.success("✔ Visa supprimé.")
            st.rerun()