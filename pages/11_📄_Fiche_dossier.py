import streamlit as st
import pandas as pd

from utils.sidebar import render_sidebar
from backend.dropbox_utils import load_database
from utils.timeline_builder import build_timeline

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
escrow_history = db.get("escrow_history", [])

if not clients:
    st.error("Aucun dossier trouvé.")
    st.stop()

df = pd.DataFrame(clients)
df["Dossier N"] = df["Dossier N"].astype(str)

# =====================================================
# SÉLECTION DOSSIER
# =====================================================
labels = df.apply(
    lambda r: f"{r['Dossier N']} — {r.get('Nom','')}", axis=1
).tolist()

mapping = dict(zip(labels, df["Dossier N"]))
selected_label = st.selectbox("Sélectionner un dossier", labels)
selected = mapping[selected_label]

dossier = df[df["Dossier N"] == selected].iloc[0].to_dict()

# =====================================================
# OUTILS
# =====================================================
def to_float(v):
    try:
        return float(v or 0)
    except Exception:
        return 0.0

def total_acomptes(d):
    return sum(to_float(d.get(f"Acompte {i}", 0)) for i in range(1, 5))

# =====================================================
# INFOS GÉNÉRALES
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
st.subheader("💰 Facturation")

hon = to_float(dossier.get("Montant honoraires (US $)", 0))
frais = to_float(dossier.get("Autres frais (US $)", 0))
total_facture = hon + frais
total_encaisse = total_acomptes(dossier)
solde = total_facture - total_encaisse

k1, k2, k3, k4 = st.columns(4)
k1.metric("Honoraires", f"${hon:,.2f}")
k2.metric("Autres frais", f"${frais:,.2f}")
k3.metric("Total encaissé", f"${total_encaisse:,.2f}")
k4.metric("Solde dû", f"${solde:,.2f}")

st.markdown("---")

# =====================================================
# ESCROW – ÉTAT ACTUEL
# =====================================================
st.subheader("💼 Escrow — État actuel")

montant_escrow = total_encaisse

if dossier.get("Escrow"):
    st.info(f"Escrow actif — ${montant_escrow:,.2f}")
elif dossier.get("Escrow_a_reclamer"):
    st.warning(f"Escrow à réclamer — ${montant_escrow:,.2f}")
elif dossier.get("Escrow_reclame"):
    st.success(f"Escrow réclamé — ${montant_escrow:,.2f}")
else:
    st.write("Aucun escrow pour ce dossier.")

# =====================================================
# 🕓 HISTORIQUE ESCROW (PAR DOSSIER)
# =====================================================
st.markdown("---")
st.subheader("🕓 Historique des escrows (dossier)")

hist = [
    h for h in escrow_history
    if str(h.get("Dossier N")) == str(dossier["Dossier N"])
]

if not hist:
    st.info("Aucun historique escrow pour ce dossier.")
else:
    hist_df = pd.DataFrame(hist)
    hist_df["Montant"] = hist_df["Montant"].astype(float)

    st.dataframe(
        hist_df.sort_values("Date", ascending=False),
        use_container_width=True,
    )

    st.metric(
        "Total escrow historisé",
        f"${hist_df['Montant'].sum():,.2f}"
    )

# =====================================================
# TIMELINE
# =====================================================
st.markdown("---")
st.subheader("🧭 Timeline du dossier")

timeline = build_timeline(dossier)

if not timeline:
    st.info("Aucun événement enregistré.")
else:
    for ev in timeline:
        line = f"**{ev['date'].date()}** — {ev['label']}"
        if ev.get("amount"):
            line += f" — ${ev['amount']:,.2f}"
        st.markdown(line)