import io
import unittest

from flopo_formats.io.csv import CSVCorpusReader
from flopo_formats.io.prolog import write_prolog


class PrologTest(unittest.TestCase):
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
100023169,2,3,1,Uuden,uusi,ADJ,A,Case=Gen|Degree=Pos|Number=Sing,3,amod,
100023169,2,3,2,suuren,suuri,ADJ,A,Case=Gen|Degree=Pos|Number=Sing,3,amod,
100023169,2,3,3,palkansaajajärjestön,palkan#saaja#järjestö,NOUN,N,Case=Gen|Number=Sing,4,nmod:gobj,
100023169,2,3,4,suunnittelu,suunnittelu,NOUN,N,Case=Nom|Derivation=U|Number=Sing,5,nsubj,
100023169,2,3,5,etenee,edetä,VERB,V,Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin|Voice=Act,0,root,
100023169,2,3,6,suunnitelmien,suunnitelma,NOUN,N,Case=Gen|Number=Plur,5,obl,
100023169,2,3,7,mukaan,mukaan,ADP,Adp,AdpType=Post,6,case,
100023169,2,3,8,syksyn,syksy,NOUN,N,Case=Gen|Number=Sing,9,nmod:poss,
100023169,2,3,9,työmarkkinamyllerryksestä,työ#markkina#myllerrys,NOUN,N,Case=Ela|Number=Sing,5,obl,
100023169,2,3,10,huolimatta,huolimatta,ADP,Adp,AdpType=Post,9,case,SpaceAfter=No
100023169,2,3,11,.,.,PUNCT,Punct,,5,punct,SpacesAfter=\\n\\n'''

    TEST_DOC_OUT = \
'''quoted_span(_, _) :- fail.
named_entity(_, _, _) :- fail.
deprel(1-1, amod).
deprel(1-2, nsubj).
deprel(1-3, root).
deprel(1-4, obl).
deprel(1-5, case).
deprel(2-1, punct).
deprel(2-2, root).
deprel(2-3, cc).
deprel(2-4, conj).
deprel(2-5, punct).
deprel(2-6, nmod:poss).
deprel(2-7, nsubj).
deprel(2-8, aux).
deprel(2-9, advmod).
deprel(2-10, parataxis).
deprel(3-1, amod).
deprel(3-2, amod).
deprel(3-3, nmod:gobj).
deprel(3-4, nsubj).
deprel(3-5, root).
deprel(3-6, obl).
deprel(3-7, case).
deprel(3-8, nmod:poss).
deprel(3-9, obl).
deprel(3-10, case).
deprel(3-11, punct).
eos(1-5).
eos(2-10).
eos(3-11).
feats(1-1, case(nom)).
feats(1-1, degree(pos)).
feats(1-1, number(sing)).
feats(1-2, case(nom)).
feats(1-2, number(sing)).
feats(1-3, mood(ind)).
feats(1-3, number(sing)).
feats(1-3, person(3)).
feats(1-3, tense(pres)).
feats(1-3, verbForm(fin)).
feats(1-3, voice(act)).
feats(1-4, case(ela)).
feats(1-4, number(sing)).
feats(2-2, case(nom)).
feats(2-2, number(sing)).
feats(2-4, case(nom)).
feats(2-4, number(sing)).
feats(2-6, case(gen)).
feats(2-6, number(sing)).
feats(2-7, case(nom)).
feats(2-7, number(sing)).
feats(2-8, mood(ind)).
feats(2-8, number(sing)).
feats(2-8, person(3)).
feats(2-8, tense(pres)).
feats(2-8, verbForm(fin)).
feats(2-8, voice(act)).
feats(2-10, case(nom)).
feats(2-10, degree(pos)).
feats(2-10, number(sing)).
feats(2-10, verbForm(part)).
feats(2-10, voice(act)).
feats(3-1, case(gen)).
feats(3-1, degree(pos)).
feats(3-1, number(sing)).
feats(3-2, case(gen)).
feats(3-2, degree(pos)).
feats(3-2, number(sing)).
feats(3-3, case(gen)).
feats(3-3, number(sing)).
feats(3-4, case(nom)).
feats(3-4, number(sing)).
feats(3-5, mood(ind)).
feats(3-5, number(sing)).
feats(3-5, person(3)).
feats(3-5, tense(pres)).
feats(3-5, verbForm(fin)).
feats(3-5, voice(act)).
feats(3-6, case(gen)).
feats(3-6, number(plur)).
feats(3-8, case(gen)).
feats(3-8, number(sing)).
feats(3-9, case(ela)).
feats(3-9, number(sing)).
head(1-1, 1-2).
head(1-2, 1-3).
head(1-3, 1-0).
head(1-4, 1-3).
head(1-5, 1-4).
head(2-1, 2-2).
head(2-2, 2-0).
head(2-3, 2-4).
head(2-4, 2-2).
head(2-5, 2-2).
head(2-6, 2-7).
head(2-7, 2-10).
head(2-8, 2-10).
head(2-9, 2-10).
head(2-10, 2-2).
head(3-1, 3-3).
head(3-2, 3-3).
head(3-3, 3-4).
head(3-4, 3-5).
head(3-5, 3-0).
head(3-6, 3-5).
head(3-7, 3-6).
head(3-8, 3-9).
head(3-9, 3-5).
head(3-10, 3-9).
head(3-11, 3-5).
lemma(1-1, "uusi").
lemma(1-2, "suur#järjestö").
lemma(1-3, "hahmottua").
lemma(1-4, "työ#markkina#myräkkä").
lemma(1-5, "huolimatta").
lemma(2-1, "##").
lemma(2-2, "SAK").
lemma(2-3, "ja").
lemma(2-4, "STTK").
lemma(2-5, ":").
lemma(2-6, "suur#järjestö").
lemma(2-7, "tarve").
lemma(2-8, "olla").
lemma(2-9, "vain").
lemma(2-10, "korostua").
lemma(3-1, "uusi").
lemma(3-2, "suuri").
lemma(3-3, "palkan#saaja#järjestö").
lemma(3-4, "suunnittelu").
lemma(3-5, "edetä").
lemma(3-6, "suunnitelma").
lemma(3-7, "mukaan").
lemma(3-8, "syksy").
lemma(3-9, "työ#markkina#myllerrys").
lemma(3-10, "huolimatta").
lemma(3-11, ".").
token(1-1, "Uusi").
token(1-2, "suurjärjestö").
token(1-3, "hahmottuu").
token(1-4, "työmarkkinamyräkästä").
token(1-5, "huolimatta").
token(2-1, "##").
token(2-2, "SAK").
token(2-3, "ja").
token(2-4, "STTK").
token(2-5, ":").
token(2-6, "Suurjärjestön").
token(2-7, "tarve").
token(2-8, "on").
token(2-9, "vain").
token(2-10, "korostunut").
token(3-1, "Uuden").
token(3-2, "suuren").
token(3-3, "palkansaajajärjestön").
token(3-4, "suunnittelu").
token(3-5, "etenee").
token(3-6, "suunnitelmien").
token(3-7, "mukaan").
token(3-8, "syksyn").
token(3-9, "työmarkkinamyllerryksestä").
token(3-10, "huolimatta").
token(3-11, ".").
upos(1-1, adj).
upos(1-2, noun).
upos(1-3, verb).
upos(1-4, noun).
upos(1-5, adp).
upos(2-1, sym).
upos(2-2, noun).
upos(2-3, cconj).
upos(2-4, propn).
upos(2-5, punct).
upos(2-6, noun).
upos(2-7, noun).
upos(2-8, aux).
upos(2-9, adv).
upos(2-10, verb).
upos(3-1, adj).
upos(3-2, adj).
upos(3-3, noun).
upos(3-4, noun).
upos(3-5, verb).
upos(3-6, noun).
upos(3-7, adp).
upos(3-8, noun).
upos(3-9, noun).
upos(3-10, adp).
upos(3-11, punct).
'''

    def test_write_prolog(self):
        corpus = CSVCorpusReader().read(io.StringIO(self.TEST_DOC))
        output = io.StringIO()
        write_prolog(corpus['100023169'], output)
        self.maxDiff = None
        self.assertEqual(output.getvalue(), self.TEST_DOC_OUT)

