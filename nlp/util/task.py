import gensim
from nlp.util import to_words, clean_punctuations, clean_digits, to_sentence


def get_org(title, ner=None):

    if ner is None:
        from nlp.processor import NERStanford
        ner = NERStanford()

    words = to_words(title.upper())
    words_ner = ner.process(words)
    org = ner.first_ne(words_ner, key="ORGANIZATION")
    return org


def clean_words(sentence, lemmatizer=None, stop_words=None):
    lm = lemmatizer
    if lm is None:
        from nlp.processor import Lemmatizer
        lm = Lemmatizer()
    sw = stop_words
    if sw is None:
        from nlp.processor import StopWords
        sw = StopWords()

    res = clean_punctuations(sentence)

    words = to_words(res)
    words = clean_digits(words)
    words = lm.process(words)
    words = sw.process(words)

    return words


def clean_sentence(sentence, lemmatizer=None, stop_words=None):
    words = clean_words(sentence, lemmatizer, stop_words)

    return to_sentence(words)


def create_gensim_model(glove_file="glove.42B.300d.w2vformat.txt"):
    model = gensim.models.KeyedVectors.load_word2vec_format(glove_file, limit=500000)
    return model


def load_gensim_model(model_file="wv_100000.model"):
    model = gensim.models.KeyedVectors.load(model_file)
    return model
