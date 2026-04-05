from pathlib import Path

from ml.data_fetcher import fetch_gold_prices
from ml.preprocessing import prepare_timeseries
from ml.tst_model import TimeSeriesTransformerModel
from ml.metrics import compute_all_metrics


MODEL_DIR = Path("artifacts/tst_model")
MODEL_DIR.mkdir(parents=True, exist_ok=True)


def train_tst(context_length=64, prediction_length=7, epochs=100):
    print("\n=== Entraînement TimeSeriesTransformer ===")

    # 1. Données
    df = fetch_gold_prices()
    ts = prepare_timeseries(df)
    values = ts.values.astype("float32")

    # 2. Split train/test
    train_values = values[:-prediction_length]
    test_values = values[-prediction_length:]

    # 3. Charger modèle
    model = TimeSeriesTransformerModel(
        context_length=context_length,
        prediction_length=prediction_length,
    )

    # 4. Entraînement
    model.fit_on_series(train_values, epochs=epochs)

    # 5. Prédiction
    preds = model.predict(train_values.tolist())

    # 6. Évaluation
    metrics = compute_all_metrics(test_values, preds)

    print("\n=== Metrics TST ===")
    for k, v in metrics.items():
        print(f"{k}: {v:.4f}")

    # 7. Sauvegarde
    model.save(str(MODEL_DIR))

    print(f"\n[OK] Modèle TST sauvegardé dans {MODEL_DIR.resolve()}")
    return metrics


if __name__ == "__main__":
    train_tst()
