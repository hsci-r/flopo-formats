import argparse
import csv
import os
import os.path
import sys

from flopo_utils.data import Corpus
import flopo_utils.io


def export_document(doc, writer, doc_id, layer, header=False, text=False, linearize=[]):
    features = None
    for l, f in doc.schema:
        if l == layer:
            features = f
            break
    if features is None:
        raise Exception('Annotation layer {} not found'.format(layer))
    if header:
        writer.writerow(
            ('articleId', 'sentenceId', 'startWordId', 'endWordId')\
            + tuple(f for f in features if f) \
            + (('text',) if text else ()) \
            + tuple('{}.{}'.format(l, f) for l, f in linearize))
    for s_id, s in enumerate(doc.sentences, 1):
        if layer in s.spans:
            for (start, end, values) in s.spans[layer]:
                row = (doc_id, s_id, start, end) \
                      + tuple(values[f] for f in features if f)
                if text:
                    row += (''.join([t.string + t.space_after \
                            for t in s.tokens[start-1:end]]).strip(),)
                if linearize:
                    for l, f in linearize:
                        relevant_spans = \
                            [sp for sp in s.spans[l] if sp[0] >= start and sp[1] <= end]
                        relevant_spans.sort()
                        row += (' '.join(str(sp[2][f]) for sp in relevant_spans),)
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
        '-t', '--text', action='store_true',
        help='Attach the text value of each annotation span.')
    parser.add_argument(
        '-l', '--linearize', nargs='+',
        help='Attach the value of some other features for each annotation'\
             ' span. Supply a list of entries of the form: LAYER.FEATURE.')
    parser.add_argument(
        '-d', '--delimiter', default=',',
        help='Delimiter to separate the fields.')
    return parser.parse_args()


def main():
    args = parse_arguments()
    first = True
    outfp = sys.stdout
    if args.output_file is not None and args.output_file != '-':
        outfp = open(args.output_file, 'w+')
    writer = csv.writer(outfp, delimiter=args.delimiter)
    linearize = [x.split('.') for x in args.linearize] if args.linearize is not None else []
    if args.input_file is not None:
        doc = flopo_utils.io.load_webanno_tsv(args.input_file)
        doc_id = os.path.basename(args.input_file).replace('.tsv', '')
        export_document(doc, writer, doc_id, args.annotation, header=first,
            text=args.text, linearize=linearize)
        first = False
    if args.input_dir is not None:
        for dirpath, dirnames, filenames in os.walk(args.input_dir):
            for f in filenames:
                doc_id = f.replace('.tsv', '')
                doc = flopo_utils.io.load_webanno_tsv(os.path.join(dirpath, f))
                export_document(doc, writer, doc_id, args.annotation,
                    header=first, text=args.text, linearize=linearize)
                first = False
    outfp.close()

