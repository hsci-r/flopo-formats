import argparse
import json
import os.path
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED


def load_template(template_file):
    template = None
    with open(template_file) as fp:
        template = json.load(fp)
    return template


def package(corpus_dir, name, template, output_file=None):
    sourceTemplate = json.loads('''{
        "name" : null,
        "format" : "ctsv3",
        "state" : "NEW",
        "timestamp" : null,
        "sentence_accessed" : 0,
        "created" : null,
        "updated" : null
      }''')
    if output_file is None:
        output_file = name + '.zip'
    with ZipFile(output_file, 'w', compression=ZIP_DEFLATED) as myzip:
        sources = []
        for path in Path(corpus_dir).glob('*'):
            sources.append(path.name)
            myzip.write(path, os.path.join('source', path.name))
        template['name'] = name
        template['source_documents'] = \
            list(map(lambda source: { **sourceTemplate, 'name' : source },
                     sources))
        myzip.writestr('exportedproject.json', json.dumps(template))


def parse_arguments():
    parser = argparse.ArgumentParser(
        description='Package a corpus of WebAnno files as a project (*.zip)'
                    ' ready to import to WebAnno.')
    parser.add_argument(
        '-I', '--input-dir', metavar='DIR',
        help='The directory containing WebAnno files.')
    parser.add_argument(
        '-t', '--template-file', metavar='FILE',
        help='The name of the JSON file containing the project template.')
    parser.add_argument(
        '-n', '--name', metavar='NAME',
        help='The name of the WebAnno project.')
    parser.add_argument(
        '-o', '--output-file', metavar='FILE',
        help='The name of the resulting zip file (default: NAME.zip)')
    return parser.parse_args()


def check_arguments(args):
    pass


def main():
    args = parse_arguments()
    check_arguments(args)
    template = load_template(args.template_file)
    package(args.input_dir, args.name, template, args.output_file)

