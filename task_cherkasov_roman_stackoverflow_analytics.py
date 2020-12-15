from collections import defaultdict

from lxml import etree
import datetime
import re
import csv
import heapq
import argparse
import json

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


def generate_indicies(docs):
    word_idx = defaultdict(set)
    year_idx = defaultdict(set)
    score_idx = defaultdict(set)
    for doc_id, doc in enumerate(docs):
        year = doc["year"]
        words = doc["title"]
        for word in words:
            word_idx[word].add(doc_id)
            year_idx[year].add(word)
    return word_idx, year_idx


def read_queries(path):
    queries = []
    with open(path, encoding='utf-8') as fp:
        reader = csv.reader(fp, delimiter=",")
        for row in reader:
            record = {
                "start": row[0],
                "finish": row[1],
                "top_n": row[2]
            }
            queries.append(record)
    return queries


def process_query(query, word_idx, year_idx, docs):

    words = set()
    for year in range(query["start"], query["finish"] + 1):
        words |= year_idx[year]
    word2score = defaultdict(int)
    for word in words:
        word2score[word] += docs[word_idx[word]]["score"]
    score_word = [(v, k) for k, v in word2score.items()]
    heap = heapq.heapify(score_word)
    result = []
    for _ in range(query["top_n"]):
        score, word = heapq.heappop(heap)
        result.append((word, score))
    return {
        "start": query["start"],
        "end": query["finish"],
        "top": result
    }


def process_queries(queries, docs, word_idx, year_idx):
    responses = []
    for query in queries:
        resp = process_query(query, word_idx, year_idx, docs)
        responses.append(resp)
    return responses


def main():
    parser = argparse.ArgumentParser(description='Work with inverted_index.py')
    parser.add_argument('--questions', action="store", dest="questions", type=str, required=True)
    parser.add_argument('--stop-words', action="store", dest="stop_words", type=str, required=True)
    parser.add_argument('--queries', action="store", dest="questions", type=str, required=True)

    args = parser.parse_args()
    queries = read_queries(args.queries)
    docs = read_docs(args.questions, args.stop_words)
    word_idx, year_idx = generate_indicies(docs)
    responses = process_queries(queries, docs, word_idx, year_idx)
    for resp in responses:
        s = json.dumps(resp)
        print(s)
