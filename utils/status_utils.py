# utils/status_utils.py
import pandas as pd

# Groupes d'alias pour chaque statut
STATUS_ALIAS_GROUPS = {
    "Dossier envoye": [
        "Dossier envoye",
        "Dossier_envoye",
        "Dossier envoyé",
        "Dossier Envoye",
    ],
    "Dossier accepte": [
        "Dossier accepte",
        "Dossier_accepté",
        "Dossier accepté",
        "Dossier Accepte",
    ],
    "Dossier refuse": [
        "Dossier refuse",
        "Dossier_refuse",
        "Dossier refusé",
        "Dossier Refuse",
    ],
    "Dossier Annule": [
        "Dossier Annule",
        "Dossier_annule",
        "Dossier annulé",
        "Dossier Annulé",
    ],
    "RFE": ["RFE"],
}


def normalize_bool(x):
    """Transforme n'importe quelle valeur en bool cohérent."""
    if isinstance(x, bool):
        return x
    if x is None:
        return False
    s = str(x).strip().lower()
    return s in ["true", "1", "1.0", "yes", "oui", "y", "vrai"]


def normalize_status_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Harmonise les colonnes de statuts dans un DataFrame :
    - crée les colonnes canoniques (Dossier envoye, Dossier accepte, etc.)
    - fusionne les valeurs venant des alias (Dossier_envoye, Dossier envoyé, ...).
    """
    df = df.copy()

    for canonical, aliases in STATUS_ALIAS_GROUPS.items():
        combined = None

        for col in aliases:
            if col in df.columns:
                s = df[col].apply(normalize_bool)
                if combined is None:
                    combined = s
                else:
                    combined = combined | s  # union logique

        if combined is None:
            df[canonical] = False
        else:
            df[canonical] = combined

    return df


def update_status_row(
    df: pd.DataFrame,
    idx,
    envoye=None,
    accepte=None,
    refuse=None,
    annule=None,
    rfe=None,
) -> pd.DataFrame:
    """
    Met à jour les statuts pour UNE ligne donnée dans le DataFrame,
    en écrivant à la fois dans la colonne canonique et dans les alias présents.
    """
    df = df.copy()

    updates = {
        "Dossier envoye": envoye,
        "Dossier accepte": accepte,
        "Dossier refuse": refuse,
        "Dossier Annule": annule,
        "RFE": rfe,
    }

    for canonical, value in updates.items():
        if value is None:
            continue

        bool_val = bool(value)

        # 1) Assure la colonne canonique
        if canonical not in df.columns:
            df[canonical] = False
        df.loc[idx, canonical] = bool_val

        # 2) Répercute sur les alias existants (pour compatibilité JSON historique)
        aliases = STATUS_ALIAS_GROUPS.get(canonical, [])
        for col in aliases:
            if col == canonical:
                continue
            if col not in df.columns:
                # On crée aussi la colonne alias pour que le JSON ait les deux si besoin
                df[col] = False
            df.loc[idx, col] = bool_val

    return df
