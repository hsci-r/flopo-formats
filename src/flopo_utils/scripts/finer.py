import argparse
import csv
import logging

from flopo_utils.io import load_conll
import flopo_utils.wrappers.finer


def write_annotations(annotations, output_file):
    with open(output_file, 'w+') as fp:
        writer = csv.writer(fp)
        writer.writerow(
            ('articleId', 'sentenceId', 'startWordId', 'endWordId', 'value'))
        for doc_id, doc_anns in annotations:
            for s_id, start_idx, end_idx, ann_type in doc_anns:
                writer.writerow((doc_id, s_id, start_idx, end_idx, ann_type))


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input-file')
    parser.add_argument('-o', '--output-file')
    parser.add_argument(\
        '-L', '--logging', default='WARNING',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'])
    return parser.parse_args()


def main():
    args = parse_arguments()
    logging.basicConfig(
        level=args.logging,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M')
    corpus = load_conll(args.input_file)
    annotations = []
    for i, (doc_id, doc) in enumerate(corpus.items(), 1):
        sentences = [[t.string for t in s.tokens] for s in doc.sentences]
        annotations.append((
            doc_id,
            flopo_utils.wrappers.finer.annotate(sentences)))
        logging.info('Processing document: {} ({}/{})'\
                     .format(doc_id, i, len(corpus)))
    write_annotations(annotations, args.output_file)

