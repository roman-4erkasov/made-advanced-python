from collections import defaultdict
from textwrap import dedent
import datetime
import task_cherkasov_roman_stackoverflow_analytics as task

import pytest

PATH_STOPWORDS = "../data/stop_words_en.txt"

DATA_MINI_STR = """<row Title="Is SEO better better better done with repetition?" PostTypeId="1" """ + \
                """ CreationDate="2019-10-15T00:44:56.847" Score="10"/>
<row Title="What is SEO?" PostTypeId="1" CreationDate="2019-10-15T00:44:56.847" Score="5"/>
<row Title="Is Python better than Javascript?" PostTypeId="1" CreationDate="2020-10-15T00:44:56.847" Score="20"/>"""

DATA_MINI_DOCS = [
    dict(
        title={"seo", "better", "repetition"},
        creation_date=datetime.datetime.strptime(
            "2019-10-15T00:44:56.847",
            "%Y-%m-%dT%H:%M:%S.%f"
        ),
        score=10
    ),
    dict(
        title={"seo"},
        creation_date=datetime.datetime.strptime(
            "2019-10-15T00:44:56.847",
            "%Y-%m-%dT%H:%M:%S.%f"
        ),
        score=5
    ),
    dict(
        title={"python", "better", "javascript"},
        creation_date=datetime.datetime.strptime(
            "2020-10-15T00:44:56.847",
            "%Y-%m-%dT%H:%M:%S.%f"
        ),
        score=20
    ),
]

QUERIES_MINI_STR = "2019,2019,2\n2019,2020,4"

QUERIES_MINI = [
    {"start": 2019, "finish": 2019, "top_n": 2},
    {"start": 2019, "finish": 2020, "top_n": 4},
]

WORD_IDX_MINI = defaultdict(
    set,
    {
        (2019, "seo"): {0, 1},
        (2019, "better"): {0},
        (2019, "repetition"): {0},
        (2020, "better"): {2},
        (2020, "python"): {2},
        (2020, "javascript"): {2}
    }
)

YEAR_IDX_MINI = {
    2019: {"seo", "better", "repetition"},
    2020: {"python", "better", "javascript"}
}

RESP_MINI = [
    {"start": 2019, "end": 2019, "top": [["seo", 15], ["better", 10]]},
    {
        "start": 2019,
        "end": 2020,
        "top": [
            ["better", 30], ["javascript", 20], ["python", 20], ["seo", 15]
        ]
    },
]


# ############################ fixtures ##################################

@pytest.fixture()
def stop_words():
    words = task.load_stop_words(PATH_STOPWORDS)
    return words


@pytest.fixture()
def data_mini(tmpdir):
    fio = tmpdir.join("data_mini.txt")
    fio.write(DATA_MINI_STR)
    return fio


@pytest.fixture()
def queries_mini(tmpdir):
    fio = tmpdir.join("queries.csv")
    fio.write(QUERIES_MINI_STR)
    return fio


# ############################### tests ##################################

def test_stop_words_loading():
    expected = 319
    words = task.load_stop_words(PATH_STOPWORDS)
    actual = len(words)
    assert expected == actual, (
        f"{expected}=={actual}"
    )


