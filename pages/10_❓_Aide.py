import streamlit as st
from utils.sidebar import render_sidebar

# ---------------------------------------------------------
# CONFIG
# ---------------------------------------------------------
st.set_page_config(
    page_title="❓ Aide & Mode d’emploi",
    page_icon="❓",
    layout="wide"
)
render_sidebar()

st.title("❓ Aide & Mode d’emploi – Berenbaum Law App")

st.markdown("""
Bienvenue dans **Berenbaum Law App**.  
Ce guide explique **pas à pas** comment utiliser l’application, même **sans aucune connaissance technique**.
""")

st.markdown("---")

# =========================================================
# NAVIGATION
# =========================================================
st.header("🧭 Navigation générale")

st.markdown("""
L’application est organisée en **onglets**, accessibles depuis la barre latérale à gauche.

### Onglets principaux :
- 🏠 Dashboard  
- 📁 Liste des dossiers  
- ➕ Nouveau dossier  
- ✏️ Modifier dossier  
- 📄 Fiche dossier  
- 📁 Fiche groupe dossier  
- 📊 Analyses  
- 💰 Escrow  
- 💲 Tarifs  
- 📤 Export Excel / JSON  
- ⚙️ Paramètres  
- ❓ Aide  

👉 Vous pouvez changer d’onglet **à tout moment**.
""")

st.markdown("---")

# =========================================================
# DASHBOARD
# =========================================================
st.header("🏠 Dashboard – Vue globale")

st.markdown("""
Le **Dashboard** est l’écran d’accueil.

### Il affiche :
- Nombre total de dossiers  
- Montant honoraires  
- Autres frais  
- Total facturé  
- Total encaissé (acomptes)  
- Solde restant dû  
- Montant total en escrow  

👉 Cet écran est **informatif uniquement**.
""")

st.markdown("---")

# =========================================================
# NOUVEAU DOSSIER
# =========================================================
st.header("➕ Nouveau dossier")

st.markdown("""
Cet onglet permet de **créer un nouveau dossier client**.

### Étapes principales :
1. Numéro de dossier (automatique)
2. Informations client
3. Catégorie → Sous-catégorie → Visa
4. Facturation
5. Acompte 1 :
   - Montant
   - Date de paiement
   - Mode de règlement (Chèque, CB, Virement, Venmo)
6. Option Escrow

⚠️ **Le montant en escrow correspond toujours à Acompte 1.**
""")

st.markdown("---")

# =========================================================
# MODIFIER DOSSIER
# =========================================================
st.header("✏️ Modifier dossier")

st.markdown("""
Permet de **modifier un dossier existant**.

### Vous pouvez :
- Modifier les informations générales
- Ajuster la facturation
- Gérer **tous les acomptes (1 à 4)** :
  - Montant
  - Date de paiement
  - Mode de règlement
- Ajouter un commentaire
- Mettre à jour les statuts :
  - Envoyé
  - Accepté
  - Refusé
  - Annulé
  - RFE
  - Chaque statut a sa **date associée**

👉 Les KPI se mettent à jour automatiquement.
""")

st.markdown("---")

# =========================================================
# ESCROW
# =========================================================
st.header("💰 Escrow")

st.markdown("""
Gestion des dossiers en escrow.

### États possibles :
- Escrow actif
- Escrow à réclamer
- Escrow réclamé

### Règles :
- Montant escrow = **Acompte 1 uniquement**
- Un dossier ne peut être que dans **un seul état à la fois**
- Boutons pour faire avancer le dossier d’un état à l’autre
""")

st.markdown("---")

# =========================================================
# ANALYSES
# =========================================================
st.header("📊 Analyses")

st.markdown("""
Outil d’analyse avancée.

### Contenu :
- KPI dynamiques
- Filtres :
  - Catégorie
  - Sous-catégorie
  - Visa
  - Statuts
  - Comparaisons temporelles
- Graphiques interactifs

👉 Cet onglet sert **uniquement à analyser**, pas à modifier.
""")

st.markdown("---")

# =========================================================
# EXPORT
# =========================================================
st.header("📤 Export Excel / JSON")

st.markdown("""
Permet d’exporter la base de données :
- JSON → Excel
- Fichier multi-feuilles
- Horodaté
- Sans signature

Utile pour sauvegarde, audit ou travail externe.
""")

st.markdown("---")

st.success("✔ Fin du guide – Vous pouvez utiliser l’application en toute autonomie.")