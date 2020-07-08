import re

from flopo_formats.data import Document, Sentence, Token, Annotation

# TODO if not included here, fall back to default:
# T_SP=de.webanno.custom.LayerName
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
    'NamedEntity' : 'T_SP=de.tudarmstadt.ukp.dkpro.core.api.ner.type.NamedEntity',
    'TextReuse' : 'T_SP=webanno.custom.TextReuse'
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
        self.sentences.append(Sentence(self.tokens, sen_id=self.sen_id))
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
        return Document(None, self.schema, self.sentences, self.annotations)


def write_webanno_tsv(document, fp):

    def _write_file_header():
        fp.write('#FORMAT=WebAnno TSV 3.2\n')
        for layer, features in document.schema:
            fp.write('#'+WEBANNO_LAYERS[layer]+'|'+'|'.join(
                [(WEBANNO_FEATURES[f] if f in WEBANNO_FEATURES else f) \
                 for f in features])+'\n')
        fp.write('\n')

    def _write_sentence_header(sentence, trailing_space=False):
        fp.write('\n')
        text = str(sentence).replace('\\', '\\\\') + \
               (' ' if trailing_space else '')
        fp.write('#Text={}\n'.format(text))

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

    def _format_token(sen_id, j, t, columns):
        return ['{}-{}'.format(sen_id, t.tok_id),
                '{}-{}'.format(t.start_idx, t.end_idx),
                t.string] + \
                [columns[layer+'.'+f][sen_id-1][j] \
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
        # if not last sentence in the paragraph -- prevent WebAnno from
        # inserting a line feed after this sentence by adding a trailing space
        tsp = (i+1 < len(document.sentences) \
               and s.par_id is not None \
               and document.sentences[i+1].par_id == s.par_id)
        _write_sentence_header(s, trailing_space=tsp)
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
            fp.write('\t'.join(_format_token(s.sen_id, j, t, columns))+'\t\n')


def save_webanno_tsv(document, filename):
    with open(filename, 'w+') as fp:
        write_webanno_tsv(document, fp)


def load_webanno_tsv(filename):
    with open(filename) as fp:
        return WebAnnoTSVReader().read(fp)

