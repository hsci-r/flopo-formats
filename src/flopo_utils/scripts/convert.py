import argparse
import os.path

from flopo_utils.data import Corpus
import flopo_utils.io


def load_corpus(args):
    if args.input_format == 'csv':
        return flopo_utils.io.load_conll(args.input_file)
    elif args.input_format == 'webanno-tsv':
        raise NotImplementedError()
    else:
        raise RuntimeError(\
            'Unknown input format: {.input_format}'.format(args))


def save_corpus(corpus, args):
    if args.output_format == 'csv':
        raise NotImplementedError()
    elif args.output_format == 'webanno-tsv':
        for doc_id in corpus:
            flopo_utils.io.save_webanno_tsv(
                corpus.documents[doc_id],
                os.path.join(args.output_dir, doc_id))
    else:
        raise RuntimeError(\
            'Unknown output format: {.output_format}'.format(args))


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--from', dest='input_format',
        choices=['csv', 'webanno-tsv'])
    parser.add_argument('-t', '--to', dest='output_format',
        choices=['csv', 'webanno-tsv'])
    parser.add_argument('-i', '--input-file')
    parser.add_argument('-o', '--output-file')
    parser.add_argument('-I', '--input-dir')
    parser.add_argument('-O', '--output-dir')
    return parser.parse_args()


def main():
    args = parse_arguments()
    corpus = load_corpus(args)
    save_corpus(corpus, args)

