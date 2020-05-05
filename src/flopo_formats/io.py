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

# The following layers are only annotated on single-token basis.
# They are thus not stored as spans, but as token propertes.
WEBANNO_SINGLE_TOKEN_LAYERS = \
    { 'Lemma', 'POS', 'Dependency', 'MorphologicalFeatures' }

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
                Annotation(
                    sp['start_sen'], sp['start_tok'], sp['end_sen'],
                    sp['end_tok'], sp['values']))
        self.last_span[layer] = \
            { 'id' : None, 'start_sen' : None, 'start_tok' : None,
              'end_sen': None, 'end_tok': None, 'values' : None }

    def _process_token_annotation(self, layer, token, values, span_ids):
        span_ids_list = list(span_ids.values())
        span_id = span_ids_list[0]
        if not all(x == span_id or x is None for x in span_ids_list):
            raise Exception(\
                'Differing span IDs in a multi-token annotation: {}'\
                .format(span_ids_list))
        if layer in WEBANNO_SINGLE_TOKEN_LAYERS:
            token.annotations[layer] = values
        # if no span ID -> single-token annotation or no annotation
        # (if there was as span ID on the previous token, it ends there)
        elif span_id is None:
            self._finalize_last_span(layer)
            # only add a single-token span if the values are not None
            # (which indicates that there is no annotation)
            if not all(x is None for x in values.values()):
                self.annotations[layer].append(
                    Annotation(self.sen_id, token.tok_id, self.sen_id, token.tok_id, values))
        # span ID differing from the previous token
        # -> the span marked on the previous token ends there,
        #    a new span starts here
        elif self.last_span[layer]['id'] != span_id:
            self._finalize_last_span(layer)
            self.last_span[layer]['id'] = span_id
            self.last_span[layer]['start_sen'] = self.sen_id
            self.last_span[layer]['start_tok'] = token.tok_id
            self.last_span[layer]['end_sen'] = self.sen_id
            self.last_span[layer]['end_tok'] = token.tok_id
            self.last_span[layer]['values'] = values
        # span ID same as on the previous token and the values match
        # -> the current token continues the existing span
        # FIXME this condition is too complicated, rewrite
        elif self.last_span[layer]['id'] == span_id \
                and (self.last_span[layer]['end_tok']+1 == token.tok_id \
                     or (self.last_span[layer]['end_sen']+1 == self.sen_id \
                         and token.tok_id == 1)) \
                and self.last_span[layer]['values'] == values:
            self.last_span[layer]['end_sen'] = self.sen_id
            self.last_span[layer]['end_tok'] = token.tok_id
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
        self.sentences.append(Sentence(self.tokens))
        self.tokens = []
        self.sen_id += 1

    def read(self, fp):
        self.schema = self._read_header(fp)
        self.annotations = \
            { layer: [] for layer, features in self.schema \
                        if layer not in WEBANNO_SINGLE_TOKEN_LAYERS}
        self.last_span = { layer: { 'id' : None, 'start' : None,
                                    'end' : None, 'values' : None } \
                           for layer, features in self.schema \
                           if layer not in WEBANNO_SINGLE_TOKEN_LAYERS }
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
                    self._process_token_annotation(layer, t, values, span_ids)
        for layer, features in self.schema:
            if layer not in WEBANNO_SINGLE_TOKEN_LAYERS:
                self._finalize_last_span(layer)
        self._finalize_sentence()
        return Document(self.schema, self.sentences, self.annotations)


