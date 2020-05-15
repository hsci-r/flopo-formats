import io
import unittest

from flopo_formats.data import Corpus
from flopo_formats.io.conll import CoNLLCorpusReader


class CoNLLCorpusReaderTest(unittest.TestCase):
    TEST_DOC = '''# 2000002814513.txt
# newdoc
# newpar
# sent_id = 1
# text = Viroon tulossa miehinen oikeiston ja demarien hallitus
1	Viroon	Viro	PROPN	N	Case=Ill|Number=Sing	2	obl	_	_
2	tulossa	tulo	NOUN	N	Case=Ine|Number=Sing	0	root	_	_
3	miehinen	miehinen	ADJ	A	Case=Nom|Degree=Pos|Derivation=Inen|Number=Sing	7	amod	_	_
4	oikeiston	oikeisto	NOUN	N	Case=Gen|Number=Sing	7	nmod:poss	_	_
5	ja	ja	CCONJ	C	_	6	cc	_	_
6	demarien	demari	NOUN	N	Case=Gen|Number=Plur	4	conj	_	_
7	hallitus	hallitus	NOUN	N	Case=Nom|Number=Sing	2	nsubj:cop	_	SpacesAfter=\\n\\n

# newpar
# sent_id = 2
# text = Tallinna.
1	Tallinna	Tallinna	PROPN	N	Case=Nom|Number=Sing	0	root	_	SpaceAfter=No
2	.	.	PUNCT	Punct	_	1	punct	_	_

# sent_id = 3
# text = Viron pääministeri Taavi Rõivas on yli kuukauden väännön päätteeksi saamassa kokoon kahden oikeistopuolueen ja sosiaalidemokraattien hallituksen.
1	Viron	Viro	PROPN	N	Case=Gen|Number=Sing	2	nmod:poss	_	_
2	pääministeri	pää#ministeri	NOUN	N	Case=Nom|Number=Sing	3	compound:nn	_	_
3	Taavi	Taavi	PROPN	N	Case=Nom|Number=Sing	10	nsubj	_	_
4	Rõivas	Rõivas	PROPN	N	Case=Nom|Number=Sing	3	flat:name	_	_
5	on	olla	AUX	V	Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin|Voice=Act	10	aux	_	_
6	yli	yli	ADV	Adv	_	7	advmod	_	_
7	kuukauden	kuu#kausi	NOUN	N	Case=Gen|Number=Sing	8	nmod:poss	_	_
8	väännön	vääntö	NOUN	N	Case=Gen|Number=Sing	9	nmod:poss	_	_
9	päätteeksi	pääte	NOUN	N	Case=Tra|Number=Sing	10	obl	_	_
10	saamassa	saada	VERB	V	Case=Ine|InfForm=3|Number=Sing|VerbForm=Inf|Voice=Act	0	root	_	_
11	kokoon	kokoon	NOUN	Adv	_	10	obl	_	_
12	kahden	kaksi	NUM	Num	Case=Gen|Number=Sing|NumType=Card	13	nummod	_	_
13	oikeistopuolueen	oikeisto#puolue	NOUN	N	Case=Gen|Number=Sing	10	obj	_	_
14	ja	ja	CCONJ	C	_	16	cc	_	_
15	sosiaalidemokraattien	sosiaali#demokraatti	NOUN	N	Case=Gen|Number=Plur	16	nmod:poss	_	_
16	hallituksen	hallitus	NOUN	N	Case=Gen|Number=Sing	13	conj	_	SpaceAfter=No
17	.	.	PUNCT	Punct	_	10	punct	_	SpacesAfter=\\n\\n

# 2000002819037.txt
# newdoc
# newpar
# sent_id = 1
# text = Muuttolinnut tulevat - HS listasi maan parhaat linturetkikohteet
1	Muuttolinnut	muutto#lintu	NOUN	N	Case=Nom|Number=Plur	2	nsubj	_	_
2	tulevat	tulla	VERB	V	Mood=Ind|Number=Plur|Person=3|Tense=Pres|VerbForm=Fin|Voice=Act	0	root	_	_
3	-	-	PUNCT	Punct	_	2	punct	_	_
4	HS	HS	NOUN	N	Abbr=Yes|Case=Nom|Number=Sing	5	nsubj	_	_
5	listasi	listata	VERB	V	Mood=Ind|Number=Sing|Person=3|Tense=Past|VerbForm=Fin|Voice=Act	2	parataxis	_	_
6	maan	maa	NOUN	N	Case=Gen|Number=Sing	7	nmod:poss	_	_
7	parhaat	hyvä	ADJ	A	Case=Nom|Degree=Sup|Number=Plur	8	amod	_	_
8	linturetkikohteet	lintu#retki#kohde	NOUN	N	Case=Nom|Number=Plur	5	obj	_	SpacesAfter=\\n\\n

# newpar
# sent_id = 2
# text = Kaukoputkessa näkyy kaareva höyhenpiikki.
1	Kaukoputkessa	kauko#putki	NOUN	N	Case=Ine|Number=Sing	2	obl	_	SpacesBefore=\\n\\n\\n
2	näkyy	näkyä	VERB	V	Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin|Voice=Act	0	root	_	_
3	kaareva	kaareva	ADJ	A	Case=Nom|Degree=Pos|Number=Sing	4	amod	_	_
4	höyhenpiikki	höyhen#piikki	NOUN	N	Case=Nom|Number=Sing	2	nsubj	_	SpaceAfter=No
5	.	.	PUNCT	Punct	_	2	punct	_	_

# sent_id = 3
# text = Se kohoaa linnun päälaelta.
1	Se	se	PRON	Pron	Case=Nom|Number=Sing|PronType=Dem	2	nsubj	_	_
2	kohoaa	kohota	VERB	V	Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin|Voice=Act	0	root	_	_
3	linnun	lintu	NOUN	N	Case=Gen|Number=Sing	4	nmod:poss	_	_
4	päälaelta	pää#laki	NOUN	N	Case=Abl|Number=Sing	2	obl	_	SpaceAfter=No
5	.	.	PUNCT	Punct	_	2	punct	_	_
    '''

    def test_read(self):
        corpus = Corpus()
        for doc in CoNLLCorpusReader().read(io.StringIO(self.TEST_DOC)):
            corpus[doc.doc_id] = doc
        # test the number of documents and their IDs
        self.assertEqual(len(corpus), 2)
        self.assertIn('2000002814513', corpus)
        self.assertIn('2000002819037', corpus)
        # test the numbers of sentences
        self.assertEqual(len(corpus['2000002814513'].sentences), 3)
        self.assertEqual(len(corpus['2000002819037'].sentences), 3)
        # test the numbers of tokens
        self.assertEqual(
            sum(len(s) for s in corpus['2000002814513'].sentences), 26)
        self.assertEqual(
            sum(len(s) for s in corpus['2000002819037'].sentences), 18)

        ## TODO test the start and end indices of last tokens

        # 7	kuukauden	kuu#kausi	NOUN	N	Case=Gen|Number=Sing	8	nmod:poss	_	_
        self.assertDictEqual(
            { 'value' : 'kuu#kausi' },
            corpus['2000002814513'].sentences[2].tokens[6]['Lemma'])
        self.assertDictEqual(
            { 'coarseValue' : 'NOUN', 'PosValue' : 'N' },
            corpus['2000002814513'].sentences[2].tokens[6]['POS'])

