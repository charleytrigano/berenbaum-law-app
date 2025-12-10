import streamlit as st
from utils.sidebar import render_sidebar
render_sidebar()
import pandas as pd
from backend.dropbox_utils import load_database
from components.export_pdf import generate_pdf




st.set_page_config(page_title="📄 Fiche dossier", page_icon="📄", layout="wide")

# ---------------------------------------------------------
# 🔹 Charger base
# ---------------------------------------------------------
db = load_database()
clients = db.get("clients", [])
df = pd.DataFrame(clients)

if df.empty:
    st.error("Aucun dossier trouvé.")
    st.stop()

# ---------------------------------------------------------
# 🔹 Normalisation Dossier N
# ---------------------------------------------------------
df["Dossier N"] = pd.to_numeric(df["Dossier N"], errors="coerce").astype("Int64")
nums = sorted(df["Dossier N"].dropna().astype(int).unique())

# ---------------------------------------------------------
# 🔹 Sélection dossier
# ---------------------------------------------------------
st.header("📄 Fiche dossier")
selected = st.selectbox("Sélectionner un dossier :", nums)

row = df[df["Dossier N"] == selected].iloc[0]

# ---------------------------------------------------------
# UTILS
# ---------------------------------------------------------
def money(x):
    try:
        return f"${float(x):,.2f}"
    except:
        return "$0.00"

def normalize_date(x):
    return "" if x in ["None", None, "", "nan"] else str(x)

# ---------------------------------------------------------
# 🔹 TITRE
# ---------------------------------------------------------
st.markdown(f"""
# 🧾 Dossier {row['Dossier N']}
### 👤 {row['Nom']}
""")

# ---------------------------------------------------------
# 🔹 FACTURATION + REGLEMENTS (sur 2 colonnes)
# ---------------------------------------------------------
st.subheader("💰 Facturation & Paiements")

# Montants
hon = float(row.get("Montant honoraires (US $)", 0))
frais = float(row.get("Autres frais (US $)", 0))
total = hon + frais

# Acomptes
ac1 = float(row.get("Acompte 1", 0))
ac2 = float(row.get("Acompte 2", 0))
ac3 = float(row.get("Acompte 3", 0))
ac4 = float(row.get("Acompte 4", 0))

total_paid = ac1 + ac2 + ac3 + ac4
solde = total - total_paid

# Badge paiement
if solde <= 0:
    badge_pay = "🟢 **Payé**"
elif total_paid == 0:
    badge_pay = "🔴 **Impayé**"
else:
    badge_pay = "🟡 **Partiellement payé**"

colF1, colF2 = st.columns(2)

with colF1:
    st.markdown("### 💵 Facturation")
    st.write(f"**Honoraires :** {money(hon)}")
    st.write(f"**Autres frais :** {money(frais)}")
    st.write(f"**Total :** {money(total)}")
    st.write(f"### 💳 Paiements : {badge_pay}")
    st.write(f"**Total payé :** {money(total_paid)}")
    st.write(f"**Solde restant :** {money(solde)}")

with colF2:
    st.markdown("### 🏦 Acomptes & Modes de règlement")

    def display_acompte(label, val, date, mode):
        st.markdown(f"""
        **{label} :** {money(val)}  
        📅 *{normalize_date(date)}*  
        💳 *{mode if mode else "—"}*
        """)

    display_acompte("Acompte 1", ac1, row.get("Date Acompte 1"), row.get("mode de paiement"))
    display_acompte("Acompte 2", ac2, row.get("Date Acompte 2"), row.get("mode de paiement2"))
    display_acompte("Acompte 3", ac3, row.get("Date Acompte 3"), row.get("mode de paiement3"))
    display_acompte("Acompte 4", ac4, row.get("Date Acompte 4"), row.get("mode de paiement4"))

# ---------------------------------------------------------
# 📝 COMMENTAIRE
# ---------------------------------------------------------

st.subheader("📝 Commentaire")

# On récupère proprement le commentaire
commentaire = str(row.get("Commentaire", "") or "").strip()

