import argparse
from pdb import help
import re
from collections import defaultdict
import struct
import array


class InvertedIndex:
    def query(self, words: list) -> list:
        """Return the list of relevant documents for the given query"""
        intersection = None
        for word in words:
            if intersection is None:
                intersection = self.data

    def dump(self, filepath: str):
        pass

    @classmethod
    def load(cls, filepath: str):
        ii = InvertedIndex()
        ii.data = dict()
        with open(filepath, 'w') as fp:
            for i, line in enumerate(fp):
                if i % 2 == 0 and len(line) > 0:
                    fmt = prev
                    data = line
                    objects = struct.unpack(fmt, data)
                    print(objects)
                if len(line) > 0:
                    prev = line


def get_words(string):
    print(f"string: '{string}'")
    string = re.sub(f"^\W+", "", string)
    string = re.sub(f"\W+$", "", string)
    return [t for t in re.split(pattern="\W", string=string) if len(t) > 0]


def load_documents(dataset_path: str):
    docs = dict()
    with open(dataset_path, "r") as fp:
        for line in fp:
            if len(line) > 0:
                doc = get_words(line)
                # doc = [t for t in re.split(pattern="\W", string=line) if len(t) > 0]
                doc_id = doc[0]
                content = set(doc[1:])
                docs[doc_id] = content
    return docs


def build_inverted_index(docs: dict, iidx_path: str):
    iindex = defaultdict(set)
    for doc_id, content in docs.items():
        for word in content:
            if doc_id not in iindex[word]:
                iindex[word].add(int(doc_id))
    with open(iidx_path, 'w') as fp:
        for word, docs in iindex.items():
            fmt = f"{len(word)}s{len(docs)}i"
            print(fmt, docs)
            # data = str(struct.pack(fmt, array.array('b', word).tobytes(), *list(docs)))
            data = str(struct.pack(fmt, str.encode(word), *list(docs)))

            fp.write(fmt + "\n")
            fp.write(data + '\n')


def buld_action(args):
    docs = load_documents(args.dataset)
    build_inverted_index(docs, args.output)


def query_action(args):
    print(args)
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
