import pandas as pd

def add_hierarchy_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    def split_dossier(val):
        try:
            s = str(val)
            if "-" in s:
                p, i = s.split("-", 1)
                return int(p), int(i)
            return int(s), 0
        except:
            return None, None

    parents = []
    indexes = []

    for v in df["Dossier N"]:
        p, i = split_dossier(v)
        parents.append(p)
        indexes.append(i)

    df["Dossier Parent"] = parents
    df["Dossier Index"] = indexes

    return df
