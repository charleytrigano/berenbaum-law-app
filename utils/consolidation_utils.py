import pandas as pd


def get_family(df: pd.DataFrame, parent_id) -> pd.DataFrame:
    """
    Retourne le dossier parent + tous ses sous-dossiers (ex: 12937, 12937-1, 12937-2)
    """
    parent_id = str(parent_id)
    df = df.copy()
    df["Dossier N"] = df["Dossier N"].astype(str)

    return df[df["Dossier N"].str.startswith(parent_id)]


def compute_consolidated_metrics(df: pd.DataFrame) -> dict:
    """
    Calcule les indicateurs financiers consolidés
    """
    if df.empty:
        return {
            "nb_dossiers": 0,
            "total_facture": 0,
            "total_encaisse": 0,
            "solde_du": 0,
            "escrow_total": 0,
            "escrow_a_reclamer": 0,
            "escrow_reclame": 0,
        }

    def fsum(col):
        return df[col].fillna(0).astype(float).sum()

    honoraires = fsum("Montant honoraires (US $)")
    frais = fsum("Autres frais (US $)")
    total_facture = honoraires + frais

    total_encaisse = (
        fsum("Acompte 1")
        + fsum("Acompte 2")
        + fsum("Acompte 3")
        + fsum("Acompte 4")
    )

    escrow_a_reclamer = df.loc[
        df["Escrow_a_reclamer"] == True, "Acompte 1"
    ].fillna(0).astype(float).sum()

    escrow_reclame = df.loc[
        df["Escrow_reclame"] == True, "Acompte 1"
    ].fillna(0).astype(float).sum()

    return {
        "nb_dossiers": len(df),
        "total_facture": total_facture,
        "total_encaisse": total_encaisse,
        "solde_du": total_facture - total_encaisse,
        "escrow_total": escrow_a_reclamer + escrow_reclame,
        "escrow_a_reclamer": escrow_a_reclamer,
        "escrow_reclame": escrow_reclame,
    }
