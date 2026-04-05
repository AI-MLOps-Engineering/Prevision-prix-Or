import numpy as np
import torch
from transformers import TimeSeriesTransformerConfig, TimeSeriesTransformerForPrediction


def _age_features(length: int, device: torch.device) -> torch.Tensor:
    """Indices temporels normalisés (forme attendue pour past/future time features)."""
    t = torch.arange(length, dtype=torch.float32, device=device)
    return (t - t.mean()) / (t.std() + 1e-6)


class TimeSeriesTransformerModel:
    def __init__(self, context_length=64, prediction_length=7):
        self.context_length = context_length
        self.prediction_length = prediction_length
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        self.config = TimeSeriesTransformerConfig(
            prediction_length=prediction_length,
            context_length=context_length,
            num_time_features=1,
            encoder_attention_heads=4,
            decoder_attention_heads=4,
            d_model=64,
            encoder_layers=3,
            decoder_layers=3,
            num_parallel_samples=8,
        )

        self.model = TimeSeriesTransformerForPrediction(self.config).to(self.device)

    def predict(self, history):
        hist = np.asarray(history, dtype=np.float32).reshape(-1)
        past_len = self.model.model._past_length

        if len(hist) < past_len:
            first = float(hist[0]) if len(hist) else 0.0
            pad = np.full(past_len - len(hist), first, dtype=np.float32)
            hist = np.concatenate([pad, hist])

        past_values = torch.from_numpy(hist[-past_len:].copy()).unsqueeze(0).float().to(self.device)

        t_past = _age_features(past_len, self.device)
        past_time_features = t_past.view(1, past_len, 1)

        pred_len = self.prediction_length
        t_future = _age_features(past_len + pred_len, self.device)[past_len:]
        future_time_features = t_future.view(1, pred_len, 1)

        past_observed_mask = torch.ones((1, past_len), dtype=torch.bool, device=self.device)

        with torch.no_grad():
            out = self.model.generate(
                past_values=past_values,
                past_time_features=past_time_features,
                future_time_features=future_time_features,
                past_observed_mask=past_observed_mask,
            )

        samples = out.sequences[0]
        point = samples.mean(dim=0).cpu().numpy()
        return point.tolist()
