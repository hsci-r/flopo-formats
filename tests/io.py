import io
import unittest

from flopo_utils.data import Corpus, Annotation
from flopo_utils.io import \
    CoNLLCorpusReader, WebAnnoTSVReader, write_webanno_tsv, \
    _webanno_escape, _webanno_unescape, read_annotation_from_csv


class CoNLLCorpusReaderTest(unittest.TestCase):

    TEST_DOC = \
'''articleId,paragraphId,sentenceId,wordId,word,lemma,upos,xpos,feats,head,deprel,misc
100023169,1,1,1,Uusi,uusi,ADJ,A,Case=Nom|Degree=Pos|Number=Sing,2,amod,
100023169,1,1,2,suurjärjestö,suur#järjestö,NOUN,N,Case=Nom|Number=Sing,3,nsubj,
100023169,1,1,3,hahmottuu,hahmottua,VERB,V,Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin|Voice=Act,0,root,
100023169,1,1,4,työmarkkinamyräkästä,työ#markkina#myräkkä,NOUN,N,Case=Ela|Number=Sing,3,obl,
100023169,1,1,5,huolimatta,huolimatta,ADP,Adp,AdpType=Post,4,case,SpacesAfter=\\n\\n
100023169,2,2,1,##,##,SYM,Punct,,2,punct,
100023169,2,2,2,SAK,SAK,NOUN,N,Abbr=Yes|Case=Nom|Number=Sing,0,root,
100023169,2,2,3,ja,ja,CCONJ,C,,4,cc,
100023169,2,2,4,STTK,STTK,PROPN,N,Abbr=Yes|Case=Nom|Number=Sing,2,conj,SpaceAfter=No
100023169,2,2,5,:,:,PUNCT,Punct,,2,punct,
100023169,2,2,6,Suurjärjestön,suur#järjestö,NOUN,N,Case=Gen|Number=Sing,7,nmod:poss,
100023169,2,2,7,tarve,tarve,NOUN,N,Case=Nom|Number=Sing,10,nsubj,
100023169,2,2,8,on,olla,AUX,V,Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin|Voice=Act,10,aux,
100023169,2,2,9,vain,vain,ADV,Adv,,10,advmod,
100023169,2,2,10,korostunut,korostua,VERB,V,Case=Nom|Degree=Pos|Number=Sing|PartForm=Past|VerbForm=Part|Voice=Act,2,parataxis,SpacesAfter=\\n\\n
100023169,3,3,1,Uuden,uusi,ADJ,A,Case=Gen|Degree=Pos|Number=Sing,3,amod,
100023169,3,3,2,suuren,suuri,ADJ,A,Case=Gen|Degree=Pos|Number=Sing,3,amod,
100023169,3,3,3,palkansaajajärjestön,palkan#saaja#järjestö,NOUN,N,Case=Gen|Number=Sing,4,nmod:gobj,
100023169,3,3,4,suunnittelu,suunnittelu,NOUN,N,Case=Nom|Derivation=U|Number=Sing,5,nsubj,
100023169,3,3,5,etenee,edetä,VERB,V,Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin|Voice=Act,0,root,
100023169,3,3,6,suunnitelmien,suunnitelma,NOUN,N,Case=Gen|Number=Plur,5,obl,
100023169,3,3,7,mukaan,mukaan,ADP,Adp,AdpType=Post,6,case,
100023169,3,3,8,syksyn,syksy,NOUN,N,Case=Gen|Number=Sing,9,nmod:poss,
100023169,3,3,9,työmarkkinamyllerryksestä,työ#markkina#myllerrys,NOUN,N,Case=Ela|Number=Sing,5,obl,
100023169,3,3,10,huolimatta,huolimatta,ADP,Adp,AdpType=Post,9,case,SpaceAfter=No
100023169,3,3,11,.,.,PUNCT,Punct,,5,punct,SpacesAfter=\\n\\n
100023169,4,4,1,Reagointi,reagointi,NOUN,N,Case=Nom|Number=Sing,5,nsubj,
100023169,4,4,2,hallituksen,hallitus,NOUN,N,Case=Gen|Number=Sing,3,nmod:poss,
100023169,4,4,3,hankkeisiin,hanke,NOUN,N,Case=Ill|Number=Plur,1,nmod,
100023169,4,4,4,on,olla,AUX,V,Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin|Voice=Act,5,aux,
100023169,4,4,5,nostanut,nostaa,VERB,V,Case=Nom|Degree=Pos|Number=Sing|PartForm=Past|VerbForm=Part|Voice=Act,0,root,
100023169,4,4,6,esiin,esiin,ADV,Adv,,5,advmod,
100023169,4,4,7,näkemyseroja,näkemy#sero,NOUN,N,Case=Par|Number=Plur,5,obj,
100023169,4,4,8,palkansaajajärjestöjen,palkan#saaja#järjestö,NOUN,N,Case=Gen|Number=Plur,11,nmod,
100023169,4,4,9,välillä,välillä,ADP,Adp,AdpType=Post,8,case,
100023169,4,4,10,etenkin,etenkin,ADV,Adv,,11,advmod,
100023169,4,4,11,suhtautumisessa,suhtautuminen,NOUN,N,Case=Ine|Derivation=Minen|Number=Sing,7,nmod,
100023169,4,4,12,yhteiskuntasopimuksen,yhteis#kunta#sopimus,NOUN,N,Case=Gen|Number=Sing,13,nmod:gobj,
100023169,4,4,13,neuvotteluun,neuvottelu,NOUN,N,Case=Ill|Derivation=U|Number=Sing,11,nmod,SpaceAfter=No
100023169,4,4,14,.,.,PUNCT,Punct,,5,punct,SpacesAfter=\\n\\n
100136470,1,1,1,Postin,posti,NOUN,N,Case=Gen|Number=Sing,2,nmod:poss,
100136470,1,1,2,työriidassa,työ#riita,NOUN,N,Case=Ine|Number=Sing,3,obl,
100136470,1,1,3,pelataan,pelata,VERB,V,Mood=Ind|Tense=Pres|VerbForm=Fin|Voice=Pass,0,root,
100136470,1,1,4,kovilla,kova,ADJ,A,Case=Ade|Degree=Pos|Number=Plur,5,amod,
100136470,1,1,5,panoksilla,panos,NOUN,N,Case=Ade|Number=Plur,3,obl,
100136470,1,1,6,–,–,PUNCT,Punct,,3,punct,
100136470,1,1,7,lakko,lakko,NOUN,N,Case=Nom|Number=Sing,9,nsubj:cop,
100136470,1,1,8,yhä,yhä,ADV,Adv,,9,advmod,
100136470,1,1,9,todennäköisempi,toden#näköinen,ADJ,A,Case=Nom|Degree=Cmp|Derivation=Inen|Number=Sing,3,parataxis,SpacesAfter=\\n\\n
100136470,2,2,1,##,##,SYM,Symb,,0,root,
100136470,2,3,1,Kiista,kiista,NOUN,N,Case=Nom|Number=Sing,2,nsubj,
100136470,2,3,2,kiristää,kiristää,VERB,V,Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin|Voice=Act,0,root,
100136470,2,3,3,muutoinkin,muutoin,ADV,Adv,Clitic=Kin,2,advmod,
100136470,2,3,4,työmarkkinoiden,työ#markkinat,NOUN,N,Case=Gen|Number=Plur,5,nmod:poss,
100136470,2,3,5,tunnelmia,tunnelma,NOUN,N,Case=Par|Number=Plur,2,obj,SpacesAfter=\\n\\n
100136470,3,4,1,Postialan,posti#ala,NOUN,N,Case=Gen|Number=Sing,2,nmod:gsubj,
100136470,3,4,2,neuvottelut,neuvottelu,NOUN,N,Case=Nom|Derivation=U|Number=Plur,3,nsubj,
100136470,3,4,3,päättyivät,päättyä,VERB,V,Mood=Ind|Number=Plur|Person=3|Tense=Past|VerbForm=Fin|Voice=Act,0,root,
100136470,3,4,4,maanantaina,maanantai,NOUN,N,Case=Ess|Number=Sing,3,obl,
100136470,3,4,5,illansuussa,illan#suu,NOUN,N,Case=Ine|Number=Sing,3,obl,
100136470,3,4,6,taas,taas,ADV,Adv,,3,advmod,
100136470,3,4,7,tuloksetta,tulos,NOUN,N,Case=Abe|Number=Sing,3,obl,SpaceAfter=No
100136470,3,4,8,",",",",PUNCT,Punct,,11,punct,
100136470,3,4,9,ja,ja,CCONJ,C,,11,cc,
100136470,3,4,10,lakko,lakko,NOUN,N,Case=Nom|Number=Sing,11,nsubj,
100136470,3,4,11,näyttää,näyttää,VERB,V,Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin|Voice=Act,3,conj,
100136470,3,4,12,entistä,entinen,ADJ,A,Case=Par|Degree=Pos|Derivation=Inen|Number=Sing,13,advcl,
100136470,3,4,13,todennäköisemmältä,toden#näköinen,ADJ,A,Case=Par|Degree=Cmp|Derivation=Inen|Number=Sing,11,xcomp,SpaceAfter=No
100136470,3,4,14,.,.,PUNCT,Punct,,3,punct,
100189803,1,1,1,Alahuhta,Alahuhta,PROPN,N,Case=Nom|Number=Sing,0,root,SpaceAfter=No
100189803,1,1,2,:,:,PUNCT,Punct,,1,punct,
100189803,1,1,3,Palkankorotuskatto,palkan#korotus#katto,NOUN,N,Case=Nom|Number=Sing,1,appos,
100189803,1,1,4,jatkossa,jatko,NOUN,N,Case=Ine|Number=Sing,3,nmod,
100189803,1,1,5,vientiliitoilta,vienti#liitto,NOUN,N,Case=Abl|Number=Plur,3,nmod,SpacesAfter=\\n\\n
100189803,2,2,1,##,##,SYM,Symb,,3,nsubj,
100189803,2,2,2,EK,EK,PROPN,N,Case=Nom|Number=Sing,1,flat:name,
100189803,2,2,3,haluaa,haluta,VERB,V,Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin|Voice=Act,0,root,
100189803,2,2,4,haudata,haudata,VERB,V,InfForm=1|Number=Sing|VerbForm=Inf|Voice=Act,3,xcomp,
100189803,2,2,5,tupot,tupo,NOUN,N,Case=Nom|Number=Plur,4,obj,
100189803,2,2,6,sääntömuutoksella,sääntö#muutos,NOUN,N,Case=Ade|Number=Sing,4,obl,SpacesAfter=\\n\\n
100189803,3,3,1,Elinkeinoelämän,elin#keino#elämä,NOUN,N,Case=Gen|Number=Sing,2,nmod:poss,
100189803,3,3,2,keskusliitto,keskus#liitto,NOUN,N,Case=Nom|Number=Sing,3,nsubj,
100189803,3,3,3,haluaa,haluta,VERB,V,Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin|Voice=Act,0,root,
100189803,3,3,4,haudata,haudata,VERB,V,InfForm=1|Number=Sing|VerbForm=Inf|Voice=Act,3,xcomp,
100189803,3,3,5,keskitetyt,keskittää,VERB,V,Case=Nom|Degree=Pos|Number=Plur|PartForm=Past|VerbForm=Part|Voice=Pass,7,acl,
100189803,3,3,6,tulopoliittiset,tulo#poliittinen,ADJ,A,Case=Nom|Degree=Pos|Derivation=Inen|Number=Plur,7,amod,
100189803,3,3,7,sopimukset,sopimus,NOUN,N,Case=Nom|Number=Plur,4,obj,
100189803,3,3,8,historian,historia,NOUN,N,Case=Gen|Number=Sing,9,nmod:poss,
100189803,3,3,9,lehdille,lehti,NOUN,N,Case=All|Number=Plur,4,obl,
100189803,3,3,10,paaluttamalla,paaluttaa,VERB,V,Case=Ade|InfForm=3|Number=Sing|VerbForm=Inf|Voice=Act,4,advcl,
100189803,3,3,11,asian,asia,NOUN,N,Case=Gen|Number=Sing,10,obj,
100189803,3,3,12,sääntöihinsä,sääntö,NOUN,N,Case=Ill|Number=Plur|Person[psor]=3,10,obl,SpaceAfter=No
100189803,3,3,13,.,.,PUNCT,Punct,,3,punct,SpacesAfter=\\n\\n'''

    def test_read(self):
        corpus = CoNLLCorpusReader().read(io.StringIO(self.TEST_DOC))
        # test the number of documents and their IDs
        self.assertEqual(len(corpus), 3)
        self.assertIn('100023169', corpus)
        self.assertIn('100136470', corpus)
        self.assertIn('100189803', corpus)
        # test the numbers of sentences
        self.assertEqual(len(corpus['100023169'].sentences), 4)
        self.assertEqual(len(corpus['100136470'].sentences), 4)
        self.assertEqual(len(corpus['100189803'].sentences), 3)
        # test the numbers of tokens
        self.assertEqual(
            sum(len(s) for s in corpus['100023169'].sentences), 40)
        self.assertEqual(
            sum(len(s) for s in corpus['100136470'].sentences), 29)
        self.assertEqual(
            sum(len(s) for s in corpus['100189803'].sentences), 24)

        # TODO test the start and end indices of last tokens

        #100023169,2,2,8,on,olla,AUX,V,...
        self.assertIn(
            Annotation(2, 8, 2, 8, { 'value' : 'olla' }),
            corpus['100023169'].sentences[1].annotations['Lemma'])
        self.assertIn(
            Annotation(2, 8, 2, 8, { 'value' : 'olla' }),
            corpus['100023169'].sentences[1].annotations['Lemma'])
        self.assertIn(
            Annotation(2, 8, 2, 8, { 'coarseValue' : 'AUX', 'PosValue' : 'V' }),
            corpus['100023169'].sentences[1].annotations['POS'])


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
        anns = doc.sentences[0].annotations['Lemma']
        self.assertEqual(anns[0]['value'], '\\')
        self.assertEqual(anns[1]['value'], '[')
        self.assertEqual(anns[2]['value'], ']')
        self.assertEqual(anns[3]['value'], 'c\\[ompl]ic|at_ed->lemma;LOL*')
        self.assertEqual(anns[4]['value'], '|')
        self.assertEqual(anns[5]['value'], '|')
        self.assertEqual(anns[6]['value'], '_')
        self.assertEqual(anns[7]['value'], '->')
        self.assertEqual(anns[8]['value'], ';')
        self.assertEqual(anns[9]['value'], '*')

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
        self.assertEqual(len(doc.sentences[0].annotations['NamedEntity']), 1)
        self.assertEqual(len(doc.sentences[1].annotations['NamedEntity']), 2)
        self.assertEqual(len(doc.sentences[2].annotations['NamedEntity']), 0)
        self.assertEqual(len(doc.sentences[3].annotations['NamedEntity']), 1)
        self.assertIn(
            Annotation(1, 3, 1, 3, { 'value': 'TimexTmeDat' }),
            doc.sentences[0].annotations['NamedEntity'])
        self.assertIn(
            Annotation(2, 2, 2, 3, { 'value': 'EnamexPrsHum' }),
            doc.sentences[1].annotations['NamedEntity'])
        self.assertIn(
            Annotation(2, 5, 2, 5, { 'value': 'EnamexOrgPlt' }),
            doc.sentences[1].annotations['NamedEntity'])
        self.assertIn(
            Annotation(4, 7, 4, 8, { 'value': 'TimexTmeDat' }),
            doc.sentences[3].annotations['NamedEntity'])
        #   Quote
        self.assertEqual(len(doc.sentences[0].annotations['Quote']), 0)
        self.assertEqual(len(doc.sentences[1].annotations['Quote']), 1)
        self.assertEqual(len(doc.sentences[2].annotations['Quote']), 1)
        self.assertEqual(len(doc.sentences[3].annotations['Quote']), 1)
        self.assertIn(
            Annotation(2, 1, 2, 19, {'' : ''}),
            doc.sentences[1].annotations['Quote'])
        self.assertIn(
            Annotation(3, 1, 3, 18, {'' : ''}),
            doc.sentences[2].annotations['Quote'])
        self.assertIn(
            Annotation(4, 1, 4, 10, {'' : ''}),
            doc.sentences[3].annotations['Quote'])
        #   Metaphor
        self.assertEqual(len(doc.sentences[0].annotations['Metaphor']), 0)
        self.assertEqual(len(doc.sentences[1].annotations['Metaphor']), 1)
        self.assertEqual(len(doc.sentences[2].annotations['Metaphor']), 2)
        self.assertEqual(len(doc.sentences[3].annotations['Metaphor']), 1)
        self.assertIn(
            Annotation(2, 15, 2, 15, { 'category': 'extension1' }),
            doc.sentences[1].annotations['Metaphor'])
        self.assertIn(
            Annotation(3, 7, 3, 7, { 'category': 'seed' }),
            doc.sentences[2].annotations['Metaphor'])
        self.assertIn(
            Annotation(3, 12, 3, 12, { 'category': 'extension1' }),
            doc.sentences[2].annotations['Metaphor'])
        self.assertIn(
            Annotation(4, 3, 4, 3, { 'category': 'seed' }),
            doc.sentences[3].annotations['Metaphor'])
        #   Hedging
        self.assertEqual(len(doc.sentences[0].annotations['Hedging']), 0)
        self.assertEqual(len(doc.sentences[1].annotations['Hedging']), 0)
        self.assertEqual(len(doc.sentences[2].annotations['Hedging']), 0)
        self.assertEqual(len(doc.sentences[3].annotations['Hedging']), 1)
        self.assertIn(
            Annotation(4, 3, 4, 3, { 'type': 'P' }),
            doc.sentences[3].annotations['Hedging'])
        # check whether detokenized sentences are equal to the Text headers
        lines = self.TEST_DOC.split('\n')
        self.assertEqual('#Text=' + str(doc.sentences[0]), lines[10])
        self.assertEqual('#Text=' + str(doc.sentences[1]), lines[15])
        self.assertEqual('#Text=' + str(doc.sentences[2]), lines[36])
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
        self.assertEqual(output.getvalue(), self.TEST_DOC)
    

