# backend/migrate_excel_to_json.py
import json
from io import BytesIO
from datetime import date, datetime

import pandas as pd

from backend.dropbox_utils import get_dbx
import streamlit as st


def _default_paths():
    """
    Chemins Dropbox par défaut (dans le dossier App /Apps/berenbaum-law/).
    Tu peux les remplacer par des secrets si tu veux, mais ici on est explicite et robuste.
    """
    base = "/Apps/berenbaum-law"
    return {
        "clients_xlsx": f"{base}/Clients.xlsx",
        "visa_xlsx": f"{base}/Visa.xlsx",
        "escrow_xlsx": f"{base}/Escrow.xlsx",
        "compta_xlsx": f"{base}/ComptaCli.xlsx",
    }


def _to_serializable(v):
    """Convertit en valeurs JSON-safe (notamment Timestamp)."""
    if v is None:
        return ""
    if isinstance(v, (pd.Timestamp, datetime, date)):
        # YYYY-MM-DD
        try:
            return str(pd.to_datetime(v).date())
        except Exception:
            return ""
    if pd.isna(v):
        return ""
    # numpy types -> python
    if hasattr(v, "item"):
        try:
            return v.item()
        except Exception:
            pass
    return v


def _clean_df(df: pd.DataFrame) -> pd.DataFrame:
    # Remplace NaN par "" pour le texte, gardera les nombres ensuite via conversion
    df = df.copy()
    df.columns = [str(c).strip() for c in df.columns]
    return df


def _download_excel(dbx, path: str) -> BytesIO:
    meta, res = dbx.files_download(path)
    return BytesIO(res.content)


def _read_excel_first_sheet(xls_bytes: BytesIO) -> pd.DataFrame:
    # On lit la première feuille (cas le plus courant)
    df = pd.read_excel(xls_bytes, sheet_name=0)
    return _clean_df(df)


def _df_to_records(df: pd.DataFrame) -> list[dict]:
    records = []
    for _, row in df.iterrows():
        d = {}
        for col in df.columns:
            d[col] = _to_serializable(row[col])
        records.append(d)
    return records


def _normalize_clients(records: list[dict]) -> list[dict]:
    """
    Normalise le minimum vital pour éviter que l’app casse.
    IMPORTANT: on conserve les colonnes existantes, on complète seulement les manquantes.
    """
    bool_fields = [
        "Escrow", "Escrow_a_reclamer", "Escrow_reclame",
        "Dossier envoye", "Dossier_envoye",
        "Dossier accepte", "Dossier refuse", "Dossier Annule", "RFE",
    ]
    float_fields = [
        "Montant honoraires (US $)", "Autres frais (US $)",
        "Acompte 1", "Acompte 2", "Acompte 3", "Acompte 4",
    ]
    text_fields = ["Nom", "Categories", "Sous-categories", "Visa", "mode de paiement", "Commentaire"]
    date_like_fields = [
        "Date", "Date envoi", "Date acceptation", "Date refus", "Date annulation", "Date reclamation",
        "Date Acompte 1", "Date Acompte 2", "Date Acompte 3", "Date Acompte 4",
        "Date Paiement 1", "Date Paiement 2", "Date Paiement 3", "Date Paiement 4",
    ]

    def to_bool(x):
        if isinstance(x, bool):
            return x
        s = str(x).strip().lower()
        return s in ["1", "true", "yes", "oui", "y", "vrai"]

    def to_float(x):
        if x in ["", None]:
            return 0.0
        try:
            return float(x)
        except Exception:
            return 0.0

    out = []
    for r in records:
        rr = dict(r)

        # Dossier N : on garde en string pour supporter 12937-1, 12937-2, etc.
        if "Dossier N" in rr:
            rr["Dossier N"] = str(rr["Dossier N"]).strip()

        # bools
        for k in bool_fields:
            if k in rr:
                rr[k] = to_bool(rr[k])

        # floats
        for k in float_fields:
            if k in rr:
                rr[k] = to_float(rr[k])

        # textes
        for k in text_fields:
            if k not in rr or rr[k] is None:
                rr[k] = ""
            rr[k] = str(rr[k]) if rr[k] is not None else ""

        # dates -> strings YYYY-MM-DD ou ""
        for k in date_like_fields:
            if k in rr:
                v = rr[k]
                if v in ["None", None]:
                    rr[k] = ""
                else:
                    try:
                        dt = pd.to_datetime(v, errors="coerce")
                        rr[k] = "" if pd.isna(dt) else str(dt.date())
                    except Exception:
                        rr[k] = ""

        # garanties minimales (sans écraser ton modèle)
        rr.setdefault("Escrow", False)
        rr.setdefault("Escrow_a_reclamer", False)
        rr.setdefault("Escrow_reclame", False)
        rr.setdefault("Dossier envoye", False)
        rr.setdefault("Dossier accepte", False)
        rr.setdefault("Dossier refuse", False)
        rr.setdefault("Dossier Annule", False)
        rr.setdefault("RFE", False)
        rr.setdefault("Commentaire", "")

        out.append(rr)

    return out


