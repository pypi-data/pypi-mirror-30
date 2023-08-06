from transform import Transform, LambdaTransform, PureTransform

@PureTransform
def Ident(src): return src

# Tokenizers

@PureTransform
def Lower(src): return src.lower()

@PureTransform
def Upper(src): return src.upper()

@PureTransform
def Split(src): return src.split()

@PureTransform
def Set(src): return set(src)

from nltk import sent_tokenize, word_tokenize
SentTokenizer = PureTransform(sent_tokenize)
WordTokenizer = PureTransform(word_tokenize)

# Note that this is not equivalent to PureTransform(sent_tokenize),
# because unlike the lambda function, sent_tokenize takes a language
# argument

# Parsers

def take_nth(src, delim, n):
    out = []
    for token in src:
        parts = token.split(delim)
        out.append(parts[n])
    return out


take_nths = [
    PureTransform(lambda src, n=n, delim=delim: take_nth(src, delim, n), name='take_nth')
    for n in [0, 1, 2, 3, -1]
    for delim in ['/', ':', '\t', '\n', ',', ';', ' ']
]

def onehot_transform(src, vocabulary):
    vecs = []
    for token in src:
        vec = [0] * len(vocabulary)
        vec[vocabulary.index(token)] = 1
        vecs.append(vec)
    return vecs


Onehot = PureTransform(onehot_transform, types={'vocabulary': list})
