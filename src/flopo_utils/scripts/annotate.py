import argparse
import logging
import os
import os.path

from flopo_utils.data import Corpus
from flopo_utils.io import \
    load_annotation_from_csv, load_webanno_tsv, save_webanno_tsv


def load_corpus(corpus_dir):
    corpus = Corpus()
    for dirpath, dirnames, filenames in os.walk(corpus_dir):
        for f in filenames:
            doc_id = f.replace('.tsv', '')
            corpus.documents[doc_id] = load_webanno_tsv(os.path.join(dirpath, f))
    return corpus


def parse_annotation_source(source):
    if ':' in source:
        return tuple(source.split(':')[:2])
    else:
        raise RuntimeError(
            'Could not parse annotation source: {}'.format(source))


def parse_arguments():
    parser = argparse.ArgumentParser(
        description='Add annotations provided as CSV files into a corpus'\
                    ' of WebAnno TSV documents.')
    parser.add_argument(
        '-a', '--annotations', nargs='+',
        help='A list of annotations to include, each having the format:'\
             ' LAYER:FILE, where LAYER is the name of the layer'\
             ' (for example \'Hedging\') and FILE is a CSV file.'\
             ' Terminate the list with "--".')
    parser.add_argument('-I', '--input-dir', metavar='DIR',
        help='input directory containing WebAnno-TSV files.')
    parser.add_argument('-O', '--output-dir', metavar='DIR',
        help='output directory (see above)')
    parser.add_argument(\
        '-L', '--logging', default='WARNING',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        help='logging level')
    return parser.parse_args()


def main():
    args = parse_arguments()
    logging.basicConfig(
        level=args.logging,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M')
    corpus = load_corpus(args.input_dir)
    for a in args.annotations:
        layer, filename = parse_annotation_source(a)
        load_annotation_from_csv(corpus, filename, layer)
    for doc_id, doc in corpus.items():
        save_webanno_tsv(doc, os.path.join(args.output_dir, doc_id))