if commentaire:
    st.markdown(
        f"""
        <div style="
            background-color:#2b2b2b;
            padding:15px;
            border-radius:10px;
            border:1px solid #444;
            color:white;
            font-size:15px;
        ">
            {commentaire}
        </div>
        """,
        unsafe_allow_html=True
    )
else:
    st.info("Aucun commentaire n’a été enregistré pour ce dossier.")

    # -----------------------------
# 📝 COMMENTAIRE DU DOSSIER
# -----------------------------

st.markdown("## 📝 Commentaire")

commentaire = dossier.get("Commentaire", "").strip()

if commentaire:
    st.markdown(
        f"""
        <div style="
            background-color:#2b2b2b;
            padding:15px;
            border-radius:10px;
            border:1px solid #444;
            color:#e6e6e6;
        ">
            {commentaire}
        </div>
        """,
        unsafe_allow_html=True
    )
else:
    st.info("Aucun commentaire n’a été enregistré pour ce dossier.")




# ---------------------------------------------------------
# 🔹 INFORMATIONS GÉNÉRALES
# ---------------------------------------------------------
st.markdown("---")
st.subheader("📚 Informations générales")

st.write(f"**Catégorie :** {row.get('Categories', '')}")
st.write(f"**Sous-catégorie :** {row.get('Sous-categories', '')}")
st.write(f"**Visa :** {row.get('Visa', '')}")
st.write(f"**Date de création :** {normalize_date(row.get('Date'))}")

# ---------------------------------------------------------
# 🔹 STATUTS & ESCROW
# ---------------------------------------------------------
st.markdown("---")
st.subheader("📦 Statuts du dossier")

colS1, colS2, colS3 = st.columns(3)

with colS1:
    st.write("**Envoyé :**", "✅" if row.get("Dossier envoye") else "❌")
    st.write("**Accepté :**", "✅" if row.get("Dossier accepte") else "❌")

with colS2:
    st.write("**Refusé :**", "❌" if not row.get("Dossier refuse") else "⛔")
    st.write("**RFE :**", "⚠️" if row.get("RFE") else "❌")

with colS3:
    st.write("**Escrow en cours :**", "💰" if row.get("Escrow") else "—")
    st.write("**Escrow à réclamer :**", "📬" if row.get("Escrow_a_reclamer") else "—")
    st.write("**Escrow réclamé :**", "✔️" if row.get("Escrow_reclame") else "—")

# ---------------------------------------------------------
# 🔹 TIMELINE
# ---------------------------------------------------------
st.markdown("---")
st.subheader("🕓 Timeline du dossier")

timeline_html = "<div style='line-height:1.8;'>"

if row.get("Date"):
    timeline_html += f"<div>📄 <b>Dossier créé :</b> {row['Date']}</div>"

if row.get("Escrow"):
    timeline_html += "<div>💰 <b>Escrow ouvert</b></div>"

if row.get("Dossier envoye"):
    timeline_html += f"<div>📤 <b>Dossier envoyé :</b> {row.get('Date envoi','')}</div>"

timeline_html += "</div>"

st.markdown(timeline_html, unsafe_allow_html=True)

# ---------------------------------------------------------
# 🔹 ACTIONS
# ---------------------------------------------------------
st.markdown("---")
st.subheader("⚙️ Actions")

colA1, colA2, colA3 = st.columns(3)

with colA1:
    if st.button("✏️ Modifier ce dossier", key="btn_edit"):
        st.switch_page("pages/03_✏️_Modifier_dossier.py")

with colA2:
    if st.button("📄 Export PDF", key="btn_pdf"):
        fname = generate_pdf(row)
        with open(fname, "rb") as f:
            st.download_button(
                label="⬇ Télécharger le PDF",
                data=f,
                file_name=f"Dossier_{row['Dossier N']}.pdf",
                mime="application/pdf",
                key="btn_pdf_dl"
            )

with colA3:
    st.button("🗑️ Supprimer", key="btn_delete")
