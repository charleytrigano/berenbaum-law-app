import io
from datetime import datetime
import pandas as pd
import streamlit as st

from utils.sidebar import render_sidebar
from backend.dropbox_utils import load_database

# Optionnel : upload Dropbox si get_dbx existe
try:
    from backend.dropbox_utils import get_dbx
    HAS_DBX = True
except Exception:
    HAS_DBX = False


# =========================================================
# CONFIG
# =========================================================
st.set_page_config(page_title="📤 Export JSON → Excel", page_icon="📤", layout="wide")
render_sidebar()
st.title("📤 Export JSON → Excel (multi-feuilles)")
st.caption("Export horodaté. Fichier Excel sans signature.")

# =========================================================
# OUTILS
# =========================================================
def _sanitize_value(v):
    """Rend sérialisable / exportable (évite Timestamp non supporté)."""
    if v is None:
        return ""
    # pandas Timestamp / datetime / date
    if isinstance(v, (pd.Timestamp, datetime)):
        try:
            return v.strftime("%Y-%m-%d %H:%M:%S")
        except Exception:
            return str(v)
    # NaN
    if isinstance(v, float) and pd.isna(v):
        return ""
    return v


def sanitize_df(df: pd.DataFrame) -> pd.DataFrame:
    if df is None or df.empty:
        return pd.DataFrame()
    out = df.copy()
    for c in out.columns:
        out[c] = out[c].map(_sanitize_value)
    return out


def to_df(obj):
    if obj is None:
        return pd.DataFrame()
    if isinstance(obj, list):
        return pd.DataFrame(obj)
    if isinstance(obj, dict):
        # si dict de dicts (rare), on tente une conversion simple
        return pd.DataFrame([obj])
    return pd.DataFrame()


def build_excel_bytes(db: dict) -> bytes:
    clients_df = sanitize_df(to_df(db.get("clients", [])))
    visa_df = sanitize_df(to_df(db.get("visa", [])))
    escrow_df = sanitize_df(to_df(db.get("escrow", [])))
    compta_df = sanitize_df(to_df(db.get("compta", [])))
    tarifs_df = sanitize_df(to_df(db.get("tarifs", [])))
    tarifs_hist_df = sanitize_df(to_df(db.get("tarifs_history", [])))
    history_df = sanitize_df(to_df(db.get("history", [])))

    # Excel en mémoire
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        clients_df.to_excel(writer, index=False, sheet_name="clients")
        visa_df.to_excel(writer, index=False, sheet_name="visa")
        escrow_df.to_excel(writer, index=False, sheet_name="escrow")
        compta_df.to_excel(writer, index=False, sheet_name="compta")
        tarifs_df.to_excel(writer, index=False, sheet_name="tarifs")
        tarifs_hist_df.to_excel(writer, index=False, sheet_name="tarifs_history")
        history_df.to_excel(writer, index=False, sheet_name="history")

    return output.getvalue()


# =========================================================
# CHARGEMENT DB
# =========================================================
db = load_database()
if not isinstance(db, dict):
    st.error("❌ Base invalide (db n'est pas un dict).")
    st.stop()

# Aperçu rapide
c1, c2, c3, c4 = st.columns(4)
c1.metric("Clients", len(db.get("clients", [])))
c2.metric("Visa", len(db.get("visa", [])))
c3.metric("Escrow", len(db.get("escrow", [])))
c4.metric("Compta", len(db.get("compta", [])))

st.markdown("---")

# =========================================================
# EXPORT
# =========================================================
ts = datetime.now().strftime("%Y%m%d_%H%M%S")
filename = f"export_database_{ts}.xlsx"

colA, colB = st.columns([2, 1])

with colA:
    st.subheader("📦 Générer l’Excel multi-feuilles")
    st.write(
        "Le fichier contiendra les onglets : clients, visa, escrow, compta, tarifs, tarifs_history, history."
    )

with colB:
    st.subheader("⚙️ Options")
    upload_dropbox = st.checkbox("Uploader aussi sur Dropbox", value=False, disabled=(not HAS_DBX))
    dropbox_folder = st.text_input(
        "Dossier Dropbox (si upload activé)",
        value="/Apps/berenbaum-law/exports",
        disabled=(not HAS_DBX or not upload_dropbox),
    )

# Bouton génération
if st.button("📤 Générer l’export Excel", type="primary"):
    try:
        excel_bytes = build_excel_bytes(db)

        st.success("✔ Export Excel généré.")
        st.download_button(
            label="⬇️ Télécharger l’Excel",
            data=excel_bytes,
            file_name=filename,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

        # Upload Dropbox (optionnel)
        if upload_dropbox and HAS_DBX:
            try:
                import dropbox

                dbx = get_dbx()

                # Créer le dossier si besoin
                try:
                    dbx.files_create_folder_v2(dropbox_folder)
                except Exception:
                    pass  # si existe déjà, Dropbox renvoie une erreur : on ignore

                target_path = f"{dropbox_folder.rstrip('/')}/{filename}"

                dbx.files_upload(
                    excel_bytes,
                    target_path,
                    mode=dropbox.files.WriteMode.overwrite,
                )

                st.success(f"✔ Upload Dropbox OK : {target_path}")
            except Exception as e:
                st.error(f"❌ Upload Dropbox impossible : {e}")

    except Exception as e:
        st.error(f"❌ Erreur export : {e}")

st.markdown("---")
st.subheader("🔎 Aperçu des données (lecture seule)")

with st.expander("Voir un aperçu 'clients' (10 premières lignes)"):
    st.dataframe(to_df(db.get("clients", [])).head(10), use_container_width=True)

with st.expander("Voir un aperçu 'visa' (10 premières lignes)"):
    st.dataframe(to_df(db.get("visa", [])).head(10), use_container_width=True)
