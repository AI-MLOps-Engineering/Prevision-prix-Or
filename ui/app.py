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

    # Sans fenêtre sur la fin de série, 5 ans d’historique écrasent visuellement
    # l’horizon (ex. 7 jours) : les prévisions sont alors invisibles sur l’axe des dates.
    tail_days = max(horizon * 6, 120)
    hist_plot = ts.iloc[-tail_days:]

    y_chronos = np.asarray(preds_chronos, dtype=float).ravel()
    y_tst = np.asarray(preds_tst, dtype=float).ravel()
    last = ts.index[-1]
    future_index = pd.date_range(start=last, periods=horizon + 1, freq="D")[1:]

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=hist_plot.index,
        y=np.asarray(hist_plot.values, dtype=float).ravel(),
        mode="lines",
        name="Historique",
        line=dict(color="#bbbbbb", width=1.5),
    ))

    fig.add_trace(go.Scatter(
        x=future_index,
        y=y_chronos,
        mode="lines+markers",
        name="Chronos",
        line=dict(color="gold", width=2),
        marker=dict(size=6),
    ))

    fig.add_trace(go.Scatter(
        x=future_index,
        y=y_tst,
        mode="lines+markers",
        name="TimeSeriesTransformer",
        line=dict(color="cyan", width=2),
        marker=dict(size=6),
    ))

    x_min = min(hist_plot.index.min(), future_index.min())
    x_max = max(hist_plot.index.max(), future_index.max())

    fig.update_layout(
        template="plotly_dark",
        height=500,
        xaxis_title="Date",
        yaxis_title="Prix de l'or (USD)",
        xaxis=dict(range=[x_min, x_max]),
        hovermode="x unified",
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
