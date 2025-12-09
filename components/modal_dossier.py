import streamlit as st

def show_dossier_modal(row):
    exp = st.expander(f"📄 Dossier {row['Dossier N']} — {row['Nom']}", expanded=True)

    with exp:
        st.header("📄 Informations générales")
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
        st.write(f"Acompte 1 : {row['Acompte 1']}")
        st.write(f"Acompte 2 : {row['Acompte 2']}")
        st.write(f"Acompte 3 : {row['Acompte 3']}")
        st.write(f"Acompte 4 : {row['Acompte 4']}")

        st.divider()

        st.header("📦 Statuts")
        st.write(f"Envoyé : {row['Dossier_envoye']}")
        st.write(f"Accepté : {row['Dossier accepte']}")
        st.write(f"Refusé : {row['Dossier refuse']}")
        st.write(f"Annulé : {row['Dossier Annule']}")
        st.write(f"RFE : {row['RFE']}")

        st.divider()

        st.header("🔧 Actions rapides")
        st.write("➡️ [Modifier ce dossier](/03_✏️_Modifier_dossier)")
        st.write("➡️ [Voir Escrow](/06_💰_Escrow)")
