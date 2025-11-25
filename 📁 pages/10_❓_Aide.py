import streamlit as st

st.title("❓ Aide & Documentation")

st.subheader("📘 Guide utilisateur")
st.write("""
Bienvenue dans le logiciel Berenbaum Law App.

Ce logiciel vous permet de :
- gérer les dossiers clients  
- suivre les procédures Visa  
- administrer les opérations Escrow  
- effectuer le suivi comptable  
- visualiser des analyses via le Dashboard  
- tout cela en temps réel via Google Sheets
""")

st.subheader("📞 Assistance interne")
st.write("""
- **Contact technique :** développeur  
- **Support comptable :** équipe financière  
- **Escrow / Visa :** service administratif  
""")

st.subheader("💡 Astuces d’utilisation")
st.write("""
- Actualisez une page pour voir les données mises à jour  
- Vérifiez l’onglet Paramètres si vous voyez un message d’erreur Google Sheets  
- Ajoutez toujours les opérations via les formulaires dédiés  
- Toutes les données sont synchronisées dans Google Sheets automatiquement  
""")

st.subheader("📝 FAQ")
st.write("""
**1. Les données ne se chargent pas ?**  
→ Vérifiez la connexion Google Sheets (page Paramètres)

**2. Comment modifier un dossier ?**  
→ Page *Modifier dossier* dans le menu

**3. Comment supprimer un dossier ?**  
→ Dans la page *Modifier dossier*, tout en bas

**4. Comment ajouter un mouvement Escrow ?**  
→ Dans la page *Escrow*, formulaire en haut de page

**5. Comment calculer les soldes ?**  
→ Page Comptabilité → Solde par dossier + Solde global
""")
