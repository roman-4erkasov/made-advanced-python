import pytest
import inverted_index
from textwrap import dedent
from pdb import set_trace
import os


DATASET_TINY_STR = dedent(
    """
    123    some words A_word  and nothing
    2      some word B_word in this dataset
    5      famous_phrases to be or not to be
    37     all words such as A_word and B_word are here
    """
)

DATASET_BIG_FPATH = "./data/wikipedia_sample"
DATASET_TINY_FPATH = "./data/tiny_wikipedia_sample"


@pytest.fixture()
def tiny_dataset_fio(tmpdir):
    dataset_fio = tmpdir.join("tiny_dataset.txt")
    dataset_fio.write(DATASET_TINY_STR)
    return dataset_fio


@pytest.fixture()
def wikipedia_document():
    documents = inverted_index.load_documents(DATASET_BIG_FPATH)
    return documents


@pytest.fixture()
def tiny_wikipedia_document():
    documents = inverted_index.load_documents(DATASET_TINY_FPATH)
    return documents


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


def test_get_words_raise_exception_for_none():
    with pytest.raises(TypeError):
        inverted_index.get_words(None)


def test_can_instantiate_inverted_index():
    inverted_index.InvertedIndex()


def test_can_load_documents(tiny_dataset_fio):
    documents = inverted_index.load_documents(tiny_dataset_fio)
    etalon_documents = {
        "123": "some words A_word  and nothing",
        "2": "some word B_word in this dataset",
        "5": "famous_phrases to be or not to be",
        "37": "all words such as A_word and B_word are here"
    }
    assert etalon_documents == documents, (
        "load_documents incorrectly loaded dataset"
    )


@pytest.mark.parametrize(
    "query, etalon_answer",
    [
        pytest.param(["A_word"], ["123", "37"]),
        pytest.param(["B_word"], ["2", "37"], id="B_word"),
        pytest.param(["A_word", "B_word"], ["37"], id="both words"),
        pytest.param(["word_does_not_exist"], [], id="word does not exist"),
    ],
)
def test_query_inverted_index_intersect_results(tiny_dataset_fio, query, etalon_answer):
    documents = inverted_index.load_documents(tiny_dataset_fio)
    print(documents)
    # pytest.set_trace()
    tiny_inverted_index = inverted_index.build_inverted_index(documents)
    answer = tiny_inverted_index.query(query)
    assert sorted(answer) == sorted(etalon_answer), (
        f"Expected answer is {etalon_answer}, but you got {answer}"
    )




def test_can_load_inverted_index_from_file(tiny_dataset_fio):
    pass


def test_can_load_tiny_wikipedia_sample(tiny_dataset_fio):
    documents = inverted_index.load_documents(tiny_dataset_fio)
    pytest.set_trace()
    assert len(documents) == 15, (
        "you incorrectly loaded Wikipedia sample"
    )


@pytest.mark.skip
def test_can_load_wikipedia_sample():
    documents = inverted_index.load_documents(DATASET_BIG_FPATH)
    assert len(documents) == 4100, (
        "you incorrectly loaded Wikipedia sample"
    )
