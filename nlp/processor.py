import os.path as osp
import pandas as pd
from openie import StanfordOpenIE
import gensim
from nltk.tag.stanford import StanfordNERTagger
from nltk.tag.stanford import StanfordPOSTagger
from nltk.stem import WordNetLemmatizer
from nltk.stem import PorterStemmer
from nltk.corpus import stopwords

from nlp.util.common import to_words


class Processor:

    def __init__(self):
        self._processor = None

    @property
    def processor(self):
        if self._processor is None:
            self._processor = self.create_processor()
        return self._processor

    def create_processor(self):
        raise ValueError("create_processor is not defined")

    def process(self, *args, **kwargs):
        raise ValueError("process function is not defined")


class NERStanford(Processor):

    def __init__(self, jar_path=None, model_path=None):
        self._jar_path = jar_path \
            if jar_path is not None \
            else osp.join(osp.dirname(__file__),
                          'model', 'stanford-ner.jar')
        self._model_path = model_path \
            if model_path is not None \
            else osp.join(osp.dirname(__file__),
                          'model', 'english.all.3class.distsim.crf.ser.gz')

        super().__init__()

    def create_processor(self):
        jar = self._jar_path
        model = self._model_path
        return StanfordNERTagger(model, jar, encoding='utf8')

    def process(self, words):
        return self.processor.tag(words)

    @staticmethod
    def nth_ne(words_ner, key, nth=0):

        for w in words_ner:
            if w[1] == key:
                nth = nth - 1
            if nth < 0:
                return w[0]
        return None

    @staticmethod
    def first_ne(words_ner, key):
        return NERStanford.nth_ne(words_ner, key, nth=0)


class POSStanford(Processor):

    def __init__(self, jar_path=None, model_path=None):
        self._jar_path = jar_path \
            if jar_path is not None \
            else osp.join(osp.dirname(__file__),
                          'model', 'stanford-postagger.jar')
        self._model_path = model_path \
            if model_path is not None \
            else osp.join(osp.dirname(__file__),
                          'model', 'english-caseless-left3words-distsim.tagger')

        super().__init__()

    def create_processor(self):
        jar = self._jar_path
        model = self._model_path
        return StanfordPOSTagger(model, path_to_jar=jar)

    def process(self, words, merge_nn=True):
        tagger = self.processor

        res_pos = tagger.tag(words)

        if merge_nn:

            def merge_nn(tg):
                word = ' '.join([t[0] for t in tg])
                pos = tg[-1][1]
                return word, pos

            res = []
            cur_tagged = []
            for tagged in res_pos:
                if tagged[1].startswith('NN'):
                    cur_tagged.append(tagged)
                else:
                    if len(cur_tagged) > 0:
                        res.append(merge_nn(cur_tagged))
                        cur_tagged = []
                    res.append(tagged)

            if len(cur_tagged) > 0:
                res.append(merge_nn(cur_tagged))

            res_pos = res

        return res_pos


class SVOStanford(Processor):

    def create_processor(self):
        return StanfordOpenIE()

    def annotate(self, text):
        return self.processor.annotate(text)

    def process(self, text, use_ner=False):

        svo_list = self.annotate(text)

        if len(svo_list) == 0:
            return pd.Series(data={'s': None, 'v': None, 'o': None})

        if not use_ner:
            svo = svo_list[0]
            return pd.Series(data={'s': svo['subject'],
                                   'v': svo['relation'],
                                   'o': svo['object']})

        for svo in svo_list:
            words = self.txtp.to_words(svo['subject'])
            words_ner = self.tokp.tag_ner(words)
            org = self.tokp.first_ne(words_ner, key="ORGANIZATION")

            if org is not None:
                return pd.Series(data={'s': org,
                                       'v': svo['relation'],
                                       'o': svo['object']})

        return pd.Series(data={'s': None, 'v': None, 'o': None})


class WordVector(Processor):

    def __init__(self, model_path=None):
        self._model_path = model_path \
            if model_path is not None \
            else osp.join(osp.dirname(__file__),
                          'model', 'wv_100000.model')

        super().__init__()

    def create_processor(self):
        return gensim.models.KeyedVectors.load(self._model_path)

    def process(self, text):

        words = to_words(text.lower())

        count = 0
        sum = 0.0
        for w in words:
            if w in self.processor:
                sum = sum + self.processor[w]
                count = count + 1.0

        if count <= 0:
            return None

        return sum / count


class Lemmatizer(Processor):

    def create_processor(self):
        return WordNetLemmatizer()

    def process(self, word):

        if isinstance(word, list):
            return [self.process(w) for w in word]

        return self.processor.lemmatize(word.lower())


class Stemmer(Processor):

    def create_processor(self):
        return PorterStemmer()

    def process(self, word):

        if isinstance(word, list):
            return [self.process(w) for w in word]

        return self.processor.stem(word)


class StopWords(Processor):

    def __init__(self, stop_words=None):
        self._stop_words = set(stop_words) if stop_words is not None else None

        super().__init__()

    def create_processor(self):

        return self._stop_words if self._stop_words is not None else set(stopwords.words('english'))

    def process(self, words):
        stop_words = self.processor

        res = []
        for w in words:
            w_test = w[0] if isinstance(w, tuple) else w
            if w_test.lower() not in stop_words:
                res.append(w)

        return res
