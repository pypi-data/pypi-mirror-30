import torch
from torch.nn import Module, Embedding

from surefire.features import CategoricalFeature


def _families(features):
    return set([f.family for f in features if isinstance(f, CategoricalFeature)])

class Combine(Module):
    def __init__(self, features):
        super().__init__()
        self._features = features
        self._embeddings = Module()
        for f in _families(features):
            self._embeddings.add_module(f.name, Embedding(f.cardinality, f.dimension))
        
    def forward(self, x):
        buffer = []
        for f in self._features:
            if isinstance(f, CategoricalFeature):
                embedding = getattr(self._embeddings, f.family.name)
                buffer.append(embedding(x[f.name]))
            else:
                buffer.append(x[f.name].unsqueeze(1))
        return torch.cat(buffer, dim=1)

    @property
    def out_features(self):
        count = 0
        for f in self._features:
            count += f.family.dimension if isinstance(f, CategoricalFeature) else 1
        return count
