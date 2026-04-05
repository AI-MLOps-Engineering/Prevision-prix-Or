import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

from ml.data_fetcher import fetch_gold_prices
from ml.preprocessing import prepare_timeseries


# -------------------------------------------------------------------
# CONFIGURATION
# -------------------------------------------------------------------
st.set_page_config(
    page_title="Comparaison des modèles - Prix de l'Or",
    layout="wide"
)

st.title("📈 Prévision du prix de l'or — Comparaison Chronos vs TimeSeriesTransformer")


# -------------------------------------------------------------------
# CHARGEMENT DES DONNÉES
# -------------------------------------------------------------------
st.subheader("📊 Données historiques")

df = fetch_gold_prices()
ts = prepare_timeseries(df)

st.line_chart(ts)


# -------------------------------------------------------------------
# PARAMÈTRES UTILISATEUR
# -------------------------------------------------------------------
st.sidebar.header("⚙️ Paramètres")

horizon = st.sidebar.slider(
    "Horizon de prévision (jours)",
    min_value=1,
    max_value=30,
    value=7
)

if st.sidebar.button("Lancer la prévision"):
    from ml.inference import predict_all
    from ml.metrics import compute_all_metrics

    st.subheader("🔮 Résultats des modèles")

    history = ts.values.tolist()

    # -------------------------------------------------------------------
    # PRÉDICTIONS MULTI-MODÈLES
    # -------------------------------------------------------------------
    results = predict_all(history, horizon)
    by_name = {m["name"]: m["predictions"] for m in results["models"]}
    preds_chronos = by_name["Chronos"]
    preds_tst = by_name["TimeSeriesTransformer"]

    # -------------------------------------------------------------------
    # COURBES COMPARATIVES
    # -------------------------------------------------------------------
    st.subheader("📈 Courbes de prévision")

    fig = go.Figure()

    # Historique
    fig.add_trace(go.Scatter(
        x=ts.index,
        y=ts.values,
        mode="lines",
        name="Historique",
        line=dict(color="white")
    ))

    # Chronos
    future_index = pd.date_range(start=ts.index[-1], periods=horizon+1, freq="D")[1:]
    fig.add_trace(go.Scatter(
        x=future_index,
        y=preds_chronos,
        mode="lines+markers",
        name="Chronos",
        line=dict(color="gold")
    ))

    # TST
    fig.add_trace(go.Scatter(
        x=future_index,
        y=preds_tst,
        mode="lines+markers",
        name="TimeSeriesTransformer",
        line=dict(color="cyan")
    ))

    fig.update_layout(
        template="plotly_dark",
        height=500,
        xaxis_title="Date",
        yaxis_title="Prix de l'or (USD)"
    )

    st.plotly_chart(fig, width="stretch")

    # -------------------------------------------------------------------
    # MÉTRIQUES
    # -------------------------------------------------------------------
    st.subheader("📊 Comparaison des métriques")

    # On compare les prédictions sur les mêmes valeurs réelles
    true_values = ts.values[-horizon:]

    metrics_chronos = compute_all_metrics(true_values, preds_chronos)
    metrics_tst = compute_all_metrics(true_values, preds_tst)

    metrics_df = pd.DataFrame({
        "Chronos": metrics_chronos,
        "TimeSeriesTransformer": metrics_tst
    })

    st.dataframe(metrics_df.style.format("{:.4f}"))

    # -------------------------------------------------------------------
    # COMMENTAIRES
    # -------------------------------------------------------------------
    st.subheader("📝 Analyse automatique")

    best_model = (
        "Chronos" if metrics_chronos["RMSE"] < metrics_tst["RMSE"] else "TimeSeriesTransformer"
    )

    st.success(f"Le meilleur modèle sur cet horizon ({horizon} jours) est : **{best_model}**")
