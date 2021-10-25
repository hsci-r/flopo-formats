import logging
import os
import os.path

from flopo_formats.io.conll import CoNLLCorpusReader
from flopo_formats.io.csv import \
    CSVCorpusReader, CSVCorpusWriter, write_split_csv
from flopo_formats.io.webannotsv import WebAnnoTSVReader, write_webanno_tsv
from flopo_formats.io.prolog import write_prolog


def _get_filenames(path, recursive=False):
    if os.path.isfile(path):
        return [path]
    elif os.path.isdir(path):
        results = []
        if not recursive:
            for f in os.listdir(path):
                filename = os.path.join(path, f)
                if os.path.isfile(filename):
                    results.append(filename)
        else:
            for dirname, dirs, files in os.walk(path):
                results.extend([os.path.join(dirname, f) for f in files])
        return results
    else:
        raise RuntimeError('File: \'{}\' does not exist!'.format(path))


# FIXME rename parameters to: "path", "format"
def read_docs(path, _format, recursive):
    '''Returns a generator of documents.'''

    if _format == 'conll':
        reader = CoNLLCorpusReader()
        for filename in _get_filenames(path, recursive):
            # FIXME don't remove the extension
            reader.set_next_doc_id(filename.replace('.txt', ''))
            with open(filename) as fp:
                for doc in reader.read(fp):
                    yield doc
    elif _format == 'csv':
        with open(path) as fp:
            for doc in CSVCorpusReader().read(fp):
                yield doc
    elif _format == 'webanno-tsv':
        if os.path.isdir(path):
            for filename in _get_filenames(path, recursive):
                with open(filename) as fp:
                    doc = WebAnnoTSVReader().read(fp)
                    doc.doc_id = filename
                    yield doc
        elif os.path.isfile(path):
            with open(path) as fp:
                yield WebAnnoTSVReader().read(fp)
    else:
        raise NotImplementedError()


# FIXME rename parameters to: "path", "format"
def write_docs(docs, path, _format, n = None):
    if n is not None:
        if _format == 'csv':
            return write_split_csv(docs, path, n)
        else:
            logging.warning(
                '-n option ignored -- only relevant for output format "csv"')

    # normal writing - without splitting the output files
    if _format == 'csv':
        with open(path, 'w+') as fp:
            writer = CSVCorpusWriter(fp)
            for doc in docs:
                writer.write(doc)
    elif _format == 'webanno-tsv':
        if os.path.isdir(path):
            for doc in docs:
                with open(os.path.join(path, doc.doc_id), 'w+') as fp:
                    write_webanno_tsv(doc, fp)
        else:
            # save a single document
            doc = next(docs)
            with open(path, 'w+') as fp:
                write_webanno_tsv(doc, fp)
            # if there are more documents, show a warning
            try:
                next(docs)
                logging.warning(
                    'Multiple documents read, but the output path'
                    ' is not a directory. Only the first document was saved'
                    ' in: {}'.format(path))
            except StopIteration:
                pass
    elif _format == 'prolog':
        if os.path.isdir(path):
            for doc in docs:
                with open(os.path.join(path, doc.doc_id+'.pl'), 'w+') as fp:
                    write_prolog(doc, fp)
        else:
            # save a single document
            doc = next(docs)
            with open(path, 'w+') as fp:
                write_prolog(doc, fp)
            # if there are more documents, show a warning
            try:
                next(docs)
                logging.warning(
                    'Multiple documents read, but the output path'
                    ' is not a directory. Only the first document was saved'
                    ' in: {}'.format(path))
            except StopIteration:
                pass
    else:
        raise NotImplementedError()

