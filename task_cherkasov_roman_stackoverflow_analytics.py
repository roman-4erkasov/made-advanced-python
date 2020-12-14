from lxml import etree
import datetime
import re
import csv

from pytest import set_trace


def load_stop_words(path):
    words = set()
    with open(path, "rb") as fp:
        lines_s = str(fp.read(), "koi8-r")
        lines = lines_s.split("\n")
        for line in lines:
            if line.strip() != "":
                words.add(line.lower())
    return words


def process_title(string, stop_words):
    result = set()
    for word in re.findall(r"\w+", string.lower()):
        if word not in stop_words:
            result.add(word)
    return result


def extract_doc(string: str, stop_words):
    tree = etree.fromstring(string)
    type_id = tree.get("PostTypeId")
    if str(type_id) == "1":
        title_str = tree.get("Title")
        title_set = process_title(title_str, stop_words)
        creation_date = datetime.datetime.strptime(
            tree.get("CreationDate"),
            "%Y-%m-%dT%H:%M:%S.%f"
        )
        score = int(tree.get("Score"))
        return {
            "title": title_set,
            "score": score,
            "creation_date": creation_date
        }
    else:
        return dict()


def read_docs(path_posts, path_stop_words):
    stop_words = load_stop_words(path_stop_words)
    docs = []
    with open(path_posts) as fp:
        for line in fp:
            doc = extract_doc(line, stop_words)
            docs.append(doc)
    return docs


def read_queries(path):
    queries = []
    with open(path, encoding='utf-8') as fp:
        reader = csv.reader(fp, delimiter=",")
        for row in reader:
            record = {
                "year_start": row[0],
                "year_finish": row[1],
                "top_n": row[2]
            }
            queries.append(record)
    return queries



def process_query(query, docs):
    pass


def process_docs(query, docs):
    pass
