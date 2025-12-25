# pages/10_❓_Aide.py
import streamlit as st
from utils.sidebar import render_sidebar

# =====================================================
# CONFIG
# =====================================================
st.set_page_config(page_title="❓ Aide", page_icon="❓", layout="wide")
render_sidebar()
st.title("❓ Aide – Guide utilisateur (débutant)")

st.info(
    "Ce guide explique, pas à pas, comment utiliser l’application Berenbaum Law App. "
    "Il est conçu pour des utilisateurs non techniques."
)

# =====================================================
# SOMMAIRE
# =====================================================
st.markdown(
    """
## Sommaire
1. Vue d’ensemble : comment l’application est organisée  
2. Comprendre les dossiers : dossiers « parents » et « fils » (sous-dossiers)  
3. Dashboard : lecture des KPI et des filtres  
4. Liste des dossiers : recherche et filtres  
5. Nouveau dossier : création d’un dossier (et création de sous-dossier)  
6. Modifier dossier : édition complète (paiements, statuts, dates, escrow, commentaires)  
7. Analyses : filtres et statistiques  
8. Escrow : fonctionnement en 3 états + logique des montants  
9. Visa / Tarifs : mise à jour des tarifs et historique  
10. Export Excel / JSON : importer et exporter sans perdre de données  
11. Problèmes fréquents et solutions (dépannage)  
12. Bonnes pratiques pour éviter les erreurs  
"""
)

st.markdown("---")

# =====================================================
# 1) VUE D'ENSEMBLE
# =====================================================
st.markdown(
    """
## 1) Vue d’ensemble (structure de l’application)

L’application est composée d’onglets (pages) accessibles depuis la **sidebar** (menu à gauche).  
Les pages principales sont :

- **🏠 Dashboard** : vue globale, KPI (indicateurs), filtres, tableau parents/fils.
- **📁 Liste dossiers** : liste filtrable, pratique pour retrouver rapidement un dossier.
- **➕ Nouveau dossier** : création d’un dossier (et éventuellement d’un sous-dossier).
- **✏️ Modifier dossier** : modification détaillée d’un dossier existant.
- **📊 Analyses** : statistiques et graphiques.
- **💰 Escrow** : suivi et transitions des escrows (actif → à réclamer → réclamé).
- **🛂 Visa** : table de référence des visas (selon votre base).
- **💲 Tarifs** : gestion du prix par Visa avec date d’effet + historique.
- **📤 Export Excel** : outils d’import/export (selon la page présente).
- **⚙️ Paramètres** : diagnostic Dropbox, import Excel→JSON, nettoyage, validation.
- **❓ Aide** : cette page.

### Où sont stockées les données ?
Les données sont stockées dans un fichier **database.json** sur **Dropbox**.  
L’application lit ce fichier au démarrage et l’écrit quand vous cliquez sur un bouton **Enregistrer**.
"""
)

# =====================================================
# 2) DOSSIERS PARENTS / FILS
# =====================================================
st.markdown(
    """
## 2) Comprendre les dossiers : parents et fils (sous-dossiers)

### Notion simple
Un **dossier parent** est le dossier principal (ex : `12937`).  
Un **dossier fils** (sous-dossier) est une variante liée au parent (ex : `12937-1`, `12937-2`).

### Pourquoi utiliser des sous-dossiers ?
Vous les utilisez lorsque vous voulez :
- garder un **même dossier “racine”**,
- mais suivre **plusieurs variantes** (ex : plusieurs visas, étapes, dépôts, dossiers liés).

### Comment l’application les reconnaît ?
- Si le numéro contient `-`, l’application considère que c’est un **fils**.  
  Exemple : `12937-2` → parent = `12937`, index = `2`
- Si le numéro ne contient pas `-`, c’est un **parent**.  
  Exemple : `12937` → parent = `12937`, index = `0`

### Important
Un dossier fils peut avoir :
- **un Visa différent**,
- des montants différents,
- des statuts différents,
- et son propre escrow.

Le Dashboard affiche les dossiers triés par **Parent**, puis par **Index**.
"""
)

