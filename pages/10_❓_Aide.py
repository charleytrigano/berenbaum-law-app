import streamlit as st

st.set_page_config(page_title="❓ Aide", page_icon="❓", layout="wide")
st.title("❓ Centre d'aide — Berenbaum Law App")

st.markdown("""
Bienvenue dans l'assistance de l'application Berenbaum Law.

## 📁 Structure de l'application

### 🏠 Dashboard  
Vue d’ensemble, KPIs, dossiers récents, filtres intelligents.

### ➕ Nouveau dossier  
Création rapide avec catégories, visa, facturation, acomptes et Escrow.

### ✏️ Modifier dossier  
Modification complète du dossier sélectionné.

### 💰 Escrow  
Gestion automatique des statuts :  
- Escrow en cours  
- Escrow à réclamer  
- Escrow réclamé  

### 🛂 Visa  
Référentiel des catégories / sous-catégories / visas.

### ⚙️ Paramètres  
Contient désormais :

- 🔐 Debug Secrets  
- 🧪 Diagnostic Dropbox  
- 📥 Import Excel → JSON  
- 🔄 Synchronisation Dropbox  

Ces outils remplacent plusieurs pages techniques précédentes.

---

## ❓ Questions fréquentes

### 🔸 Pourquoi mon JSON ne se charge-t-il pas ?
Utilisez **⚙️ Paramètres → Diagnostic Dropbox** pour vérifier l'accès.

### 🔸 Comment importer de nouvelles données Excel ?
Un bouton dédié se trouve dans :  
👉 **⚙️ Paramètres → Import Excel → JSON**

### 🔸 Comment fonctionne l’Escrow ?
La logique automatisée :  
- En cours → À réclamer dès que le dossier est envoyé  
- À réclamer → basculé en « réclamé » manuellement  
- L’IA empêche les incohérences  

---

## 📞 Support technique
Pour toute aide, contactez l’administrateur du système ou ChatGPT 😉
""")
