import argparse
from pdb import help
import re
from collections import defaultdict
import struct
import array
from pdb import set_trace


class StoragePolicy:
    @staticmethod
    def dump(word_to_doc_mapping, filepath):
        pass

    @staticmethod
    def load(filepath):
        pass


class SimplePolicy(StoragePolicy):
    @staticmethod
    def dump(word_to_doc_mapping, filepath):
        with open(filepath, 'w') as fp:
            for word, docs in word_to_doc_mapping.items():
                # w_len = struct.calcsize(word)
                word_enc = word.encode()
                fmt = f"{len(word_enc)}s{len(docs)}i"
                data = str(struct.pack(fmt, word_enc, *list(docs)))
                fp.write(fmt + "\n")
                fp.write(data + '\n')

    @staticmethod
    def load(filepath):
        result = dict()
        prev = None
        with open(filepath, 'rb') as fp:
            for i, line in enumerate(fp):
                if i % 2 == 1 and len(line) > 0:
                    fmt = prev[:-1]
                    data = eval(line[:-1])
                    objects = struct.unpack(fmt, data)
                    # print(objects)
                    result[objects[0].decode("utf-8")] = set(objects[1:])
                if len(line) > 0:
                    prev = line
        return result


class InvertedIndex:
    def __init__(self):
        self.data = None

    def query(self, words: list) -> list:
        """Return the list of relevant documents for the given query"""
        intersection = None
        for word in words:
            if intersection is None:
                intersection = self.data[word].copy()
            else:
                intersection &= self.data[word]
        return [str(v) for v in intersection]

    def dump(self, filepath: str, storage_policy=None):
        if storage_policy is None:
            storage_policy = SimplePolicy
        storage_policy.dump(word_to_doc_mapping=self.data, filepath=filepath)

    @classmethod
    def load(cls, filepath: str, storage_policy=None):
        if storage_policy is None:
            storage_policy = SimplePolicy
        ii = InvertedIndex()
        ii.data = storage_policy.load(filepath=filepath)
        return ii

    def __eq__(self, other):
        if self.data.keys() != other.data.keys():
            # set_trace()
            return False
        else:
            result = True
            for key in self.data.keys():
                if self.data[key] != other.data[key]:
                    # set_trace()
                    result = False
                    break
            return result


def get_words(string):
    # print(f"string: '{string}'")
    string = re.sub(r"^\W+", "", string)
    string = re.sub(r"\W+$", "", string)
    return [t for t in re.split(pattern=r"\W", string=string) if len(t) > 0]


def extract_document(line):
    line = re.sub(r"\W+$", "", re.sub(r"^\W+", "", line))
    if len(line) > 0:
        doc_id, text = [t for t in re.split(pattern=r"\W+", string=line, maxsplit=1) if len(t) > 0]
        return str(doc_id), re.sub(r"\W+$", "", re.sub(r"^\W+", "", text))
    else:
        return None, None


def load_documents(dataset_path: str):
    docs = dict()
    with open(dataset_path, "r") as fp:
        for line in fp:
            if len(line) > 0:
                doc_id, text = extract_document(line)
                if doc_id is not None:
                    docs[doc_id] = text
    return docs


def build_inverted_index(docs: dict):
    iidx_data = defaultdict(set)
    for doc_id, text in docs.items():
        content = set(get_words(text))
        for word in content:
            if doc_id not in iidx_data[word]:
                iidx_data[word].add(int(doc_id))
    iidx = InvertedIndex()
    iidx.data = iidx_data
    return iidx


def buld_action(args):
    docs = load_documents(args.dataset)
    idx = build_inverted_index(docs)
    idx.dump(args.output)


def process_queries(inv_index, queries):
    if queries is not None:
        for query_s in queries:
            query = [x for x in query_s.split()]
            # set_trace()
            res = inv_index.query(query)
            print(" ".join(res))


def query_action(arguments):
    # set_trace()
    count = 0
    for obj in [
        arguments.file_cp,
        arguments.file_utf,
        arguments.queries
    ]:
        if obj is not None:
            count += 1
    if count != 1:
        return Exception(
            "You must use one and only one of "
            "the following arguments:\n"
            "  --query query1 [--query query2] or "
            "  --query-file-cp1251 or\n"
            "  --query-file-utf8"
        )
    # if args.file_cp is not None
    if arguments.index is None:
        raise Exception("index is undefined")
    else:
        idx = InvertedIndex.load(arguments.index)
    if arguments.queries is not None:
        process_queries(idx, arguments.queries)
    elif arguments.file_cp is not None:
        queries = []
        with open(arguments.file_cp, encoding='cp1251') as fp:
            for line in fp:
                queries.append(line)
        process_queries(idx, queries)
    elif arguments.file_utf is not None:
        queries = []
        with open(arguments.file_utf, encoding='utf8') as fp:
            for line in fp:
                queries.append(line)
        process_queries(idx, queries)
    else:
        raise Exception("You must define --query or ----query-file-cp1251 or --query-file-utf8")


def main():
    """
    runs cli interface with the following commands:
    1) python3 inverted_index.py build --dataset /path/to/dataset --output /path/to/inverted.index
    2) python3 inverted_index.py query --index /path/to/inverted.index --query-file-utf8 /path/to/quries.txt
    3) cat /path/to/quries.txt | python3 inverted_index.py query --index /path/to/inverted.index --query-file-utf8 -
    4) python3 inverted_index.py query --index /path/to/inverted.index --query-file-cp1251 /path/to/quries.txt
    5) cat /path/to/quries.txt | python3 inverted_index.py query --index /path/to/inverted.index --query-file-cp1251 -
    6) python3 inverted_index.py query --index /path/to/inverted.index --query first query [--query the second query]6
    :return:
    """

    parser = argparse.ArgumentParser(description='Work with inverted_index.py')
    subparsers = parser.add_subparsers(dest='command')
    subparsers.required = True

    build_parser = subparsers.add_parser("build", help="build inverted index")
    build_parser.add_argument('--dataset', action="store", dest="dataset", type=str, required=True)
    build_parser.add_argument('--output', action="store", dest="output", type=str, required=True)
    build_parser.set_defaults(func=buld_action)

    query_parser = subparsers.add_parser("query", help="build inverted index")
    query_parser.add_argument('--index', action="store", dest="index", type=str, required=True)
    query_parser.add_argument('--query-file-utf8', action="store", dest="file_utf", type=str)
    query_parser.add_argument('--query-file-cp1251', action="store", dest="file_cp", type=str)
    query_parser.add_argument('--query', action="append", dest="queries")
    query_parser.set_defaults(func=query_action)

    args = parser.parse_args()
    if not vars(args):
        parser.print_usage()
    else:
        args.func(args)



if __name__ == "__main__":
    main()

"""
build --dataset data/wikipedia_sample --output iidx

"""
