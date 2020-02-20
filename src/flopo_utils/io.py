import csv
import logging
import re

from .data import Corpus, Document, Sentence, Token, Annotation


WEBANNO_LAYERS = {
    'Lemma' :'T_SP=de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Lemma',
    'POS' : 'T_SP=de.tudarmstadt.ukp.dkpro.core.api.lexmorph.type.pos.POS',
    'MorphologicalFeatures' : 'T_SP=de.tudarmstadt.ukp.dkpro.core.api.lexmorph.type.morph.MorphologicalFeatures',
    'Dependency' : 'T_RL=de.tudarmstadt.ukp.dkpro.core.api.syntax.type.dependency.Dependency',
    'Hedging' : 'T_SP=webanno.custom.Hedging',
    'Quote' : 'T_SP=webanno.custom.Quote',
    'Metaphor' : 'T_SP=webanno.custom.Metaphor',
    'Misc' : 'T_SP=webanno.custom.Misc',
    'IQuote' : 'T_SP=webanno.custom.IQuote',
    'NamedEntity' : 'T_SP=de.tudarmstadt.ukp.dkpro.core.api.ner.type.NamedEntity'
}
WEBANNO_LAYERS_INV = { val: key for key, val in WEBANNO_LAYERS.items() }

# TODO this needs to be made less hard-coded (sorry for the English, it's late...)
WEBANNO_FEATURES = {
    'head' : 'BT_de.tudarmstadt.ukp.dkpro.core.api.lexmorph.type.pos.POS',
    'type' : 'hedgingType',
    'author' : 'ROLE_webanno.custom.Quote:author_webanno.custom.QuoteAuthorLink',
    'authorHead' : 'de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Lemma'
}
WEBANNO_FEATURES_INV = { val: key for key, val in WEBANNO_FEATURES.items() }

WEBANNO_ESCAPE_PATTERN = re.compile('([\\\[\]\|_;\*\]]|->)')
WEBANNO_UNESCAPE_PATTERN = re.compile('\\\\([\\\[\]\|_;\*\]]|->)')


HEADER_PATTERN = re.compile('^#([^|]+)\|(.*)$')
SPAN_PATTERN = re.compile('(.+)(\[([0-9]+)\])')

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
        self.annotations = {'Lemma' : [], 'POS' : [], 'Dependency' : [],
                            'MorphologicalFeatures' : []}
        self.idx = 0
        self.corpus = Corpus()

    def _finalize_sentence(self, line):
        if self.tokens:
            s = Sentence(self.tokens, self.annotations)
            self.sentences.append(s)
            self.tokens = []
            self.annotations = {'Lemma' : [], 'POS' : [], 'Dependency' : [],
                                'MorphologicalFeatures' : []}
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
        self.tokens.append(t)
        self.annotations['Lemma'].append(
            Annotation(
                self.sen_id, t.tok_id, t.tok_id, { 'value' : line['lemma'] }))
        self.annotations['POS'].append(
            Annotation(
                self.sen_id, t.tok_id, t.tok_id,
                { 'coarseValue' : line['upos'], 'PosValue' : line['xpos'] }))
        feats = self._parse_feats(line['feats'])
        if feats is not None:
            self.annotations['MorphologicalFeatures'].append(
                Annotation(
                    self.sen_id, t.tok_id, t.tok_id, feats))
        self.annotations['Dependency'].append(
            Annotation(
                self.sen_id, t.tok_id, t.tok_id,
                { 'DependencyType' : line['deprel'], 'flavor' : '',
                  'head' : int(line['head']) }))

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


def _webanno_escape(string):
    return WEBANNO_ESCAPE_PATTERN.sub('\\\\\\1', string)


def _webanno_unescape(string):
    return WEBANNO_UNESCAPE_PATTERN.sub('\\1', string)


