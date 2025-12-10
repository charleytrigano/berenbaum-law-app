import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

# ================================================
# 🎨 THEME LUXE – COULEURS PREMIUM
# ================================================
COLOR_GOLD = "#B8860B"
COLOR_GOLD_SOFT = "#8C6A18"
COLOR_BG = "#111111"
COLOR_TEXT = "#E6E6E6"
COLOR_GRID = "rgba(255,255,255,0.08)"

# ================================================
# 🔧 PALETTE DÉDIÉE POUR MULTI-ANNÉES
# ================================================
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
        font=dict(color=COLOR_TEXT, size=14),
        margin=dict(l=20, r=20, t=40, b=20),
        xaxis=dict(gridcolor=COLOR_GRID, zerolinecolor=COLOR_GRID),
        yaxis=dict(gridcolor=COLOR_GRID, zerolinecolor=COLOR_GRID),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            bordercolor=COLOR_GRID,
            borderwidth=1,
            font=dict(color=COLOR_TEXT),
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

    # Normalisation du nom de la colonne "Dossier envoye"
    if "Dossier_envoye" in df.columns:
        df.rename(columns={"Dossier_envoye": "Dossier envoye"}, inplace=True)

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
# 📊 2 — Comparaison multi-années (revenus)
# ===========================================================
def multi_year_line(df):
    if df.empty:
        return go.Figure()

    df = df.copy()
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df["Année"] = df["Date"].dt.year
    df["Mois"] = df["Date"].dt.month

    grouped = df.groupby(["Année", "Mois"])["Montant honoraires (US $)"].sum().reset_index()

    fig = go.Figure()

    for i, year in enumerate(sorted(grouped["Année"].unique())):
        sub = grouped[grouped["Année"] == year]
        fig.add_trace(go.Scatter(
            x=sub["Mois"],
            y=sub["Montant honoraires (US $)"],
            mode="lines+markers",
            name=str(year),
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

    fig.update_layout(
        title="Répartition par catégories",
        legend_title="Catégories"
    )

    return apply_theme(fig)

# ===========================================================
# 📊 4 — Heatmap mensuelle (Volume dossiers)
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
        aspect="auto",
        labels=dict(color="Nombre de dossiers")
    )

    fig.update_layout(title="Heatmap activité mensuelle")
    return apply_theme(fig)

# ===========================================================
# 📊 5 — Bar chart comparatif (catégories)
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
