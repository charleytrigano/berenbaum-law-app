import pandas as pd

# Correction des noms de colonnes venant d’Excel ou mal encodés
COLUMN_RENAMES = {
    "Cat\u00e9gories": "Catégories",
    "Sous-cat\u00e9gories": "Sous-catégories",
    "Visa ": "Visa",
    " visa": "Visa",
    "Categorie": "Catégories",
    "Sous categorie": "Sous-catégories",
}

def clean_record(rec: dict):
    """Corrige les colonnes mal encodées dans un dossier."""
    new = {}

    for k, v in rec.items():
        key = COLUMN_RENAMES.get(k, k)
        new[key] = v

    # Normalisation vide
    for col in ["Catégories", "Sous-catégories", "Visa"]:
        if col not in new:
            new[col] = ""

        if pd.isna(new[col]):
            new[col] = ""

    return new


def clean_database(db: dict):
    """Corrige toute la base JSON."""
    for section in ["clients", "visa", "escrow", "compta"]:
        if section in db:
            db[section] = [clean_record(r) for r in db[section]]
    return db
