import streamlit as st
from datetime import date

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

# =====================================================
# HEADER
# =====================================================
st.title("❓ AIDE & MODE D’EMPLOI")
st.subheader("Application de gestion des dossiers – Cabinet (usage interne)")

st.markdown(
    f"""
    **Version interne – Cabinet**  
    Dernière mise à jour : **{date.today().strftime("%d/%m/%Y")}**

    Cette documentation constitue le **manuel officiel interne** de l’application.
    """
)

st.markdown("---")

# =====================================================
# 1. OBJECTIF GÉNÉRAL
# =====================================================
st.header("1. 🎯 Objectif de l’application")

st.markdown("""
Cette application permet de gérer **l’ensemble des dossiers clients du cabinet**, depuis leur création jusqu’à leur clôture, avec :

- le suivi **administratif**
- le suivi **financier**
- la gestion **des escrows**
- l’organisation **dossiers parents / sous-dossiers**
- des **analyses avancées**, KPI et exports

👉 Elle est conçue pour être utilisée **sans aucune connaissance technique**.
""")

# =====================================================
# 2. NAVIGATION GÉNÉRALE
# =====================================================
st.header("2. 🧭 Navigation générale")

st.markdown("""
Le menu latéral (sidebar) permet d’accéder à toutes les fonctionnalités :

- 🏠 **Dashboard** – Vue globale
- 📁 **Liste des dossiers**
- ➕ **Nouveau dossier**
- ✏️ **Modifier un dossier**
- 📊 **Analyses**
- 💰 **Escrow**
- 🛂 **Visa**
- 💲 **Tarifs**
- 📄 **Fiche dossier**
- 📁 **Fiche groupe dossier**
- 📤 **Export Excel / JSON**
- ⚙️ **Paramètres**
- ❓ **Aide**

👉 Si une page n’apparaît pas :
- vérifier son **nom exact** dans le dossier `/pages`
- vérifier qu’elle est bien référencée dans la sidebar
""")

# =====================================================
# 3. DASHBOARD
# =====================================================
st.header("3. 🏠 Dashboard – Vue globale")

st.markdown("""
Le **Dashboard** est la page principale.  
Il donne une **vision instantanée de l’activité du cabinet**.
""")

st.subheader("3.1 Filtres")

st.markdown("""
Les filtres permettent de restreindre l’affichage :

- Année
- Catégorie
- Sous-catégorie
- Visa
- Statuts (envoyé, accepté, refusé, annulé…)
- Dossiers soldés / non soldés / solde négatif

⚠️ Tous les KPI et tableaux se recalculent **en temps réel** selon les filtres.
""")

st.subheader("3.2 KPI affichés")

st.markdown("""
- Nombre de dossiers
- Montant honoraires
- Autres frais
- Total facturé
- Total encaissé (somme des acomptes)
- Solde dû
- **Montant total en Escrow**
""")

st.info("""
⚠️ RÈGLE ESCROW IMPORTANTE  
Le montant en escrow dépend de l’état du dossier :
- tant que le dossier **n’est ni accepté, ni refusé, ni annulé** → **TOUS les acomptes sont en escrow**
- dès que le dossier est accepté / refusé / annulé → l’escrow passe en **Escrow à réclamer**
""")

# =====================================================
# 4. DOSSIERS PARENTS & FILS
# =====================================================
st.header("4. 📁 Dossiers parents & sous-dossiers")

st.markdown("""
Un dossier peut être :

### ✔ Dossier parent
- numéro simple (ex: `13068`)
- dossier principal

### ✔ Sous-dossier (fils)
- numéro dérivé :  
  `13068-1`, `13068-2`, etc.
- rattaché à un parent
- **peut avoir un visa différent du parent**

👉 Utilisation typique :
- plusieurs procédures pour un même client
- visas multiples
""")

# =====================================================
# 5. NOUVEAU DOSSIER
# =====================================================
st.header("5. ➕ Nouveau dossier")

st.markdown("""
Lors de la création d’un dossier :
""")

st.markdown("""
### 5.1 Informations obligatoires
- Nom
- Date
- Catégorie
- Sous-catégorie
- Visa
""")

st.markdown("""
### 5.2 Facturation
- Montant honoraires
- Autres frais
- Total calculé automatiquement
""")

