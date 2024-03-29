import argparse
from collections import defaultdict
import csv
from operator import itemgetter
import sys
import warnings

from flopo_formats.data import Annotation

# TODO
# - cleaner code

EXCLUDE_CSV_KEYS = { 'articleId', 'paragraphId', 'sentenceId', 'wordId',
                     'startWordId', 'endWordId', 'startSentenceId',
                     'endSentenceId' }

def read_annotations(fp, only_doc_ids=None):

    # TODO unify with io.read_annotation_from_csv
    def _parse_line(line, features):
        doc_id = line['articleId']
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
        a = Annotation(start_sen_id, start_w_id, end_sen_id, end_w_id, values)
        return doc_id, a

    # result: dict doc_id -> [Annotation]
    result = defaultdict(lambda: list())
    reader = csv.DictReader(fp)
    features = tuple(k for k in reader.fieldnames if k not in EXCLUDE_CSV_KEYS)
    if not features:
        features = ('',)
    for line in reader:
        doc_id, a = _parse_line(line, features)
        if only_doc_ids is None or doc_id in only_doc_ids:
            result[doc_id].append(a)
    return result, features


def load_annotations(filename, only_doc_ids=None):
    result = None
    with open(filename) as fp:
        result = read_annotations(fp, only_doc_ids)
    return result

def load_corpus(filename, only_doc_ids=None):
    corpus = defaultdict(lambda: list())
    cur_doc_id, cur_s_id, cur_sentence = None, None, None
    with open(filename) as fp:
        reader = csv.DictReader(fp)
        for line in reader:
            doc_id = line['articleId']
            if only_doc_ids is None or doc_id in only_doc_ids:
                s_id, word = int(line['sentenceId']), line['word']
                if s_id != cur_s_id:
                    if cur_s_id is not None:
                        corpus[cur_doc_id].append(cur_sentence)
                    cur_doc_id, cur_s_id, cur_sentence = doc_id, s_id, []
                cur_sentence.append(line)
        if cur_sentence:
            corpus[cur_doc_id].append(cur_sentence)
    return corpus


def unfold_annotations(doc, anns):
    '''Create a vector of per-token annotations.'''

    def _unfold_ann(results, a):
        i, j = a.start_sen-1, a.start_tok-1
        while i <= a.end_sen-1 and (i < a.end_sen-1 or j <= a.end_tok-1):
            if i < len(results) and j < len(results[i]):
                results[i][j] = a.features
            else:
                # TODO the annotations exceed sentence boundaries?
                # TODO raise an exception and print a warning higher in the code
                if i >= len(results):
                    break
            j += 1
            if j >= len(results[i]):
                i += 1
                j = 0

    results = []
    for s in doc:
        results.append([None] * len(s))
    for a in anns:
        _unfold_ann(results, a)
    return results


def compare_annotations(src_anns, tgt_anns, feature=None):

    def _get_feature_value(ann, feature):
        if ann is None:
            return None
        elif feature is None:
            return True
        else:
            return ann[feature]

    results = []
    for sen_src_ann, sen_tgt_ann in zip(src_anns, tgt_anns):
        sen_results = []
        for src_ann, tgt_ann in zip(sen_src_ann, sen_tgt_ann):
            result = {
                'srcValue': _get_feature_value(src_ann, feature),
                'tgtValue': _get_feature_value(tgt_ann, feature),
                'TP': 0, 'FP': 0, 'FN': 0
            }
            if result['srcValue'] == result['tgtValue']:
                result['TP'] = int(result['tgtValue'] is not None)
            else:
                result['FP'] = int(result['srcValue'] is not None)
                result['FN'] = int(result['tgtValue'] is not None)
            sen_results.append(result)
        results.append(sen_results)
    return results
        

def print_detailed_results(doc_id, doc, results, print_all=True):

    def _print_sentence_results(s_id, sentence, sen_results):
        print('doc_id={} s_id={} TP={} FP={} FN={}'.format(
            doc_id, s_id,
            sum(r['TP'] for r in sen_results),
            sum(r['FP'] for r in sen_results),
            sum(r['FN'] for r in sen_results)))
        string = []
        for (token, r) in zip(sentence, sen_results):
            label = '+'.join([x for x in ['TP', 'FP', 'FN'] if r[x] > 0])
            value = r['tgtValue'] if label in ('TP', 'FN') \
                    else r['srcValue'] if label == 'FP' \
                    else '{},{}'.format(r['srcValue'], r['tgtValue'])
            if label:
                string.append('{}[{},{}]'.format(token['word'], label, value))
            else:
                string.append(token['word'])
        print(' '.join(string))
        print()

    for i, s in enumerate(doc):
        if print_all or any(r['TP']+r['FP']+r['FN'] > 0 for r in results[i]):
            _print_sentence_results(i+1, s, results[i])


