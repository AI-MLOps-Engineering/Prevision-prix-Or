from ml.train_chronos import train_chronos
from ml.train_tst import train_tst


def train_all():
    print("\n=== TRAINING ALL MODELS ===")
    metrics_chronos = train_chronos(horizon=7)
    metrics_tst = train_tst(context_length=64, prediction_length=7, epochs=50)

    print("\n=== Résumé global ===")
    print("Chronos :", metrics_chronos)
    print("TST     :", metrics_tst)


if __name__ == "__main__":
    train_all()
