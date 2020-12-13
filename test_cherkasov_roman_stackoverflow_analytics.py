from textwrap import dedent
import datetime
import task_cherkasov_roman_stackoverflow_analytics as task

import pytest


PATH_STOPWORDS = "./data/stop_words_en.txt"

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
    ]
)
def test_extract_doc(stop_words, string, expected):
    actual = task.extract_doc(string=string, stop_words=stop_words)
    assert expected == actual, (
        f"{expected}=={actual}"
    )


def test_read_docs(data_mini):
    # pytest.set_trace()
    actual = task.read_docs(data_mini, PATH_STOPWORDS)
    expected = DATA_MINI_DOCS
    assert expected == actual, (
        f"{expected}=={actual}"
    )

# @pytest.mark.parametrize(
#     "source, query, result",
#     [
#         (
#             """
#             <row
#                 Title="Is SEO better better better done with repetition?"
#                 PostTypeId=2
#                 CreationDate="2019-10-15T00:44:56.847"
#                 Score="10"
#             />
#             <row
#                 Title="What is SEO?”
#                 PostTypeId=2
#                 CreationDate="2019-10-15T00:44:56.847"
#                 Score="5"
#             />
#             <row
#                 Title="Is Python better than Javascript?”
#                 PostTypeId=2
#                 CreationDate="2020-10-15T00:44:56.847"
#                 Score="20"
#             />
#             """,
#             []
#         ),
#         (
#             """
#             <row
#                 Title="Setting style on first and last visible TabItem of TabControl"
#                 PostTypeId=1
#                 CreationDate="2008-10-15T00:44:56.847"
#                 Score="5"
#             />
#             """,
#             []
#         ),
#     ]
# )
# def extract(source, query, result):
#     pass
