# components/analysis_charts.py
import pandas as pd
import plotly.express as px


# -----------------------------
# Helpers
# -----------------------------
def _ensure_datetime(df: pd.DataFrame, col: str = "Date") -> pd.DataFrame:
    df = df.copy()
    if col in df.columns:
        df[col] = pd.to_datetime(df[col], errors="coerce")
    return df


def _coerce_float(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series, errors="coerce").fillna(0.0)


def _infer_period_col(df: pd.DataFrame) -> str | None:
    """
    Détecte une colonne déjà agrégée type 'Periode', 'Mois', etc.
    """
    for c in ["Periode", "Période", "Mois", "Trimestre", "Semestre", "Année", "Annee", "Year", "Month"]:
        if c in df.columns:
            return c
    return None


def _build_period(df: pd.DataFrame, period_type: str) -> pd.DataFrame:
    """
    Ajoute une colonne 'Periode' à partir de 'Date'
    """
    df = _ensure_datetime(df, "Date")
    df = df[df["Date"].notna()].copy()

    if df.empty:
        df["Periode"] = pd.Series([], dtype=str)
        return df

    if period_type == "Mois":
        df["Periode"] = df["Date"].dt.to_period("M").astype(str)
    elif period_type == "Trimestre":
        df["Periode"] = df["Date"].dt.to_period("Q").astype(str)
    elif period_type == "Semestre":
        # Semestre : S1/S2
        half = df["Date"].dt.month.apply(lambda m: "S1" if m <= 6 else "S2")
        df["Periode"] = df["Date"].dt.year.astype(str) + "-" + half
    elif period_type == "Année":
        df["Periode"] = df["Date"].dt.year.astype(str)
    else:
        # "Date à date" => on garde la date jour
        df["Periode"] = df["Date"].dt.date.astype(str)

    return df


def _empty_fig(title: str):
    fig = px.scatter(title=title)
    fig.update_layout(
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        annotations=[
            dict(
                text="Aucune donnée à afficher avec les filtres actuels.",
                x=0.5,
                y=0.5,
                xref="paper",
                yref="paper",
                showarrow=False,
                font=dict(size=14),
            )
        ],
    )
    return fig


# -----------------------------
# Charts
# -----------------------------
def monthly_hist(df: pd.DataFrame, period_type: str = "Mois"):
    """
    Histogramme de volume de dossiers par période.
    Fonctionne si df contient 'Date' OU s'il contient déjà une colonne de période (Periode/Mois/etc).
    """
    if df is None or df.empty:
        return _empty_fig("📅 Histogramme — aucune donnée")

    df = df.copy()

    # Si Date existe => on reconstruit Periode proprement
    if "Date" in df.columns:
        df = _build_period(df, period_type)
        if df.empty:
            return _empty_fig("📅 Histogramme — aucune donnée")
        g = df.groupby("Periode").size().reset_index(name="Dossiers")
        xcol = "Periode"
    else:
        # Déjà agrégé
        xcol = _infer_period_col(df)
        if not xcol:
            return _empty_fig("📅 Histogramme — colonnes période introuvables")
        if "Dossiers" not in df.columns:
            # Si df contient déjà un count sous un autre nom
            if "Count" in df.columns:
                df["Dossiers"] = df["Count"]
            else:
                # dernier recours
                df["Dossiers"] = 0
        g = df[[xcol, "Dossiers"]].copy()
        g = g.dropna(subset=[xcol])

    fig = px.bar(g.sort_values(xcol), x=xcol, y="Dossiers", title="📅 Dossiers par période")
    fig.update_layout(xaxis_title="Période", yaxis_title="Nombre de dossiers")
    return fig


def multi_year_line(df: pd.DataFrame, years: list[int] | None = None):
    """
    Courbes multi-années : compare l’activité mois par mois (Jan..Déc) pour plusieurs années.
    Requiert 'Date'. Si 'Date' absent => renvoie une figure explicite (au lieu de vide/erreur).
    """
    if df is None or df.empty:
        return _empty_fig("📈 Courbes multi-années — aucune donnée")

    if "Date" not in df.columns:
        return _empty_fig("📈 Courbes multi-années — colonne 'Date' introuvable")

    df = _ensure_datetime(df, "Date")
    df = df[df["Date"].notna()].copy()
    if df.empty:
        return _empty_fig("📈 Courbes multi-années — aucune date valide")

    df["Année"] = df["Date"].dt.year
    df["MoisNum"] = df["Date"].dt.month
    df["Mois"] = df["Date"].dt.strftime("%b")  # Jan, Feb...

    if years:
        df = df[df["Année"].isin(years)].copy()

    if df.empty:
        return _empty_fig("📈 Courbes multi-années — aucune donnée pour ces années")

    g = df.groupby(["Année", "MoisNum"]).size().reset_index(name="Dossiers")
    # Mois label stable
    g["Mois"] = pd.to_datetime(g["MoisNum"], format="%m").dt.strftime("%b")
    g = g.sort_values(["Année", "MoisNum"])

    fig = px.line(
        g,
        x="MoisNum",
        y="Dossiers",
        color="Année",
        markers=True,
        title="📈 Comparaison multi-années (volume mensuel)",
    )
    fig.update_layout(
        xaxis_title="Mois",
        yaxis_title="Nombre de dossiers",
        xaxis=dict(
            tickmode="array",
            tickvals=list(range(1, 13)),
            ticktext=[pd.to_datetime(m, format="%m").strftime("%b") for m in range(1, 13)],
        ),
    )
    return fig