st.markdown("""
### 5.3 Acompte 1 (seul visible à la création)
- Montant
- Date de paiement
- Mode de règlement :
  - Chèque
  - CB
  - Virement
  - Venmo

⚠️ Les acomptes 2, 3 et 4 seront saisis plus tard dans **Modifier dossier**.
""")

# =====================================================
# 6. MODIFIER UN DOSSIER
# =====================================================
st.header("6. ✏️ Modifier un dossier")

st.markdown("""
C’est la **page centrale de gestion quotidienne**.
""")

st.subheader("6.1 Informations générales")

st.markdown("""
- Nom
- Date du dossier
- Catégorie / Sous-catégorie
- Visa
- Commentaire (toujours sauvegardé)
""")

st.subheader("6.2 Facturation")

st.markdown("""
- Montant honoraires
- Autres frais
- Total facturé
- Total encaissé
- Solde dû
""")

st.subheader("6.3 Acomptes")

st.markdown("""
Pour chaque acompte (1 à 4) :
- Montant
- Date de paiement
- Mode de règlement
""")

st.subheader("6.4 Statuts du dossier")

st.markdown("""
Cases à cocher :
- Dossier envoyé
- Dossier accepté
- Dossier refusé
- Dossier annulé
- RFE

Chaque statut possède sa **date associée**.
""")

# =====================================================
# 7. ESCROW
# =====================================================
st.header("7. 💰 Gestion des Escrows")

st.markdown("""
### États possibles :
- Escrow actif
- Escrow à réclamer
- Escrow réclamé
""")

st.markdown("""
### Logique officielle Escrow :
1. Tant que le dossier n’est **ni accepté, ni refusé, ni annulé**  
   👉 **tous les acomptes sont en escrow**
2. Dès que le dossier est accepté / refusé / annulé  
   👉 le montant passe en **Escrow à réclamer**
3. Une fois réclamé  
   👉 passe en **Escrow réclamé**
""")

st.markdown("""
✔ Chaque transition est :
- tracée
- horodatée
- historisée
""")

# =====================================================
# 8. ANALYSES
# =====================================================
st.header("8. 📊 Analyses")

st.markdown("""
Les analyses permettent :
- le suivi de performance
- le contrôle financier
- la vision multi-années
""")

st.markdown("""
### KPI disponibles :
- Dossiers acceptés
- Dossiers refusés
- Dossiers annulés
- Dossiers soldés
- Dossiers non soldés
- Solde négatif
""")

# =====================================================
# 9. TARIFS PAR VISA
# =====================================================
st.header("9. 💲 Tarifs par Visa")

st.markdown("""
- Chaque visa possède un tarif
- Les changements sont horodatés
- L’historique est conservé
- Le tarif applicable dépend de la **date du dossier**
""")

# =====================================================
# 10. EXPORTS
# =====================================================
st.header("10. 📤 Exports")

st.markdown("""
### Export JSON → Excel
- Fichier Excel multi-feuilles
- Horodaté
- Sans signature
- Prêt pour audit ou archivage
""")

st.markdown("""
### Export PDF
- Fiche dossier
- Fiche groupe dossier (parent + fils)
""")

# =====================================================
# 11. BONNES PRATIQUES
# =====================================================
st.header("11. ✅ Bonnes pratiques")

st.markdown("""
✔ Toujours utiliser les filtres  
✔ Ne jamais modifier le JSON manuellement  
✔ Vérifier les dates de paiement  
✔ Utiliser les sous-dossiers pour visas multiples  
✔ Utiliser les exports pour archivage
""")

# =====================================================
# 12. FAQ
# =====================================================
st.header("12. ❓ FAQ rapide")

st.markdown("""
**Q : Pourquoi un dossier n’apparaît pas dans un KPI ?**  
➡ Vérifier les filtres actifs.

**Q : Pourquoi l’escrow ne correspond pas au total encaissé ?**  
➡ Tant que le dossier n’est pas finalisé, **tous les acomptes sont en escrow**.

**Q : Un sous-dossier peut-il avoir un visa différent ?**  
➡ Oui, totalement indépendant du parent.
""")

# =====================================================
# FIN
# =====================================================
st.markdown("---")
st.success("📘 Manuel interne à conserver et à diffuser au sein du cabinet.")