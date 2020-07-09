import argparse
import logging
import os
import os.path

from flopo_formats.data import Corpus
from flopo_formats.io.generic import read_docs, write_docs
from flopo_formats.io.csv import load_annotation_from_csv


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
    parser.add_argument('-i', '--input-path', metavar='PATH',
        help='path to the input file or directory')
    parser.add_argument('-o', '--output-path', metavar='PATH',
        help='path to the output file or directory')
    parser.add_argument('-r', '--recursive', default=False, action='store_true',
        help='in combination with -I, search also subdirectories')
    parser.add_argument(
        '-a', '--annotations', nargs='+', default=[],
        help='A list of annotations to include, each having the format:'\
             ' LAYER:FILE, where LAYER is the name of the layer'\
             ' (for example \'Hedging\') and FILE is a CSV file.'\
             ' Terminate the list with "--".')
    parser.add_argument(\
        '-L', '--logging', default='WARNING',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        help='logging level')
    return parser.parse_args()


def check_arguments(args):
    'Check the validity of the command-line argument combination.'
    # is the input and output format specified?
    if args.input_format is None:
        raise RuntimeError('No input format supplied (use -f option).')
    if args.output_format is None:
        raise RuntimeError('No output format supplied (use -t option).')


def main():
    args = parse_arguments()
    check_arguments(args)
    logging.basicConfig(
        level=args.logging,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M')
    docs = read_docs(args.input_path, args.input_format, args.recursive)
    for a in args.annotations:
        layer, filename = parse_annotation_source(a)
        docs = load_annotation_from_csv(docs, filename, layer)
    write_docs(docs, args.output_path, args.output_format)

