class Token:
    def __init__(self, tok_id, start_idx, end_idx, string, space_after=' '):
        self.tok_id = int(tok_id)
        self.start_idx = int(start_idx)
        self.end_idx = int(end_idx)
        self.string = string
        self.space_after = space_after


class Sentence:
    def __init__(self, tokens, spans=None):
        self.tokens = tokens
        self.spans = spans if spans is not None else {}

    def __len__(self):
        return len(self.tokens)


class Document:
    def __init__(self, schema, sentences):
        self.schema = schema.copy() if schema else []
        self.sentences = sentences


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


