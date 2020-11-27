import pytest
import inverted_index
from textwrap import dedent
from pdb import set_trace
import os
from collections import namedtuple


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
def tiny_document_sample(tiny_dataset_fio):
    documents = inverted_index.load_documents(tiny_dataset_fio)
    return documents


@pytest.fixture()
def wikipedia_documents():
    documents = inverted_index.load_documents(DATASET_BIG_FPATH)
    return documents


@pytest.fixture()
def small_sample_wikipedia_documents():
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
    tiny_inverted_index = inverted_index.build_inverted_index(documents)
    answer = tiny_inverted_index.query(query)
    assert sorted(answer) == sorted(etalon_answer), (
        f"Expected answer is {etalon_answer}, but you got {answer}"
    )


def test_can_load_tiny_wikipedia_sample():
    documents = inverted_index.load_documents(DATASET_TINY_FPATH)
    assert len(documents) == 15, (
        "you incorrectly loaded small Wikipedia sample"
    )


@pytest.mark.skip
def test_can_load_wikipedia_sample():
    documents = inverted_index.load_documents(DATASET_BIG_FPATH)
    assert len(documents) == 4100, (
        "you incorrectly loaded Wikipedia sample"
    )


def test_can_build_and_query_small_inverted_index(small_sample_wikipedia_documents):
    wiki_inverted_index = inverted_index.build_inverted_index(small_sample_wikipedia_documents)
    doc_ids = wiki_inverted_index.query(["often"])
    assert isinstance(doc_ids, list), "Inverted index query should return list"


@pytest.mark.skip
def test_can_build_and_query_inverted_index(wikipedia_documents):
    wiki_inverted_index = inverted_index.build_inverted_index(wikipedia_documents)
    doc_ids = wiki_inverted_index.query(["often"])
    assert isinstance(doc_ids, list), "Inverted index query should return list"


@pytest.fixture()
def small_wiki_inverted_index(small_sample_wikipedia_documents):
    inv_index = inverted_index.build_inverted_index(small_sample_wikipedia_documents)
    return inv_index


@pytest.fixture()
def tiny_inverted_index(tiny_document_sample):
    inv_index = inverted_index.build_inverted_index(tiny_document_sample)
    return inv_index


@pytest.fixture()
def wiki_inverted_index(wikipedia_documents):
    inv_index = inverted_index.build_inverted_index(wikipedia_documents)
    return inv_index


def test_can_dump_and_load_small_inverted_index(tmpdir, small_wiki_inverted_index):
    index_fio = tmpdir.join("index.dump")
    small_wiki_inverted_index.dump(index_fio)
    loaded_inverted_index = inverted_index.InvertedIndex.load(index_fio)
    return loaded_inverted_index == small_wiki_inverted_index, (
        "Load should return the same inverted index"
    )


@pytest.mark.skip
def test_can_dump_and_load_inverted_index(tmpdir, wiki_inverted_index):
    index_fio = tmpdir.join("index.dump")
    wiki_inverted_index.dump(index_fio)
    loaded_inverted_index = inverted_index.InvertedIndex.load(index_fio)
    return loaded_inverted_index == wiki_inverted_index, (
        "Load should return the same inverted index"
    )


def test_can_save_and_load_simple_policy_tiny(tmpdir, small_wiki_inverted_index):
    index_fio = tmpdir.join("index.dump")
    mapping = small_wiki_inverted_index.data
    inverted_index.SimplePolicy.dump(mapping, index_fio)
    mapping_loaded = inverted_index.SimplePolicy.load(index_fio)
    return mapping == mapping_loaded, (
        "Load should return the same inverted index"
    )


@pytest.mark.parametrize(
    "left, right, are_equal",
    [
        pytest.param(
            {
                "A_word":[123, 37],
            },
            {
                "A_word": [123, 37],
            },
            True
        ),
        pytest.param(
            {
                "A_word":[123, 37],
            },
            {
                "B_word": [123, 37],
            },
            False
        ),
        pytest.param(
            {
                "A_word":[123, 37],
            },
            {
                "A_word": [123, 38],
            },
            False
        ),
        pytest.param(
            {
                "A_word":[123, 37],
            },
            {
                "A_word": [123],
            },
            False
        ),
        pytest.param(
            {
                "A_word":[123],
            },
            {
                "A_word": [123, 37],
            },
            False
        ),
        pytest.param(
            {
                "A_word":[123, 37],
                "B_word": [124, 38],
            },
            {
                "B_word": [124, 38],
                "A_word": [123, 37],
            },
            True
        ),
        pytest.param(
            {
                "A_word": [123, 37],
            },
            {
                "A_word": [123, 37],
                "B_word": [124, 38],
            },
            False
        ),
        pytest.param(
            {
                "A_word": [123, 37],
                "B_word": [124, 38],
            },
            {
                "A_word": [123, 37],
            },
            False
        ),
    ],
)
def test_inverted_index_equality(left, right, are_equal):
    idx_left = inverted_index.InvertedIndex()
    idx_left.data = left

    idx_right = inverted_index.InvertedIndex()
    idx_right.data = right

    assert are_equal == (idx_left==idx_right), (
        "Method InveredIndex.__eq__ works incorrectly"
    )


@pytest.mark.skip
def test_build_action_smal_wiki(small_wiki_inverted_index, tmpdir):
    fpath = tmpdir.join("output")
    Args = namedtuple("Args", ["dataset", "output"])
    args = Args(dataset=DATASET_TINY_FPATH, output=fpath)
    inverted_index.buld_action(args)

    loaded_index = inverted_index.InvertedIndex.load(fpath)
    assert small_wiki_inverted_index == loaded_index, (
        f"index was built incorrectly etalon={small_wiki_inverted_index.data} actual={loaded_index.data}"
    )


def test_build_action_tiny_dataset(tiny_dataset_fio, tmpdir):

    # make etalone
    docs = inverted_index.load_documents(tiny_dataset_fio)
    etalon = inverted_index.build_inverted_index(docs)

    # make actual
    fpath = tmpdir.join("tiny_output")

    Args = namedtuple("Args", ["dataset", "output"])
    args = Args(dataset=tiny_dataset_fio, output=fpath)
    inverted_index.buld_action(args)
    loaded_index = inverted_index.InvertedIndex.load(fpath)

    assert etalon == loaded_index, (
        f"index was built incorrectly etalone={etalon.data} actual={loaded_index.data}"
    )
