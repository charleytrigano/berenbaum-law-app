import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

# ================================================
# 🎨 THEME LUXE – COULEURS PREMIUM
# ================================================
COLOR_GOLD = "#B8860B"
COLOR_TEXT = "#E6E6E6"
COLOR_GRID = "rgba(255,255,255,0.08)"

PALETTE = [
    "#B8860B",  # Gold deep
    "#8C6A18",  # Gold soft
    "#D2B48C",  # Tan gold
    "#C0903D",  # Bronze
    "#A67C00",  # Golden brown
]

# ================================================
# 🔧 BASE LAYOUT GRAPHES (premium)
# ================================================
def apply_theme(fig):
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=COLOR_TEXT),
        margin=dict(l=20, r=20, t=40, b=20),
        xaxis=dict(gridcolor=COLOR_GRID),
        yaxis=dict(gridcolor=COLOR_GRID),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            bordercolor=COLOR_GRID,
            borderwidth=1
        )
    )
    return fig


# ===========================================================
# 📊 1 — Histogramme mensuel premium
# ===========================================================
def monthly_hist(df, date_col="Date", amount_col="Montant honoraires (US $)"):
    if df.empty:
        return go.Figure()

    df = df.copy()
    df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
    df["Mois"] = df[date_col].dt.to_period("M").astype(str)

    grouped = df.groupby("Mois")[amount_col].sum().reset_index()

    fig = px.bar(
        grouped,
        x="Mois",
        y=amount_col,
        title="Revenus mensuels",
        color_discrete_sequence=[COLOR_GOLD]
    )

    return apply_theme(fig)


# ===========================================================
# 📊 2 — Comparaison multi-années (version patchée)
# ===========================================================
def multi_year_line(df_grouped):
    """
    df_grouped doit contenir : Année, Mois, Montant honoraires (US $)
    """
    if df_grouped.empty:
        return go.Figure()

    df = df_grouped.copy()

    df["Année"] = pd.to_numeric(df["Année"], errors="coerce")
    df["Mois"] = pd.to_numeric(df["Mois"], errors="coerce")

    fig = go.Figure()

    for i, year in enumerate(sorted(df["Année"].dropna().unique())):
        sub = df[df["Année"] == year]
        fig.add_trace(go.Scatter(
            x=sub["Mois"],
            y=sub["Montant honoraires (US $)"],
            mode="lines+markers",
            name=str(int(year)),
            line=dict(color=PALETTE[i % len(PALETTE)], width=3)
        ))

    fig.update_layout(title="Comparaison multi-années")
    return apply_theme(fig)


# ===========================================================
# 📊 3 — Donut catégories
# ===========================================================
def category_donut(df):
    df = df.copy()
    df["Categories"] = df["Categories"].fillna("Non défini")

    summary = df["Categories"].value_counts().reset_index()
    summary.columns = ["Categories", "count"]

    if summary.empty:
        return px.pie(values=[1], names=["Aucune donnée"])

    fig = px.pie(
        summary,
        values="count",
        names="Categories",
        hole=0.5,
        color_discrete_sequence=px.colors.sequential.Oranges
    )

    fig.update_layout(title="Répartition par catégories")
    return apply_theme(fig)


# ===========================================================
# 📊 4 — Heatmap mensuelle
# ===========================================================
def heatmap_month(df):
    if df.empty:
        return go.Figure()

    df = df.copy()
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df["Année"] = df["Date"].dt.year
    df["Mois"] = df["Date"].dt.month

    pivot = df.pivot_table(
        index="Année",
        columns="Mois",
        values="Dossier N",
        aggfunc="count",
        fill_value=0
    )

    fig = px.imshow(
        pivot,
        color_continuous_scale=["#2b2b2b", COLOR_GOLD],
        labels=dict(color="Nb dossiers")
    )

    fig.update_layout(title="Heatmap activité mensuelle")
    return apply_theme(fig)


# ===========================================================
# 📊 5 — Bar chart revenus / catégories
# ===========================================================
def category_bars(df):
    if df.empty:
        return go.Figure()

    grouped = df.groupby("Categories")["Montant honoraires (US $)"].sum().reset_index()

    fig = px.bar(
        grouped,
        x="Categories",
        y="Montant honoraires (US $)",
        title="Revenus par catégories",
        color="Categories",
        color_discrete_sequence=PALETTE
    )
    return apply_theme(fig)
