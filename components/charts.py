import plotly.express as px

def chart_categories(df):
    if "Catégorie" in df.columns:
        return px.histogram(df, x="Catégorie", title="Répartition par catégorie")
    return None

def chart_compta(df):
    if "Date" in df.columns and "Montant" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"])
        return px.line(df, x="Date", y="Montant", title="Évolution financière")
    return None

