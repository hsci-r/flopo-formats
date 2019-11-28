import logging
from operator import itemgetter
import re
import subprocess


ANNOTATION_PATTERN = re.compile('<(/?)(\w+)(/?)>')


def annotate(sentences):
    '''
    Takes a list of sentences (each being a list of tokens) and runs a
    FINER subprocess. Returns a list of tuples:
    (sentence_id, tok_start_id, tok_end_id, label)
    '''

    def _flatten_sentences(sentences):
        '''
        Flatten a list of sentences to a list of tuples:
        (sentence_id, token_id, token)
        '''
        return [(s_id, t_id, token) \
                for s_id, sen in enumerate(sentences, 1) \
                for t_id, token in enumerate(sen, 1)]

    def _finer_annotate(tokens):
        '''
        Annotate a list of tokens with FINER. Return a list of pairs:
        (token, finer_tag)
        '''
        p = subprocess.Popen(
            ['finnish-nertag', '--no-tokenize'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            text=True)
        out, err = p.communicate(input='\n'.join(tokens))
        result = []
        for i, line in enumerate(out.split('\n'), 1):
            if not line.strip():
                continue
            try:
                token, tag = tuple(line.split('\t'))
                result.append((token, tag))
            except ValueError:
                logging.warning(\
                    'FINER output is not in two-column format in line {}: {}'\
                    .format(i, line))
        p.wait()
        return result

    def _process_single_token_tag(label, s_id, t_id, start):
        err_msg = \
            None if start is None \
            else 'Nested or overlapping annotation'
        span = (s_id, t_id, t_id, label)
        return span, None, err_msg

    def _process_opening_tag(label, s_id, t_id, start):
        err_msg = \
            None if start is None \
            else 'Nested or overlapping annotation'
        start = (s_id, t_id, label)
        return None, start, err_msg

    def _process_closing_tag(label, s_id, t_id, start):
        span, err_msg = None, None
        if start is not None \
                and s_id == start[0] \
                and label == start[2]:
            span = (s_id, start[1], t_id, label)
            start = None
        else:
            if start is None:
                err_msg = 'Unmatched closing tag'
            elif s_id != start[0]:
                err_msg = 'Annotation crosses sentence boundary'
            elif label != start[2]:
                err_msg = 'Overlapping annotations or unmatched closing tag'
            else:
                # This may logically never occur, but just in case...
                err_msg = 'Unknown error in processing NER output'
        return span, None, err_msg

    def _process_tag(tag, s_id, t_id, start):
        m = ANNOTATION_PATTERN.match(tag)
        if m is not None:
            label = m.group(2)
            if m.group(3):        # <Annotation/>
                return _process_single_token_tag(label, s_id, t_id, start)
            elif m.group(1):      # </Annotation>
                return _process_closing_tag(label, s_id, t_id, start)
            else:                 # <Annotation>
                return _process_opening_tag(label, s_id, t_id, start)
        else:
            return None, start, 'Ignoring invalid tag'

    tokens = _flatten_sentences(sentences)
    finer_out = _finer_annotate(map(itemgetter(2), tokens))
    spans = []
    start = None
    for i, ((s_id, t_id, t1), (t2, tag)) in enumerate(zip(tokens, finer_out)):
        if t1 != t2:
            logging.error(
                'Token mismatch in FINER input/output: sentence={}, token={}.'\
                ' Further output for this document might be garbage.'\
                .format(s_id, t_id))
        if not tag: continue
        span, start, err_msg = _process_tag(tag, s_id, t_id, start)
        if span is not None:
            spans.append(span)
        if err_msg is not None:
            logging.warning('{}: sentence={}, token={}, tag={}'\
                            .format(err_msg, s_id, t_id, tag))
    return spans

