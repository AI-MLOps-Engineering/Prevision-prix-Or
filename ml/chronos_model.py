import ast
import re

import numpy as np
import torch
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer


def _parse_chronos_output(decoded: str):
    """Interprète la sortie texte du modèle (liste ou nombres séparés)."""
    text = decoded.strip()
    try:
        parsed = ast.literal_eval(text)
        if isinstance(parsed, (list, tuple)):
            return [float(x) for x in parsed]
    except (ValueError, SyntaxError, TypeError):
        pass
    m = re.search(r"\[[^\]]+\]", text)
    if m:
        try:
            parsed = ast.literal_eval(m.group(0))
            if isinstance(parsed, (list, tuple)):
                return [float(x) for x in parsed]
        except (ValueError, SyntaxError, TypeError):
            pass
    nums = []
    for part in re.split(r"[,\s;]+", text):
        part = part.strip().strip("[]()")
        if not part:
            continue
        try:
            nums.append(float(part))
        except ValueError:
            continue
    if nums:
        return nums
    raise ValueError(f"Sortie Chronos non interprétable: {text[:200]!r}")


class ChronosModel:
    def __init__(self, model_name="amazon/chronos-t5-base"):
        self.model_name = model_name
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = None
        self.tokenizer = None

    def load(self):
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(
            self.model_name,
            trust_remote_code=True,
        ).to(self.device)
        self.model.eval()

    def predict(self, history, horizon):
        arr = np.array(history, dtype=np.float32).flatten()
        mean, std = float(arr.mean()), float(arr.std() or 1.0)
        normalized = (arr - mean) / std

        # Les tokenizers HF attendent du texte, pas une liste de floats (Transformers ≥ récents).
        text = " ".join(f"{float(x):.6f}" for x in normalized.tolist())
        enc = self.tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            max_length=min(getattr(self.tokenizer, "model_max_length", 512) or 512, 2048),
        )
        input_ids = enc["input_ids"].to(self.device)
        attn = enc.get("attention_mask")
        if attn is not None:
            attn = attn.to(self.device)

        gen_kw = {"max_new_tokens": max(horizon, 16), "do_sample": False}
        if attn is not None:
            gen_kw["attention_mask"] = attn

        with torch.no_grad():
            output = self.model.generate(input_ids, **gen_kw)

        decoded = self.tokenizer.decode(output[0], skip_special_tokens=True)
        preds_norm = _parse_chronos_output(decoded)
        if len(preds_norm) < horizon:
            raise ValueError(
                f"Chronos a renvoyé {len(preds_norm)} points, horizon={horizon}"
            )
        preds_norm = preds_norm[:horizon]
        return [float(p) * std + mean for p in preds_norm]
