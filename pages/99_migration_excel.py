import streamlit as st
import dropbox
import pandas as pd
import json

# ----------------------------------------------------
# CONFIG : récupère token & chemin depuis secrets.toml
# ----------------------------------------------------
DROPBOX_TOKEN = st.secrets["dropbox"]["DROPBOX_TOKEN"]
DROPBOX_FILE_PATH = st.secrets["paths"]["DROPBOX_FILE_PATH"]

# Nom EXACT du fichier Excel dans Dropbox
EXCEL_PATH = "/Clients BL.xlsx"  # ⚠️ Respecter le nom et les espaces


# ----------------------------------------------------
# Connexion Dropbox
# ----------------------------------------------------
def get_dbx():
    return dropbox.Dropbox(DROPBOX_TOKEN)


# ----------------------------------------------------
# Charger database.json depuis Dropbox
# ----------------------------------------------------
def load_db():
    dbx = get_dbx()
    try:
        _, res = dbx.files_download(DROPBOX_FILE_PATH)
        return json.loads(res.content.decode())
    except Exception:
        return {"clients": []}  # Base vide si fichier inexistant


# ----------------------------------------------------
# Sauver database.json sur Dropbox
# ----------------------------------------------------
def save_db(data):
    dbx = get_dbx()

    dbx.files_upload(
        json.dumps(data, indent=2).encode(),
        DROPBOX_FILE_PATH,
        mode=dropbox.files.WriteMode("overwrite")
    )


# ----------------------------------------------------
# Charger Excel depuis Dropbox → DataFrame
# ----------------------------------------------------
def load_excel_from_dropbox():
    dbx = get_dbx()
    try:
        _, res = dbx.files_download(EXCEL_PATH)
        excel_bytes = res.content
        df = pd.read_excel(excel_bytes)
        return df
    except Exception as e:
        st.error(f"❌ Impossible de charger l'Excel depuis Dropbox : {e}")
        return None


# ----------------------------------------------------
# 🔥 MIGRATION PRINCIPALE
# ----------------------------------------------------
def migrate_clients():
    st.title("Migration Excel → Dropbox JSON")

    st.info("📥 Téléchargement du fichier Excel depuis Dropbox…")
    df = load_excel_from_dropbox()

    if df is None:
        st.stop()

    st.success("Excel chargé ✔")
    st.dataframe(df.head())

    # Charger base existante
    db = load_db()

    # ----------------------------------------------------
    # 🔧 Convertir tous les types Excel → JSON-compatibles
    # ----------------------------------------------------
    # Remplacer NaN
    df = df.fillna("")

    # Conversion des dates
    for col in df.columns:
        if "date" in col.lower() or "Date" in col or df[col].dtype.kind == "M":
            try:
                df[col] = pd.to_datetime(df[col], errors="ignore").dt.strftime("%Y-%m-%d")
            except:
                pass  # si pas date, ignore

    # Supprimer types numpy (convertir en Python natif)
    df = df.astype(object)

    # Conversion finale
    clients_list = df.to_dict(orient="records")

    # Mise à jour JSON
    db["clients"] = clients_list

    # Sauvegarde
    save_db(db)

    st.success("🎉 Migration terminée ! Les clients ont été importés dans database.json")

    st.subheader("Aperçu des données migrées :")
    st.dataframe(clients_list)


# ----------------------------------------------------
# LANCEMENT
# ----------------------------------------------------
if __name__ == "__main__":
    migrate_clients()
