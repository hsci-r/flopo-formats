import csv
import logging
import re

from flopo_formats.data import Corpus, Document, Sentence, Token, Annotation


class CoNLLCorpusReader:
    PATTERN_SPACES_AFTER = re.compile('SpacesAfter=([^|]*)')
    SCHEMA = [('Lemma', ('value',)),
              ('POS', ('coarseValue', 'PosValue')),
              ('MorphologicalFeatures',
               ('animacy', 'aspect', 'case', 'definiteness', 'degree',
                'gender', 'mood', 'negative', 'numType', 'number', 'person',
                'possessive', 'pronType', 'reflex', 'tense', 'transitivity',
                'value', 'verbForm', 'voice')),
              ('Dependency', ('DependencyType', 'flavor', 'head'))]

    def __init__(self):
        self.doc_id = None
        self.sen_id = None
        self.sentences = []
        self.tokens = []
        self.idx = 0
        self.corpus = Corpus()

    def _finalize_sentence(self, line):
        if self.tokens:
            s = Sentence(self.tokens)
            self.sentences.append(s)
            self.tokens = []
        self.sen_id = int(line['sentenceId']) if line is not None else None

    def _finalize_document(self, line):
        self._finalize_sentence(line)
        if self.sentences:
            doc = Document(CoNLLCorpusReader.SCHEMA, self.sentences)
            self.corpus.documents[self.doc_id] = doc
        self.sentences = []
        self.doc_id = line['articleId'] if line is not None else None
        self.idx = 0

    def _determine_space_after(self, line):
        m = CoNLLCorpusReader.PATTERN_SPACES_AFTER.match(line['misc'])
        if m is not None:
            return m.group(1).replace('\\n', '\n')
        elif 'SpaceAfter=No' in line['misc']:
            return ''
        else:
            return ' '

    def _parse_feats(self, feats):
        def _uncapitalize(string):
            return string[0].lower() + string[1:] if len(string) >= 0 \
                   else string
        if '=' not in feats:
            return None
        result = { key: '' for key in CoNLLCorpusReader.SCHEMA[2][1] }
        if feats != '_':
            for feat in feats.split('|'):
                key, val = feat.split('=')
                key = _uncapitalize(key)
                if key in result:
                    result[key] = val.lower()
                # some special rules to cover differences between CoNLL and
                # WebAnno-TSV formats
                elif key == 'polarity' and val == 'Neg':
                    result['negative'] = 'true'
        return result

    def _read_token(self, line):
        space_after = self._determine_space_after(line)
        # FIXME for now, only distinguish between space or no space
        # (other types cause bugs further in the pipeline)
        if space_after:
            space_after = ' '
        t = Token(
            line['wordId'],
            self.idx,
            self.idx+len(line['word']),
            line['word'],
            space_after=space_after)
        t.annotations['Lemma'] = { 'value' : line['lemma'] }
        t.annotations['POS'] = \
            { 'coarseValue' : line['upos'], 'PosValue' : line['xpos'] }
        feats = self._parse_feats(line['feats'])
        if feats is not None:
            t.annotations['MorphologicalFeatures'] = feats
        t.annotations['Dependency'] = \
            { 'DependencyType' : line['deprel'], 'flavor' : '',
              'head' : int(line['head']) }
        self.tokens.append(t)
        self.idx += len(line['word']) + len(space_after)


    def read(self, fp):
        reader = csv.DictReader(fp)
        for line in reader:
            if line['articleId'] != self.doc_id:
                self._finalize_document(line)
            elif int(line['sentenceId']) != self.sen_id:
                self._finalize_sentence(line)
            self._read_token(line)
        self._finalize_document(None)
        return self.corpus


def load_conll(filename):
    with open(filename) as fp:
        return CoNLLCorpusReader().read(fp)


EXCLUDE_CSV_KEYS = { 'articleId', 'paragraphId', 'sentenceId', 'wordId',
                     'startWordId', 'endWordId', 'startSentenceId',
                     'endSentenceId' }


def read_annotation_from_csv(corpus, fp, layer):

    def _parse_line(line, features):
        start_sen_id, end_sen_id = None, None
        start_w_id, end_w_id = None, None
        if 'startWordId' in line and 'endWordId' in line:
            start_w_id = int(line['startWordId'])
            end_w_id = int(line['endWordId'])
        elif 'wordId' in line:
            start_w_id = int(line['wordId'])
            end_w_id = int(line['wordId'])
        else:
            raise Exception('No word ID')
        if 'startSentenceId' in line and 'endSentenceId' in line:
            start_sen_id = int(line['startSentenceId'])
            end_sen_id = int(line['endSentenceId'])
        elif 'sentenceId' in line:
            start_sen_id = int(line['sentenceId'])
            end_sen_id = int(line['sentenceId'])
        else:
            raise Exception('No sentence ID')
        values = { '' : '' } if '' in features \
                 else { key : line[key] for key in line \
                        if key not in EXCLUDE_CSV_KEYS }
        return start_sen_id, start_w_id, end_sen_id, end_w_id, values

    def _check_boundaries(doc, start_sen_id, start_w_id, end_sen_id, end_w_id):
        if start_sen_id > len(doc.sentences) \
                or end_sen_id > len(doc.sentences):
            raise Exception('Sentence ID out of range')
        if start_w_id < 1 or start_w_id > len(doc.sentences[start_sen_id-1]):
            raise Exception('Span start ID out of range')
        if end_w_id < 1 or end_w_id > len(doc.sentences[end_sen_id-1]):
            raise Exception('Span end ID out of range')
        if start_sen_id > end_sen_id \
                or (start_sen_id == end_sen_id and start_w_id > end_w_id):
            raise Exception('Span end before start')
    
    # determine the layer features from the CSV header
    reader = csv.DictReader(fp)
    features = tuple(k for k in reader.fieldnames if k not in EXCLUDE_CSV_KEYS)
    if not features:
        features = ('',)
    # add the annotation layer in each document
    for doc_id in corpus.documents:
        corpus.documents[doc_id].schema.append((layer, features))
        corpus.documents[doc_id].annotations[layer] = []
    # read the annotation spans from CSV lines
    for line in reader:
        doc_id = line['articleId']
        if doc_id not in corpus.documents:
            continue
        try:
            start_sen_id, start_w_id, end_sen_id, end_w_id, values = \
                _parse_line(line, features)
            _check_boundaries(
                corpus[doc_id], start_sen_id, start_w_id, end_sen_id, end_w_id)
            corpus[doc_id].annotations[layer].append(
                Annotation(
                    start_sen_id, start_w_id, end_sen_id, end_w_id, values))
        except Exception as e:
            logging.warning(
                '{}: layer={} articleId={} start_sen_id={} start_w_id={}'\
                ' end_sen_id={} end_w_id={}'\
                .format(str(e), layer, line['articleId'],
                        start_sen_id, start_w_id, end_sen_id, end_w_id))


def load_annotation_from_csv(corpus, filename, annotation_name):
    with open(filename) as fp:
        read_annotation_from_csv(corpus, fp, annotation_name)

