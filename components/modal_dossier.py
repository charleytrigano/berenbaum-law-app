import streamlit as st
import pandas as pd

def show_dossier_modal(row):
    with st.modal(f"Dossier {row['Dossier N']} — {row['Nom']}"):
        st.header("📄 Informations générales")
        st.write(f"**Nom :** {row['Nom']}")
        st.write(f"**Catégorie :** {row['Categories']}")
        st.write(f"**Sous-catégorie :** {row['Sous-categories']}")
        st.write(f"**Visa :** {row['Visa']}")
        st.write(f"**Date :** {row['Date']}")

        st.divider()

        st.header("💰 Escrow")
        if row["Escrow"]:
            st.success("Escrow en cours")
        elif row["Escrow_a_reclamer"]:
            st.warning("Escrow à réclamer")
        elif row["Escrow_reclame"]:
            st.info("Escrow réclamé")
        else:
            st.error("Aucun escrow")

        st.divider()

        st.header("🏦 Paiements")
        total = (
            float(row["Acompte 1"])
            + float(row["Acompte 2"])
            + float(row["Acompte 3"])
            + float(row["Acompte 4"])
        )
        st.write(f"**Acompte total :** {total}$")
        st.write(f"**Montant honoraires :** {row['Montant honoraires (US $)']}")

        st.divider()

        st.header("📦 Statuts")
        st.write(f"Envoyé : {row['Dossier_envoye']}")
        st.write(f"Accepté : {row['Dossier accepte']}")
        st.write(f"Refusé : {row['Dossier refuse']}")

        st.divider()

        st.header("🛠️ Actions")
        st.write("👉 [Modifier ce dossier](/03_✏️_Modifier_dossier)")
        st.write("👉 [Voir escrow](/06_💰_Escrow)")
