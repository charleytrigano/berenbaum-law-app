import streamlit as st
import pandas as pd
import json
from backend.dropbox_utils import save_database

st.title("Migration Excel → JSON (Dropbox)")

EXCEL_FILE = "Clients BL.xlsx"   # Ton fichier importé

st.info("Chargement du fichier Excel…")

# Chargement des feuilles
xls = pd.ExcelFile(EXCEL_FILE)

# --- 1. Clients ---
df_clients = pd.read_excel(xls, "Clients")
clients = df_clients.fillna("").to_dict(orient="records")

# --- 2. Visa ---
df_visa = pd.read_excel(xls, "Visa")
visa = df_visa.fillna("").to_dict(orient="records")

# --- 3. Escrow (existe mais vide ou partiel) ---
if "Escrow" in xls.sheet_names:
    df_escrow = pd.read_excel(xls, "Escrow").fillna("")
    escrow = df_escrow.to_dict(orient="records")
else:
    escrow = []

# --- 4. ComptaCli (vide → structure simple) ---
if "ComptaCli" in xls.sheet_names:
    df_compta = pd.read_excel(xls, "ComptaCli").fillna("")
    compta = df_compta.to_dict(orient="records")
else:
    compta = []

# --- JSON final ---
db = {
    "clients": clients,
    "visa": visa,
    "escrow": escrow,
    "compta": compta
}

# Sauvegarde dans Dropbox
save_database(db)

st.success("Migration terminée 🎉 Fichier JSON mis à jour dans Dropbox.")
st.json(db)

