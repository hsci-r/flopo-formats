import csv
import re
import warnings

from .data import Corpus, Document, Sentence, Token

# TODO convert to a library, divide into smaller modules

WEBANNO_LAYERS = {
    'Lemma' :'T_SP=de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Lemma',
    'POS' : 'T_SP=de.tudarmstadt.ukp.dkpro.core.api.lexmorph.type.pos.POS',
    'Dependency' : 'T_RL=de.tudarmstadt.ukp.dkpro.core.api.syntax.type.dependency.Dependency',
    'Hedging' : 'T_SP=webanno.custom.Hedging',
    'Quote' : 'T_SP=webanno.custom.Quote',
    'Metaphor' : 'T_SP=webanno.custom.Metaphor',
    'Misc' : 'T_SP=webanno.custom.Misc',
    'NamedEntity' : 'T_SP=de.tudarmstadt.ukp.dkpro.core.api.ner.type.NamedEntity'
}
WEBANNO_LAYERS_INV = { val: key for key, val in WEBANNO_LAYERS.items() }

# TODO this needs to be made less hard-coded (sorry for the English, it's late...)
WEBANNO_FEATURES = {
    'head' : 'BT_de.tudarmstadt.ukp.dkpro.core.api.lexmorph.type.pos.POS',
    'type' : 'hedgingType'
}
WEBANNO_FEATURES_INV = { val: key for key, val in WEBANNO_FEATURES.items() }


HEADER_PATTERN = re.compile('^#([^|]+)\|(.*)$')
SPAN_PATTERN = re.compile('([^[]+)(\[([0-9]+)\])?')

class CoNLLCorpusReader:
    PATTERN_SPACES_AFTER = re.compile('SpacesAfter=([^|]*)')
    SCHEMA = [('Lemma', ('value',)),
              ('POS', ('coarseValue', 'PosValue')),
              ('Dependency', ('DependencyType', 'flavor', 'head'))]

    def __init__(self):
        self.doc_id = None
        self.sen_id = None
        self.sentences = []
        self.tokens = []
        self.spans = {'Lemma' : [], 'POS' : [], 'Dependency' : []}
        self.idx = 0
        self.corpus = Corpus()

    def _finalize_sentence(self, line):
        if self.tokens:
            s = Sentence(self.tokens, self.spans)
            self.sentences.append(s)
            self.tokens = []
            self.spans = {'Lemma' : [], 'POS' : [], 'Dependency' : []}
        self.sen_id = line['sentenceId'] if line is not None else None

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
        self.spans['Lemma'].append((
            t.tok_id, t.tok_id, { 'value' : line['lemma'] }))
        self.spans['POS'].append((
            t.tok_id, t.tok_id,
            { 'coarseValue' : line['upos'], 'PosValue' : line['xpos'] }))
        self.spans['Dependency'].append((
            t.tok_id, t.tok_id,
            { 'DependencyType' : line['deprel'], 'flavor' : '*',
              'head' : int(line['head']) }))

        self.idx += len(line['word']) + len(space_after)


    def read(self, filename):
        with open(filename) as fp:
            reader = csv.DictReader(fp)
            for line in reader:
                if line['articleId'] != self.doc_id:
                    self._finalize_document(line)
                elif line['sentenceId'] != self.sen_id:
                    self._finalize_sentence(line)
                self._read_token(line)
            self._finalize_document(None)
        return self.corpus


def save_webanno_tsv(document, filename):
    last_span_id = 1
    with open(filename, 'w+') as fp:
        fp.write('#FORMAT=WebAnno TSV 3.2\n')
        for layer, features in document.schema:
            fp.write('#'+WEBANNO_LAYERS[layer]+'|'+'|'.join(
                [(WEBANNO_FEATURES[f] if f in WEBANNO_FEATURES else f) \
                 for f in features])+'\n')
        fp.write('\n')
        for s_id, s in enumerate(document.sentences, 1):
            fp.write('\n')
            text = ''.join([t.string+t.space_after for t in s.tokens]).strip()
            fp.write('#Text={}\n'.format(text))
            columns = {}
            for layer, features in document.schema:
                for f in features:
                    key = layer+'.'+f
                    columns[key] = ['_'] * len(s.tokens)
            for layer, spans in s.spans.items():
                for start_idx, end_idx, features in spans:
                    for f in features:
                        key = layer+'.'+f
                        value = str(features[f])
                        if f == 'head':
                            if value == '0':
                                value = start_idx
                            value = '{}-{}'.format(s_id, value)
                        if end_idx > start_idx:
                            value += '[{}]'.format(last_span_id)
                            last_span_id += 1
                        for i in range(start_idx, end_idx+1):
                            columns[key][i-1] = value
            for i, t in enumerate(s.tokens):
                fp.write('\t'.join([
                    '{}-{}'.format(s_id, t.tok_id),
                    '{}-{}'.format(t.start_idx, t.end_idx),
                    t.string] + \
                    [columns[layer+'.'+f][i] for layer, features in document.schema for f in features])+'\t\n')


