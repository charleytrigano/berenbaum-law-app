import pandas as pd


def _safe_str(x) -> str:
    if x is None:
        return ""
    if isinstance(x, float) and pd.isna(x):
        return ""
    s = str(x)
    return "" if s.lower() in ["nan", "none"] else s.strip()


def _safe_float(x) -> float:
    try:
        if x is None:
            return 0.0
        if isinstance(x, float) and pd.isna(x):
            return 0.0
        return float(x)
    except Exception:
        return 0.0


def _safe_bool(x) -> bool:
    if isinstance(x, bool):
        return x
    if x is None:
        return False
    s = str(x).strip().lower()
    return s in ["1", "true", "yes", "oui", "y", "vrai"]


def convert_clients_excel_to_json(df_clients: pd.DataFrame):
    """
    Convertit l'onglet clients (Clients.xlsx) en liste de dict compatible database.json.
    Ajout : Commentaire (si absent dans Excel -> défaut "").
    """
    df = df_clients.copy()

    # Harmonisation minimale des colonnes possibles
    rename_map = {
        "Sous categories": "Sous-categories",
        "Sous-catégories": "Sous-categories",
        "Catégorie": "Categories",
        "Catégories": "Categories",
        "Dossier N°": "Dossier N",
        "Dossier No": "Dossier N",
        "Dossier_envoye": "Dossier_envoye",
        "Dossier envoyé": "Dossier_envoye",
    }
    df.rename(columns=rename_map, inplace=True)

    # Garantir présence des colonnes attendues (sans casser si Excel est incomplet)
    required_cols = [
        "Dossier N", "Nom", "Date", "Categories", "Sous-categories", "Visa",
        "Montant honoraires (US $)", "Autres frais (US $)",
        "Acompte 1", "Acompte 2", "Acompte 3", "Acompte 4",
        "Date Acompte 1", "Date Acompte 2", "Date Acompte 3", "Date Acompte 4",
        "mode de paiement",
        "Commentaire",  # ✅ AJOUT
        "Escrow", "Escrow_a_reclamer", "Escrow_reclame",
        "Dossier_envoye", "Date envoi",
        "Dossier accepte", "Date acceptation",
        "Dossier refuse", "Date refus",
        "Dossier Annule", "Date annulation",
        "RFE", "Date reclamation",
    ]
    for c in required_cols:
        if c not in df.columns:
            df[c] = ""

    clients = []
    for _, r in df.iterrows():
        clients.append({
            "Dossier N": _safe_str(r.get("Dossier N")),
            "Nom": _safe_str(r.get("Nom")),
            "Date": _safe_str(r.get("Date")),
            "Categories": _safe_str(r.get("Categories")),
            "Sous-categories": _safe_str(r.get("Sous-categories")),
            "Visa": _safe_str(r.get("Visa")),

            "Montant honoraires (US $)": _safe_float(r.get("Montant honoraires (US $)")),
            "Autres frais (US $)": _safe_float(r.get("Autres frais (US $)")),

            "Acompte 1": _safe_float(r.get("Acompte 1")),
            "Acompte 2": _safe_float(r.get("Acompte 2")),
            "Acompte 3": _safe_float(r.get("Acompte 3")),
            "Acompte 4": _safe_float(r.get("Acompte 4")),

            "Date Acompte 1": _safe_str(r.get("Date Acompte 1")),
            "Date Acompte 2": _safe_str(r.get("Date Acompte 2")),
            "Date Acompte 3": _safe_str(r.get("Date Acompte 3")),
            "Date Acompte 4": _safe_str(r.get("Date Acompte 4")),

            "mode de paiement": _safe_str(r.get("mode de paiement")),

            # ✅ AJOUT : Commentaire persisté
            "Commentaire": _safe_str(r.get("Commentaire")),

            "Escrow": _safe_bool(r.get("Escrow")),
            "Escrow_a_reclamer": _safe_bool(r.get("Escrow_a_reclamer")),
            "Escrow_reclame": _safe_bool(r.get("Escrow_reclame")),

            "Dossier_envoye": _safe_bool(r.get("Dossier_envoye")),
            "Date envoi": _safe_str(r.get("Date envoi")),

            "Dossier accepte": _safe_bool(r.get("Dossier accepte")),
            "Date acceptation": _safe_str(r.get("Date acceptation")),

            "Dossier refuse": _safe_bool(r.get("Dossier refuse")),
            "Date refus": _safe_str(r.get("Date refus")),

            "Dossier Annule": _safe_bool(r.get("Dossier Annule")),
            "Date annulation": _safe_str(r.get("Date annulation")),

            "RFE": _safe_bool(r.get("RFE")),
            "Date reclamation": _safe_str(r.get("Date reclamation")),
        })

    return clients
