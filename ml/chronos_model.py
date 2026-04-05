import numpy as np
import torch
from chronos import ChronosPipeline


class ChronosModel:
    """
    Inférence via le pipeline officiel Amazon (tokenisation + generate + décodage).
    Un usage « T5 + texte » ne produit pas une sortie exploitable (décodage vide).
    """

    def __init__(self, model_name="amazon/chronos-t5-base"):
        self.model_name = model_name
        self.pipeline = None
        self.device = "cpu"

    def load(self):
        device_map = "cuda" if torch.cuda.is_available() else "cpu"
        self.device = device_map
        self.pipeline = ChronosPipeline.from_pretrained(
            self.model_name,
            device_map=device_map,
            trust_remote_code=True,
        )

    def predict(self, history, horizon):
        if self.pipeline is None:
            self.load()

        ctx = torch.tensor(
            np.asarray(history, dtype=np.float32).flatten(),
            dtype=torch.float32,
        )

        # Plusieurs trajectoires échantillonnées ; médiane = prévision ponctuelle stable.
        samples = self.pipeline.predict(
            inputs=ctx,
            prediction_length=horizon,
            num_samples=20,
            limit_prediction_length=False,
        )
        # samples: (batch, num_samples, prediction_length)
        point = samples[0].median(dim=0).values
        return point.numpy().astype(np.float64).tolist()
