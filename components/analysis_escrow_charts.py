import pandas as pd
import plotly.express as px
from datetime import datetime

# -----------------------------------------------------
# UTILS
# -----------------------------------------------------
def to_float(v):
    try:
        return float(v or 0)
    except Exception:
        return 0.0

def total_acomptes(row):
    return sum(to_float(row.get(f"Acompte {i}", 0)) for i in range(1, 5))


# -----------------------------------------------------
# 1️⃣ RÉPARTITION PAR ÉTAT
# -----------------------------------------------------
def escrow_state_donut(df):
    data = {
        "Escrow actif": 0.0,
        "Escrow à réclamer": 0.0,
        "Escrow réclamé": 0.0,
    }

    for _, r in df.iterrows():
        amount = total_acomptes(r)

        if r.get("Escrow_reclame"):
            data["Escrow réclamé"] += amount
        elif r.get("Escrow_a_reclamer"):
            data["Escrow à réclamer"] += amount
        elif r.get("Escrow"):
            data["Escrow actif"] += amount

    plot_df = pd.DataFrame({
        "État": list(data.keys()),
        "Montant": list(data.values())
    })

    fig = px.pie(
        plot_df,
        values="Montant",
        names="État",
        title="Répartition des montants en Escrow",
        hole=0.45
    )
    fig.update_traces(textinfo="percent+label")

    return fig


# -----------------------------------------------------
# 2️⃣ ANCIENNETÉ DES ESCROWS
# -----------------------------------------------------
def escrow_aging_bar(df):
    today = datetime.today()
    buckets = {
        "0–30 jours": 0,
        "31–60 jours": 0,
        "60+ jours": 0,
    }

    for _, r in df.iterrows():
        if not (r.get("Escrow") or r.get("Escrow_a_reclamer")):
            continue

        date_str = r.get("Date envoi") or r.get("Date")
        try:
            d = pd.to_datetime(date_str)
            days = (today - d).days
        except Exception:
            continue

        if days <= 30:
            buckets["0–30 jours"] += 1
        elif days <= 60:
            buckets["31–60 jours"] += 1
        else:
            buckets["60+ jours"] += 1

    plot_df = pd.DataFrame({
        "Ancienneté": list(buckets.keys()),
        "Dossiers": list(buckets.values())
    })

    fig = px.bar(
        plot_df,
        x="Ancienneté",
        y="Dossiers",
        title="Ancienneté des dossiers en Escrow"
    )

    return fig


# -----------------------------------------------------
# 3️⃣ ÉVOLUTION TEMPORELLE
# -----------------------------------------------------
def escrow_monthly_line(df):
    rows = []

    for _, r in df.iterrows():
        if not (r.get("Escrow") or r.get("Escrow_a_reclamer") or r.get("Escrow_reclame")):
            continue

        amount = total_acomptes(r)
        date_str = r.get("Date") or r.get("Date envoi")

        try:
            d = pd.to_datetime(date_str)
            month = d.to_period("M").astype(str)
        except Exception:
            continue

        rows.append({
            "Mois": month,
            "Montant": amount
        })

    if not rows:
        return None

    plot_df = pd.DataFrame(rows).groupby("Mois", as_index=False).sum()

    fig = px.line(
        plot_df,
        x="Mois",
        y="Montant",
        markers=True,
        title="Évolution mensuelle des montants en Escrow"
    )

    return fig