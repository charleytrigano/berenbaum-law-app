import streamlit as st
import pandas as pd

from utils.sidebar import render_sidebar
from backend.dropbox_utils import load_database
from utils.timeline_builder import build_timeline
from utils.pdf_export import export_dossier_pdf
from utils.status_utils import normalize_bool

# =====================================================
# CONFIG
# =====================================================
st.set_page_config(page_title="📄 Fiche dossier", page_icon="📄", layout="wide")
render_sidebar()
st.title("📄 Fiche dossier")

# =====================================================
# LOAD DATABASE
# =====================================================
db = load_database()
clients = db.get("clients", [])

if not clients:
    st.error("Aucun dossier trouvé.")
    st.stop()

df = pd.DataFrame(clients)
df["Dossier N"] = df["Dossier N"].astype(str)

# =====================================================
# SELECTION DOSSIER
# =====================================================
labels = df.apply(
    lambda r: f"{r['Dossier N']} — {r.get('Nom','')}", axis=1
).tolist()

label_to_id = dict(zip(labels, df["Dossier N"]))

selected_label = st.selectbox("Sélectionner un dossier", labels)
selected_id = label_to_id[selected_label]

row = df[df["Dossier N"] == selected_id].iloc[0]
dossier = row.to_dict()

# =====================================================
# ESCROW — LOGIQUE UNIQUE
# =====================================================
def compute_escrow_amount(d):
    if (
        normalize_bool(d.get("Dossier accepte"))
        or normalize_bool(d.get("Dossier refuse"))
        or normalize_bool(d.get("Dossier Annule"))
    ):
        return 0.0

    total = 0.0
    for i in range(1, 5):
        try:
            total += float(d.get(f"Acompte {i}", 0) or 0)
        except:
            pass
    return total


escrow_amount = compute_escrow_amount(dossier)

# =====================================================
# INFOS GENERALES
# =====================================================
st.subheader(f"Dossier {dossier['Dossier N']} — {dossier.get('Nom','')}")

c1, c2, c3 = st.columns(3)
c1.write(f"**Catégorie** : {dossier.get('Categories','')}")
c2.write(f"**Sous-catégorie** : {dossier.get('Sous-categories','')}")
c3.write(f"**Visa** : {dossier.get('Visa','')}")

st.markdown("---")

# =====================================================
# FACTURATION
# =====================================================
hon = float(dossier.get("Montant honoraires (US $)", 0))
frais = float(dossier.get("Autres frais (US $)", 0))
total_facture = hon + frais

total_encaisse = sum(
    float(dossier.get(f"Acompte {i}", 0) or 0) for i in range(1, 5)
)
solde = total_facture - total_encaisse

c1, c2, c3 = st.columns(3)
c1.metric("Total facturé", f"${total_facture:,.2f}")
c2.metric("Total encaissé", f"${total_encaisse:,.2f}")
c3.metric("Solde dû", f"${solde:,.2f}")

st.markdown("---")

# =====================================================
# ESCROW
# =====================================================
st.subheader("💼 Escrow")

if escrow_amount > 0:
    st.warning(f"💼 Montant en escrow : **${escrow_amount:,.2f}**")
else:
    st.success("Aucun montant en escrow pour ce dossier.")

st.caption(
    "Règle : les acomptes restent en escrow tant que le dossier n’est ni accepté, ni refusé, ni annulé."
)

st.markdown("---")

# =====================================================
# STATUTS
# =====================================================
st.subheader("📦 Statuts du dossier")

s1, s2, s3, s4, s5 = st.columns(5)
s1.metric("Envoyé", "✔" if dossier.get("Dossier envoye") else "—")
s2.metric("Accepté", "✔" if dossier.get("Dossier accepte") else "—")
s3.metric("Refusé", "✔" if dossier.get("Dossier refuse") else "—")
s4.metric("Annulé", "✔" if dossier.get("Dossier Annule") else "—")
s5.metric("RFE", "✔" if dossier.get("RFE") else "—")

# =====================================================
# TIMELINE
# =====================================================
st.markdown("---")
st.subheader("🕓 Timeline")

timeline = build_timeline(dossier)
for ev in timeline:
    st.markdown(f"**{ev['date'].date()}** — {ev['label']}")

# =====================================================
# EXPORT PDF
# =====================================================
st.markdown("---")
if st.button("📄 Exporter la fiche dossier en PDF"):
    output = f"/tmp/dossier_{dossier['Dossier N']}.pdf"
    export_dossier_pdf(dossier, output)
    with open(output, "rb") as f:
        st.download_button(
            "⬇️ Télécharger le PDF",
            f,
            file_name=f"Dossier_{dossier['Dossier N']}.pdf",
            mime="application/pdf",
        )