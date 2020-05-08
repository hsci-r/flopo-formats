class Token:
    def __init__(self, tok_id, start_idx, end_idx, string, feats = '',
                 misc = '', space_after=' '):
        self.tok_id = int(tok_id)
        self.start_idx = int(start_idx)
        self.end_idx = int(end_idx)
        self.string = string
        self.space_after = space_after
        self.feats = feats
        self.misc = misc
        self.annotations = {}

    def __getitem__(self, key):
        return self.annotations[key]


class Sentence:
    def __init__(self, tokens, sen_id = None, par_id = None):
        self.sen_id = sen_id
        self.par_id = par_id
        self.tokens = tokens

    def __len__(self):
        return len(self.tokens)

    def __str__(self):
        return ''.join([t.string+t.space_after for t in self.tokens]).strip()


class Annotation:
    def __init__(self, start_sen, start_tok, end_sen, end_tok, features):
        self.start_sen = start_sen
        self.start_tok = start_tok
        self.end_sen = end_sen
        self.end_tok = end_tok
        self.features = features

    def __eq__(self, other):
        return self.start_sen == other.start_sen \
            and self.start_tok == other.start_tok \
            and self.end_sen == other.end_sen \
            and self.end_tok == other.end_tok \
            and self.features == other.features

    def __getitem__(self, key):
        return self.features[key]

    def items(self):
        return self.features.items()

    def __iter__(self):
        return self.features.__iter__()


class Document:
    def __init__(self, doc_id, schema, sentences, annotations=None):
        self.doc_id = doc_id
        self.schema = schema.copy() if schema else []
        self.sentences = sentences
        self.annotations = annotations if annotations is not None else {}


class Corpus:
    '''
    A set of Documents that might correspond to a single CSV file.

    Currently, this is just a wrapper over a dictionary of documents.
    '''

    def __init__(self):
        self.documents = {}

    def __getitem__(self, key):
        return self.documents.__getitem__(key)

    def __setitem__(self, key, val):
        self.documents[key] = val

    def items(self):
        return self.documents.items()

    def __iter__(self):
        return self.documents.__iter__()

    def __len__(self):
        return self.documents.__len__()

    def __contains__(self, key):
        return self.documents.__contains__(key)


