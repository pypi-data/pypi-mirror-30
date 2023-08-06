from torch.nn import Module, Sequential

from surefire.modules.combine import Combine


class Feedforward(Module):
    def __init__(self, features, out_features):
        super().__init__()
        self._combine = Combine(features)
        self._sequential = Sequential(
            Linear(self._combine.out_features, out_features)
        )
        
    def forward(self, x):
        x = self._combine(x)
        return self._sequential(x)
