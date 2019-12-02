import argparse
import os.path

from flopo_utils.data import Corpus
import flopo_utils.io


def load_document(filename, _format):
    if _format == 'webanno-tsv':
        return flopo_utils.io.load_webanno_tsv(filename)
    else:
        raise RuntimeError('Unknown format: {}'.format(_format))


def save_document(document, filename, _format):
    if _format == 'webanno-tsv':
        flopo_utils.io.save_webanno_tsv(document, filename)
    elif _format == 'prolog':
        flopo_utils.io.save_prolog(document, filename)
    else:
        raise RuntimeError('Unknown format: {}'.format(_format))


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
        # TODO save whole corpus as CSV
        raise NotImplementedError()
    else:
        # one-document-per-file formats
        for doc_id in corpus:
            filename = doc_id + \
                      ('.pl' if args.output_format == 'prolog' else '')
            save_document(
                corpus[doc_id],
                os.path.join(args.output_dir, filename),
                args.output_format)


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--from', dest='input_format',
        choices=['csv', 'webanno-tsv'])
    parser.add_argument('-t', '--to', dest='output_format',
        choices=['csv', 'webanno-tsv', 'prolog'])
    parser.add_argument('-i', '--input-file')
    parser.add_argument('-o', '--output-file')
    parser.add_argument('-I', '--input-dir')
    parser.add_argument('-O', '--output-dir')
    return parser.parse_args()


def main():
    args = parse_arguments()
    if args.input_format is None:
        raise RuntimeError('No input format supplied (use -f option).')
    if args.output_format is None:
        raise RuntimeError('No output format supplied (use -t option).')
    if (args.input_format == 'csv' and args.input_file is not None) \
            or args.input_dir is not None:  # convert corpus
        if args.output_dir is None:
            raise RuntimeError(
                'Requested conversion of a whole corpus, but no'\
                ' output directory supplied.')
        corpus = load_corpus(args)
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

