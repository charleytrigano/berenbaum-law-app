import streamlit as st
from utils.sidebar import render_sidebar
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import io

# ---------------------------------------------------------
# CONFIG
# ---------------------------------------------------------
st.set_page_config(
    page_title="❓ Aide & Mode d’emploi",
    page_icon="❓",
    layout="wide"
)

render_sidebar()
st.title("❓ Aide & Mode d’emploi")

# ---------------------------------------------------------
# SÉLECTEUR DE LANGUE
# ---------------------------------------------------------
lang = st.radio(
    "🌍 Langue / Language",
    ["Français 🇫🇷", "English 🇺🇸"],
    horizontal=True
)

# ---------------------------------------------------------
# CONTENU FRANÇAIS
# ---------------------------------------------------------
HELP_FR = """
# 📘 BERENBAUM LAW APP  
## Guide utilisateur officiel

---

## 🎯 Objectif de l’application
Berenbaum Law App est une application professionnelle destinée à la **gestion complète des dossiers juridiques d’immigration**.

Elle permet de :
- gérer les clients,
- suivre les paiements,
- gérer les escrows,
- analyser l’activité,
- exporter les données.

Aucune compétence technique n’est requise.

---

## 🧭 Navigation générale

Le menu à gauche est toujours visible et permet d’accéder aux pages suivantes :

- 🏠 Dashboard
- 📁 Liste des dossiers
- ➕ Nouveau dossier
- ✏️ Modifier dossier
- 📊 Analyses
- 💰 Escrow
- 🛂 Visa
- 💲 Tarifs
- 📤 Export Excel / JSON
- ⚙️ Paramètres
- ❓ Aide

---

## 🏠 Dashboard – Vue globale

Le Dashboard donne une **vue immédiate** de la situation du cabinet.

### Indicateurs clés (KPI)

- **Nombre de dossiers**  
  Tous les dossiers, y compris parents et sous-dossiers.

- **Montant honoraires (US $)**  
  Somme des honoraires.

- **Autres frais (US $)**  
  Frais additionnels.

- **Total facturé**  
  Honoraires + autres frais.

- **Total encaissé**  
  Somme des acomptes 1 à 4.

- **Solde dû**  
  Total facturé – total encaissé.

- **Escrow**  
  Le montant en escrow correspond **uniquement à Acompte 1**.

---

## 📁 Dossiers parents et sous-dossiers

Exemples :
- 12937 → dossier parent
- 12937-1, 12937-2 → sous-dossiers

Chaque sous-dossier :
- peut avoir un visa différent,
- possède ses propres montants,
- est comptabilisé séparément.

---

## ➕ Créer un nouveau dossier

Lors de la création :
- le numéro est généré automatiquement,
- vous pouvez créer un dossier parent ou un sous-dossier.

### Paiement à la création
- Acompte 1
- Date de paiement
- Mode de règlement :
  - Chèque
  - CB
  - Virement
  - Venmo

---

## ✏️ Modifier un dossier

Vous pouvez modifier :
- les informations client,
- la facturation,
- tous les acomptes (1 à 4),
- les dates et modes de paiement,
- les statuts et leurs dates,
- le commentaire (toujours sauvegardé).

---

## 📦 Statuts du dossier

Chaque statut possède une date :
- Dossier envoyé
- Dossier accepté
- Dossier refusé
- Dossier annulé
- RFE

---

## 💼 Gestion Escrow

### États possibles
1. Escrow actif
2. Escrow à réclamer
3. Escrow réclamé

Le montant correspond toujours à **Acompte 1**.

---

## 📊 Analyses

La page Analyses permet :
- la comparaison multi-années,
- l’analyse par période,
- le filtrage par statut,
- l’identification des dossiers soldés / non soldés.

---

## 💲 Tarifs par Visa

- Chaque visa a un tarif.
- Toute modification crée un historique.
- Les tarifs sont appliqués automatiquement selon la date.

---

## 📤 Export des données

Vous pouvez exporter :
- Excel multi-feuilles,
- JSON,
- fichiers horodatés,
- sans signature.

---

## ❓ Besoin d’aide ?
Ce guide est imprimable et exportable en PDF.
"""

# ---------------------------------------------------------
# CONTENU ANGLAIS
# ---------------------------------------------------------
HELP_EN = """
# 📘 BERENBAUM LAW APP  
## Official User Guide

---

## 🎯 Application Purpose
Berenbaum Law App is a professional application designed for **full immigration case management**.

It allows you to:
- manage clients,
- track payments,
- manage escrows,
- analyze activity,
- export data.

No technical knowledge is required.

---

## 🧭 Navigation

The left sidebar is always visible and provides access to:

- 🏠 Dashboard
- 📁 Case list
- ➕ New case
- ✏️ Edit case
- 📊 Analytics
- 💰 Escrow
- 🛂 Visa
- 💲 Pricing
- 📤 Export Excel / JSON
- ⚙️ Settings
- ❓ Help

---

## 🏠 Dashboard – Global View

The Dashboard gives an **instant overview** of firm activity.

### Key Indicators (KPIs)

- **Number of cases**
- **Legal fees**
- **Additional fees**
- **Total billed**
- **Total received**
- **Outstanding balance**
- **Escrow amount (Acompte 1 only)**

---

## 📁 Parent & Child Cases

Examples:
- 12937 → parent case
- 12937-1, 12937-2 → sub-cases

Each sub-case:
- may have a different visa,
- has its own amounts,
- is counted independently.

---

## ➕ Create a New Case

At creation:
- the case number is automatic,
- parent or sub-case supported.

### Payment at creation
- Deposit 1
- Payment date
- Payment method

---

## ✏️ Edit a Case

You can edit:
- client data,
- billing,
- all deposits,
- payment dates & methods,
- statuses & dates,
- comments.

---

## 💼 Escrow Management

Three states:
1. Active
2. To be claimed
3. Claimed

Escrow amount always equals **Deposit 1**.

---

## 📊 Analytics

Advanced analytics:
- multi-year comparison,
- period comparison,
- status filters,
- paid / unpaid cases.

---

## 💲 Visa Pricing

- Each visa has a price.
- All changes are historized.
- Pricing applied by effective date.

---

## 📤 Data Export

You can export:
- Excel (multi-sheet),
- JSON,
- timestamped files.

---

## ❓ Need help?
This guide can be printed or exported as PDF.
"""

# ---------------------------------------------------------
# AFFICHAGE
# ---------------------------------------------------------
content = HELP_FR if "Français" in lang else HELP_EN
st.markdown(content)

# ---------------------------------------------------------
# EXPORT PDF
# ---------------------------------------------------------
st.markdown("---")
st.subheader("📄 Export du guide")

if st.button("📤 Exporter en PDF"):
    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    textobject = pdf.beginText(40, height - 40)
    textobject.setFont("Helvetica", 10)

    for line in content.split("\n"):
        textobject.textLine(line)

    pdf.drawText(textobject)
    pdf.showPage()
    pdf.save()

    buffer.seek(0)

    st.download_button(
        label="⬇️ Télécharger le guide PDF",
        data=buffer,
        file_name=f"Aide_Berenbaum_{'FR' if 'Français' in lang else 'EN'}.pdf",
        mime="application/pdf"
    )