import pandas as pd

# ---------------------------------------------------------
# Nettoyage léger et sécurisé du JSON
# ---------------------------------------------------------
def clean_database(db):
    """
    Nettoie en sécurité la base JSON sans jamais casser la structure.
    Remplace NaN par "", force les types simples.
    """

    new_db = {}

    for key, value in db.items():

        # --- Si c’est une liste de dictionnaires ---
        if isinstance(value, list):

            cleaned_list = []

            for item in value:
                if isinstance(item, dict):
                    # Nettoyage léger des valeurs
                    clean_item = {}
                    for k, v in item.items():

                        # Dates
                        if isinstance(v, pd.Timestamp):
                            clean_item[k] = v.strftime("%Y-%m-%d")

                        # NaN, None → ""
                        elif v is None or (isinstance(v, float) and pd.isna(v)):
                            clean_item[k] = ""

                        # Nombre
                        elif isinstance(v, (int, float)):
                            clean_item[k] = v

                        # Texte
                        else:
                            clean_item[k] = str(v)

                    cleaned_list.append(clean_item)

            new_db[key] = cleaned_list

        else:
            # Tout autre format est simplement copié
            new_db[key] = value

    return new_db
