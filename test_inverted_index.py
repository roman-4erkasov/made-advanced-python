import pytest
import inverted_index
from textwrap import dedent

DATASET_TINY_STR = dedent(
    """
    123    some words A_word  and nothing
    2      some word B_word in this dataset
    5      famous_phrases to be or not to be
    37     all words such as A_word and B_word are here
    """
)



def test_get_words_can_split_lines_correctly():
    text = "   yet or another     word, test"
    # в примере  запятая почему-то не выкидывалась запятая у токена "word,"
    # то есть expected_words = ["yet", "or", "another", "word,", "text"]
    expected_words = ["yet", "or", "another", "word", "test"]
    actual_words = inverted_index.get_words(text)
    assert expected_words == actual_words, (
        "expected words and phrases are not the same"
    )


def test_get_words_returns_empty_list_for_empty_text():
    text = ""
    expected_words = []
    actual_words = inverted_index.get_words(text)
    assert expected_words == actual_words


def test_get_words_rase_exception_for_none():
    with pytest.raises(TypeError):
        inverted_index.get_words(None)


def test_can_instantiate_inverted_index():
    inverted_index.InvertedIndex()


def test_can_load_documents(tmpdir):

    dataset_file = tmpdir.join("tiny.dataset")
    dataset_file.write(DATASET_TINY_STR)
    documents = inverted_index.load_documents(dataset_file)
    etalon_documents = {
        "123": "some words A_word  and nothing",
        "2": "some word B_word in this dataset",
        "5": "famous_phrases to be or not to be",
        "37": "all words such as A_word and B_word are here"
    }
    assert etalon_documents == documents, (
        "load_documents incorrectly loaded dataset"
    )


def test_can_load_inverted_index_from_file():
    pass