# =====================================================
# 3) DASHBOARD
# =====================================================
st.markdown(
    """
## 3) Dashboard : KPI et filtres (lecture simple)

Le Dashboard présente :
1) des **filtres** (année, catégorie, sous-catégorie, visa, statut)  
2) des **KPI** (indicateurs chiffrés)  
3) un **tableau** des dossiers (parents et fils)

### Les KPI standards
- **Nombre de dossiers** : total des dossiers filtrés (parents + fils).
- **Montant honoraires (US $)** : somme des honoraires sur les dossiers filtrés.
- **Autres frais (US $)** : somme des frais additionnels.
- **Total facturé** = honoraires + autres frais
- **Total encaissé** = Acompte 1 + Acompte 2 + Acompte 3 + Acompte 4
- **Solde dû** = Total facturé − Total encaissé

### KPI Escrow (logique métier)
- Le **montant escrow** correspond à **Acompte 1 uniquement** (règle actuelle).  
  Donc “Escrow total (Acompte 1)” est la somme de **Acompte 1** sur :
  - les dossiers **Escrow actif**
  - + les dossiers **Escrow à réclamer**
  - + les dossiers **Escrow réclamé**

### À quoi servent les filtres ?
Les filtres servent à “rétrécir” l’affichage et recalculer les KPI :
- Une fois un filtre appliqué, **les KPI changent** (c’est normal).
- Pour revenir à la vue globale, remettez les filtres sur **Toutes / Tous**.
"""
)

# =====================================================
# 4) LISTE DES DOSSIERS
# =====================================================
st.markdown(
    """
## 4) Liste des dossiers : retrouver un dossier rapidement

Cette page est votre moteur de recherche.
Selon votre configuration, elle propose généralement :
- filtres par **Année**
- **Catégorie**
- **Sous-catégorie**
- **Visa**
- **Statut**

### Conseils rapides
- Si vous cherchez un dossier : filtrez d’abord par **Nom** ou **Dossier N** (si disponible).
- Si vous comparez des dossiers : filtrez par **Visa** et **Statut**.
"""
)

# =====================================================
# 5) NOUVEAU DOSSIER
# =====================================================
st.markdown(
    """
## 5) Nouveau dossier : création (et création de sous-dossier)

### Créer un dossier “standard”
Dans **➕ Nouveau dossier** :
1) Remplissez **Nom** et **Date**  
2) Choisissez **Catégorie**, **Sous-catégorie**, **Visa**  
3) Saisissez les montants :
   - **Montant honoraires (US $)**
   - **Autres frais (US $)**
4) Paiement :
   - Acompte 1 (et plus tard Acompte 2/3/4 dans Modifier)
   - Mode de règlement : Chèque / CB / Virement / Venmo
   - Date de paiement de l’acompte
5) Option Escrow : cochez si le dossier commence en **Escrow actif**
6) Cliquez **Enregistrer le dossier**

### Créer un sous-dossier (fils) – principe
Un sous-dossier se note `PARENT-INDEX`, par exemple :
- parent : `12937`
- fils : `12937-1`, `12937-2`

Le plus important est la **discipline de numérotation** :
- Gardez le même parent (avant le `-`)
- Incrémentez l’index (après le `-`)

### Recommandation pour l’avenir (simple et robuste)
- Créez d’abord le parent `12937`
- Puis créez les fils : `12937-1`, `12937-2`, etc.
- N’utilisez jamais le même numéro deux fois.
"""
)

