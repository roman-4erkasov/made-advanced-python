import argparse
from pdb import help
import re
from collections import defaultdict


class InvertedIndex:
    def query(self, words: list) -> list:
        """Return the list of relevant documents for the given query"""
        pass

    def dump(self, filepath: str):
        pass

    @classmethod
    def load(cls, filepath: str):
        pass


def load_documents(args):
    pass


def build_inverted_index(args):
    pass


def buld_action(args):
    vocab = set()
    docs = dict()
    iindex = defaultdict(list)
    print(args)
    with open(args.dataset, "r") as fp:
        for line in fp:
            doc = [t.lower()     for t in re.split(pattern="\W", string=line) if len(t) > 0]
            doc_id = doc[0]
            word = doc[1]
            content = set(doc[2:])
            docs[doc_id] = (word, content)
            vocab |= set(content)
            for word in content:
                if doc_id not in iindex[word]:
                    iindex[word].append(doc_id)
            # print(vocab)
            del doc, content
            # break
    vocab = sorted(vocab)
    # for word in vocab:
    #     if word not in iindex[word]

def query_action(args):
    print(args)


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
    query_parser.add_argument('--query-file-utf8', action="store", dest="fin", type=str)
    query_parser.add_argument('--query-file-cp1251', action="store", dest="fin", type=str)
    query_parser.add_argument('--query', action="append")
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

# inverted_index.dump("/path/to/inverted.index")
# inverted_index = InvertedIndex.load("/path/to/inverted.index")
# document_ids = inverted_index.query(["two", "words"])


if __name__ == "__main__":
    main()
