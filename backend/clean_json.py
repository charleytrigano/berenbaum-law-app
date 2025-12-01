import pandas as pd

COLUMN_RENAMES = {
    "Cat\u00e9gories": "Catégories",
    "Sous-cat\u00e9gories": "Sous-catégories",
    "Categorie": "Catégories",
    "Sous categorie": "Sous-catégories",
    "Visa ": "Visa",
    " visa": "Visa",
}

def clean_record(rec: dict):
    """Corrige les noms de colonnes mal encodés dans un dossier."""
    new = {}

    for k, v in rec.items():
        # Renommage intelligent
        key = COLUMN_RENAMES.get(k, k)

        # Remplacement NaN → ""
        if v is None or (isinstance(v, float) and pd.isna(v)):
            v = ""

        new[key] = v

    # Colonnes obligatoires
    for col in ["Catégories", "Sous-catégories", "Visa"]:
        if col not in new:
            new[col] = ""

    return new


def clean_database(db: dict):
    """Applique la correction à toute la base JSON."""
    for section in ["clients", "visa", "escrow", "compta"]:
        if section in db:
            db[section] = [clean_record(r) for r in db[section]]
    return db
