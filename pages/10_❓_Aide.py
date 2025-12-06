import streamlit as st

st.set_page_config(page_title="Aide", page_icon="❓", layout="wide")

st.title("❓ Centre d’aide — Berenbaum Law App")
st.write("Bienvenue dans le guide utilisateur complet de l’application. Sélectionnez une section ci-dessous pour obtenir une explication détaillée de chaque fonction.")

st.markdown("---")

# ------------------------------------------------------------------
# 1. Introduction
# ------------------------------------------------------------------
st.header("1️⃣ Présentation générale de l’application")

st.markdown("""
L’application **Berenbaum Law App** a été conçue pour permettre une **gestion complète et intuitive** des dossiers clients au sein du cabinet.  
Elle fonctionne avec une base centralisée synchronisée avec **Dropbox**, ce qui garantit :

- Sauvegarde automatique des données  
- Accès multi-appareils  
- Mise à jour instantanée  
- Sécurité renforcée  

Chaque module de l’application traite un aspect spécifique :  
👉 création de dossiers  
👉 modification  
👉 suivi financier  
👉 analyses statistiques  
👉 gestion des Escrow  
👉 comptabilité détaillée  
👉 gestion des visas  

---

""")


# ------------------------------------------------------------------
# 2. Dashboard
# ------------------------------------------------------------------
st.header("2️⃣ Dashboard — Tableau de bord principal")

st.markdown("""
Le **Dashboard** est votre page de synthèse. Vous y trouverez :

### 🧮 Indicateurs clés (KPI)
- Nombre total de dossiers  
- Honoraires totaux  
- Autres frais  
- Montant facturé  
- Montant encaissé  
- Solde dû  

Ces indicateurs se mettent **automatiquement à jour** lorsque vous utilisez les filtres.

### 🎛️ Filtres disponibles
Vous pouvez filtrer tous les KPIs et le tableau selon :

- **Catégorie de visa**
- **Sous-catégorie**
- **Visa spécifique**
- **Année**
- **Période personnalisée** (Date de début → Date de fin)

Les filtres s'appliquent **instantanément** et permettent :
- d’isoler des performances sur un visa donné  
- d’analyser une période comptable  
- de comparer des catégories  

### 📋 Tableau filtré
Sous les KPIs se trouve un tableau qui affiche **uniquement les dossiers correspondant aux filtres**.

Toutes les colonnes clés sont affichées :
- Dossier  
- Nom  
- Visa  
- Montants  
- Dates  
- Statuts  

---

""")


# ------------------------------------------------------------------
# 3. Liste des dossiers
# ------------------------------------------------------------------
st.header("3️⃣ Liste des dossiers")

st.markdown("""
Cette page affiche **tous les dossiers enregistrés dans la base Dropbox**.  

### ⚡ Fonctionnalités principales
- Recherche rapide  
- Filtres identiques au Dashboard  
- Calculs automatiques des montants  
- Export Excel, CSV ou PDF  

### 📦 Contenu affiché
La liste inclut :

- Informations client  
- Catégorie, sous-catégorie, visa  
- Acomptes  
- Montants  
- Solde  
- Dates importantes  

Cette page est idéale pour **audits**, **contrôles**, **préparations de rendez-vous**, et **exports administratifs**.

---

""")


# ------------------------------------------------------------------
# 4. Nouveau dossier
# ------------------------------------------------------------------
st.header("4️⃣ Nouveau dossier")

st.markdown("""
Cette section permet de **créer un nouveau dossier client**.

### 🆔 Numérotation automatique
Le numéro de dossier est généré automatiquement à partir du dernier numéro existant.

### 📄 Informations à saisir
1. **Dossier N**, **Nom**, **Date**  
2. **Catégorie**, **Sous-catégorie**, **Visa**  
3. **Montant honoraires**, **Autres frais**, **Total facturé**  
4. **Acompte 1** + **Mode de règlement**  
5. Option **Escrow** (génère automatiquement un suivi dans l’onglet Escrow)

### ✔ Validation
Une fois sauvegardé :
- Le dossier apparaît immédiatement dans la base
- La synchronisation Dropbox est instantanée

---

""")


# ------------------------------------------------------------------
# 5. Modifier un dossier
# ------------------------------------------------------------------
st.header("5️⃣ Modifier un dossier")

