from typing import List
import torch
from transformers import RealmPreTrainedModel, RealmEmbedder, AutoTokenizer


class RealmEncoderIntermediate(RealmPreTrainedModel):
    """TODO: this class is written because RealmEmbedder.from_pretrained() results in a different model weight."""
    def __init__(self, config):
        super().__init__(config)
        self.embedder = RealmEmbedder(config)

    def __call__(self, **kwargs) -> List[float]:
        outputs = self.embedder(**kwargs, return_dict=True)[0]
        return outputs.numpy()[0]


class RealmEncoder:
    def __init__(self, model_name: str = "google/realm-orqa-nq-openqa"):
        self.model_name = model_name
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = RealmEncoderIntermediate.from_pretrained(model_name)

    def encode(self, text: str) -> List[float]:
        inputs = self.tokenizer([text], return_tensors="pt")
        with torch.no_grad():
            output = self.model(**inputs)
        return output.tolist()
