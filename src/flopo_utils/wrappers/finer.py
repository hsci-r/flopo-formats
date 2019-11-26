import re
import subprocess
import warnings


ANNOTATION_PATTERN = re.compile('<(/?)(\w+)(/?)>')


# TODO refactor
def annotate(sentences):
    '''
    Takes a list of sentences (each being a list of tokens) and runs a
    FINER subprocess. Returns a list of tuples:
    (sentence_id, tok_start_id, tok_end_id, annotation_type)
    '''
    # flatten sentences to a list of tokens
    tokens = []
    result = []
    sen_tok_ids = []
    for s_id, s in enumerate(sentences, 1):
        tokens.extend(s)
        for t_id, t in enumerate(s, 1):
            sen_tok_ids.append((s_id, t_id))
    # call FINER
    p = subprocess.Popen(
        ['finnish-nertag', '--no-tokenize'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        text=True)
    out, err = p.communicate(input='\n'.join(tokens))
    for line in out.split('\n'):
        result.append(tuple(line.split('\t')))
    p.wait()
    # convert the results in form of tuples to spans
    spans = []
    for i, ((s_id, t_id), (token, ann)) in enumerate(zip(sen_tok_ids, result)):
        if not ann:
            continue
        m = ANNOTATION_PATTERN.match(ann)
        if m is not None:
            ann_type = m.group(2)
            if m.group(3):
                spans.append((s_id, t_id, t_id, ann_type))
                start = None
            elif m.group(1) and start is not None:
                if s_id == start[0] and m.group(2) == start[2]:
                    spans.append((s_id, start[1], t_id, ann_type))
                    start = None
                else:
                    warnings.warn('Overlapping annotations')
            else:
                start = (s_id, t_id, ann_type)
    return spans