def load_webanno_tsv(filename):
    # FIXME is there an empty line at the end of the file?
    # if not, we might be losing the last sentence!

    def _finalize_last_span(layer, last_spans, spans):
        sp = last_spans[layer]
        if sp['id'] is not None:
            spans[layer].append((sp['start'], sp['end'], sp['values']))
            print(sp['start'], sp['end'], sp['values'])
        last_spans[layer] = { 'id' : None, 'start' : None, 'end' : None,
                              'values' : None }

    schema, sentences = [], []
    with open(filename) as fp:
        line = fp.readline()        # first line -- format declaration
        while line:
            line = fp.readline().strip()
            m = HEADER_PATTERN.match(line)
            if m is not None:
                schema.append((
                    WEBANNO_LAYERS_INV[m.group(1)],
                    tuple(m.group(2).split('|')) if m.group(2) else ('',)))
        #print(schema)
        line = fp.readline()
        tokens = []
        spans = { layer: [] for layer, features in schema }
        last_span = { layer: { 'id' : None, 'start' : None, 'end' : None,
                                'values' : None } \
                      for layer, features in schema }
        for line in fp:
            line = line.rstrip()
            if not line:
                # fix space after
                # TODO not quite correct
                for i, t in enumerate(tokens[1:], 1):
                    if t.start_idx == tokens[i-1].end_idx:
                        tokens[i-1].space_after = ''
                _finalize_last_span(layer, last_span, spans)
                sentences.append(Sentence(tokens, spans))
                tokens, spans = [], { layer: [] for layer, features in schema }
            elif line.startswith('#'):
                continue
            else:
                cols = line.split('\t')
                tok_id = int(cols[0].split('-')[1])
                start_idx, end_idx = cols[1].split('-')
                string = cols[2]
                # TODO space after
                t = Token(tok_id, start_idx, end_idx, string)
                tokens.append(t)
                c = 3
                for layer, features in schema:
                    values, span_ids = {}, {}
                    for f in features:
                        m = SPAN_PATTERN.match(cols[c])
                        if m is not None:
                            if m.group(2):
                                values[f], span_ids[f] = m.group(1), m.group(3)
                            else:
                                values[f], span_ids[f] = m.group(1), None
                        else:
                            raise RuntimeError('This shouldn\'t happen')
                        c += 1
                    # add span (TODO refactor):
                    # - add as a single-span annotation if no span ID
                    # - create a new multi-token span if there is no current
                    # - add to current multi-token span if conditions satisfied
                    #   - span_id 
                    #   - feature values match
                    span_ids_list = list(span_ids.values())
                    span_id = span_ids_list[0]
                    if not all(x == span_id for x in span_ids_list):
                        raise Exception(\
                            'Differing span IDs in a multi-token annotation')
                    if span_id is None:
                        _finalize_last_span(layer, last_span, spans)
                        spans[layer].append((tok_id, tok_id, values))
                    elif last_span[layer]['id'] != span_id:
                        _finalize_last_span(layer, last_span, spans)
                        last_span[layer]['id'] = span_id
                        last_span[layer]['start'] = tok_id
                        last_span[layer]['end'] = tok_id
                        last_span[layer]['values'] = values
                    elif last_span[layer]['id'] == span_id \
                            and last_span[layer]['end']+1 == tok_id \
                            and last_span[layer]['values'] == values:
                        last_span[layer]['end'] = tok_id
                    else:
                        raise RuntimeError('This shouldn\'t happen')
    return Document(schema, sentences)


def read_conll(filename):
    return CoNLLCorpusReader().read(filename)


EXCLUDE_CSV_KEYS = { 'articleId', 'paragraphId', 'sentenceId', 'wordId',
                     'startWordId', 'endWordId' }


def read_annotation_from_csv(corpus, filename, annotation_name):
    with open(filename) as fp:
        reader = csv.DictReader(fp)
        keys = [k for k in reader.fieldnames if k not in EXCLUDE_CSV_KEYS]
        layer = (annotation_name,
                 tuple(keys) if keys else ('',))
        for doc_id in corpus.documents:
            corpus.documents[doc_id].schema.append(layer)
            for s in corpus.documents[doc_id].sentences:
                s.spans[layer[0]] = []
        for line in reader:
            doc_id = line['articleId']
            if doc_id not in corpus.documents:
                continue
            s_id = int(line['sentenceId'])-1
            start_w_id, end_w_id = None, None
            if 'startWordId' in line and 'endWordId' in line:
                start_w_id = int(line['startWordId'])
                end_w_id = int(line['endWordId'])
            elif 'wordId' in line:
                start_w_id = int(line['wordId'])
                end_w_id = int(line['wordId'])
            else:
                raise Exception('No word ID')
            try:
                if '' in layer[1]:
                    corpus.documents[doc_id].sentences[s_id].spans[layer[0]].append(
                        (start_w_id, end_w_id, { '' : '*' }))
                else:
                    corpus.documents[doc_id].sentences[s_id].spans[layer[0]].append(
                        (start_w_id, end_w_id, 
                         { key : line[key] for key in line \
                               if key not in EXCLUDE_CSV_KEYS }))
            except Exception:
                warnings.warn(
                    'articleId={} sentenceId={} '
                    'start_w_id={} end_w_id={} failed'\
                    .format(line['articleId'], line['sentenceId'],
                            start_w_id, end_w_id))