st.markdown("""
Permet d’ouvrir un dossier existant et de modifier **toutes les informations**.

### 🔍 Étapes
1. Sélectionner le dossier dans la liste déroulante  
2. Le formulaire se remplit automatiquement  
3. Modifier les données souhaitées  
4. Cliquer sur **Mettre à jour**  

### 🧾 Champs modifiables
- Visa / Catégorie / Sous-catégorie  
- Honoraires, frais, acomptes  
- Dates d’acomptes  
- Statuts :
  - Dossier envoyé  
  - Accepté  
  - Refusé  
  - Annulé  
  - RFE  
- Option Escrow  

### 🗑 Suppression d’un dossier
Un bouton **Supprimer** permet de retirer un dossier définitivement.  
Un **historique des suppressions** est conservé automatiquement.

---

""")


# ------------------------------------------------------------------
# 6. Analyses & Statistiques
# ------------------------------------------------------------------
st.header("6️⃣ Analyses & Statistiques")

st.markdown("""
Cet onglet fournit une **analyse comptable et opérationnelle avancée** du cabinet.

### 📌 KPIs dynamiques
Les indicateurs se recalculent en fonction des filtres.

### 📊 Graphiques inclus
- Évolution annuelle (bar chart)
- Évolution mensuelle (courbe)
- Répartition par catégorie (pie chart)
- Heatmap Catégorie × Année
- Heatmap Visa × Année

### 🔍 Filtres disponibles
- Catégorie  
- Sous-catégorie  
- Visa  
- Année  

### 📤 Export complet
Vous pouvez exporter :
- Excel
- CSV
- PDF professionnel (incluant logos et mise en page)

---

""")


# ------------------------------------------------------------------
# 7. Escrow
# ------------------------------------------------------------------
st.header("7️⃣ Gestion des Escrow")

st.markdown("""
La gestion des Escrow est entièrement automatisée.

### 💼 Fonctionnement
- Lorsqu’un dossier a **Escrow = Oui**, son **Acompte 1** apparaît dans *Escrow en cours*  
- Lorsque le dossier est **envoyé**, l’Escrow passe en *Escrow à réclamer*  
- Un bouton **Réclamer** permet de transférer automatiquement la ligne dans *Escrow réclamé*  

### 📦 Trois tableaux
1. **Escrow en cours**  
2. **Escrow à réclamer**  
3. **Escrow réclamé**

Chaque tableau se met à jour automatiquement lorsque le statut du dossier change.

---

""")


# ------------------------------------------------------------------
# 8. Comptabilité
# ------------------------------------------------------------------
st.header("8️⃣ Comptabilité")

st.markdown("""
Cet onglet génère une **fiche comptable complète** pour chaque dossier.

### 📃 Contenu de la fiche
- Informations personnelles  
- Informations visa  
- Dates clés (envoi, acceptation, refus, annulation, RFE)  
- Honoraires + frais  
- Acomptes ligne par ligne  
- Mode de paiement  
- Totaux calculés  
- Solde dû  

### 📕 Export
Un bouton permet de télécharger une **version PDF professionnelle**, prête à imprimer ou à joindre au dossier client.

---

""")


# ------------------------------------------------------------------
# 9. Synchronisation Dropbox
# ------------------------------------------------------------------
st.header("9️⃣ Synchronisation Dropbox")

st.markdown("""
L’application lit et écrit toutes les données dans un fichier JSON hébergé sur Dropbox.

Avantages :
- Aucun risque de perte de données  
- Données toujours à jour entre plusieurs appareils  
- Import automatique des fichiers Excel  
- Migration propre et sécurisée  

### ⚠ Important
Ne modifiez jamais manuellement le fichier `database.json` sauf assistance technique.

---

""")


# ------------------------------------------------------------------
# 10. Questions fréquentes (FAQ)
# ------------------------------------------------------------------
st.header("🔟 FAQ")

st.markdown("""
### ❓ Pourquoi un filtre n’affiche aucun dossier ?
Car aucun dossier ne correspond à la combinaison des filtres.  
Essayez d’élargir la recherche.

### ❓ Pourquoi certains montants semblent faux ?
Vérifiez :
- Les acomptes (tout doit être numérique)
- Les dates (une mauvaise date peut exclure un dossier)

### ❓ Comment ajouter un nouveau visa ?
Ouvrir l’onglet **Visa**, modifier le tableau, et sauvegarder.

### ❓ Comment réinitialiser la base ?
Importer à nouveau les 4 fichiers Excel depuis l’onglet **Synchronisation**.

---

""")


# ------------------------------------------------------------------
# 11. Support technique
# ------------------------------------------------------------------
st.header("1️⃣1️⃣ Support & Maintenance")

st.markdown("""
En cas de problème technique :  
📧 **support@berenbaum-law.com**  
📞 **+1 (XXX) XXX-XXXX**

Merci d’utiliser Berenbaum Law App.
""")
