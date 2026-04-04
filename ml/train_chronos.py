import numpy as np
from pathlib import Path

from ml.data_fetcher import fetch_gold_prices
from ml.preprocessing import prepare_timeseries
from ml.chronos_model import ChronosModel
from ml.metrics import compute_all_metrics


MODEL_DIR = Path("artifacts/chronos_model")
MODEL_DIR.mkdir(parents=True, exist_ok=True)


def train_chronos(horizon=7):
    print("\n=== Entraînement Chronos ===")

    # 1. Données
    df = fetch_gold_prices()
    ts = prepare_timeseries(df)
    values = ts.values.astype("float32")

    # 2. Split train/test
    train_values = values[:-horizon]
    test_values = values[-horizon:]

    # 3. Charger modèle
    model = ChronosModel()
    model.load()

    # 4. Prédiction (Chronos n’a pas de fine‑tuning simple → inference only)
    preds = model.predict(train_values.tolist(), horizon)

    # 5. Évaluation
    metrics = compute_all_metrics(test_values, preds)

    print("\n=== Metrics Chronos ===")
    for k, v in metrics.items():
        print(f"{k}: {v:.4f}")

    # 6. Sauvegarde (tokenizer + modèle)
    model.model.save_pretrained(MODEL_DIR)
    model.tokenizer.save_pretrained(MODEL_DIR)

    print(f"\n[OK] Modèle Chronos sauvegardé dans {MODEL_DIR.resolve()}")
    return metrics


if __name__ == "__main__":
    train_chronos()