class ReadAnnotationTest(unittest.TestCase):
    TEST_DOC = \
'''#FORMAT=WebAnno TSV 3.2
#T_SP=de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Lemma|value
#T_SP=de.tudarmstadt.ukp.dkpro.core.api.lexmorph.type.pos.POS|coarseValue|PosValue
#T_RL=de.tudarmstadt.ukp.dkpro.core.api.syntax.type.dependency.Dependency|DependencyType|flavor|BT_de.tudarmstadt.ukp.dkpro.core.api.lexmorph.type.pos.POS


#Text=Yhteiskuntasopimusta pohjustetaan elokuussa
1-1	0-20	Yhteiskuntasopimusta	yhteis#kunta#sopimus	NOUN	N	obj	*	1-2	
1-2	21-33	pohjustetaan	pohjustaa	VERB	V	root	*	1-2	
1-3	34-43	elokuussa	elokuu	NOUN	N	obl	*	1-2	

#Text=– Juha Sipilän (kesk.) hallitus haluaa työmarkkinajärjestöjen kanssa laajan yhteiskuntasopimuksen, joka vauhdittaisi talouskasvua ja työllisyyttä.
2-1	44-45	–	–	PUNCT	Punct	punct	*	2-8	
2-2	46-50	Juha	Juha	PROPN	N	nmod:poss	*	2-7	
2-3	51-58	Sipilän	Sipilä	PROPN	N	flat:name	*	2-2	
2-4	59-60	(	(	PUNCT	Punct	punct	*	2-5	
2-5	60-65	kesk.	kesko	NOUN	N	appos	*	2-2	
2-6	65-66	)	)	PUNCT	Punct	punct	*	2-5	
2-7	67-75	hallitus	hallitus	NOUN	N	nsubj	*	2-8	
2-8	76-82	haluaa	haluta	VERB	V	root	*	2-8	
2-9	83-105	työmarkkinajärjestöjen	työ#markkina#järjestö	NOUN	N	obl	*	2-8	
2-10	106-112	kanssa	kanssa	ADP	Adp	case	*	2-9	
2-11	113-119	laajan	laaja	ADJ	A	amod	*	2-12	
2-12	120-141	yhteiskuntasopimuksen	yhteis#kunta#sopimus	NOUN	N	obj	*	2-8	
2-13	141-142	,	,	PUNCT	Punct	punct	*	2-15	
2-14	143-147	joka	joka	PRON	Pron	nsubj	*	2-15	
2-15	148-160	vauhdittaisi	vauhdittaa	VERB	V	acl:relcl	*	2-12	
2-16	161-173	talouskasvua	talous#kasvu	NOUN	N	obj	*	2-15	
2-17	174-176	ja	ja	CCONJ	C	cc	*	2-18	
2-18	177-189	työllisyyttä	työllisyys	NOUN	N	conj	*	2-16	
2-19	189-190	.	.	PUNCT	Punct	punct	*	2-8	

#Text=– Hallitus tekee torstaina työmarkkinajärjestöille esityksen toimista, joihin kuuluu yksikkötyökustannusten alentaminen vähintään 5 prosentilla ja muutosturva.
3-1	191-192	–	–	PUNCT	Punct	punct	*	3-3	
3-2	193-201	Hallitus	hallitus	NOUN	N	nsubj	*	3-3	
3-3	202-207	tekee	tehdä	VERB	V	root	*	3-3	
3-4	208-217	torstaina	torstai	NOUN	N	obl	*	3-3	
3-5	218-241	työmarkkinajärjestöille	työ#markkina#järjestö	NOUN	N	obl	*	3-3	
3-6	242-251	esityksen	esitys	NOUN	N	obj	*	3-3	
3-7	252-260	toimista	toimi	NOUN	N	nmod	*	3-6	
3-8	260-261	,	,	PUNCT	Punct	punct	*	3-10	
3-9	262-268	joihin	joka	PRON	Pron	obl	*	3-10	
3-10	269-275	kuuluu	kuulua	VERB	V	acl:relcl	*	3-7	
3-11	276-298	yksikkötyökustannusten	yksikkö#työ#kustannus	NOUN	N	nmod:gobj	*	3-12	
3-12	299-310	alentaminen	alentaminen	NOUN	N	nsubj	*	3-10	
3-13	311-320	vähintään	vähintään	ADV	Adv	advmod	*	3-14	
3-14	321-322	5	5	NUM	Num	nummod	*	3-15	
3-15	323-334	prosentilla	prosentti	NOUN	N	nmod	*	3-12	
3-16	335-337	ja	ja	CCONJ	C	cc	*	3-17	
3-17	338-349	muutosturva	muutos#turva	NOUN	N	conj	*	3-12	
3-18	349-350	.	.	PUNCT	Punct	punct	*	3-3	

#Text=– Hallitus toivoo työmarkkinajärjestöjen sitoutuvan sopimukseen 21. elokuuta mennessä.
4-1	351-352	–	–	PUNCT	Punct	punct	*	4-3	
4-2	353-361	Hallitus	hallitus	NOUN	N	nsubj	*	4-3	
4-3	362-368	toivoo	toivoa	VERB	V	root	*	4-3	
4-4	369-391	työmarkkinajärjestöjen	työ#markkina#järjestö	NOUN	N	nsubj	*	4-5	
4-5	392-402	sitoutuvan	sitoutua	VERB	V	xcomp:ds	*	4-3	
4-6	403-414	sopimukseen	sopimus	NOUN	N	obl	*	4-5	
4-7	415-418	21.	21.	ADJ	Num	obl	*	4-5	
4-8	419-427	elokuuta	elokuu	NOUN	N	flat	*	4-7	
4-9	428-436	mennessä	mennessä	ADP	Adp	case	*	4-7	
4-10	436-437	.	.	PUNCT	Punct	punct	*	4-3	
'''

    TEST_DOC_OUT = \
