"""
Application for stackoverflow analytics
"""
from collections import defaultdict

import datetime
import re
import csv
import heapq
import argparse
import json
import logging
import logging.config
from lxml import etree
import yaml

logger = logging.getLogger("application_logger")

LOG_CONFIG_NM = "logging.conf.yml"


def load_stop_words(path):
    """
    load stop words
    :param path:
    :return:
    """
    words = set()
    with open(path, "rb") as file_pointer:
        lines_s = str(file_pointer.read(), "koi8-r")
        lines = lines_s.split("\n")
        for line in lines:
            if line.strip() != "":
                words.add(line.lower())
    return words


def process_title(string, stop_words):
    """
    process title
    :param string:
    :param stop_words:
    :return:
    """
    result = set()
    for word in re.findall(r"\w+", string.lower()):
        if word not in stop_words:
            result.add(word)
    return result


def extract_doc(string: str, stop_words):
    """
    exctract document
    :param string:
    :param stop_words:
    :return:
    """
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
        result = {
            "title": title_set,
            "score": score,
            "creation_date": creation_date
        }
    else:
        result = dict()
    return result


def read_docs(path_posts, path_stop_words):
    """
    read documents
    :param path_posts:
    :param path_stop_words:
    :return:
    """
    stop_words = load_stop_words(path_stop_words)
    docs = []
    with open(path_posts) as file_pointer:
        for line in file_pointer:
            doc = extract_doc(line, stop_words)
            docs.append(doc)
    return docs


def generate_indicies(docs):
    """
    generate inverted indicies
    :param docs:
    :return:
    """
    word_idx = defaultdict(set)
    year_idx = defaultdict(set)
    for doc_id, doc in enumerate(docs):
        try:
            logger.log(level=logging.DEBUG - 5, msg=f"processing document #{doc_id} for indicies")
            year = doc["creation_date"].year
            words = doc["title"]
            for word in words:
                word_idx[(year, word)].add(doc_id)
                year_idx[year].add(word)
        except Exception as exc:
            logger.log(
                level=logging.DEBUG - 5,
                msg=f"Exception while processing doc_id={doc_id} in 'generate_indicies': {exc}"
            )
    return word_idx, year_idx


def read_queries(path):
    """
    read queries
    :param path:
    :return:
    """
    queries = []
    with open(path, encoding='utf-8') as file_pointer:
        reader = csv.reader(file_pointer, delimiter=",")
        for row in reader:
            record = {
                "start": int(row[0]),
                "finish": int(row[1]),
                "top_n": int(row[2])
            }
            queries.append(record)
    return queries


def process_query(query, word_idx, year_idx, docs):
    """
    process one query
    :param query:
    :param word_idx:
    :param year_idx:
    :param docs:
    :return:
    """
    word2score = defaultdict(int)
    for year in range(query["start"], query["finish"] + 1):
        words = year_idx[year]
        for word in words:
            for word_index in word_idx[(year, word)]:
                word2score[word] += docs[word_index]["score"]
    score_word = [(-v, k) for k, v in word2score.items()]
    heapq.heapify(score_word)
    result = []
    no_loop = True
    for k in range(query["top_n"]):
        if len(score_word) > 0:
            no_loop = False
            score, word = heapq.heappop(score_word)
            result.append([word, -score])
        else:
            logger.warning(
                f"not enough data to answer, "
                f"found {k} words out of {query['top_n']} "
                f"for period \"{query['start']},{query['finish']}\""
            )
            break
    if no_loop and query['top_n'] > 0:
        logger.warning(
            f"not enough data to answer, "
            f"found 0 words out of {query['top_n']} "
            f"for period \"{query['start']},{query['finish']}\""
        )
    return {
        "start": query["start"],
        "end": query["finish"],
        "top": result
    }


def process_queries(queries, docs, word_idx, year_idx):
    """
    process queries
    :param queries:
    :param docs:
    :param word_idx:
    :param year_idx:
    :return:
    """
    responses = []
    for query in queries:
        logger.debug(
            f"got query \"{query['start']},{query['finish']},{query['top_n']}\"")
        resp = process_query(query, word_idx, year_idx, docs)
        responses.append(resp)
    return responses


def setup_logging():
    """
    setup logging with config file
    :return:
    """
    with open(LOG_CONFIG_NM) as file_pointer:
        logging.config.dictConfig(yaml.safe_load(file_pointer.read()))


def main():
    """
    main function
    :return:
    """
    logger.debug("Application started")
    setup_logging()
    parser = argparse.ArgumentParser(description='Work with inverted_index.py')
    parser.add_argument('--questions', action="store",
                        dest="questions", type=str, required=True)
    parser.add_argument('--stop-words', action="store",
                        dest="stop_words", type=str, required=True)
    parser.add_argument('--queries', action="store",
                        dest="queries", type=str, required=True)

    args = parser.parse_args()
    logger.info("process XML dataset")
    docs = read_docs(args.questions, args.stop_words)
    logger.info("process XML dataset, ready to serve queries")
    logger.info("ready to serve queries")
    queries = read_queries(args.queries)
    logger.info("finish processing queries")
    word_idx, year_idx = generate_indicies(docs)
    responses = process_queries(queries, docs, word_idx, year_idx)
    for resp in responses:
        string = json.dumps(resp)
        print(string)
    logger.debug("Application finished.")


if __name__ == '__main__':
    main()
