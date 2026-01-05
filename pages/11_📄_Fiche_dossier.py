import streamlit as st
import pandas as pd

from utils.sidebar import render_sidebar
from backend.dropbox_utils import load_database
from utils.timeline_builder import build_timeline
from utils.pdf_export import export_dossier_pdf


# ---------------------------------------------------------
# Helpers
# ---------------------------------------------------------
def to_float(v):
    try:
        return float(v or 0)
    except Exception:
        return 0.0


def safe_str(v):
    return "" if v is None else str(v)


def sum_acomptes(dossier: dict) -> float:
    return sum(to_float(dossier.get(f"Acompte {i}", 0)) for i in range(1, 5))


def escrow_state(dossier: dict) -> str:
    if bool(dossier.get("Escrow", False)):
        return "Actif"
    if bool(dossier.get("Escrow_a_reclamer", False)):
        return "À réclamer"
    if bool(dossier.get("Escrow_reclame", False)):
        return "Réclamé"
    return "Aucun"


# ---------------------------------------------------------
# CONFIG & SIDEBAR
# ---------------------------------------------------------
st.set_page_config(page_title="📄 Fiche dossier", page_icon="📄", layout="wide")
render_sidebar()
st.title("📄 Fiche dossier")

# ---------------------------------------------------------
# CHARGEMENT BASE
# ---------------------------------------------------------
db = load_database()
clients = db.get("clients", [])

if not clients:
    st.error("Aucun dossier trouvé.")
    st.stop()

df = pd.DataFrame(clients).copy()
df["Dossier N"] = df.get("Dossier N", "").astype(str).fillna("").str.strip()
df["Nom"] = df.get("Nom", "").astype(str).fillna("").str.strip()

# ---------------------------------------------------------
# Sélection dossier (Dossier N + Nom)
# ---------------------------------------------------------
df["Label"] = df.apply(lambda r: f"{r['Dossier N']} — {r['Nom']}".strip(" —"), axis=1)
labels = df["Label"].dropna().unique().tolist()
labels = sorted(labels, key=lambda x: x.lower())

selected_label = st.selectbox("Rechercher / sélectionner un dossier", labels)
selected_dossier_n = selected_label.split(" — ", 1)[0].strip()

dossier = df[df["Dossier N"] == selected_dossier_n].iloc[0].to_dict()

# ---------------------------------------------------------
# INFOS GÉNÉRALES
# ---------------------------------------------------------
st.subheader(f"Dossier {dossier.get('Dossier N','')} — {dossier.get('Nom','')}")

c1, c2, c3 = st.columns(3)
c1.write(f"**Catégorie** : {dossier.get('Categories','')}")
c2.write(f"**Sous-catégorie** : {dossier.get('Sous-categories','')}")
c3.write(f"**Visa** : {dossier.get('Visa','')}")

st.markdown("---")

# ---------------------------------------------------------
# FACTURATION & RÈGLEMENTS
# ---------------------------------------------------------
st.subheader("💰 Facturation & règlements")

colF, colP = st.columns(2)

with colF:
    honoraires = to_float(dossier.get("Montant honoraires (US $)", 0))
    frais = to_float(dossier.get("Autres frais (US $)", 0))
    total_facture = honoraires + frais

    st.metric("Montant honoraires", f"${honoraires:,.2f}")
    st.metric("Autres frais", f"${frais:,.2f}")
    st.metric("Total facturé", f"${total_facture:,.2f}")

with colP:
    total_encaisse = sum_acomptes(dossier)

    # Détail des acomptes payés
    for i in range(1, 5):
        a = to_float(dossier.get(f"Acompte {i}", 0))
        if a > 0:
            date_pay = dossier.get(f"Date Acompte {i}", "")
            mode = dossier.get(f"Mode Acompte {i}", "") or dossier.get("mode de paiement", "")
            st.write(
                f"**Acompte {i}** : ${a:,.2f}  "
                f"{('— ' + mode) if mode else ''}  "
                f"{('— ' + str(date_pay)) if date_pay else ''}"
            )

    solde = total_facture - total_encaisse
    st.metric("Total encaissé", f"${total_encaisse:,.2f}")
    st.metric("Solde dû", f"${solde:,.2f}")

st.markdown("---")

# ---------------------------------------------------------
# STATUT FINANCIER
# ---------------------------------------------------------
if solde <= 0:
    st.success("✅ Dossier payé")
elif total_encaisse > 0:
    st.warning("🟡 Paiement partiel")
else:
    st.error("🔴 Impayé")

# ---------------------------------------------------------
# STATUTS & ESCROW (présentation alignée)
# ---------------------------------------------------------
st.markdown("---")
st.subheader("📦 Statuts & Escrow")

# On construit une vue “tableau” : libellé à gauche, valeur à droite
rows = []

rows.append(("Dossier envoyé", "Oui" if bool(dossier.get("Dossier envoye", False)) else "Non"))
rows.append(("Date dossier envoyé", safe_str(dossier.get("Date envoi", ""))))

rows.append(("Dossier accepté", "Oui" if bool(dossier.get("Dossier accepte", False)) else "Non"))
rows.append(("Date dossier accepté", safe_str(dossier.get("Date acceptation", ""))))

rows.append(("Dossier refusé", "Oui" if bool(dossier.get("Dossier refuse", False)) else "Non"))
rows.append(("Date dossier refusé", safe_str(dossier.get("Date refus", ""))))

rows.append(("Dossier annulé", "Oui" if bool(dossier.get("Dossier Annule", False)) else "Non"))
rows.append(("Date dossier annulé", safe_str(dossier.get("Date annulation", ""))))

rows.append(("RFE", "Oui" if bool(dossier.get("RFE", False)) else "Non"))
rows.append(("Date RFE", safe_str(dossier.get("Date reclamation", ""))))

esc_state = escrow_state(dossier)
esc_amount = sum_acomptes(dossier)  # ✅ IMPORTANT: total acomptes, pas Acompte 1
rows.append(("Escrow (état)", esc_state))
rows.append(("Montant en escrow", f"${esc_amount:,.2f}" if esc_state != "Aucun" else ""))

status_df = pd.DataFrame(rows, columns=["Élément", "Valeur"])
st.dataframe(status_df, use_container_width=True, hide_index=True)

# ---------------------------------------------------------
# TIMELINE
# ---------------------------------------------------------
st.markdown("---")
st.subheader("🕓 Timeline du dossier (faits datés)")

timeline = build_timeline(dossier)

if not timeline:
    st.info("Aucun événement daté enregistré.")
else:
    for ev in timeline:
        line = f"**{ev['date'].date()}** — {ev['label']}"
        if ev.get("amount") is not None:
            line += f" — ${float(ev['amount']):,.2f}"
        if ev.get("meta"):
            line += f" — {ev['meta']}"
        st.markdown(line)

# ---------------------------------------------------------
# EXPORT PDF
# ---------------------------------------------------------
st.markdown("---")
if st.button("📄 Exporter la fiche dossier en PDF", type="primary"):
    output = f"/tmp/dossier_{dossier['Dossier N']}.pdf"
    export_dossier_pdf(dossier, output)
    with open(output, "rb") as f:
        st.download_button(
            "⬇️ Télécharger le PDF",
            f,
            file_name=f"Dossier_{dossier['Dossier N']}.pdf",
            mime="application/pdf",
        )