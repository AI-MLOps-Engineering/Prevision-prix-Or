import torch
import numpy as np
from transformers import AutoModelForCausalLM, AutoTokenizer


class ChronosModel:
    def __init__(self, model_name="amazon/chronos-t5-base"):
        self.model_name = model_name
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = None
        self.tokenizer = None

    def load(self):
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            torch_dtype=torch.float32
        ).to(self.device)

    def predict(self, history, horizon):
        arr = np.array(history, dtype=np.float32)
        mean, std = arr.mean(), arr.std() or 1.0
        normalized = (arr - mean) / std

        tokens = self.tokenizer.encode(normalized.tolist(), return_tensors="pt").to(self.device)

        with torch.no_grad():
            output = self.model.generate(tokens, max_new_tokens=horizon, do_sample=False)

        decoded = self.tokenizer.decode(output[0], skip_special_tokens=True)
        preds_norm = eval(decoded)
        preds = [(p * std) + mean for p in preds_norm]
        return preds