def category_donut(df: pd.DataFrame):
    if df is None or df.empty:
        return _empty_fig("🎯 Répartition catégories — aucune donnée")

    col = "Categories" if "Categories" in df.columns else None
    if not col:
        return _empty_fig("🎯 Répartition catégories — colonne introuvable")

    g = df[col].fillna("").replace("", "Non renseigné").value_counts().reset_index()
    g.columns = ["Catégorie", "Dossiers"]

    fig = px.pie(g, names="Catégorie", values="Dossiers", hole=0.55, title="🎯 Répartition par catégorie")
    return fig


def heatmap_month(df: pd.DataFrame):
    """
    Heatmap activité (année x mois) - nécessite Date
    """
    if df is None or df.empty:
        return _empty_fig("🔥 Heatmap — aucune donnée")

    if "Date" not in df.columns:
        return _empty_fig("🔥 Heatmap — colonne 'Date' introuvable")

    df = _ensure_datetime(df, "Date")
    df = df[df["Date"].notna()].copy()
    if df.empty:
        return _empty_fig("🔥 Heatmap — aucune date valide")

    df["Année"] = df["Date"].dt.year
    df["MoisNum"] = df["Date"].dt.month
    df["Mois"] = df["Date"].dt.strftime("%b")

    g = df.groupby(["Année", "MoisNum"]).size().reset_index(name="Dossiers")
    pivot = g.pivot(index="Année", columns="MoisNum", values="Dossiers").fillna(0)

    fig = px.imshow(
        pivot,
        aspect="auto",
        title="🔥 Heatmap d’activité (année × mois)",
    )
    fig.update_layout(
        xaxis=dict(
            tickmode="array",
            tickvals=list(range(0, 12)),
            ticktext=[pd.to_datetime(m, format="%m").strftime("%b") for m in range(1, 13)],
        ),
        yaxis_title="Année",
        xaxis_title="Mois",
    )
    return fig


def category_bars(df: pd.DataFrame):
    if df is None or df.empty:
        return _empty_fig("📊 Revenus par catégories — aucune donnée")

    if "Categories" not in df.columns:
        return _empty_fig("📊 Revenus par catégories — colonne 'Categories' introuvable")

    honor_col = "Montant honoraires (US $)" if "Montant honoraires (US $)" in df.columns else None
    frais_col = "Autres frais (US $)" if "Autres frais (US $)" in df.columns else None

    if not honor_col and not frais_col:
        return _empty_fig("📊 Revenus par catégories — colonnes montants introuvables")

    d = df.copy()
    d["Catégorie"] = d["Categories"].fillna("").replace("", "Non renseigné")

    d["Honoraires"] = _coerce_float(d[honor_col]) if honor_col else 0.0
    d["Frais"] = _coerce_float(d[frais_col]) if frais_col else 0.0
    d["Total"] = d["Honoraires"] + d["Frais"]

    g = d.groupby("Catégorie")["Total"].sum().reset_index().sort_values("Total", ascending=False)

    fig = px.bar(g, x="Catégorie", y="Total", title="📊 Revenus (honoraires + frais) par catégorie")
    fig.update_layout(xaxis_title="Catégorie", yaxis_title="Montant (US $)")
    return fig


# Bonus (optionnel, non bloquant) : top visas
def top_visa(df: pd.DataFrame, top_n: int = 10):
    if df is None or df.empty:
        return _empty_fig("🛂 Top Visas — aucune donnée")

    if "Visa" not in df.columns:
        return _empty_fig("🛂 Top Visas — colonne 'Visa' introuvable")

    g = df["Visa"].fillna("").replace("", "Non renseigné").value_counts().head(top_n).reset_index()
    g.columns = ["Visa", "Dossiers"]
    fig = px.bar(g, x="Visa", y="Dossiers", title=f"🛂 Top {top_n} Visas (volume)")
    fig.update_layout(xaxis_title="Visa", yaxis_title="Nombre de dossiers")
    return fig
