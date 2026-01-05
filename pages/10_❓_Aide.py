import streamlit as st
from utils.sidebar import render_sidebar

# =====================================================
# CONFIG
# =====================================================
st.set_page_config(
    page_title="❓ Aide & Mode d’emploi",
    page_icon="❓",
    layout="wide"
)
render_sidebar()

st.title("❓ AIDE & MODE D’EMPLOI")
st.markdown("### Application de gestion des dossiers – Cabinet (usage interne)")

st.markdown("---")

# =====================================================
# SOMMAIRE CLIQUABLE
# =====================================================
st.markdown("""
### 📑 Sommaire

- [1. Objectif de l’application](#objectif)
- [2. Navigation générale](#navigation)
- [3. Gestion des dossiers](#dossiers)
- [4. Facturation & Escrow](#facturation)
- [5. Analyses & KPI](#analyses)
- [6. Exports](#exports)
- [7. Bonnes pratiques](#bonnes-pratiques)
- [8. FAQ](#faq)
- [9. Impression & PDF](#pdf)
- [10. Index alphabétique](#index)
""", unsafe_allow_html=True)

st.markdown("---")

# =====================================================
# 1. OBJECTIF
# =====================================================
st.markdown('<a id="objectif"></a>', unsafe_allow_html=True)
st.subheader("1. Objectif de l’application")

st.write("""
Cette application permet de gérer **l’ensemble des dossiers clients du cabinet**, de manière centralisée et sécurisée.

Elle couvre :
- le suivi administratif des dossiers,
- la gestion financière (honoraires, acomptes, soldes),
- la gestion des escrows,
- l’organisation des dossiers parents et sous-dossiers,
- les analyses, KPI et exports (Excel / PDF).

👉 **Aucune compétence informatique n’est requise.**
""")

# =====================================================
# 2. NAVIGATION
# =====================================================
st.markdown('<a id="navigation"></a>', unsafe_allow_html=True)
st.subheader("2. Navigation générale")

st.write("""
La navigation se fait via le **menu latéral à gauche**.

Pages principales :
- 🏠 Dashboard – Vue globale
- 📁 Liste des dossiers
- ➕ Nouveau dossier
- ✏️ Modifier un dossier
- 📊 Analyses
- 💰 Escrow
- 🛂 Visa
- 💲 Tarifs
- 📤 Exports Excel / JSON
- ⚙️ Paramètres
- ❓ Aide
""")

st.info("💡 Astuce : si une page n’apparaît pas, vérifier son nom exact dans le dossier `/pages`.")

# =====================================================
# 3. DOSSIERS
# =====================================================
st.markdown('<a id="dossiers"></a>', unsafe_allow_html=True)
st.subheader("3. Gestion des dossiers")

st.write("""
### Types de dossiers

Il existe **deux types de dossiers** :

**1️⃣ Dossier parent**
- Numéro simple : `13068`
- Dossier principal du client

**2️⃣ Sous-dossier (fils)**
- Numérotation : `13068-1`, `13068-2`, etc.
- Utilisé lorsque :
  - un client a plusieurs procédures,
  - des visas différents sont nécessaires.

👉 Les sous-dossiers peuvent avoir **un visa différent** du parent.
""")

# =====================================================
# 4. FACTURATION & ESCROW
# =====================================================
st.markdown('<a id="facturation"></a>', unsafe_allow_html=True)
st.subheader("4. Facturation & Escrow")

st.write("""
### Facturation
- Montant honoraires (US $)
- Autres frais
- Total facturé (calcul automatique)
- Acomptes 1 à 4 (montant, date, mode de règlement)

### Règle Escrow (ESSENTIELLE)

- **Tant que le dossier n’est ni accepté, ni refusé, ni annulé** :
  👉 **TOUS les acomptes sont en escrow**

- Lorsque le dossier est :
  - accepté
  - refusé
  - annulé  
  👉 le montant passe en **Escrow à réclamer**

- Une fois réclamé :
  👉 **Escrow réclamé**

Un **historique escrow** est conservé automatiquement.
""")

# =====================================================
# 5. ANALYSES & KPI
# =====================================================
st.markdown('<a id="analyses"></a>', unsafe_allow_html=True)
st.subheader("5. Analyses & KPI")

st.write("""
Les analyses permettent de piloter l’activité du cabinet.

### KPI disponibles
- Nombre de dossiers
- Dossiers acceptés / refusés / annulés
- Dossiers soldés / non soldés
- Dossiers avec solde négatif
- Montants facturés / encaissés
- Escrow total

### Filtres avancés
- Année
- Catégorie
- Sous-catégorie
- Visa
- Statuts
- Comparaison multi-années
""")

# =====================================================
# 6. EXPORTS
# =====================================================
st.markdown('<a id="exports"></a>', unsafe_allow_html=True)
st.subheader("6. Exports")

st.write("""
### Export Excel
- Export JSON → Excel multi-feuilles
- Fichier horodaté
- Sans signature
- Prêt pour audit ou archivage

### Export PDF
- Fiche dossier (un dossier)
- Fiche groupe dossier (parent + fils)
- Documents professionnels imprimables
""")

# =====================================================
# 7. BONNES PRATIQUES
# =====================================================
st.markdown('<a id="bonnes-pratiques"></a>', unsafe_allow_html=True)
st.subheader("7. Bonnes pratiques")

st.write("""
✔ Toujours utiliser les filtres  
✔ Ne jamais modifier le JSON manuellement  
✔ Vérifier les dates de paiement  
✔ Utiliser les sous-dossiers pour visas multiples  
✔ Utiliser les exports pour archivage  
""")

# =====================================================
# 8. FAQ
# =====================================================
st.markdown('<a id="faq"></a>', unsafe_allow_html=True)
st.subheader("8. FAQ")

st.write("""
**Q : Pourquoi un dossier n’apparaît pas ?**  
➡ Vérifier les filtres actifs.

**Q : Pourquoi l’escrow ne correspond pas au total encaissé ?**  
➡ Tant que le dossier n’est pas accepté/refusé/annulé, tous les acomptes sont en escrow.

**Q : Puis-je modifier un visa sur un sous-dossier ?**  
➡ Oui, indépendamment du parent.
""")

# =====================================================
# 9. PDF
# =====================================================
st.markdown('<a id="pdf"></a>', unsafe_allow_html=True)
st.subheader("9. Impression & PDF")

st.write("""
Cette aide est :
- consultable en ligne,
- imprimable,
- exportable en PDF,
- déclinable en version française ou américaine.

Elle constitue le **manuel interne officiel du cabinet**.
""")

# =====================================================
# 10. INDEX ALPHABÉTIQUE AUTOMATIQUE
# =====================================================
st.markdown('<a id="index"></a>', unsafe_allow_html=True)
st.subheader("10. Index alphabétique")

index_items = sorted([
    "Acompte",
    "Analyses",
    "Dashboard",
    "Dossier parent",
    "Dossier fils",
    "Escrow",
    "Export Excel",
    "Export PDF",
    "Facturation",
    "KPI",
    "Sous-dossier",
    "Statuts",
    "Tarifs Visa",
    "Timeline",
    "Visa"
])

cols = st.columns(4)
for i, item in enumerate(index_items):
    cols[i % 4].write(f"• {item}")