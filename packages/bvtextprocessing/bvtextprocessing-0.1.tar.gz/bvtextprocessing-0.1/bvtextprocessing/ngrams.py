from collections import Counter
from .stem import stem_text


def char_ngrams(text, n, to_tuple=False):
    ngrams = Counter()
    for i in range(len(text) - n + 1):
        gram = text[i: i+n]
        if to_tuple:
            gram = tuple(gram)
        ngrams[gram] += 1
    return ngrams


def word_ngrams(text, n, stem_language=None):
    if stem_language:
        words = stem_text(text, language=stem_language)
    else:
        words = text.split()
    ngrams = char_ngrams(words, n, to_tuple=True)
    return ngrams
