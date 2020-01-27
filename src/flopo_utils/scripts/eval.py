import argparse
from collections import defaultdict
import csv
from operator import itemgetter

# TODO
# - evaluate also feature values (now only span markings are evaluated)
# - cleaner code and documentation

def read_spans(fp, only_doc_ids=None):

    # TODO unify with io.read_annotation_from_csv
    def _parse_line(line):
        doc_id = line['articleId']
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
        return doc_id, s_id, start_w_id, end_w_id

    # result: dict doc_id -> s_id -> (start_w_id, end_w_id)
    result = defaultdict(lambda: defaultdict(lambda: list()))
    reader = csv.DictReader(fp)
    for line in reader:
        doc_id, s_id, start_w_id, end_w_id = _parse_line(line)
        if only_doc_ids is None or doc_id in only_doc_ids:
            result[doc_id][s_id].append((start_w_id, end_w_id))
    return result


def load_spans(filename, only_doc_ids=None):
    result = None
    with open(filename) as fp:
        result = read_spans(fp, only_doc_ids)
    return result

def load_corpus(filename, only_doc_ids=None):
    corpus = defaultdict(lambda: defaultdict(lambda: list()))
    with open(filename) as fp:
        reader = csv.DictReader(fp)
        for line in reader:
            if only_doc_ids is None or line['articleId'] in only_doc_ids:
                s_id, word = int(line['sentenceId']), line['word']
                corpus[line['articleId']][s_id].append(word)
    return corpus

def eval_sentence(input_spans, gs_spans):
    last_idx = max(map(itemgetter(1), input_spans + gs_spans))
    # TODO return a list: (token_pos, TP/FP/FN)
    results = [None] * last_idx
    for start, end in input_spans:
        for i in range(start, end+1):
            results[i-1] = 'FP'
    for start, end in gs_spans:
        for i in range(start, end+1):
            if results[i-1] is None:
                results[i-1] = 'FN'
            else:
                results[i-1] = 'TP'
    return results


def parse_arguments():
    parser = argparse.ArgumentParser(
        description='Compare annotations to a gold standard.')
    # TODO arguments
    parser.add_argument(
        '-i', '--input-file', metavar='FILE',
        help='input file')
    parser.add_argument(
        '-g', '--gs-file', metavar='FILE',
        help='gold standard file')
    parser.add_argument(
        '-c', '--corpus-file',
        help='corpus file')
    return parser.parse_args()


def main():
    args = parse_arguments()
    gs_spans = load_spans(args.gs_file)
    input_spans = load_spans(
        args.input_file,
        only_doc_ids=set(gs_spans.keys()))
    corpus = None
    if args.corpus_file is not None:
        corpus = load_corpus(args.corpus_file, only_doc_ids=set(gs_spans.keys()))
    tp, fp, fn = 0, 0, 0
    for doc_id in gs_spans:
        s_ids = sorted(set(gs_spans[doc_id].keys()) | set(input_spans[doc_id].keys()))
        for s_id in s_ids:
            results = eval_sentence(input_spans[doc_id][s_id], gs_spans[doc_id][s_id])
            if corpus:
                print('doc_id={} s_id={} TP={} FP={} FN={}'.format(
                    doc_id, s_id, results.count('TP'), results.count('FP'),
                    results.count('FN')))
                sentence = corpus[doc_id][s_id]
                s = []
                results_padded = results+[None]*(len(sentence)-len(results))
                for (token, label) in zip(sentence, results_padded):
                    if label is not None:
                        s.append('{}[{}]'.format(token, label))
                    else:
                        s.append(token)
                print(' '.join(s))
                print()
            for r in results:
                tp += int(r == 'TP')
                fp += int(r == 'FP')
                fn += int(r == 'FN')
    pre = tp / (tp + fp)
    rec = tp / (tp + fn)
    fsc = 2 / (1/pre + 1/rec) if pre*rec > 0 else 0
    print(tp, fp, fn, pre, rec, fsc)