class WebAnnoTSVReader:
    FORMAT_DECLARATION = '#FORMAT=WebAnno TSV 3.2\n'

    def __init__(self):
        self.schema = []
        self.sentences = []
        self.tokens = []
        self.last_span = None
        self.annotations = None
        self.sen_id = 1

    def _read_features(self, string):
        return [(WEBANNO_FEATURES_INV[f] if f in WEBANNO_FEATURES_INV else f) \
                for f in string.split('|')]

    def _read_header(self, fp):
        schema = []
        line = fp.readline()        # first line -- format declaration
        if line != WebAnnoTSVReader.FORMAT_DECLARATION:
            raise Exception('Bad format declaration: {}'.format(line))
        while line:
            line = fp.readline().strip()
            m = HEADER_PATTERN.match(line)
            if m is not None:
                schema.append((
                    WEBANNO_LAYERS_INV[m.group(1)],
                    self._read_features(m.group(2)) if m.group(2) else ('',)))
        # two empty lines after the header
        line = fp.readline()
        if line.strip():
            raise Exception('Two empty lines after header missing.')
        return schema

    def _token_from_row(self, row):
        tok_id = int(row.pop(0).split('-')[1])
        start_idx, end_idx = row.pop(0).split('-')
        string = row.pop(0)
        # TODO space after
        return Token(tok_id, start_idx, end_idx, string)

    def _parse_cell(self, cell):
        '''
        Parse the cell in format "value" or "value[span_id]".
        Return the tuple (value, span_id).
        There are two special values:
        - '_' is mapped to None (no annotation present),
        - '*' is mapped to '' (empty string; valueless annotation
          present).
        '''
        m = SPAN_PATTERN.match(cell)
        if m is not None:
            value = _webanno_unescape(m.group(1)) \
                    if m.group(1) != '*' else ''
            span_id = m.group(3) if m.group(2) is not None else None
            return value, span_id
        else:
            value = None
            if cell == '*':
                value = ''
            elif cell != '_':
                value = _webanno_unescape(cell)
            return value, None

    def _finalize_last_span(self, layer):
        sp = self.last_span[layer]
        if sp['id'] is not None:
            self.annotations[layer].append(
                Annotation(self.sen_id, sp['start'], sp['end'], sp['values']))
        self.last_span[layer] = { 'id' : None, 'start' : None, 'end' : None,
                                  'values' : None }

    def _process_token_annotation(self, layer, tok_id, values, span_ids):
        span_ids_list = list(span_ids.values())
        span_id = span_ids_list[0]
        if not all(x == span_id or x is None for x in span_ids_list):
            raise Exception(\
                'Differing span IDs in a multi-token annotation: {}'\
                .format(span_ids_list))
        # if no span ID -> single-token annotation or no annotation
        # (if there was as span ID on the previous token, it ends there)
        if span_id is None:
            self._finalize_last_span(layer)
            # only add a single-token span if the values are not None
            # (which indicates that there is no annotation)
            if not all(x is None for x in values.values()):
                self.annotations[layer].append(
                    Annotation(self.sen_id, tok_id, tok_id, values))
        # span ID differing from the previous token
        # -> the span marked on the previous token ends there,
        #    a new span starts here
        elif self.last_span[layer]['id'] != span_id:
            self._finalize_last_span(layer)
            self.last_span[layer]['id'] = span_id
            self.last_span[layer]['start'] = tok_id
            self.last_span[layer]['end'] = tok_id
            self.last_span[layer]['values'] = values
        # span ID same as on the previous token and the values match
        # -> the current token continues the existing span
        elif self.last_span[layer]['id'] == span_id \
                and self.last_span[layer]['end']+1 == tok_id \
                and self.last_span[layer]['values'] == values:
            self.last_span[layer]['end'] = tok_id
        else:
            # TODO what went wrong?
            # - span ID same but values don't match?
            # - the "current" span ends before the previous token?
            raise RuntimeError('This shouldn\'t happen')

    def _finalize_sentence(self):
        # fix space after
        # TODO not quite correct
        for i, t in enumerate(self.tokens[1:], 1):
            if t.start_idx == self.tokens[i-1].end_idx:
                self.tokens[i-1].space_after = ''
        for layer, features in self.schema:
            self._finalize_last_span(layer)
        self.sentences.append(Sentence(self.tokens, self.annotations))
        self.tokens = []
        self.annotations = { layer: [] for layer, features in self.schema }
        self.sen_id += 1

    def read(self, fp):
        self.schema = self._read_header(fp)
        self.annotations = { layer: [] for layer, features in self.schema }
        self.last_span = { layer: { 'id' : None, 'start' : None,
                                    'end' : None, 'values' : None } \
                           for layer, features in self.schema }
        for line in fp:
            line = line.rstrip()
            if not line:
                self._finalize_sentence()
            elif line.startswith('#'):
                continue
            else:
                row = line.split('\t')
                t = self._token_from_row(row)
                self.tokens.append(t)
                for layer, features in self.schema:
                    values, span_ids = {}, {}
                    for f in features:
                        values[f], span_ids[f] = self._parse_cell(row.pop(0))
                        # if feature is "head" -- remove the sentence ID
                        # and set to 0 for root
                        if f == 'head':
                            i = values[f].index('-')
                            values[f] = int(values[f][i+1:])
                            if values[f] == t.tok_id:
                                values[f] = 0
                    self._process_token_annotation(
                        layer, t.tok_id, values, span_ids)
        self._finalize_sentence()
        return Document(self.schema, self.sentences)


