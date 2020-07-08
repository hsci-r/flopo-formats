import io
import unittest

from flopo_formats.data import Annotation
from flopo_formats.io.webannotsv import \
    WebAnnoTSVReader, write_webanno_tsv, _webanno_escape, _webanno_unescape
    

class WebAnnoEscapeTest(unittest.TestCase):

    UNESCAPED = \
        'This \\ is a [test] for | WebAnno | s _ reserved -> characters ;'\
        ' (all * of them)'
    ESCAPED = \
        'This \\\\ is a \\[test\\] for \\| WebAnno \\| s \\_ reserved \\->'\
        ' characters \\; (all \\* of them)'
    TEST_DOC = \
'''#FORMAT=WebAnno TSV 3.2
#T_SP=de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Lemma|value


#Text=This \\\\ is a [test] for | WebAnno | s _ reserved -> characters ; (all * of them).
1-1	0-4	This	_	
1-2	5-6	\	\\\\	
1-3	7-9	is	_	
1-4	10-11	a	_	
1-5	12-13	[	\[	
1-6	13-17	test	_	
1-7	17-18	]	\]	
1-8	19-22	for	c\\\\\\[ompl\\]ic\\|at\\_ed\\->lemma\\;LOL\\*	
1-9	23-24	|	\|	
1-10	25-32	WebAnno	_	
1-11	33-34	|	\|	
1-12	35-36	s	_	
1-13	37-38	_	\_	
1-14	39-47	reserved	_	
1-15	48-49	-	\->	
1-16	49-50	>	_	
1-17	51-61	characters	_	
1-18	62-63	;	\;	
1-19	64-65	(	_	
1-20	65-68	all	_	
1-21	69-70	*	\*	
1-22	71-73	of	_	
1-23	74-78	them	_	
1-24	78-79	)	_	
1-25	79-80	.	_	
'''

    def test_escape(self):
        escaped = _webanno_escape(self.UNESCAPED)
        self.assertEqual(escaped, self.ESCAPED)

    def test_unescape(self):
        unescaped = _webanno_unescape(self.ESCAPED)
        self.assertEqual(unescaped, self.UNESCAPED)

    def test_read_write(self):
        # read the document
        doc = WebAnnoTSVReader().read(io.StringIO(self.TEST_DOC))

        # check the (unescaped) lemma values
        toks = doc.sentences[0].tokens
        self.assertEqual(toks[1]['Lemma']['value'], '\\')
        self.assertEqual(toks[4]['Lemma']['value'], '[')
        self.assertEqual(toks[6]['Lemma']['value'], ']')
        self.assertEqual(toks[7]['Lemma']['value'], 'c\\[ompl]ic|at_ed->lemma;LOL*')
        self.assertEqual(toks[8]['Lemma']['value'], '|')
        self.assertEqual(toks[10]['Lemma']['value'], '|')
        self.assertEqual(toks[12]['Lemma']['value'], '_')
        self.assertEqual(toks[14]['Lemma']['value'], '->')
        self.assertEqual(toks[17]['Lemma']['value'], ';')
        self.assertEqual(toks[20]['Lemma']['value'], '*')

        # write and check whether it is identical to the original
        output = io.StringIO()
        write_webanno_tsv(doc, output)
        self.assertEqual(output.getvalue(), self.TEST_DOC)


class WebAnnoTSVReaderTest(unittest.TestCase):

    TEST_DOC = \
