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

