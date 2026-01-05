import streamlit as st
from utils.sidebar import render_sidebar

# =====================================================
# CONFIG
# =====================================================
st.set_page_config(
    page_title="❓ Aide & Mode d’emploi – Cabinet",
    page_icon="❓",
    layout="wide"
)
render_sidebar()

st.title("❓ AIDE & MODE D’EMPLOI")
st.markdown("### Application de gestion des dossiers – **Cabinet (usage interne)**")

# =====================================================
# ONGLET NAVIGATION
# =====================================================
tabs = st.tabs([
    "📘 1. Objectif",
    "🧭 2. Navigation générale",
    "📁 3. Gestion des dossiers",
    "💰 4. Facturation & Escrow",
    "📊 5. Analyses & KPI",
    "📤 6. Exports & PDF",
    "⚠️ 7. Bonnes pratiques",
    "❓ 8. FAQ",
    "📄 9. Impression & PDF"
])

# =====================================================
# 1. OBJECTIF
# =====================================================
with tabs[0]:
    st.subheader("1. Objectif de l’application")

    st.write("""
Cette application a été conçue pour centraliser **l’intégralité de la gestion des dossiers du cabinet**, sans nécessiter de compétences techniques.

Elle permet :

- La création et le suivi administratif des dossiers
- Le suivi financier détaillé (honoraires, acomptes, soldes)
- La gestion complète des **escrows**
- L’organisation hiérarchique **dossiers parents / sous-dossiers**
- Des analyses globales avec indicateurs (KPI)
- Des exports professionnels (Excel / PDF)

👉 **Aucun calcul manuel n’est nécessaire** : tout est automatisé.
    """)

# =====================================================
# 2. NAVIGATION GÉNÉRALE (TRÈS DÉTAILLÉ)
# =====================================================
with tabs[1]:
    st.subheader("2. Navigation générale")

    st.write("""
Le **menu latéral (sidebar)** est le point d’entrée principal de l’application.  
Il permet de naviguer entre les différents modules sans perdre de données.

### Pages principales
""")

    st.markdown("""
- **🏠 Dashboard – Vue globale**  
  Vue synthétique de l’activité du cabinet avec KPI et filtres.

- **📁 Liste des dossiers**  
  Tableau complet de tous les dossiers avec filtres avancés.

- **➕ Nouveau dossier**  
  Création d’un dossier parent ou d’un sous-dossier (fils).

- **✏️ Modifier un dossier**  
  Page centrale de gestion quotidienne (statuts, paiements, escrow).

- **📊 Analyses**  
  Statistiques avancées, comparaisons multi-années, graphiques.

- **💰 Escrow**  
  Gestion, suivi et historique des escrows.

- **🛂 Visa**  
  Référentiel des visas utilisés par le cabinet.

- **💲 Tarifs**  
  Tarifs par visa avec historique et dates d’effet.

- **📤 Export Excel / JSON**  
  Exports complets pour audit, archivage ou mise à jour Excel.

- **📄 Fiche dossier**  
  Fiche détaillée d’un dossier unique avec export PDF.

- **📁 Fiche groupe dossier**  
  Vue parent + sous-dossiers avec export PDF groupe.

- **⚙️ Paramètres**  
  Outils techniques (import Excel, validation JSON, diagnostic Dropbox).

- **❓ Aide**  
  La présente documentation.
    """)

    st.info("""
Astuce importante :
Si une page n’apparaît pas dans le menu, vérifier :
1️⃣ Son nom exact dans le dossier `/pages`  
2️⃣ Sa présence dans la sidebar
    """)