'''#FORMAT=WebAnno TSV 3.2
#T_SP=de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Lemma|value
#T_SP=de.tudarmstadt.ukp.dkpro.core.api.lexmorph.type.pos.POS|coarseValue|PosValue
#T_RL=de.tudarmstadt.ukp.dkpro.core.api.syntax.type.dependency.Dependency|DependencyType|flavor|BT_de.tudarmstadt.ukp.dkpro.core.api.lexmorph.type.pos.POS
#T_SP=de.tudarmstadt.ukp.dkpro.core.api.ner.type.NamedEntity|value
#T_SP=webanno.custom.Quote|
#T_SP=webanno.custom.Hedging|hedgingType
#T_SP=webanno.custom.Metaphor|category


#Text=Yhteiskuntasopimusta pohjustetaan elokuussa 
1-1	0-20	Yhteiskuntasopimusta	yhteis#kunta#sopimus	NOUN	N	obj	*	1-2	_	_	_	_	
1-2	21-33	pohjustetaan	pohjustaa	VERB	V	root	*	1-2	_	_	_	_	
1-3	34-43	elokuussa	elokuu	NOUN	N	obl	*	1-2	TimexTmeDat	_	_	_	

#Text=– Juha Sipilän (kesk.) hallitus haluaa työmarkkinajärjestöjen kanssa laajan yhteiskuntasopimuksen, joka vauhdittaisi talouskasvua ja työllisyyttä. 
2-1	44-45	–	–	PUNCT	Punct	punct	*	2-8	_	*[2]	_	_	
2-2	46-50	Juha	Juha	PROPN	N	nmod:poss	*	2-7	EnamexPrsHum[1]	*[2]	_	_	
2-3	51-58	Sipilän	Sipilä	PROPN	N	flat:name	*	2-2	EnamexPrsHum[1]	*[2]	_	_	
2-4	59-60	(	(	PUNCT	Punct	punct	*	2-5	_	*[2]	_	_	
2-5	60-65	kesk.	kesko	NOUN	N	appos	*	2-2	EnamexOrgPlt	*[2]	_	_	
2-6	65-66	)	)	PUNCT	Punct	punct	*	2-5	_	*[2]	_	_	
2-7	67-75	hallitus	hallitus	NOUN	N	nsubj	*	2-8	_	*[2]	_	_	
2-8	76-82	haluaa	haluta	VERB	V	root	*	2-8	_	*[2]	_	_	
2-9	83-105	työmarkkinajärjestöjen	työ#markkina#järjestö	NOUN	N	obl	*	2-8	_	*[2]	_	_	
2-10	106-112	kanssa	kanssa	ADP	Adp	case	*	2-9	_	*[2]	_	_	
2-11	113-119	laajan	laaja	ADJ	A	amod	*	2-12	_	*[2]	_	_	
2-12	120-141	yhteiskuntasopimuksen	yhteis#kunta#sopimus	NOUN	N	obj	*	2-8	_	*[2]	_	_	
2-13	141-142	,	,	PUNCT	Punct	punct	*	2-15	_	*[2]	_	_	
2-14	143-147	joka	joka	PRON	Pron	nsubj	*	2-15	_	*[2]	_	_	
2-15	148-160	vauhdittaisi	vauhdittaa	VERB	V	acl:relcl	*	2-12	_	*[2]	_	extension1	
2-16	161-173	talouskasvua	talous#kasvu	NOUN	N	obj	*	2-15	_	*[2]	_	_	
2-17	174-176	ja	ja	CCONJ	C	cc	*	2-18	_	*[2]	_	_	
2-18	177-189	työllisyyttä	työllisyys	NOUN	N	conj	*	2-16	_	*[2]	_	_	
2-19	189-190	.	.	PUNCT	Punct	punct	*	2-8	_	*[2]	_	_	

#Text=– Hallitus tekee torstaina työmarkkinajärjestöille esityksen toimista, joihin kuuluu yksikkötyökustannusten alentaminen vähintään 5 prosentilla ja muutosturva. 
3-1	191-192	–	–	PUNCT	Punct	punct	*	3-3	_	*[3]	_	_	
3-2	193-201	Hallitus	hallitus	NOUN	N	nsubj	*	3-3	_	*[3]	_	_	
3-3	202-207	tekee	tehdä	VERB	V	root	*	3-3	_	*[3]	_	_	
3-4	208-217	torstaina	torstai	NOUN	N	obl	*	3-3	_	*[3]	_	_	
3-5	218-241	työmarkkinajärjestöille	työ#markkina#järjestö	NOUN	N	obl	*	3-3	_	*[3]	_	_	
3-6	242-251	esityksen	esitys	NOUN	N	obj	*	3-3	_	*[3]	_	_	
3-7	252-260	toimista	toimi	NOUN	N	nmod	*	3-6	_	*[3]	_	seed	
3-8	260-261	,	,	PUNCT	Punct	punct	*	3-10	_	*[3]	_	_	
3-9	262-268	joihin	joka	PRON	Pron	obl	*	3-10	_	*[3]	_	_	
3-10	269-275	kuuluu	kuulua	VERB	V	acl:relcl	*	3-7	_	*[3]	_	_	
3-11	276-298	yksikkötyökustannusten	yksikkö#työ#kustannus	NOUN	N	nmod:gobj	*	3-12	_	*[3]	_	_	
3-12	299-310	alentaminen	alentaminen	NOUN	N	nsubj	*	3-10	_	*[3]	_	extension1	
3-13	311-320	vähintään	vähintään	ADV	Adv	advmod	*	3-14	_	*[3]	_	_	
3-14	321-322	5	5	NUM	Num	nummod	*	3-15	_	*[3]	_	_	
3-15	323-334	prosentilla	prosentti	NOUN	N	nmod	*	3-12	_	*[3]	_	_	
3-16	335-337	ja	ja	CCONJ	C	cc	*	3-17	_	*[3]	_	_	
3-17	338-349	muutosturva	muutos#turva	NOUN	N	conj	*	3-12	_	*[3]	_	_	
3-18	349-350	.	.	PUNCT	Punct	punct	*	3-3	_	*[3]	_	_	

#Text=– Hallitus toivoo työmarkkinajärjestöjen sitoutuvan sopimukseen 21. elokuuta mennessä.
4-1	351-352	–	–	PUNCT	Punct	punct	*	4-3	_	*[5]	_	_	
4-2	353-361	Hallitus	hallitus	NOUN	N	nsubj	*	4-3	_	*[5]	_	_	
4-3	362-368	toivoo	toivoa	VERB	V	root	*	4-3	_	*[5]	P	seed	
4-4	369-391	työmarkkinajärjestöjen	työ#markkina#järjestö	NOUN	N	nsubj	*	4-5	_	*[5]	_	_	
4-5	392-402	sitoutuvan	sitoutua	VERB	V	xcomp:ds	*	4-3	_	*[5]	_	_	
4-6	403-414	sopimukseen	sopimus	NOUN	N	obl	*	4-5	_	*[5]	_	_	
4-7	415-418	21.	21.	ADJ	Num	obl	*	4-5	TimexTmeDat[4]	*[5]	_	_	
4-8	419-427	elokuuta	elokuu	NOUN	N	flat	*	4-7	TimexTmeDat[4]	*[5]	_	_	
4-9	428-436	mennessä	mennessä	ADP	Adp	case	*	4-7	_	*[5]	_	_	
4-10	436-437	.	.	PUNCT	Punct	punct	*	4-3	_	*[5]	_	_	
'''

    def test_read(self):
        doc = WebAnnoTSVReader().read(io.StringIO(self.TEST_DOC))
        # test the document structure
        self.assertEqual(len(doc.sentences), 4)
        self.assertEqual(len(doc.sentences[0]), 3)
        self.assertEqual(len(doc.sentences[1]), 19)
        self.assertEqual(len(doc.sentences[2]), 18)
        self.assertEqual(len(doc.sentences[3]), 10)
        # test the annotations
        #   NamedEntity
        self.assertEqual(len(doc.annotations['NamedEntity']), 4)
        self.assertIn(
            Annotation(1, 3, 1, 3, { 'value': 'TimexTmeDat' }),
            doc.annotations['NamedEntity'])
        self.assertIn(
            Annotation(2, 2, 2, 3, { 'value': 'EnamexPrsHum' }),
            doc.annotations['NamedEntity'])
        self.assertIn(
            Annotation(2, 5, 2, 5, { 'value': 'EnamexOrgPlt' }),
            doc.annotations['NamedEntity'])
        self.assertIn(
            Annotation(4, 7, 4, 8, { 'value': 'TimexTmeDat' }),
            doc.annotations['NamedEntity'])
        #   Quote
        self.assertEqual(len(doc.annotations['Quote']), 3)
        self.assertIn(
            Annotation(2, 1, 2, 19, {'' : ''}),
            doc.annotations['Quote'])
        self.assertIn(
            Annotation(3, 1, 3, 18, {'' : ''}),
            doc.annotations['Quote'])
        self.assertIn(
            Annotation(4, 1, 4, 10, {'' : ''}),
            doc.annotations['Quote'])
        #   Metaphor
        self.assertEqual(len(doc.annotations['Metaphor']), 4)
        self.assertIn(
            Annotation(2, 15, 2, 15, { 'category': 'extension1' }),
            doc.annotations['Metaphor'])
        self.assertIn(
            Annotation(3, 7, 3, 7, { 'category': 'seed' }),
            doc.annotations['Metaphor'])
        self.assertIn(
            Annotation(3, 12, 3, 12, { 'category': 'extension1' }),
            doc.annotations['Metaphor'])
        self.assertIn(
            Annotation(4, 3, 4, 3, { 'category': 'seed' }),
            doc.annotations['Metaphor'])
        #   Hedging
        self.assertEqual(len(doc.annotations['Hedging']), 1)
        self.assertIn(
            Annotation(4, 3, 4, 3, { 'type': 'P' }),
            doc.annotations['Hedging'])
        # check whether detokenized sentences are equal to the Text headers
        lines = self.TEST_DOC.split('\n')
        self.assertEqual('#Text=' + str(doc.sentences[0]) + ' ', lines[10])
        self.assertEqual('#Text=' + str(doc.sentences[1]) + ' ', lines[15])
        self.assertEqual('#Text=' + str(doc.sentences[2]) + ' ', lines[36])
        self.assertEqual('#Text=' + str(doc.sentences[3]), lines[56])

