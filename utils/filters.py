import pandas as pd

def filter_by_category(df, category):
    if category == "Toutes":
        return df
    return df[df["Categories"] == category]


def build_period_options(years):
    return sorted(list(set(years)))


def filter_by_period(df, period_type):
    df = df.copy()
    df["année"] = df["Date"].dt.year
    df["mois"] = df["Date"].dt.month

    if period_type == "Mois":
        mois = st.selectbox("Choisir un mois", list(range(1, 13)))
        return df[df["mois"] == mois]

    if period_type == "Trimestre":
        trimestre = st.selectbox("Choisir un trimestre", [1, 2, 3, 4])
        return df[df["mois"].between((trimestre - 1) * 3 + 1, trimestre * 3)]

    if period_type == "Semestre":
        semestre = st.selectbox("Choisir un semestre", [1, 2])
        return df[df["mois"].between(1, 6)] if semestre == 1 else df[df["mois"].between(7, 12)]

    if period_type == "Date à date":
        start = st.date_input("De")
        end = st.date_input("À")
        return df[(df["Date"] >= pd.to_datetime(start)) & (df["Date"] <= pd.to_datetime(end))]

    if period_type == "Comparaison multi-années":
        years = sorted(df["année"].dropna().unique())
        selected = st.multiselect("Sélectionner jusqu'à 5 années", years, max_selections=5)
        return df[df["année"].isin(selected)]

    return df