def convert_all_excels_to_json(paths: dict | None = None) -> dict:
    """
    Reconstruit la base JSON à partir des fichiers Excel Dropbox.
    IMPORTANT:
      - Si Clients.xlsx manque ou contient 0 ligne -> on lève une erreur.
      - On ne renvoie plus un JSON vide silencieux.
    """
    paths = paths or _default_paths()

    # Si tu as déjà des paths dans secrets, on les privilégie s'ils existent
    try:
        sp = st.secrets.get("paths", {})
        # Optionnel : si tu veux déclarer ces chemins dans secrets.toml plus tard
        paths["clients_xlsx"] = sp.get("DROPBOX_CLIENTS_XLSX", paths["clients_xlsx"])
        paths["visa_xlsx"] = sp.get("DROPBOX_VISA_XLSX", paths["visa_xlsx"])
        paths["escrow_xlsx"] = sp.get("DROPBOX_ESCROW_XLSX", paths["escrow_xlsx"])
        paths["compta_xlsx"] = sp.get("DROPBOX_COMPTA_XLSX", paths["compta_xlsx"])
    except Exception:
        pass

    dbx = get_dbx()

    # --- CLIENTS (obligatoire) ---
    try:
        clients_bytes = _download_excel(dbx, paths["clients_xlsx"])
    except Exception as e:
        raise RuntimeError(f"Impossible de télécharger Clients.xlsx ({paths['clients_xlsx']}): {e}")

    clients_df = _read_excel_first_sheet(clients_bytes)
    if clients_df is None or clients_df.empty:
        raise RuntimeError(
            f"Clients.xlsx est vide ou illisible ({paths['clients_xlsx']}). "
            "Vérifie que le fichier contient bien les dossiers."
        )

    clients_records = _df_to_records(clients_df)
    clients_records = _normalize_clients(clients_records)

    # --- VISA (optionnel) ---
    visa_records = []
    try:
        visa_bytes = _download_excel(dbx, paths["visa_xlsx"])
        visa_df = _read_excel_first_sheet(visa_bytes)
        if visa_df is not None and not visa_df.empty:
            visa_records = _df_to_records(visa_df)
    except Exception:
        visa_records = []

    # --- ESCROW (optionnel) ---
    escrow_records = []
    try:
        escrow_bytes = _download_excel(dbx, paths["escrow_xlsx"])
        escrow_df = _read_excel_first_sheet(escrow_bytes)
        if escrow_df is not None and not escrow_df.empty:
            escrow_records = _df_to_records(escrow_df)
    except Exception:
        escrow_records = []

    # --- COMPTA (optionnel) ---
    compta_records = []
    try:
        compta_bytes = _download_excel(dbx, paths["compta_xlsx"])
        compta_df = _read_excel_first_sheet(compta_bytes)
        if compta_df is not None and not compta_df.empty:
            compta_records = _df_to_records(compta_df)
    except Exception:
        compta_records = []

    return {
        "clients": clients_records,
        "visa": visa_records,
        "escrow": escrow_records,
        "compta": compta_records,
    }
