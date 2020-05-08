import logging
import os
import os.path
import re

from flopo_formats.data import Corpus, Document, Sentence
from flopo_formats.io.csv import CSVCorpusReader


# the parsing of individual tokens is same as in the CSV format, thus
# inheritance
class CoNLLCorpusReader(CSVCorpusReader):

    CONLL_FIELDS = \
        ('wordId', 'word', 'lemma', 'upos', 'xpos',
         'feats', 'head', 'deprel', 'deps', 'misc')

    def __init__(self):
        self.doc_id = None
        self.sen_id = None
        self.sen_id_shift = 0
        self.par_id = 0
        self.sentences = []
        self.tokens = []
        self.idx = 0
        self.doc = None

    def set_next_doc_id(self, next_doc_id):
        self.next_doc_id = next_doc_id

    def _finalize_sentence(self):
        if self.tokens:
            s = Sentence(self.tokens, sen_id=self.sen_id, par_id=self.par_id)
            self.sentences.append(s)
            self.tokens = []

    def _finalize_document(self, force=False):
        self._finalize_sentence()
        if self.next_doc_id is not None or force:
            if self.sentences:
                self.doc = Document(self.doc_id, CSVCorpusReader.SCHEMA, self.sentences)
            self.sentences = []
            self.idx = 0
            self.doc_id = self.next_doc_id
            self.par_id = 0
            self.sen_id_shift = 0
        else:
            logging.warning(
                'Finalizing document ("# newdoc" encountered), but no ID'
                 ' for the next document ready. The following text will'
                 ' be appended to the current document.')
            self.sen_id_shift = len(self.sentences)
        self.next_doc_id = None

    def _read_header_line(self, line):
        if line == '# newdoc':
            self._finalize_document()
        elif line == '# newpar':
            self.par_id += 1
        elif line.startswith('# sent_id = '):
            self.sen_id = \
                int(line.replace('# sent_id = ', '')) + self.sen_id_shift
        elif line.startswith('# text ='):
            # we've noticed it, but we're not doing anything with it
            pass
        else:
            # anything else is treated as a "loose" document ID
            # the ".txt" file extension is removed
            self.next_doc_id = re.sub('^#\s*', '', line).replace('.txt', '')

    def read(self, fp):
        for line in fp:
            line = line.rstrip()
            if not line:
                # empty lines end the sentence
                self._finalize_sentence()
            elif line.startswith('#'):
                self._read_header_line(line)
            elif line.count('\t') >= 9: 
                line = dict(zip(
                    CoNLLCorpusReader.CONLL_FIELDS, line.split('\t')))
                self._read_token(line)
            else:
                logging.warning('Ignoring malformed line: {}'.format(line))
            # if a document is ready, yield it
            if self.doc:
                yield self.doc
                self.doc = None
        self._finalize_document(force=True)
        yield self.doc