# =====================================================
# 6) MODIFIER DOSSIER
# =====================================================
st.markdown(
    """
## 6) Modifier dossier : édition complète (ce que vous pouvez faire)

Dans **✏️ Modifier dossier**, vous pouvez modifier :

### Informations générales
- Nom
- Date du dossier
- Catégorie / Sous-catégorie / Visa
- Commentaire (notes internes)

### Facturation
- Montant honoraires (US $)
- Autres frais (US $)
- Total facturé (calculé)

### Paiements (Acomptes)
Pour chaque acompte, l’objectif est d’avoir :
- le **montant**
- la **date de paiement**
- le **mode de règlement** (Chèque / CB / Virement / Venmo)

### Statuts
Les statuts d’un dossier peuvent être cochés :
- Dossier envoyé
- Dossier accepté
- Dossier refusé
- Dossier annulé
- RFE

Et **chaque statut** doit idéalement avoir sa **date associée** :
- Date dossier envoyé
- Date dossier accepté
- Date dossier refusé
- Date dossier annulé
- Date RFE

### Escrow (case à cocher)
- **Escrow actif** : le dossier est actuellement en escrow (état 1)
- Ensuite, il peut passer à **Escrow à réclamer** (état 2)
- Puis à **Escrow réclamé** (état 3)

Important : vous utilisez la page **Escrow** pour faire les transitions via des boutons.

### Règle d’or
Après modification, il faut cliquer **💾 Enregistrer les modifications**.  
Sans ce bouton, rien n’est écrit dans Dropbox.
"""
)

# =====================================================
# 7) ANALYSES
# =====================================================
st.markdown(
    """
## 7) Analyses : statistiques et filtres

La page **📊 Analyses** sert à observer des tendances :
- par catégorie, visa, période, etc.
- avec des KPI et des graphiques

### Filtres utiles
- Catégorie / Sous-catégorie / Visa
- Statut
- Filtres financiers (ex : dossiers soldés / non soldés si activés)
- Comparaisons temporelles (mois / années / date à date selon version)

### Si un filtre “ne fonctionne pas”
Dans 90% des cas, c’est lié à :
- des colonnes vides (ex : Visa manquant)
- des dates vides/invalides
- des colonnes au mauvais nom (alias)
- un import Excel incomplet

Dans ce cas : utilisez **⚙️ Paramètres → Validation / Nettoyage** puis réessayez.
"""
)

# =====================================================
# 8) ESCROW (3 états + montants)
# =====================================================
st.markdown(
    """
## 8) Escrow : fonctionnement en 3 états + montants

### Les 3 états
1) **Escrow actif** : l’escrow est en cours
2) **Escrow à réclamer** : le dossier est prêt, vous devez réclamer
3) **Escrow réclamé** : vous avez réclamé, le dossier passe en “terminé”

### Transitions (boutons)
Sur la page **💰 Escrow**, vous devez avoir des actions :
- “Passer en Escrow à réclamer” (depuis Escrow actif)
- “Marquer comme réclamé” (depuis Escrow à réclamer)

Après transition :
- le dossier doit **disparaître** de l’onglet précédent
- et **apparaître** dans l’onglet suivant

### Montant escrow (règle actuelle)
Le **montant escrow affiché** doit être :
- **Acompte 1**, à chaque étape (actif / à réclamer / réclamé)

Donc :
- Total Escrow actif = somme des Acompte 1 des dossiers “Escrow actif”
- Total Escrow à réclamer = somme des Acompte 1 des dossiers “Escrow à réclamer”
- Total Escrow réclamé = somme des Acompte 1 des dossiers “Escrow réclamé”
"""
)

# =====================================================
# 9) VISA / TARIFS
# =====================================================
st.markdown(
    """
## 9) Visa / Tarifs : mise à jour des tarifs + historique

### Objectif
Chaque Visa a un tarif, et les tarifs peuvent changer dans le temps.
Vous gardez l’historique et la date d’effet.

### Comment modifier un tarif
Dans **💲 Tarifs** :
1) Choisissez un Visa
2) Entrez le nouveau prix
3) Choisissez une **date d’effet**
4) Cliquez **Enregistrer**

L’ancien tarif devient “inactif” et une ligne est ajoutée à l’historique.

### Pourquoi la date d’effet est importante ?
Parce que :
- un dossier créé à une date donnée doit appliquer le tarif correspondant à cette période.
"""
)

