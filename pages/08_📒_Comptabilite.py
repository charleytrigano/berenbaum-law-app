import streamlit as st
import pandas as pd
from backend.dropbox_utils import load_database
from components.export_pdf import generate_pdf_from_dataframe

st.set_page_config(page_title="Comptabilité", page_icon="📒", layout="wide")
st.title("📒 Comptabilité — Berenbaum Law App")

# ----------------------------------------------
# LOAD DATABASE
# ----------------------------------------------
db = load_database()
clients = db.get("clients", [])

if not clients:
    st.warning("Aucun dossier trouvé.")
    st.stop()

df = pd.DataFrame(clients)

DOSSIER_COL = "Dossier N"

# ----------------------------------------------
# SELECT DOSSIER
# ----------------------------------------------
try:
    dossiers = sorted([int(x) for x in df[DOSSIER_COL].dropna().unique().tolist()])
except:
    dossiers = df[DOSSIER_COL].dropna().unique().tolist()

selected = st.selectbox("Sélectionner un dossier", dossiers)

dossier = df[df[DOSSIER_COL] == selected].iloc[0]

# ----------------------------------------------
# SAFE GETTER
# ----------------------------------------------
def val(k):
    v = dossier.get(k, "")
    if pd.isna(v) or v == "":
        return ""
    return v

# ----------------------------------------------
# CALCULS
# ----------------------------------------------
honoraires = float(val("Montant honoraires (US $)") or 0)
autres = float(val("Autres frais (US $)") or 0)
total_facture = honoraires + autres

acomptes = [
    float(val("Acompte 1") or 0),
    float(val("Acompte 2") or 0),
    float(val("Acompte 3") or 0),
    float(val("Acompte 4") or 0),
]
total_encaisse = sum(acomptes)
solde = total_facture - total_encaisse

# ----------------------------------------------
# AFFICHAGE FICHE
# ----------------------------------------------

st.markdown(f"""
<h2 style="margin-top:20px;">📁 Dossier ref. : {val('Dossier N')} — {val('Nom')}</h2>

### 🛂 Informations Visa
**Visa :** {val("Sous-categories")} / {val("Visa")}  
**Date d’envoi :** {val("Date envoi")}  
**Dossier accepté le :** {val("Date acceptation")}  
**Dossier refusé le :** {val("Date refus")}  
**Dossier annulé le :** {val("Date annulation")}  
**RFE :** {val("RFE")}

---

### 💰 Comptabilité

| Intitulé | Montant |
|---------|---------|
| **Honoraires** | ${honoraires:,.2f} |
| **Frais annexes** | ${autres:,.2f} |
| **Total facturé** | **${total_facture:,.2f}** |

### 💵 Acomptes
""", unsafe_allow_html=True)

# Tableau des acomptes
acomptes_data = {
    "Date": [
        val("Date Acompte 1"),
        val("Date Acompte 2"),
        val("Date Acompte 3"),
        val("Date Acompte 4"),
    ],
    "Mode de paiement": [
        val("mode de paiement"),
        val("mode de paiement"),
        val("mode de paiement"),
        val("mode de paiement"),
    ],
    "Montant": acomptes
}

st.table(pd.DataFrame(acomptes_data))

st.markdown(f"""
### 🧾 Totaux

| Intitulé | Montant |
|----------|---------|
| **Total encaissé** | ${total_encaisse:,.2f} |
| **Solde dû** | **${solde:,.2f}** |

---
""", unsafe_allow_html=True)

# ----------------------------------------------
# EXPORT PDF
# ----------------------------------------------

export_df = pd.DataFrame({
    "Champ": [
        "Dossier N", "Nom", "Visa", "Date envoi", "Date acceptation",
        "Date refus", "Date annulation", "RFE", "Honoraires",
        "Autres frais", "Total facturé", "Total encaissé", "Solde dû"
    ],
    "Valeur": [
        val("Dossier N"), val("Nom"),
        f"{val('Sous-categories')} / {val('Visa')}",
        val("Date envoi"), val("Date acceptation"),
        val("Date refus"), val("Date annulation"), val("RFE"),
        honoraires, autres, total_facture, total_encaisse, solde
    ]
})

st.download_button(
    "📕 Télécharger la fiche comptabilité (PDF)",
    data=generate_pdf_from_dataframe(export_df),
    file_name=f"Comptabilite_{val('Dossier N')}.pdf",
    mime="application/pdf"
)
