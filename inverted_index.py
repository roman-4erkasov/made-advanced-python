import argparse
from pdb import help
import re
from collections import defaultdict
import struct
import array


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

                fmt = f"{len(word)}s{len(docs)}i"
                data = str(struct.pack(fmt, str.encode(word), *list(docs)))
                fp.write(fmt + "\n")
                fp.write(data + '\n')

    @staticmethod
    def load(filepath):
        result = dict()
        with open(filepath, 'w') as fp:
            for i, line in enumerate(fp):
                if i % 2 == 0 and len(line) > 0:
                    fmt = prev
                    data = line
                    objects = struct.unpack(fmt, data)
                    result[objects[0]] = objects[1:]
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
                intersection = self.data[word]
            else:
                intersection &= self.data[word]
        return list(intersection)

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
        if self.data.keys() != other.keys():
            return False
        else:
            result = True
            for key in self.data.keys():
                if self.data[key] != other[key]:
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
                # doc = get_words(line)
                # doc = [t for t in re.split(pattern="\W", string=line) if len(t) > 0]
                # doc_id = doc[0]
                # content = set(doc[1:])
                # docs[doc_id] = content
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
    build_inverted_index(docs)


def query_action(args):
    # print(args)
    if args.fin_cp is not None:
        with open(args.fin_cp) as fp:
            for line in fp:
                words = line.split()


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
    query_parser.add_argument('--query-file-utf8', action="store", dest="fin_utf", type=str)
    query_parser.add_argument('--query-file-cp1251', action="store", dest="fin_cp", type=str)
    query_parser.add_argument('--query', action="append", dest="queries")
    query_parser.set_defaults(func=query_action)

    args = parser.parse_args()
    if not vars(args):
        parser.print_usage()
    else:
        args.func(args)
    #
    # if args.command == "build":
    #     print(f"command={args.command}")
    #
    # elif args.command == "query":
    #     print(f"command={args.command}")


# documents = load_documents("/path/to/dataset")
# inverted_index = build_inverted_index(documents)
#
# inverted_index.dump("/path/to/inverted.index")
# inverted_index = InvertedIndex.load("/path/to/inverted.index")
# document_ids = inverted_index.query(["two", "words"])


if __name__ == "__main__":
    main()

"""
build --dataset data/wikipedia_sample --output iidx

"""