# =====================================================
# 3. GESTION DES DOSSIERS (TRÈS DÉTAILLÉ)
# =====================================================
with tabs[2]:
    st.subheader("3. Gestion des dossiers (parents & sous-dossiers)")

    st.write("""
### 3.1 Types de dossiers

L’application gère **deux types de dossiers** :
""")

    st.markdown("""
#### 📁 Dossier parent
- Numéro simple : `13068`
- Représente le dossier principal du client
- Contient les informations générales

#### 📎 Sous-dossier (fils)
- Numérotation : `13068-1`, `13068-2`, etc.
- Rattaché à un dossier parent
- Peut avoir :
  - Un **visa différent**
  - Des **honoraires différents**
  - Des **paiements distincts**
""")

    st.write("""
👉 Les sous-dossiers sont utilisés lorsque :
- Un client a plusieurs procédures
- Plusieurs visas sont nécessaires
- Le cabinet souhaite un suivi séparé
""")

    st.markdown("---")

    st.write("""
### 3.2 Création d’un dossier

Dans **➕ Nouveau dossier** :

1. Choisir le type :
   - Dossier parent
   - Sous-dossier (sélection du parent)

2. Renseigner :
   - Nom
   - Date de création
   - Catégorie / Sous-catégorie
   - Visa

3. Facturation :
   - Montant honoraires
   - Autres frais

4. Paiement initial :
   - **Acompte 1**
   - Date de paiement
   - Mode de règlement (Chèque / CB / Virement / Venmo)
""")

    st.warning("""
Important :
Les acomptes 2, 3 et 4 ne sont saisis que dans **Modifier dossier**.
    """)

    st.markdown("---")

    st.write("""
### 3.3 Modification d’un dossier

Dans **✏️ Modifier un dossier**, il est possible de :

- Modifier toutes les informations administratives
- Gérer les paiements (acomptes 1 à 4)
- Suivre le solde
- Activer ou désactiver l’escrow
- Mettre à jour les statuts
- Ajouter des commentaires (toujours sauvegardés)
""")

# =====================================================
# 4. FACTURATION & ESCROW
# =====================================================
with tabs[3]:
    st.subheader("4. Facturation & Escrow")

    st.write("""
### Facturation
- Montant honoraires (US $)
- Autres frais
- Total facturé (automatique)
- Total encaissé
- Solde dû

### Règle Escrow (ESSENTIELLE)
- Tant que le dossier n’est **ni accepté, ni refusé, ni annulé** :
  👉 **TOUS les acomptes sont en escrow**
- Lorsque le dossier est :
  - Accepté
  - Refusé
  - Annulé  
  👉 L’escrow passe en **Escrow à réclamer**
- Action manuelle :
  👉 **Escrow réclamé**

L’historique des escrows est conservé.
    """)

# =====================================================
# 5. ANALYSES & KPI
# =====================================================
with tabs[4]:
    st.subheader("5. Analyses & KPI")

    st.write("""
KPI disponibles :
- Nombre total de dossiers
- Dossiers envoyés
- Acceptés / Refusés / Annulés
- Dossiers soldés / non soldés
- Solde négatif
- Escrow total

Filtres :
- Année / multi-années
- Comparaison de périodes
- Catégorie / Sous-catégorie / Visa
- Statuts
    """)

# =====================================================
# 6. EXPORTS
# =====================================================
with tabs[5]:
    st.subheader("6. Exports")

    st.write("""
### Export Excel
- Multi-feuilles
- Horodaté
- Sans signature
- Prêt pour audit

### Export PDF
- Fiche dossier
- Fiche groupe dossier
- Manuel Aide
    """)

# =====================================================
# 7. BONNES PRATIQUES
# =====================================================
with tabs[6]:
    st.subheader("7. Bonnes pratiques")

    st.markdown("""
✔ Toujours utiliser les filtres  
✔ Ne jamais modifier le JSON manuellement  
✔ Vérifier les dates de paiement  
✔ Utiliser les sous-dossiers pour visas multiples  
✔ Utiliser les exports pour archivage
    """)

# =====================================================
# 8. FAQ
# =====================================================
with tabs[7]:
    st.subheader("8. FAQ")

    st.markdown("""
**Pourquoi un dossier n’apparaît pas dans un KPI ?**  
➡ Vérifier les filtres actifs.

**Pourquoi l’escrow est élevé ?**  
➡ Tous les acomptes sont en escrow tant que le dossier n’est pas finalisé.

**Puis-je modifier un visa sur un sous-dossier ?**  
➡ Oui, indépendamment du parent.
    """)

# =====================================================
# 9. IMPRESSION & PDF
# =====================================================
with tabs[8]:
    st.subheader("9. Impression & PDF")

    st.write("""
Cette aide est :
- Consultable dans l’application
- Imprimable
- Exportable en PDF
- Déclinable en version américaine (EN)
    """)

    st.button("📄 Générer le PDF du manuel (activation ultérieure)")