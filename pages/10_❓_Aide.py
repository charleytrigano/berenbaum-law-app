import streamlit as st
from utils.sidebar import render_sidebar

# ---------------------------------------------------------
# CONFIG PAGE
# ---------------------------------------------------------
st.set_page_config(
    page_title="❓ Aide & Guide utilisateur",
    page_icon="❓",
    layout="wide"
)

render_sidebar()

# ---------------------------------------------------------
# TITRE
# ---------------------------------------------------------
st.title("❓ Aide & Guide utilisateur")
st.markdown(
    """
    Bienvenue dans le **guide officiel de l’application Berenbaum Law App**.  
    Cette page explique **pas à pas** comment utiliser l’application,  
    **sans aucune connaissance technique**.
    """
)

st.markdown("---")

# =========================================================
# OBJECTIF
# =========================================================
st.header("🎯 Objectif de l’application")

st.markdown(
    """
    Cette application permet de gérer **l’ensemble des dossiers clients du cabinet** :

    - création et suivi des dossiers,
    - gestion des dossiers parents et sous-dossiers,
    - suivi financier et acomptes,
    - gestion complète de l’**Escrow**,
    - statistiques et tableaux de bord,
    - export et contrôle des données.

    👉 **Tout est automatisé et sécurisé.**
    """
)

# =========================================================
# NAVIGATION
# =========================================================
st.header("🧭 Navigation générale")

st.markdown(
    """
    L’application est organisée autour d’un **menu latéral** :

    1. 🏠 **Dashboard** – Vue globale  
    2. ➕ **Nouveau dossier** – Création  
    3. 📋 **Liste des dossiers** – Consultation  
    4. ✏️ **Modifier dossier** – Édition complète  
    5. 💰 **Escrow** – Suivi financier  
    6. 📊 **Analyses** – Statistiques  
    7. ⚙️ **Paramètres** – Outils avancés  
    """
)

# =========================================================
# DASHBOARD
# =========================================================
st.header("🏠 Dashboard – Vue d’ensemble")

st.markdown(
    """
    Le **Dashboard** est la page d’accueil.

    ### 📊 Indicateurs clés (KPI)

    - **Nombre de dossiers** (parents + sous-dossiers)
    - **Montant honoraires**
    - **Autres frais**
    - **Total facturé**
    - **Total encaissé**
    - **Solde dû**
    - **Montant total en Escrow**

    👉 Tous les indicateurs se mettent à jour **automatiquement**.
    """
)

# =========================================================
# DOSSIERS PARENTS / FILS
# =========================================================
st.header("📂 Dossiers parents et sous-dossiers")

st.markdown(
    """
    L’application gère **deux niveaux de dossiers** :

    ### Dossier parent
    Exemple :
    ```
    12937
    ```

    ### Sous-dossiers
    Exemples :
    ```
    12937-1
    12937-2
    ```

    ✔ Les sous-dossiers :
    - dépendent d’un dossier parent,
    - peuvent avoir un **visa différent**,
    - ont leurs propres montants et statuts,
    - sont inclus dans les KPI globaux.
    """
)

# =========================================================
# CREATION DOSSIER
# =========================================================
st.header("➕ Création d’un dossier")

st.markdown(
    """
    Lors de la création d’un dossier :

    ### Champs obligatoires
    - Nom du client
    - Date
    - Catégorie
    - Sous-catégorie
    - Visa

    ### Facturation
    - Montant honoraires
    - Autres frais
    - Total calculé automatiquement

    ### Acomptes
    - Jusqu’à **4 acomptes**
    - Solde restant calculé automatiquement
    """
)

# =========================================================
# ESCROW
# =========================================================
st.header("💰 Escrow – Règles importantes")

st.markdown(
    """
    ### ⚠️ Règle fondamentale
    **Seul l’Acompte 1 est concerné par l’Escrow.**

    Les acomptes 2, 3 et 4 **ne vont jamais en Escrow**.

    ### États possibles
    1. Escrow actif  
    2. Escrow à réclamer  
    3. Escrow réclamé  

    ### Transitions
    - Escrow actif → Escrow à réclamer  
    - Escrow à réclamer → Escrow réclamé  

    ✔ Un dossier ne peut être que dans **un seul état à la fois**.
    """
)

# =========================================================
# MODIFIER DOSSIER
# =========================================================
st.header("✏️ Modifier un dossier")

st.markdown(
    """
    La page **Modifier dossier** permet :

    - modifier les informations générales,
    - ajuster les montants et acomptes,
    - gérer les statuts,
    - piloter l’Escrow,
    - ajouter des commentaires.

    ### 📦 Statuts disponibles
    - Dossier envoyé
    - Dossier accepté
    - Dossier refusé
    - Dossier annulé
    - RFE

    ✔ Les statuts sont sauvegardés immédiatement  
    ✔ Ils impactent les KPI et les analyses
    """
)

# =========================================================
# LISTE DOSSIERS
# =========================================================
st.header("📋 Liste des dossiers")

st.markdown(
    """
    La liste des dossiers permet :

    - de voir tous les dossiers,
    - d’identifier clairement parents et sous-dossiers,
    - de filtrer par :
      - Année
      - Catégorie
      - Sous-catégorie
      - Visa
      - Statut

    👉 Les sous-dossiers apparaissent **sous leur dossier parent**.
    """
)

# =========================================================
# ANALYSES
# =========================================================
st.header("📊 Analyses & statistiques")

st.markdown(
    """
    L’onglet Analyses permet :

    - analyses mensuelles,
    - comparaisons par année,
    - répartition par catégories et visas,
    - suivi des statuts,
    - heatmaps d’activité.

    ✔ Tous les filtres sont combinables.
    """
)

# =========================================================
# PARAMETRES
# =========================================================
st.header("⚙️ Paramètres & sécurité")

st.markdown(
    """
    L’onglet Paramètres propose :

    - validation automatique de la base JSON,
    - correction des incohérences,
    - import Excel → JSON,
    - synchronisation Dropbox,
    - analyse des incohérences,
    - historique des modifications.

    ⚠️ **Ne jamais modifier le JSON manuellement.**
    """
)

# =========================================================
# BONNES PRATIQUES
# =========================================================
st.header("✅ Bonnes pratiques")

st.markdown(
    """
    - Utiliser **Acompte 1** pour l’Escrow
    - Créer les sous-dossiers avec `-1`, `-2`, etc.
    - Utiliser les statuts plutôt que les commentaires
    - Passer par *Escrow à réclamer* avant *Escrow réclamé*
    """
)

# =========================================================
# FIN
# =========================================================
st.markdown("---")
st.success("✔ Guide utilisateur chargé avec succès.")