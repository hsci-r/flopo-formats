import argparse
import logging
import os
import os.path

from flopo_formats.data import Corpus
import flopo_formats.io.conll
import flopo_formats.io.csv
import flopo_formats.io.webannotsv
import flopo_formats.io.prolog


def load_document(filename, _format):
    if _format == 'webanno-tsv':
        return flopo_formats.io.webannotsv.load_webanno_tsv(filename)
    else:
        raise RuntimeError('Unknown format: {}'.format(_format))


def save_document(document, filename, _format):
    if _format == 'webanno-tsv':
        flopo_formats.io.webannotsv.save_webanno_tsv(document, filename)
    elif _format == 'prolog':
        flopo_formats.io.prolog.save_prolog(document, filename)
    else:
        raise RuntimeError('Unknown format: {}'.format(_format))


def load_corpus(args):
    if args.input_format == 'csv':
        return flopo_formats.io.csv.load_csv(args.input_file)
    elif args.input_format == 'conll':
        filename = args.input_file if args.input_file is not None \
                   else args.input_dir
        return flopo_formats.io.conll.load_conll(filename)
    elif args.input_format == 'webanno-tsv':
        corpus = Corpus()
        for filename in os.listdir(args.input_dir):
            doc_id = filename.replace('.tsv', '')
            path = os.path.join(args.input_dir, filename)
            corpus[doc_id] = flopo_formats.io.webannotsv.load_webanno_tsv(path)
        return corpus
    else:
        raise RuntimeError(\
            'Unknown input format: {.input_format}'.format(args))


def save_corpus(corpus, args):
    if args.output_format == 'csv':
        # save whole corpus as CSV
        flopo_formats.io.csv.save_csv(corpus, args.output_file)
    else:
        # one-document-per-file formats
        for doc_id in corpus:
            try:
                filename = doc_id + \
                          ('.pl' if args.output_format == 'prolog' else '')
                save_document(
                    corpus[doc_id],
                    os.path.join(args.output_dir, filename),
                    args.output_format)
            except Exception:
                logging.warning('Ignoring document: %s', str(doc_id))


def parse_annotation_source(source):
    if ':' in source:
        return tuple(source.split(':')[:2])
    else:
        raise RuntimeError(
            'Could not parse annotation source: {}'.format(source))


def parse_arguments():
    parser = argparse.ArgumentParser(
        description='Convert between different file formats used in FLOPO.')
    parser.add_argument('-f', '--from', dest='input_format',
        choices=['conll', 'csv', 'webanno-tsv'],
        help='input file format')
    parser.add_argument('-t', '--to', dest='output_format',
        choices=['csv', 'webanno-tsv', 'prolog'],
        help='output file format')
    parser.add_argument('-i', '--input-file', metavar='FILE')
    parser.add_argument('-o', '--output-file', metavar='FILE')
    parser.add_argument('-I', '--input-dir', metavar='DIR',
        help='input directory for formats storing each document in a'\
             ' separate file -- all documents in the given directory'
             ' are treated as a corpus and processed')
    parser.add_argument('-O', '--output-dir', metavar='DIR',
        help='output directory (see above)')
    parser.add_argument(
        '-a', '--annotations', nargs='+', default=[],
        help='A list of annotations to include, each having the format:'\
             ' LAYER:FILE, where LAYER is the name of the layer'\
             ' (for example \'Hedging\') and FILE is a CSV file.'\
             ' Terminate the list with "--".')
    return parser.parse_args()


def main():
    args = parse_arguments()
    # FIXME simplify and correct these parameter checks
    if args.input_format is None:
        raise RuntimeError('No input format supplied (use -f option).')
    if args.output_format is None:
        raise RuntimeError('No output format supplied (use -t option).')
    if (args.input_format == 'csv' and args.input_file is not None) \
        or (args.input_format == 'conll' and args.input_file is not None) \
            or args.input_dir is not None:  # convert corpus
        if args.output_dir is None and args.output_format != 'csv':
            raise RuntimeError(
                'Requested conversion of a whole corpus, but no'\
                ' output directory supplied.')
        corpus = load_corpus(args)
        for a in args.annotations:
            layer, filename = parse_annotation_source(a)
            flopo_formats.io.csv.load_annotation_from_csv(
                corpus, filename, layer)
        save_corpus(corpus, args)
    elif args.input_file is not None:       # convert a single document
        if args.output_file is None:
            raise RuntimeError(
                'Requested conversion of a single file, but no'\
                ' output file supplied.')
        document = load_document(args.input_file, args.input_format)
        save_document(document, args.output_file, args.output_format)
    else:
        raise RuntimeError('No input data supplied. Use -i or -I.')

