import argparse
import csv


def group_blocks(rows):
    cur_doc_id, cur_block_id, cur_doc, cur_block = None, None, [], []
    for r in rows:
        idx = r['articleId'].find('_')
        doc_id = r['articleId'][:idx] if idx > -1 else r['articleId']
        block_id = r['articleId'][idx+1:] if idx > -1 else None
        if doc_id != cur_doc_id:
            if cur_block:
                cur_doc.append((cur_block_id, cur_block))
            if cur_doc:
                yield (cur_doc_id, cur_doc)
            cur_doc_id = doc_id
            cur_block_id = block_id
            cur_doc = []
            cur_block = []
        elif cur_block_id != block_id:
            if cur_block:
                cur_doc.append((cur_block_id, cur_block))
            cur_block_id = block_id
            cur_block = []
        cur_block.append(r)
    if cur_block:
        cur_doc.append((cur_block_id, cur_block))
    if cur_doc:
        yield (cur_doc_id, cur_doc)


def parse_arguments():
    parser = argparse.ArgumentParser(
        description='Merge different structural parts of same articles.')
    parser.add_argument('-i', '--input-file', metavar='FILE')
    parser.add_argument('-o', '--output-file', metavar='FILE')
    parser.add_argument('-p', '--parts-file', metavar='FILE')
    return parser.parse_args()


def main():
    args = parse_arguments()
    with open(args.input_file) as infp, \
         open(args.output_file, 'w+') as outfp, \
         open(args.parts_file, 'w+') as partsfp:
        reader = csv.DictReader(infp)
        outw = csv.DictWriter(outfp, reader.fieldnames)
        outw.writeheader()
        partsw = csv.DictWriter(
            partsfp,
            ('articleId', 'blockId', 'startParagraphId', 'endParagraphId'))
        partsw.writeheader()

        for doc_id, blocks in group_blocks(reader):
            par_offset, sent_offset = 0, 0
            max_par_id, max_sent_id = 0, 0
            for block_id, rows in blocks:
                for r in rows:
                    r['articleId'] = doc_id
                    r['paragraphId'] = par_offset + int(r['paragraphId'])
                    r['sentenceId'] = sent_offset + int(r['sentenceId'])
                    outw.writerow(r)
                    max_par_id = max(max_par_id, r['paragraphId'])
                    max_sent_id = max(max_sent_id, r['sentenceId'])
                partsw.writerow({
                    'articleId': doc_id,
                    'blockId': block_id,
                    'startParagraphId': par_offset+1,
                    'endParagraphId': max_par_id,
                })
                par_offset, sent_offset = max_par_id, max_sent_id

