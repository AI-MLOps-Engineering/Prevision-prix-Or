import time
from ml.chronos_model import ChronosModel
from ml.tst_model import TimeSeriesTransformerModel
from ml.metrics import compute_all_metrics


_chronos = None
_tst = None


def load_models(prediction_length=7):
    global _chronos, _tst

    if _chronos is None:
        _chronos = ChronosModel()
        _chronos.load()

    if _tst is None:
        _tst = TimeSeriesTransformerModel(prediction_length=prediction_length)

    return _chronos, _tst


def predict_all(history, horizon):
    chronos, tst = load_models(prediction_length=horizon)

    # Mesure du temps
    t0 = time.time()
    preds_chronos = chronos.predict(history, horizon)
    t_chronos = time.time() - t0

    t1 = time.time()
    preds_tst = tst.predict(history)
    t_tst = time.time() - t1

    # Calcul des métriques (si on a les vraies valeurs)
    true_values = history[-horizon:] if len(history) >= horizon else None

    metrics_chronos = compute_all_metrics(true_values, preds_chronos) if true_values else None
    metrics_tst = compute_all_metrics(true_values, preds_tst) if true_values else None

    return {
        "models": [
            {
                "name": "Chronos",
                "predictions": preds_chronos,
                "metrics": metrics_chronos,
                "inference_time": t_chronos,
            },
            {
                "name": "TimeSeriesTransformer",
                "predictions": preds_tst,
                "metrics": metrics_tst,
                "inference_time": t_tst,
            }
        ],
        "metadata": {
            "horizon": horizon,
            "history_length": len(history),
            "models_loaded": ["Chronos", "TimeSeriesTransformer"],
            "device": chronos.device,
        }
    }
