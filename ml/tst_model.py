import torch
import numpy as np
from transformers import TimeSeriesTransformerConfig, TimeSeriesTransformerForPrediction


class TimeSeriesTransformerModel:
    def __init__(self, context_length=64, prediction_length=7):
        self.context_length = context_length
        self.prediction_length = prediction_length
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

        self.config = TimeSeriesTransformerConfig(
            prediction_length=prediction_length,
            context_length=context_length,
            num_time_features=1,
            num_static_categorical_features=0,
            num_static_real_features=0,
            d_model=64,
            encoder_layers=3,
            decoder_layers=3,
            n_heads=4,
        )

        self.model = TimeSeriesTransformerForPrediction(self.config).to(self.device)

    def _build_batch(self, series):
        values = torch.tensor(series, dtype=torch.float32).unsqueeze(0)
        past = values[:, :self.context_length]
        future = values[:, self.context_length:self.context_length + self.prediction_length]

        total_len = self.context_length + self.prediction_length
        time_idx = torch.arange(total_len, dtype=torch.float32).unsqueeze(0)
        time_idx = (time_idx - time_idx.mean()) / (time_idx.std() + 1e-6)

        past_tf = time_idx[:, :self.context_length].unsqueeze(-1)
        future_tf = time_idx[:, self.context_length:total_len].unsqueeze(-1)

        return {
            "past_values": past.to(self.device),
            "past_time_features": past_tf.to(self.device),
            "future_values": future.to(self.device),
            "future_time_features": future_tf.to(self.device),
        }

    def predict(self, history):
        ctx = np.asarray(history[-self.context_length :], dtype=np.float32).reshape(-1)
        future_placeholder = np.zeros(self.prediction_length, dtype=np.float32)
        full = np.concatenate([ctx, future_placeholder])

        batch = self._build_batch(full)

        with torch.no_grad():
            outputs = self.model(**batch)
            distr = self.model.output_distribution(outputs)
            preds = distr.mean[0].cpu().numpy().tolist()

        return preds
