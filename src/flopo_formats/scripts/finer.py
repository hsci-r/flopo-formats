import argparse
import csv
import logging

#from flopo_formats.io.csv import load_csv
from flopo_formats.io.generic import read_docs
import flopo_formats.wrappers.finer


def write_annotations(annotations, output_file):
    with open(output_file, 'w+') as fp:
        writer = csv.writer(fp, lineterminator='\n')
        writer.writerow(
            ('articleId', 'sentenceId', 'startWordId', 'endWordId', 'value'))
        for doc_id, doc_anns in annotations:
            for s_id, start_idx, end_idx, ann_type in doc_anns:
                writer.writerow((doc_id, s_id, start_idx, end_idx, ann_type))


def parse_arguments():
    parser = argparse.ArgumentParser(
        description='Tag named entities using FINER.')
    parser.add_argument(
        '-i', '--input-file', metavar='FILE',
        help='CSV file containing a corpus to annotate.')
    parser.add_argument(
        '-o', '--output-file', metavar='FILE',
        help='CSV file to save FINER annotations.')
    parser.add_argument(
        '--remote', action='store_true',
        help='Use a remote FINER instance via POST requests.')
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
    annotations = []
    for i, doc in enumerate(read_docs(args.input_file, 'csv', False), 1):
        sentences = [[t.string for t in s.tokens] for s in doc.sentences]
        annotations.append((
            doc.doc_id,
            flopo_formats.wrappers.finer.annotate(sentences, args.remote)))
        logging.info('Processing document: {} ({})'.format(doc.doc_id, i))
    write_annotations(annotations, args.output_file)

