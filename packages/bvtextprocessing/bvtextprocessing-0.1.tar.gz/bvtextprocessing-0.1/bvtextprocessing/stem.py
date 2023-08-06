import snowballstemmer


def stem_text(text, language):
    stemmer = snowballstemmer.stemmer(language)
    for word in text.split():
        yield stemmer.stemWord(word)
