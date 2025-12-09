import streamlit as st

def show_dossier_modal(row):
    # Sécurité : convertir en dictionnaire si Series
    if hasattr(row, "to_dict"):
        row = row.to_dict()

    # Titre du bloc
    exp = st.expander(f"📄 Dossier {row.get('Dossier N', '?')} — {row.get('Nom', '?')}", expanded=True)

    with exp:
        st.header("📄 Informations générales")
        st.write(f"**Catégorie :** {row.get('Categories')}")
        st.write(f"**Sous-catégorie :** {row.get('Sous-categories')}")
        st.write(f"**Visa :** {row.get('Visa')}")
        st.write(f"**Date :** {row.get('Date')}")

        st.divider()

        st.header("💰 Escrow")
        if row.get("Escrow"):
            st.success("Escrow en cours")
        elif row.get("Escrow_a_reclamer"):
            st.warning("Escrow à réclamer")
        elif row.get("Escrow_reclame"):
            st.info("Escrow réclamé")
        else:
            st.error("Aucun escrow")

        st.divider()

        st.header("🏦 Paiements")
        total = 0
        for k in ["Acompte 1", "Acompte 2", "Acompte 3", "Acompte 4"]:
            try:
                total += float(row.get(k, 0))
            except:
                pass
            st.write(f"{k} : {row.get(k)}")

        st.write(f"**Total acomptes : {total} $**")

        st.divider()

        st.header("📦 Statuts")
        st.write(f"Envoyé : {row.get('Dossier_envoye')}")
        st.write(f"Accepté : {row.get('Dossier accepte')}")
        st.write(f"Refusé : {row.get('Dossier refuse')}")
        st.write(f"Annulé : {row.get('Dossier Annule')}")
        st.write(f"RFE : {row.get('RFE')}")

        st.divider()

        st.header("🛠️ Actions rapides")
        st.write("➡️ [Modifier ce dossier](/03_✏️_Modifier_dossier)")
        st.write("➡️ [Voir Escrow](/06_💰_Escrow)")
