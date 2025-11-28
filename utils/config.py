FILE_ID = "1HU8rfXaG_uu-TVcAEtbs00jsvpQaiAgP"
import streamlit as st

DROPBOX_TOKEN = st.secrets["DROPBOX_TOKEN"]
DROPBOX_FILE_PATH = "/database.json"  # ton fichier est bien à la racine
SHEET_CLIENTS = "Clients"
SHEET_ESCROW = "Escrow"
SHEET_VISA = "Visa"
SHEET_COMPTA = "ComptaCli"
# Dropbox
DROPBOX_TOKEN = st.secrets["DROPBOX_TOKEN"]

# Chemin du fichier Excel source
DROPBOX_EXCEL_PATH = "/Clients BL.xlsx"

# Chemin de la base JSON générée
DROPBOX_JSON_PATH = "/database.json"

import streamlit as st

DROPBOX_TOKEN = st.secrets["dropbox"]["DROPBOX_TOKEN"]

DROPBOX_EXCEL_PATH = "/Clients BL.xlsx"    # le nom exact dans ton Dropbox
DROPBOX_JSON_PATH = "/database.json"       # fichier généré

import streamlit as st

DROPBOX_TOKEN = st.secrets["dropbox"]["DROPBOX_TOKEN"]

DROPBOX_EXCEL_PATH = "/Clients BL.xlsx"  # ton Excel
DROPBOX_JSON_PATH = "/database.json"     # base générée




