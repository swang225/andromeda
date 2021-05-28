import string
from nltk.tokenize import word_tokenize, sent_tokenize
from sklearn.cluster import KMeans
from langdetect import detect_langs


def clean_symbols(text, symbols):

    if isinstance(text, list):
        return [clean_symbols(w, symbols) for w in text]

    return text.translate(str.maketrans('', '', symbols))


def clean_punctuations(text):
    return clean_symbols(text, string.punctuation)


def clean_digits(text):
    return clean_symbols(text, string.digits)


def to_words(text):
    return word_tokenize(text)


def parse_sentences(text):
    return sent_tokenize(text)


def upper(text):

    if isinstance(text, list):
        return [upper(w) for w in text]

    return text.upper()


def lower(text):
    if isinstance(text, list):
        return [lower(w) for w in text]

    return text.lower()


def to_sentence(words):
    return " ".join(words)


def kmean(n_clusters, train_data):
    km = KMeans(n_clusters=n_clusters)
    km.fit(train_data)

    return km


def is_english(title):
    # checks if article is english
    # not very accuracy given short titles

    res = detect_langs(title.lower())

    for r in res:
        if r.lang == 'en':
            return True

    return False