def write_webanno_tsv(document, fp):

    def _write_file_header():
        fp.write('#FORMAT=WebAnno TSV 3.2\n')
        for layer, features in document.schema:
            fp.write('#'+WEBANNO_LAYERS[layer]+'|'+'|'.join(
                [(WEBANNO_FEATURES[f] if f in WEBANNO_FEATURES else f) \
                 for f in features])+'\n')
        fp.write('\n')

    def _write_sentence_header(sentence):
        fp.write('\n')
        fp.write('#Text={}\n'.format(str(sentence).replace('\\', '\\\\')))

    def _create_empty_columns():
        result = {}
        for layer, features in document.schema:
            for f in features:
                key = layer+'.'+f
                result[key] = []
                for s in document.sentences:
                    result[key].append(['_'] * len(s))
        return result

    def _format_value(value, feature, s_id, t_id, span_id):
        result = _webanno_escape(str(value)) \
                 if value != '' else '*'
        # for Dependency layer: if the token is a root, let it
        # point to itself (0 is not acceptable in WebAnno)
        if feature == 'head':
            if result == '0':
                result = t_id
            result = '{}-{}'.format(s_id, result)
        # exception rule: if feature is "author" and the result is
        # empty, this fact is marked by "_" instead of "*"
        if feature == 'author' and result == '*':
            result = '_'
        # for some weird reason, the annotations pointing to
        # another token (like "head") must not contain a span ID
        # (is this a WebAnno bug?)
        if span_id is not None and feature != 'authorHead':
            result += '[{}]'.format(span_id)
        return result

    def _insert_annotation(a, layer, span_id, columns):
        for f in a:
            key = layer+'.'+f
            # FIXME it is not necessary to pass sentence and token ID here
            value = _format_value(a[f], f, a.start_sen, a.start_tok, span_id)
            i, j = a.start_sen-1, a.start_tok-1
            while i <= a.end_sen-1 and (i < a.end_sen-1 or j <= a.end_tok-1):
                columns[key][i][j] = value
                j += 1
                if j >= len(columns[key][i]):
                    i += 1
                    j = 0

    def _format_token(i, j, t, columns):
        return ['{}-{}'.format(i+1, t.tok_id),
                '{}-{}'.format(t.start_idx, t.end_idx),
                t.string] + \
                [columns[layer+'.'+f][i][j] \
                    for layer, features in document.schema \
                    for f in features]

    last_span_id = 1
    _write_file_header()
    columns = _create_empty_columns()
    # fill the columns with span feature values
    for layer, annotations in document.annotations.items():
        for a in annotations:
            span_id = None
            # only multi-token spans have IDs
            if (a.end_sen, a.end_tok) > (a.start_sen, a.start_tok):
                span_id = last_span_id
                last_span_id += 1
            _insert_annotation(a, layer, span_id, columns)
    for i, s in enumerate(document.sentences):
        _write_sentence_header(s)
        # fill the columns with single-token annotations
        # FIXME rewrite in a more readable way
        for j, t in enumerate(s.tokens):
            for layer in WEBANNO_SINGLE_TOKEN_LAYERS:
                if layer in t.annotations:
                    for f, val in t.annotations[layer].items():
                        if val is not None:
                            columns[layer+'.'+f][i][j] = \
                                _format_value(val, f, i+1, j+1, None)
        # write the tokens
        for j, t in enumerate(s.tokens):
            fp.write('\t'.join(_format_token(i, j, t, columns))+'\t\n')


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


def _prolog_escape(string):
    return string.replace('"', '""').replace('\\', '\\\\')


def write_prolog(document, fp):

    def _arg_to_str(arg):
        if isinstance(arg, tuple):
            return '-'.join(map(str, arg))
        elif isinstance(arg, int):
            return str(arg)
        elif isinstance(arg, str):
            return arg

    def _quote(arg):
        return '"{}"'.format(arg)

    results = []
    for s_id, s in enumerate(document.sentences, 1):
        for t_id, t in enumerate(s.tokens, 1):
            tok = (s_id, t_id)
            results.append(('token', tok, _quote(_prolog_escape(t.string))))
            lemma = t['Lemma']['value']
            results.append(('lemma', tok, _quote(_prolog_escape(lemma))))
            results.append(('upos', tok, t['POS']['coarseValue'].lower()))
            d = t['Dependency']
            results.append(('head', tok, (s_id, d['head'])))
            results.append(('deprel', tok, d['DependencyType']))
            if 'MorphologicalFeatures' in t.annotations:
                for key, val in t['MorphologicalFeatures'].items():
                    if val:
                        results.append(('feats', tok,
                                        '{}({})'.format(key, val)))
        results.append(('eos', (s_id, len(s.tokens))))
    if 'QuotedSpan' in document.annotations \
            and document.annotations['QuotedSpan']:
        for a in document.annotations['QuotedSpan']:
            results.append(\
                ('quoted_span',
                 (a.start_sen, a.start_tok),
                 (a.end_sen, a.end_tok)))
    else:
        fp.write('quoted_span(_, _) :- fail.\n')
    if 'NamedEntity' in document.annotations \
            and document.annotations['NamedEntity']:
        for a in document.annotations['NamedEntity']:
            results.append(\
                ('named_entity',
                 (a.start_sen, a.start_tok),
                 (a.end_sen, a.end_tok),
                 a['value'].lower()))
    else:
        fp.write('named_entity(_, _, _) :- fail.\n')
    results.sort()
    for r in results:
        fp.write('{}({}).\n'.format(r[0], ', '.join(map(_arg_to_str, r[1:]))))


def save_prolog(document, filename):
    with open(filename, 'w+') as fp:
        write_prolog(document, fp)

