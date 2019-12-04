import argparse

from flopo_utils.data import Corpus
import flopo_utils.io


def parse_arguments():
    parser = argparse.ArgumentParser(
        description='Print the spans of a given annotation layer as text.')
    parser.add_argument(
        '-i', '--input-file', metavar='FILE',
        help='A WebAnno-TSV document.')
    parser.add_argument('-l', '--layer', metavar='LAYER')
    return parser.parse_args()


def main():
    args = parse_arguments()
    doc = flopo_utils.io.load_webanno_tsv(args.input_file)
    features = None
    for l, f in doc.schema:
        if l == args.layer:
            features = f
            break
    for s in doc.sentences:
        if args.layer in s.spans:
            for (start, end, values) in s.spans[args.layer]:
                text = ''.join([t.string + t.space_after for t in s.tokens[start-1:end]]).strip()
                values_lst = [values[f] for f in features]
                print('\t'.join(values_lst + [text]))