# =====================================================
# 10) EXPORT / IMPORT
# =====================================================
st.markdown(
    """
## 10) Export Excel / JSON : importer et exporter sans perdre de données

### Import Excel → JSON (⚙️ Paramètres)
Vous l’utilisez si vous devez reconstruire `database.json` depuis des fichiers Excel.
Attention : l’import doit convertir correctement :
- dates
- montants
- booléens (true/false)
- colonnes obligatoires (dont Commentaire)

### Export JSON → Excel (multi-feuilles, horodaté)
L’objectif est de produire un fichier Excel propre, téléchargeable, contenant :
- une feuille **Clients**
- une feuille **Visa**
- une feuille **Escrow** (si utilisée)
- une feuille **Compta** (si utilisée)
- une feuille **Tarifs**
- une feuille **Tarifs_History**
- éventuellement **History** selon votre structure

Ce fichier permet ensuite :
- une mise à jour manuelle dans Excel
- puis un réimport contrôlé (si besoin)

### Règle importante
Ne faites pas Import/Export “au hasard”.
Si vous devez corriger des données :
1) Export JSON → Excel
2) Corriger Excel
3) Import Excel → JSON
4) Vérifier sur Dashboard + Liste dossiers
"""
)

# =====================================================
# 11) DEPANNAGE
# =====================================================
st.markdown(
    """
## 11) Problèmes fréquents et solutions (dépannage)

### “J’ai coché une case mais en revenant elle est décochée”
Cause la plus fréquente :
- vous avez oublié de cliquer **Enregistrer**
- ou la sauvegarde a échoué (Dropbox / JSON / types)

À faire :
1) cliquez Enregistrer
2) allez dans **⚙️ Paramètres → Diagnostic Dropbox**
3) vérifiez que le JSON se met à jour

### “Les KPI ne correspondent pas au nombre de dossiers”
Causes fréquentes :
- filtres actifs (année / visa / statut)
- dossiers “fils” non pris en compte si la page trie mal
- Dossier N non standard (ex : valeur vide, espace, format non attendu)

À faire :
- remettre les filtres sur “Toutes/Tous”
- vérifier que Dossier N est bien renseigné

### “Import terminé mais base vide”
Causes fréquentes :
- mauvais fichier Excel importé
- onglet Excel manquant
- colonnes pas reconnues
- erreurs de type (Timestamp non sérialisable)

À faire :
- utiliser Export JSON → Excel pour repartir d’une base saine
- vérifier les colonnes obligatoires
- relancer l’import

### “Erreur StreamlitPageNotFoundError dans la sidebar”
Cause :
- la sidebar pointe vers un fichier qui n’existe pas ou dont le nom a changé.

Solution :
- mettre à jour `utils/sidebar.py` pour correspondre exactement aux noms présents dans `pages/`.
"""
)

# =====================================================
# 12) BONNES PRATIQUES
# =====================================================
st.markdown(
    """
## 12) Bonnes pratiques (pour éviter les erreurs)

1) **Toujours cliquer Enregistrer** après une modification.  
2) Ne pas laisser de champs critiques vides :
   - Dossier N
   - Nom
   - Date
   - Visa
3) Utiliser une numérotation claire pour les fils :
   - `12937-1`, `12937-2`, etc.
4) Éviter les doublons de Dossier N.
5) Après un Import Excel, vérifier :
   - Dashboard (KPI)
   - Liste des dossiers
   - Modifier dossier (un dossier au hasard)
6) Si un comportement vous semble “bizarre” :
   - aller dans **⚙️ Paramètres → Diagnostic Dropbox**
   - et vérifier que les données sont cohérentes dans le JSON.
"""
)

st.markdown("---")
st.success("Guide chargé. Vous pouvez laisser cette page ouverte pendant votre utilisation de l’application.")