@pytest.mark.parametrize(
    "string, expected",
    [
        (
                dedent("""
            <row
                Title="Is SEO better better better done with repetition?" 
                PostTypeId="1"
                CreationDate="2019-10-15T00:44:56.847"
                Score="10"
            />
            """),
                dict(
                    title={"seo", "better", "repetition"},
                    creation_date=datetime.datetime.strptime(
                        "2019-10-15T00:44:56.847",
                        "%Y-%m-%dT%H:%M:%S.%f"
                    ),
                    score=10
                )
        ),
        (
                dedent("""
            <row
                Title="What is SEO?"
                PostTypeId="1"
                CreationDate="2019-10-15T00:44:56.847"
                Score="5"
            />
            """),
                dict(
                    title={"seo"},
                    creation_date=datetime.datetime.strptime(
                        "2019-10-15T00:44:56.847",
                        "%Y-%m-%dT%H:%M:%S.%f"
                    ),
                    score=5
                )
        ),
        (
                dedent("""
            <row
                Title="Is Python better than Javascript?"
                PostTypeId="1"
                CreationDate="2020-10-15T00:44:56.847"
                Score="20"
            />
            """),
                dict(
                    title={"python", "better", "javascript"},
                    creation_date=datetime.datetime.strptime(
                        "2020-10-15T00:44:56.847",
                        "%Y-%m-%dT%H:%M:%S.%f"
                    ),
                    score=20
                )
        ),
        (
                dedent("""
            <row
                Title="Setting style on first and last visible TabItem of TabControl"
                PostTypeId="1"
                CreationDate="2008-10-15T00:44:56.847"
                Score="5"
            />
            """),
                dict(
                    title={"setting", "style", "visible", "tabitem", "tabcontrol"},
                    creation_date=datetime.datetime.strptime(
                        "2008-10-15T00:44:56.847",
                        "%Y-%m-%dT%H:%M:%S.%f"
                    ),
                    score=5
                )
        ),
        (
                dedent("""
            <row
                Title="Setting style on first and last visible TabItem of TabControl"
                PostTypeId="2"
                CreationDate="2008-10-15T00:44:56.847"
                Score="5"
            />
            """),
                dict()
        ),
    ]
)
def test_extract_doc(stop_words, string, expected):
    actual = task.extract_doc(string=string, stop_words=stop_words)
    assert expected == actual, (
        f"{expected}=={actual}"
    )


def test_read_docs(data_mini):
    actual = task.read_docs(data_mini, PATH_STOPWORDS)
    expected = DATA_MINI_DOCS
    assert expected == actual, (
        f"{expected}=={actual}"
    )


def test_generate_indicies_data_mini(data_mini):
    docs = task.read_docs(data_mini, PATH_STOPWORDS)
    wi_act, yi_act = task.generate_indicies(docs)
    assert WORD_IDX_MINI == wi_act, (
        f"{WORD_IDX_MINI}=={wi_act}"
    )
    assert YEAR_IDX_MINI == yi_act, (
        f"{YEAR_IDX_MINI}=={yi_act}"
    )


def test_read_queries_data_mini(queries_mini):
    expected = [
        {"start": 2019, "finish": 2019, "top_n": 2},
        {"start": 2019, "finish": 2020, "top_n": 4},
    ]
    actual = task.read_queries(queries_mini)
    assert expected == actual, (
        f"{expected}=={actual}"
    )


@pytest.mark.parametrize(
    "query, expected",
    [
        (
                QUERIES_MINI[0],
                RESP_MINI[0]
        ),
        (
                QUERIES_MINI[1],
                RESP_MINI[1]
        )
    ]
)
def test_process_query_mini(query, expected):
    actual = task.process_query(
        query=query,
        word_idx=WORD_IDX_MINI,
        year_idx=YEAR_IDX_MINI,
        docs=DATA_MINI_DOCS
    )
    assert expected == actual, (
        f"{expected}=={actual}"
    )


@pytest.mark.parametrize(
    "query",
    [
        {"start": 2019, "finish": 2019, "top_n": 200},
        {"start": 2019, "finish": 2020, "top_n": 400},
    ]
)
def test_process_query_warn(query, caplog):
    _ = task.process_query(
        query=query,
        word_idx=WORD_IDX_MINI,
        year_idx=YEAR_IDX_MINI,
        docs=DATA_MINI_DOCS
    )
    assert any("not enough data to answer" in message for message in caplog.messages)


def test_process_queries_mini():
    actual = task.process_queries(
        queries=QUERIES_MINI,
        docs=DATA_MINI_DOCS,
        word_idx=WORD_IDX_MINI,
        year_idx=YEAR_IDX_MINI
    )
    assert RESP_MINI == actual, (
        f"{RESP_MINI}=={actual}"
    )
