from collections import namedtuple


EmbeddingFamily = namedtuple('EmbeddingFamily', ['name', 'cardinality', 'dimension'])


BinaryFeature = namedtuple('BinaryFeature', ['name'])


NumericalFeature = namedtuple('NumericalFeature', ['name'])


CategoricalFeature = namedtuple('CategoricalFeature', ['name', 'family'])