def write_webanno_tsv(document, fp):
    last_span_id = 1
    fp.write('#FORMAT=WebAnno TSV 3.2\n')
    for layer, features in document.schema:
        fp.write('#'+WEBANNO_LAYERS[layer]+'|'+'|'.join(
            [(WEBANNO_FEATURES[f] if f in WEBANNO_FEATURES else f) \
             for f in features])+'\n')
    fp.write('\n')
    for s_id, s in enumerate(document.sentences, 1):
        fp.write('\n')
        fp.write('#Text={}\n'.format(str(s).replace('\\', '\\\\')))
        columns = {}
        for layer, features in document.schema:
            for f in features:
                key = layer+'.'+f
                columns[key] = ['_'] * len(s.tokens)
        for layer, annotations in s.annotations.items():
            for a in annotations:
                span_id = None
                if a.end > a.start:
                    span_id = last_span_id
                    last_span_id += 1
                for f in a:
                    key = layer+'.'+f
                    value = _webanno_escape(str(a[f])) \
                            if a[f] != '' else '*'
                    if f == 'head':
                        if value == '0':
                            value = a.start
                        value = '{}-{}'.format(s_id, value)
                    # exception rule: if feature is "author" and the value is
                    # empty, this fact is marked by "_" instead of "*"
                    if f == 'author' and value == '*':
                        value = '_'
                    # for some weird reason, the annotations pointing to
                    # another token (like "head") must not contain a span ID
                    # (is this a WebAnno bug?)
                    if span_id is not None and f != 'authorHead':
                        value += '[{}]'.format(span_id)
                    for i in range(a.start, a.end+1):
                        columns[key][i-1] = value
        for i, t in enumerate(s.tokens):
            fp.write('\t'.join([
                '{}-{}'.format(s_id, t.tok_id),
                '{}-{}'.format(t.start_idx, t.end_idx),
                t.string] + \
                [columns[layer+'.'+f][i] for layer, features in document.schema for f in features])+'\t\n')


def save_webanno_tsv(document, filename):
    with open(filename, 'w+') as fp:
        write_webanno_tsv(document, fp)


def load_conll(filename):
    with open(filename) as fp:
        return CoNLLCorpusReader().read(fp)


def load_webanno_tsv(filename):
    with open(filename) as fp:
        return WebAnnoTSVReader().read(fp)


EXCLUDE_CSV_KEYS = { 'articleId', 'paragraphId', 'sentenceId', 'wordId',
                     'startWordId', 'endWordId' }