class WebAnnoTSVReadWriteTest(unittest.TestCase):

    TEST_DOC = \
'''#FORMAT=WebAnno TSV 3.2
#T_SP=de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Lemma|value
#T_SP=de.tudarmstadt.ukp.dkpro.core.api.lexmorph.type.pos.POS|coarseValue|PosValue
#T_RL=de.tudarmstadt.ukp.dkpro.core.api.syntax.type.dependency.Dependency|DependencyType|flavor|BT_de.tudarmstadt.ukp.dkpro.core.api.lexmorph.type.pos.POS


#Text=Uusi suurjärjestö hahmottuu työmarkkinamyräkästä huolimatta 
1-1	0-4	Uusi	uusi	ADJ	A	amod	*	1-2	
1-2	5-17	suurjärjestö	suur#järjestö	NOUN	N	nsubj	*	1-3	
1-3	18-27	hahmottuu	hahmottua	VERB	V	root	*	1-3	
1-4	28-48	työmarkkinamyräkästä	työ#markkina#myräkkä	NOUN	N	obl	*	1-3	
1-5	49-59	huolimatta	huolimatta	ADP	Adp	case	*	1-4	

#Text=## SAK ja STTK: Suurjärjestön tarve on vain korostunut 
2-1	60-62	##	##	SYM	Punct	punct	*	2-2	
2-2	63-66	SAK	SAK	NOUN	N	root	*	2-2	
2-3	67-69	ja	ja	CCONJ	C	cc	*	2-4	
2-4	70-74	STTK	STTK	PROPN	N	conj	*	2-2	
2-5	74-75	:	:	PUNCT	Punct	punct	*	2-2	
2-6	76-89	Suurjärjestön	suur#järjestö	NOUN	N	nmod:poss	*	2-7	
2-7	90-95	tarve	tarve	NOUN	N	nsubj	*	2-10	
2-8	96-98	on	olla	AUX	V	aux	*	2-10	
2-9	99-103	vain	vain	ADV	Adv	advmod	*	2-10	
2-10	104-114	korostunut	korostua	VERB	V	parataxis	*	2-2	

#Text=Uuden suuren palkansaajajärjestön suunnittelu etenee suunnitelmien mukaan syksyn työmarkkinamyllerryksestä huolimatta. 
3-1	115-120	Uuden	uusi	ADJ	A	amod	*	3-3	
3-2	121-127	suuren	suuri	ADJ	A	amod	*	3-3	
3-3	128-148	palkansaajajärjestön	palkan#saaja#järjestö	NOUN	N	nmod:gobj	*	3-4	
3-4	149-160	suunnittelu	suunnittelu	NOUN	N	nsubj	*	3-5	
3-5	161-167	etenee	edetä	VERB	V	root	*	3-5	
3-6	168-181	suunnitelmien	suunnitelma	NOUN	N	obl	*	3-5	
3-7	182-188	mukaan	mukaan	ADP	Adp	case	*	3-6	
3-8	189-195	syksyn	syksy	NOUN	N	nmod:poss	*	3-9	
3-9	196-221	työmarkkinamyllerryksestä	työ#markkina#myllerrys	NOUN	N	obl	*	3-5	
3-10	222-232	huolimatta	huolimatta	ADP	Adp	case	*	3-9	
3-11	232-233	.	.	PUNCT	Punct	punct	*	3-5	

#Text=Reagointi hallituksen hankkeisiin on nostanut esiin näkemyseroja palkansaajajärjestöjen välillä etenkin suhtautumisessa yhteiskuntasopimuksen neuvotteluun.
4-1	234-243	Reagointi	reagointi	NOUN	N	nsubj	*	4-5	
4-2	244-255	hallituksen	hallitus	NOUN	N	nmod:poss	*	4-3	
4-3	256-267	hankkeisiin	hanke	NOUN	N	nmod	*	4-1	
4-4	268-270	on	olla	AUX	V	aux	*	4-5	
4-5	271-279	nostanut	nostaa	VERB	V	root	*	4-5	
4-6	280-285	esiin	esiin	ADV	Adv	advmod	*	4-5	
4-7	286-298	näkemyseroja	näkemy#sero	NOUN	N	obj	*	4-5	
4-8	299-321	palkansaajajärjestöjen	palkan#saaja#järjestö	NOUN	N	nmod	*	4-11	
4-9	322-329	välillä	välillä	ADP	Adp	case	*	4-8	
4-10	330-337	etenkin	etenkin	ADV	Adv	advmod	*	4-11	
4-11	338-353	suhtautumisessa	suhtautuminen	NOUN	N	nmod	*	4-7	
4-12	354-375	yhteiskuntasopimuksen	yhteis#kunta#sopimus	NOUN	N	nmod:gobj	*	4-13	
4-13	376-388	neuvotteluun	neuvottelu	NOUN	N	nmod	*	4-11	
4-14	388-389	.	.	PUNCT	Punct	punct	*	4-5	
'''

    def test_read_write(self):
        doc = WebAnnoTSVReader().read(io.StringIO(self.TEST_DOC))
        output = io.StringIO()
        write_webanno_tsv(doc, output)
        self.maxDiff = None
        self.assertEqual(output.getvalue(), self.TEST_DOC)

