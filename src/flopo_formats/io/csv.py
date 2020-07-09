import csv
import logging
import re

from flopo_formats.data import Corpus, Document, Sentence, Token, Annotation


class CSVCorpusReader:
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
        self.par_id = None
        self.sentences = []
        self.tokens = []
        self.doc = None

    def _finalize_sentence(self, line):
        if self.tokens:
            s = Sentence(
                self.tokens, sen_id = self.sen_id, par_id = self.par_id)
            self.sentences.append(s)
            self.tokens = []
        self.sen_id = int(line['sentenceId']) if line is not None else None
        self.par_id = int(line['paragraphId']) if line is not None else None

    def _finalize_document(self, line):
        self._finalize_sentence(line)
        doc = Document(self.doc_id, CSVCorpusReader.SCHEMA, self.sentences)
        self.sentences = []
        self.doc_id = line['articleId'] if line is not None else None
        return doc

    def _determine_space_after(self, line):
        m = CSVCorpusReader.PATTERN_SPACES_AFTER.match(line['misc'])
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
        result = { key: '' for key in CSVCorpusReader.SCHEMA[2][1] }
        if feats != '_':
            for feat in feats.split('|'):
                key, val = feat.split('=')
                key = _uncapitalize(key)
                if key in result:
                    result[key] = val.lower()
                # some special rules to cover differences between CSV and
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
            line['word'],
            misc=line['misc'],
            space_after=space_after)
        t.annotations['Lemma'] = { 'value' : line['lemma'] }
        t.annotations['POS'] = \
            { 'coarseValue' : line['upos'], 'PosValue' : line['xpos'] }
        # FIXME when do we really need to parse the features?
        t.annotations['feats'] = line['feats']
        feats = self._parse_feats(line['feats'])
        if feats is not None:
            t.annotations['MorphologicalFeatures'] = feats
        t.annotations['Dependency'] = \
            { 'DependencyType' : line['deprel'], 'flavor' : '',
              'head' : int(line['head']) }
        self.tokens.append(t)


    def read(self, fp):
        reader = csv.DictReader(fp)
        for line in reader:
            if line['articleId'] != self.doc_id:
                if self.doc_id is not None:
                    yield self._finalize_document(line)
                else:
                    self.doc_id = line['articleId']
            elif int(line['sentenceId']) != self.sen_id:
                if self.sen_id is not None:
                    self._finalize_sentence(line)
                else:
                    self.sen_id = int(line['sentenceId'])
                    self.par_id = int(line['paragraphId'])
            self._read_token(line)
        yield self._finalize_document(None)


def load_csv(filename):
    corpus = Corpus()
    with open(filename) as fp:
        for doc in CSVCorpusReader().read(fp):
            corpus[doc_id] = doc
    return corpus


class CSVCorpusWriter:
    FIELDNAMES = \
        ('articleId', 'paragraphId', 'sentenceId', 'wordId', 'word',
         'lemma', 'upos', 'xpos', 'feats', 'head', 'deprel', 'misc')

    def __init__(self, fp):
        self.fp = fp
        self.writer = csv.DictWriter(
            self.fp, CSVCorpusWriter.FIELDNAMES,
            delimiter=',', lineterminator='\n')
        self.writer.writeheader()

    def write(self, doc):
        for s in doc.sentences:
            for t in s.tokens:
                row = {
                    'articleId': doc.doc_id, 'paragraphId': s.par_id,
                    'sentenceId': s.sen_id, 'wordId': t.tok_id,
                    'word': t.string, 'lemma': t['Lemma']['value'],
                    'upos': t['POS']['coarseValue'],
                    'xpos': t['POS']['PosValue'],
                    'feats': t['feats'] if t['feats'] != '_' else '',
                    'head': t['Dependency']['head'],
                    'deprel': t['Dependency']['DependencyType'],
                    'misc': t.misc if t.misc != '_' else '' }
                self.writer.writerow(row)


EXCLUDE_CSV_KEYS = { 'articleId', 'paragraphId', 'sentenceId', 'wordId',
                     'startWordId', 'endWordId', 'startSentenceId',
                     'endSentenceId' }


def read_annotation_from_csv(docs, fp, layer):

    def _add_layer_to_schema(doc, layer, features):
        doc.schema.append((layer, features))
        doc.annotations[layer] = []

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

    def _process_line(line, doc, layer, features):
        try:
            start_sen_id, start_w_id, end_sen_id, end_w_id, values = \
                _parse_line(line, features)
            _check_boundaries(
                doc, start_sen_id, start_w_id, end_sen_id, end_w_id)
            doc.annotations[layer].append(
                Annotation(
                    start_sen_id, start_w_id, end_sen_id, end_w_id, values))
        except Exception as e:
            logging.warning(
                '{}: layer={} articleId={} start_sen_id={} start_w_id={}'\
                ' end_sen_id={} end_w_id={}'\
                .format(str(e), layer, line['articleId'],
                        start_sen_id, start_w_id, end_sen_id, end_w_id))

    def _next_line(reader, prev_doc_id=None):
        result = None
        try:
            result = next(reader)
            if prev_doc_id is not None and prev_doc_id > result['articleId']:
                logging.warning(
                    'Annotation CSV not sorted: {} > {} for layer {}!'\
                    .format(prev_doc_id, result['articleId'], layer))
        except StopIteration:
            pass
        return result
    
    # determine the layer features from the CSV header
    reader = csv.DictReader(fp)
    features = tuple(k for k in reader.fieldnames if k not in EXCLUDE_CSV_KEYS)
    if not features:
        features = ('',)
    cur_line = _next_line(reader)
    for doc in docs:
        _add_layer_to_schema(doc, layer, features)
        # skip all the annotations for documents preceding the current one
        while cur_line is not None and cur_line['articleId'] < doc.doc_id:
            cur_line = _next_line(reader, prev_doc_id=cur_line['articleId'])
        # read the annotations for the current document
        while cur_line is not None and cur_line['articleId'] == doc.doc_id:
            _process_line(cur_line, doc, layer, features)
            cur_line = _next_line(reader, prev_doc_id=cur_line['articleId'])
        # now cur_line['articleId'] > doc.doc_id, so we can advance
        # to the next document
        yield doc


def load_annotation_from_csv(docs, filename, annotation_name):
    with open(filename) as fp:
        for doc in read_annotation_from_csv(docs, fp, annotation_name):
            yield doc

