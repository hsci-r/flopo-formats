import argparse
import csv
import os
import os.path
import sys

from flopo_formats.data import Corpus
import flopo_formats.io


def export_document(doc, writer, doc_id, layer, header=False):
    features = None
    for l, f in doc.schema:
        if l == layer:
            features = f
            break
    if features is None:
        raise Exception('Annotation layer {} not found'.format(layer))
    if header:
        writer.writerow(
            ('articleId', 'startSentenceId', 'startWordId', 'endSentenceId',
             'endWordId')\
            + tuple(f for f in features if f))
    for a in doc.annotations[layer]:
        row = (doc_id, a.start_sen, a.start_tok, a.end_sen, a.end_tok) \
              + tuple(a[f] for f in features if f)
        writer.writerow(row)


def parse_arguments():
    parser = argparse.ArgumentParser(
        description='Export the annotations from a given layer as text'\
                    ' or CSV.')
    parser.add_argument(
        '-i', '--input-file', metavar='FILE',
        help='A WebAnno-TSV document.')
    parser.add_argument(
        '-I', '--input-dir', metavar='DIR',
        help='A directory containing WebAnno-TSV documents.')
    parser.add_argument(
        '-o', '--output-file', metavar='FILE', default='-',
        help='Output CSV file - if none given, the standard output is used.')
    parser.add_argument(
        '-a', '--annotation', metavar='LAYER',
        help='The annotation layer to export.')
    parser.add_argument(
        '-d', '--delimiter', default=',',
        help='Delimiter to separate the fields.')
    parser.add_argument(
        '--doc-id',
        help='ID of the current document (default: filename '\
             'without \'.tsv\' suffix).')
    return parser.parse_args()


def main():
    args = parse_arguments()
    first = True
    outfp = sys.stdout
    if args.output_file is not None and args.output_file != '-':
        outfp = open(args.output_file, 'w+')
    writer = csv.writer(outfp, delimiter=args.delimiter, lineterminator='\n')
    if args.input_file is not None:
        doc = flopo_formats.io.load_webanno_tsv(args.input_file)
        doc_id = args.doc_id
        if doc_id is None:
            doc_id = os.path.basename(args.input_file).replace('.tsv', '')
        export_document(doc, writer, doc_id, args.annotation, header=first)
        first = False
    if args.input_dir is not None:
        for dirpath, dirnames, filenames in os.walk(args.input_dir):
            for f in filenames:
                doc_id = f.replace('.tsv', '')
                doc = flopo_formats.io.load_webanno_tsv(os.path.join(dirpath, f))
                export_document(doc, writer, doc_id, args.annotation,
                                header=first)
                first = False
    outfp.close()

