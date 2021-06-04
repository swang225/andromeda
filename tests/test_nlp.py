from andromeda.nlp.util import *
from andromeda.nlp.processor import *


def test_0001():

    text = 'abc,!l--ccd'

    res = clean_punctuations(text)
    expected = 'abclccd'

    assert res == expected


def test_0002():
    text = 'aa123-dde-'

    res = clean_digits(text)
    expected = 'aa-dde-'

    assert res == expected


def test_0003():
    text = 'I love you.'

    res = to_words(text)
    expected = ['I', 'love', 'you', '.']

    assert res == expected


def test_0004():
    text = 'I woke up. It was cold.'

    res = parse_sentences(text)
    expected = ['I woke up.', 'It was cold.']

    assert res == expected


def test_0005():

    text = "studies studying cries cry"

    res1 = to_words(text)
    assert res1 == ['studies', 'studying', 'cries', 'cry']

    lm = Lemmatizer()
    res2 = lm.process(res1)
    assert res2 == ['study', 'studying', 'cry', 'cry']


def test_0006():
    text = "tired tiring tires tire boredom bored boring bore"

    res1 = to_words(text)
    assert res1 == ['tired', 'tiring', 'tires', 'tire', 'boredom', 'bored', 'boring', 'bore']

    stm = Stemmer()
    res2 = stm.process(res1)
    assert res2 == ['tire', 'tire', 'tire', 'tire', 'boredom', 'bore', 'bore', 'bore']


def test_0007():
    text = "I ate breakfast in the morning. I had an apple and some eggs."

    res1 = to_words(text)
    assert res1 == ['I', 'ate', 'breakfast', 'in', 'the',
                    'morning', '.', 'I', 'had', 'an',
                    'apple', 'and', 'some', 'eggs', '.']

    sw = StopWords()
    res2 = sw.process(res1)
    assert res2 == ['ate', 'breakfast', 'morning', '.', 'apple', 'eggs', '.']


def test_0008():
    text = "Apple Google Shuo Johnson John MIT Berkeley"

    ner = NERStanford()

    res1 = to_words(text)
    assert res1 == ['Apple', 'Google', 'Shuo', 'Johnson', 'John', 'MIT', 'Berkeley']

    res2 = ner.process(res1)
    assert res2 == [('Apple', 'O'), ('Google', 'PERSON'), ('Shuo', 'PERSON'),
                    ('Johnson', 'PERSON'), ('John', 'PERSON'),
                    ('MIT', 'PERSON'), ('Berkeley', 'PERSON')]

    res3 = to_words(upper(text))
    assert res3 == ['APPLE', 'GOOGLE', 'SHUO', 'JOHNSON', 'JOHN', 'MIT', 'BERKELEY']

    res4 = ner.process(res3)
    assert res4 == [('APPLE', 'ORGANIZATION'), ('GOOGLE', 'O'), ('SHUO', 'PERSON'),
                    ('JOHNSON', 'PERSON'), ('JOHN', 'PERSON'),
                    ('MIT', 'PERSON'), ('BERKELEY', 'PERSON')]


def test_0009():
    text = "I ate McDonald breakfast in the morning. I had an apple and some eggs."

    pos = POSStanford()

    res1 = to_words(text)
    assert res1 == ['I', 'ate', 'McDonald', 'breakfast', 'in',
                    'the', 'morning', '.', 'I', 'had', 'an',
                    'apple', 'and', 'some', 'eggs', '.']

    res2 = pos.process(res1)
    assert res2 == [('I', 'PRP'), ('ate', 'VBD'),
                    ('McDonald breakfast', 'NNP'),
                    ('in', 'IN'), ('the', 'DT'), ('morning', 'NN'),
                    ('.', '.'), ('I', 'PRP'), ('had', 'VBD'),
                    ('an', 'DT'), ('apple', 'NN'), ('and', 'CC'),
                    ('some', 'DT'), ('eggs', 'NNS'), ('.', '.')]

    res3 = pos.process(res1, merge_nn=False)
    assert res3 == [('I', 'PRP'), ('ate', 'VBD'),
                    ('McDonald', 'NNP'), ('breakfast', 'NNP'),
                    ('in', 'IN'), ('the', 'DT'), ('morning', 'NN'),
                    ('.', '.'), ('I', 'PRP'), ('had', 'VBD'),
                    ('an', 'DT'), ('apple', 'NN'), ('and', 'CC'),
                    ('some', 'DT'), ('eggs', 'NNS'), ('.', '.')]


if __name__ == "__main__":

    test_0001()
    test_0002()
    test_0003()
    test_0004()
    test_0005()
    test_0006()
    test_0007()
    test_0008()
    test_0009()

    print("success")

