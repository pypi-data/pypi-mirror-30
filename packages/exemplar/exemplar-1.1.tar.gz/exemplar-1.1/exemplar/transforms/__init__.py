from transform import (
  Transform, LambdaTransform, PureTransform, TransformMap, TransformChain,
  CompoundTransform
  )

from transforms import Ident

# Tokenizers
from transforms import SentTokenizer, WordTokenizer, Upper, Split, Lower, Set
tokenizers = [
    Ident,
    SentTokenizer,
    WordTokenizer, 
    Upper,
    Split, 
    Lower,
    Set
]

# Parsers
from transforms import Onehot, take_nths
parsers = [
    Ident,
    Onehot
] + take_nths