def read_annotation_from_csv(corpus, fp, layer):

    def _parse_line(line, features):
        s_id = int(line['sentenceId'])
        start_w_id, end_w_id = None, None
        if 'startWordId' in line and 'endWordId' in line:
            start_w_id = int(line['startWordId'])
            end_w_id = int(line['endWordId'])
        elif 'wordId' in line:
            start_w_id = int(line['wordId'])
            end_w_id = int(line['wordId'])
        else:
            raise Exception('No word ID')
        values = { '' : '' } if '' in features \
                 else { key : line[key] for key in line \
                        if key not in EXCLUDE_CSV_KEYS }
        return s_id, start_w_id, end_w_id, values

    def _check_boundaries(doc, s_id, start_w_id, end_w_id):
        if s_id > len(doc.sentences):
            raise Exception('Sentence ID out of range')
        if start_w_id < 1 or start_w_id > len(doc.sentences[s_id-1]):
            raise Exception('Span start ID out of range')
        if end_w_id < 1 or end_w_id > len(doc.sentences[s_id-1]):
            raise Exception('Span end ID out of range')
    
    # determine the layer features from the CSV header
    reader = csv.DictReader(fp)
    features = tuple(k for k in reader.fieldnames if k not in EXCLUDE_CSV_KEYS)
    if not features:
        features = ('',)
    # add the annotation layer in each document
    for doc_id in corpus.documents:
        corpus.documents[doc_id].schema.append((layer, features))
        for s in corpus.documents[doc_id].sentences:
            s.annotations[layer] = []
    # read the annotation spans from CSV lines
    for line in reader:
        doc_id = line['articleId']
        if doc_id not in corpus.documents:
            continue
        try:
            s_id, start_w_id, end_w_id, values = _parse_line(line, features)
            _check_boundaries(corpus[doc_id], s_id, start_w_id, end_w_id)
            corpus[doc_id].sentences[s_id-1].annotations[layer].append(
                Annotation(s_id, start_w_id, end_w_id, values))
        except Exception as e:
            logging.warning(
                '{}: layer={} articleId={} sentenceId={} start_w_id={}'\
                ' end_w_id={}'\
                .format(str(e), layer, line['articleId'],
                        line['sentenceId'], start_w_id, end_w_id))


def load_annotation_from_csv(corpus, filename, annotation_name):
    with open(filename) as fp:
        read_annotation_from_csv(corpus, fp, annotation_name)


def _prolog_escape(string):
    return string.replace('"', '""').replace('\\', '\\\\')


def write_prolog(document, fp):
    results = []
    for s_id, s in enumerate(document.sentences, 1):
        for t_id, t in enumerate(s.tokens, 1):
            results.append(
                ('token', s_id, t_id,
                 '"{}"'.format(_prolog_escape(t.string))))
        results.append(('eos', s_id, len(s.tokens), None))
        for a in s.annotations['Lemma']:
            results.append(
                ('lemma', s_id, a.start,
                 '"{}"'.format(_prolog_escape(a['value']))))
        for a in s.annotations['POS']:
            results.append(('upos', s_id, a.start, a['coarseValue'].lower()))
            results.append(('xpos', s_id, a.start, a['PosValue'].lower()))
        for a in s.annotations['Dependency']:
            head = '{}-{}'.format(s_id, a['head'])
            results.append(('head', s_id, a.start, head))
            results.append(('deprel', s_id, a.start, a['DependencyType']))
        for a in s.annotations['MorphologicalFeatures']:
            for key, val in a.items():
                if val:
                    results.append(('feats', s_id, a.start,
                                    '{}({})'.format(key, val)))
    results.sort()
    for predicate, s_id, t_id, arg in results:
        if arg is not None:
            fp.write('{}({}-{}, {}).\n'.format(predicate, s_id, t_id, arg))
        else:
            fp.write('{}({}-{}).\n'.format(predicate, s_id, t_id))


def save_prolog(document, filename):
    with open(filename, 'w+') as fp:
        write_prolog(document, fp)

