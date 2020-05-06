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


def load_corpus(input_loc, _format):
    if _format == 'csv':
        return flopo_formats.io.csv.load_csv(input_loc)
    elif _format == 'conll':
        return flopo_formats.io.conll.load_conll(input_loc)
    elif _format == 'webanno-tsv':
        corpus = Corpus()
        for filename in os.listdir(input_loc):
            doc_id = filename.replace('.tsv', '')
            path = os.path.join(input_loc, filename)
            corpus[doc_id] = flopo_formats.io.webannotsv.load_webanno_tsv(path)
        return corpus
    else:
        raise RuntimeError(\
            'Don\'t know how to load the corpus for format {}'.format(_format))


def save_corpus(corpus, output_loc, _format):
    if _format == 'csv':
        # save whole corpus as CSV
        flopo_formats.io.csv.save_csv(corpus, output_loc)
    elif _format in ('webanno-tsv', 'prolog'):
        # one-document-per-file formats
        for doc_id in corpus:
            try:
                filename = doc_id + \
                          ('.pl' if _format == 'prolog' else '')
                save_document(
                    corpus[doc_id],
                    os.path.join(output_loc, filename),
                    _format)
            except Exception:
                logging.warning('Ignoring document: %s', str(doc_id))
    else:
        raise RuntimeError(\
            'Don\'t know how to save the corpus for format {}'.format(_format))


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


def check_arguments(args):
    '''
    Check the validity of the command-line argument combination
    and determine what to do exactly.
    Returns:
    - `input_loc` -- the location of input (either a file or directory)
    - `output_loc` -- the location of output (same)
    - `processing_level` -- 'corpus' or 'document', accordingly to what
                            we are processing
    '''
    # is the input and output format specified?
    if args.input_format is None:
        raise RuntimeError('No input format supplied (use -f option).')
    if args.output_format is None:
        raise RuntimeError('No output format supplied (use -t option).')
    # is there confusion as to input/output locations?
    if (args.input_file is not None) == (args.input_dir is not None):
        raise RuntimeError('You must supply EITHER -i OR -I.')
    if (args.output_file is not None) == (args.output_dir is not None):
        raise RuntimeError('You must supply EITHER -o OR -O.')
    # good, there isn't -> find out where the input/output really is
    input_loc = args.input_file if args.input_file is not None \
                else args.input_dir
    output_loc = args.output_file if args.output_file is not None \
                 else args.output_dir
    # determine the processing level (document/corpus)
    # from the combination of input/output file/directory
    # FIXME this should rather be expressed in some data structure
    # than in nested ifs
    pl_input, pl_output = None, None
    if args.input_file is not None:
        if args.input_format == 'csv':
            pl_input = 'corpus'
        elif args.input_format == 'webanno-tsv':
            pl_input = 'document'
        # for conll we don't know at this point
    elif args.input_dir is not None:
        if args.input_format in ('conll', 'webanno-tsv'):
            pl_input = 'corpus'
        else:
            raise RuntimeError(
                'Reading from a directory is not supported for'
                ' input format \'{}\'.'.format(args.input_format))
    if args.output_file is not None:
        if args.output_format == 'csv':
            pl_output = 'corpus'
        elif args.output_format in ('webanno-tsv', 'prolog'):
            pl_output = 'document'
    elif args.output_dir is not None:
        if args.output_format in ('webanno-tsv', 'prolog'):
            pl_output = 'document'
        else:
            raise RuntimeError(
                'Writing to a directory is not supported for'
                ' output format \'{}\'.'.format(args.output_format))
    # if we couldn't figure out the input level, set it to the same as output
    if pl_input is None:
        pl_input = pl_output
    # now they must match
    if pl_input != pl_output:
        raise RuntimeError(
            'Processing level mismatch: input is a {}, output is a {}.'\
            .format(pl_input, pl_output))
    # one last thing... adding annotations is currently
    # not supported for single documents
    if pl_input == 'document' and args.annotations:
        logging.warning(
            'Adding annotations to single documents is currently'
            ' not supported. The -a parameter will be ignored.')
    return input_loc, output_loc, pl_input


def main():
    args = parse_arguments()
    input_loc, output_loc, processing_level = check_arguments(args)
    if processing_level == 'document':
        document = load_document(input_loc, args.input_format)
        save_document(document, output_loc, args.output_format)
    elif processing_level == 'corpus':
        corpus = load_corpus(input_loc, args.input_format)
        for a in args.annotations:
            layer, filename = parse_annotation_source(a)
            flopo_formats.io.csv.load_annotation_from_csv(
                corpus, filename, layer)
        save_corpus(corpus, output_loc, args.output_format)