'''#FORMAT=WebAnno TSV 3.2
#T_SP=de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Lemma|value
#T_SP=de.tudarmstadt.ukp.dkpro.core.api.lexmorph.type.pos.POS|coarseValue|PosValue
#T_RL=de.tudarmstadt.ukp.dkpro.core.api.syntax.type.dependency.Dependency|DependencyType|flavor|BT_de.tudarmstadt.ukp.dkpro.core.api.lexmorph.type.pos.POS
#T_SP=de.tudarmstadt.ukp.dkpro.core.api.ner.type.NamedEntity|value
#T_SP=webanno.custom.Quote|


#Text=Yhteiskuntasopimusta pohjustetaan elokuussa
1-1	0-20	Yhteiskuntasopimusta	yhteis#kunta#sopimus	NOUN	N	obj	*	1-2	_	_	
1-2	21-33	pohjustetaan	pohjustaa	VERB	V	root	*	1-2	_	_	
1-3	34-43	elokuussa	elokuu	NOUN	N	obl	*	1-2	TimexTmeDat	_	

#Text=– Juha Sipilän (kesk.) hallitus haluaa työmarkkinajärjestöjen kanssa laajan yhteiskuntasopimuksen, joka vauhdittaisi talouskasvua ja työllisyyttä.
2-1	44-45	–	–	PUNCT	Punct	punct	*	2-8	_	*[2]	
2-2	46-50	Juha	Juha	PROPN	N	nmod:poss	*	2-7	EnamexPrsHum[1]	*[2]	
2-3	51-58	Sipilän	Sipilä	PROPN	N	flat:name	*	2-2	EnamexPrsHum[1]	*[2]	
2-4	59-60	(	(	PUNCT	Punct	punct	*	2-5	_	*[2]	
2-5	60-65	kesk.	kesko	NOUN	N	appos	*	2-2	_	*[2]	
2-6	65-66	)	)	PUNCT	Punct	punct	*	2-5	_	*[2]	
2-7	67-75	hallitus	hallitus	NOUN	N	nsubj	*	2-8	_	*[2]	
2-8	76-82	haluaa	haluta	VERB	V	root	*	2-8	_	*[2]	
2-9	83-105	työmarkkinajärjestöjen	työ#markkina#järjestö	NOUN	N	obl	*	2-8	_	*[2]	
2-10	106-112	kanssa	kanssa	ADP	Adp	case	*	2-9	_	*[2]	
2-11	113-119	laajan	laaja	ADJ	A	amod	*	2-12	_	*[2]	
2-12	120-141	yhteiskuntasopimuksen	yhteis#kunta#sopimus	NOUN	N	obj	*	2-8	_	*[2]	
2-13	141-142	,	,	PUNCT	Punct	punct	*	2-15	_	*[2]	
2-14	143-147	joka	joka	PRON	Pron	nsubj	*	2-15	_	*[2]	
2-15	148-160	vauhdittaisi	vauhdittaa	VERB	V	acl:relcl	*	2-12	_	*[2]	
2-16	161-173	talouskasvua	talous#kasvu	NOUN	N	obj	*	2-15	_	*[2]	
2-17	174-176	ja	ja	CCONJ	C	cc	*	2-18	_	*[2]	
2-18	177-189	työllisyyttä	työllisyys	NOUN	N	conj	*	2-16	_	*[2]	
2-19	189-190	.	.	PUNCT	Punct	punct	*	2-8	_	*[2]	

#Text=– Hallitus tekee torstaina työmarkkinajärjestöille esityksen toimista, joihin kuuluu yksikkötyökustannusten alentaminen vähintään 5 prosentilla ja muutosturva.
3-1	191-192	–	–	PUNCT	Punct	punct	*	3-3	_	*[3]	
3-2	193-201	Hallitus	hallitus	NOUN	N	nsubj	*	3-3	_	*[3]	
3-3	202-207	tekee	tehdä	VERB	V	root	*	3-3	_	*[3]	
3-4	208-217	torstaina	torstai	NOUN	N	obl	*	3-3	_	*[3]	
3-5	218-241	työmarkkinajärjestöille	työ#markkina#järjestö	NOUN	N	obl	*	3-3	_	*[3]	
3-6	242-251	esityksen	esitys	NOUN	N	obj	*	3-3	_	*[3]	
3-7	252-260	toimista	toimi	NOUN	N	nmod	*	3-6	_	*[3]	
3-8	260-261	,	,	PUNCT	Punct	punct	*	3-10	_	*[3]	
3-9	262-268	joihin	joka	PRON	Pron	obl	*	3-10	_	*[3]	
3-10	269-275	kuuluu	kuulua	VERB	V	acl:relcl	*	3-7	_	*[3]	
3-11	276-298	yksikkötyökustannusten	yksikkö#työ#kustannus	NOUN	N	nmod:gobj	*	3-12	_	*[3]	
3-12	299-310	alentaminen	alentaminen	NOUN	N	nsubj	*	3-10	_	*[3]	
3-13	311-320	vähintään	vähintään	ADV	Adv	advmod	*	3-14	_	*[3]	
3-14	321-322	5	5	NUM	Num	nummod	*	3-15	_	*[3]	
3-15	323-334	prosentilla	prosentti	NOUN	N	nmod	*	3-12	_	*[3]	
3-16	335-337	ja	ja	CCONJ	C	cc	*	3-17	_	*[3]	
3-17	338-349	muutosturva	muutos#turva	NOUN	N	conj	*	3-12	_	*[3]	
3-18	349-350	.	.	PUNCT	Punct	punct	*	3-3	_	*[3]	

#Text=– Hallitus toivoo työmarkkinajärjestöjen sitoutuvan sopimukseen 21. elokuuta mennessä.
4-1	351-352	–	–	PUNCT	Punct	punct	*	4-3	_	*[5]	
4-2	353-361	Hallitus	hallitus	NOUN	N	nsubj	*	4-3	_	*[5]	
4-3	362-368	toivoo	toivoa	VERB	V	root	*	4-3	_	*[5]	
4-4	369-391	työmarkkinajärjestöjen	työ#markkina#järjestö	NOUN	N	nsubj	*	4-5	_	*[5]	
4-5	392-402	sitoutuvan	sitoutua	VERB	V	xcomp:ds	*	4-3	_	*[5]	
4-6	403-414	sopimukseen	sopimus	NOUN	N	obl	*	4-5	_	*[5]	
4-7	415-418	21.	21.	ADJ	Num	obl	*	4-5	TimexTmeDat[4]	*[5]	
4-8	419-427	elokuuta	elokuu	NOUN	N	flat	*	4-7	TimexTmeDat[4]	*[5]	
4-9	428-436	mennessä	mennessä	ADP	Adp	case	*	4-7	_	*[5]	
4-10	436-437	.	.	PUNCT	Punct	punct	*	4-3	_	*[5]	
'''

    TEST_ANN = {
        'NamedEntity' : \
'''articleId,sentenceId,startWordId,endWordId,value
99511266,1,3,3,TimexTmeDat
99511266,2,2,3,EnamexPrsHum
99511266,4,7,8,TimexTmeDat''',
        'Quote' : \
'''articleId,paragraphId,sentenceId,startWordId,endWordId
99511266,2,2,1,19
99511266,3,3,1,18
99511266,5,6,1,21
99511266,7,9,1,11
99511266,4,4,1,10
99511266,4,5,1,6
99511266,6,7,1,13
99511266,6,8,1,15
''',
    }

    def test_read_annotation(self):
        corpus = Corpus()
        corpus['99511266'] = \
            WebAnnoTSVReader().read(io.StringIO(self.TEST_DOC))
        for name, csv_content in self.TEST_ANN.items():
            fp = io.StringIO(csv_content)
            read_annotation_from_csv(corpus, fp, name)

        # test whether the annotations were read
        doc = corpus['99511266']
        #   NamedEntity
        self.assertEqual(len(doc.sentences[0].annotations['NamedEntity']), 1)
        self.assertEqual(len(doc.sentences[1].annotations['NamedEntity']), 1)
        self.assertEqual(len(doc.sentences[2].annotations['NamedEntity']), 0)
        self.assertEqual(len(doc.sentences[3].annotations['NamedEntity']), 1)
        self.assertIn(
            Annotation(1, 3, 1, 3, { 'value': 'TimexTmeDat' }),
            doc.sentences[0].annotations['NamedEntity'])
        self.assertIn(
            Annotation(2, 2, 2, 3, { 'value': 'EnamexPrsHum' }),
            doc.sentences[1].annotations['NamedEntity'])
        self.assertIn(
            Annotation(4, 7, 4, 8, { 'value': 'TimexTmeDat' }),
            doc.sentences[3].annotations['NamedEntity'])
        #   Quote
        self.assertEqual(len(doc.sentences[0].annotations['Quote']), 0)
        self.assertEqual(len(doc.sentences[1].annotations['Quote']), 1)
        self.assertEqual(len(doc.sentences[2].annotations['Quote']), 1)
        self.assertEqual(len(doc.sentences[3].annotations['Quote']), 1)
        self.assertIn(
            Annotation(2, 1, 2, 19, { '': '' }),
            doc.sentences[1].annotations['Quote'])
        self.assertIn(
            Annotation(3, 1, 3, 18, { '': '' }),
            doc.sentences[2].annotations['Quote'])
        self.assertIn(
            Annotation(4, 1, 4, 10, { '': '' }),
            doc.sentences[3].annotations['Quote'])

        self.maxDiff = None
        output = io.StringIO()
        write_webanno_tsv(doc, output)
        self.assertEqual(output.getvalue(), self.TEST_DOC_OUT)