def print_csv_results(writer, doc_id, doc, src_ann, tgt_ann, results, \
                      features, header=False):
# FIXME adjust to the new format of the results
    if header:
        header_row = ['articleId', 'sentenceId', 'wordId', 'word', 'result']
        for f in features:
            header_row.append('src'+f[0].upper()+f[1:])
            header_row.append('tgt'+f[0].upper()+f[1:])
        writer.writerow(header_row)
    for i, (sen, sen_src_ann, sen_tgt_ann, sen_res) in \
            enumerate(zip(doc, src_ann, tgt_ann, results)):
        for j, (tok, src_ann, tgt_ann, res) in \
                enumerate(zip(sen, sen_src_ann, sen_tgt_ann, sen_res)):
            if res is not None:
                row = [doc_id, i+1, j+1, tok['word'], res]
                for f in features:
                    row.append(src_ann[f] if src_ann is not None else 'NA')
                    row.append(tgt_ann[f] if tgt_ann is not None else 'NA')
                writer.writerow(row)


def parse_arguments():
    parser = argparse.ArgumentParser(
        description='Compare annotations to a gold standard.')
    parser.add_argument(
        '-i', '--input-file', metavar='FILE',
        help='input file')
    parser.add_argument(
        '-g', '--gs-file', metavar='FILE',
        help='gold standard file')
    parser.add_argument(
        '-c', '--corpus-file',
        help='corpus file')
    parser.add_argument(
        '-f', '--feature', metavar='FEATURE',
        help='Evaluate classes separately according to the feature.')
    parser.add_argument(
        '-r', '--results-format',
        choices=['short', 'long', 'csv'], default='long')
    parser.add_argument(
        '--exclude-punct', action='store_true',
        help='Exclude punctuation marks from evaluation metrics.')
    return parser.parse_args()


def main():
    args = parse_arguments()
    gs_anns, gs_ann_feats = load_annotations(args.gs_file)
    doc_ids = set(gs_anns.keys())
    input_anns, input_ann_feats = \
        load_annotations(args.input_file, only_doc_ids=doc_ids)
    features = tuple(sorted(list(set(input_ann_feats) & set(gs_ann_feats))))
    corpus = None
    corpus = load_corpus(args.corpus_file, only_doc_ids=doc_ids)
    tp, fp, fn = defaultdict(lambda: 0), defaultdict(lambda: 0), defaultdict(lambda: 0)
    writer = csv.writer(sys.stdout, lineterminator='\n') \
             if args.results_format == 'csv' else None
    first = True
    for doc_id in sorted(doc_ids):
        doc_src_anns = unfold_annotations(corpus[doc_id], input_anns[doc_id])
        doc_tgt_anns = unfold_annotations(corpus[doc_id], gs_anns[doc_id])
        results = compare_annotations(doc_src_anns, doc_tgt_anns, feature=args.feature)
        if args.results_format == 'long':
            print_detailed_results(doc_id, corpus[doc_id], results)
        elif args.results_format == 'csv':
            print_csv_results(
                writer, doc_id, corpus[doc_id], doc_src_anns, doc_tgt_anns,
                results, features, first)
            first = False
        for i, sen_results in enumerate(results):
            for j, r in enumerate(sen_results):
                if not args.exclude_punct or corpus[doc_id][i][j]['upos'] != 'PUNCT':
                    if r['srcValue'] is not None:
                        fp[r['srcValue']] += r['FP']
                    if r['tgtValue'] is not None:
                        tp[r['tgtValue']] += r['TP']
                        fn[r['tgtValue']] += r['FN']
    if args.results_format in ['short', 'long']:
        keys = set(tp.keys()) | set(fp.keys()) | set(fn.keys())
        for key in keys:
            pre = tp[key] / (tp[key] + fp[key]) \
                  if (tp[key] + fp[key]) > 0 else 0
            rec = tp[key] / (tp[key] + fn[key]) \
                  if (tp[key] + fn[key]) > 0 else 0
            fsc = 2 / (1/pre + 1/rec) if pre*rec > 0 else 0
            print(key, tp[key], fp[key], fn[key], pre, rec, fsc)

