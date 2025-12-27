import os
import sys

# Use local pydicate checkout for hot-reload during development.
sys.path.insert(
    0,
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "nhe-enga", "pydicate")
    ),
)
sys.path.insert(
    0,
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "nhe-enga", "tupi")),
)
from pydicate.lang.tupilang import *
from pydicate.lang.tupilang.pos import *

arakae = Adverb(
    "araka'e", definition="a long time ago, distant past", tag="[ADVERB:DISTANT_PAST]"
)
rakae = Adverb(
    "raka'e", definition="a long time ago, distant past", tag="[ADVERB:DISTANT_PAST]"
)
kunumim = Noun("kunum˜i", definition="young boy")
ikó = Verb("ikó", definition="to live")
taba = Noun("taba", definition="village")
irun = Noun("ir˜u", definition="friend")
era = Noun("er", definition="(t); name")

pindo = ProperNoun("Pindoba Mirĩ")
pedro = ProperNoun("Pedro")
love = Verb("aûsub", definition="to love")
kunhatai = Noun("kunhataĩ", definition="young girl")
abét = Adverb("abé", definition="also, as well")
ara = Noun("'ara", definition="day, light, sunlight, time, period, era")
ekar = Verb("ekar", definition="to search, to seek, to look for")
só = Verb("só", definition="to go, to leave, to travel")
îuká = Verb("îuká", definition="to murder, to kill, to slay")
monhang = Verb(
    "monhang", definition="to do, to make, to create, to cause, to perform, to commit"
)
mongetá = Verb("mongetá", definition="to talk, to converse, to speak with")
kanhem = Verb("kanhem", definition="to disappear, to vanish, to lose oneself")
oka = Noun("oka", definition="(t); house, home, dwelling, abode, residence")
lost = bae * kanhem
potar = Verb("potar", definition="to want, to desire, to wish for")
kaa = Noun("ka'a", definition="(t); forest, jungle, woods, bush, thicket")
opá = Adverb(
    "opá", definition="everything, all, whole, entire, complete", tag="[ADVERB:ALL]"
)
basem = Verb("basem", definition="to find, to discover, to encounter")
mboryb = Verb("mboryb", definition="to please, to delight, to satisfy")
eté = Adverb(
    "eté",
    definition="true, real, genuine, authentic, very good, more, better",
    tag="[ADVERB:TRUE]",
)
apé = Noun("apé", definition="(s, r, s) path, way, road, route")
epenhan = Verb("epenhan", definition="to attack, to assault, to fight with")
îagûara = Noun(
    "îagûara",
    definition="jaguar, onça, onça-pintada, large wild cat of the Americas, also means dog in some contexts",
)
îebyr = Verb("îebyr", definition="to return, to come back, to go back")
epîak = Verb("epîak", definition="to see, to look at, to watch, to observe")
atã = Noun("atã", definition="(t) strong, brave, firm, hard, tough, rigid, arduous")
gûarinin = Noun("gûarinin", definition="war, warfare, battle, warrior, soldier")
ur = Verb("îur", definition="to come")
poî = Verb("poî", definition="to feed, to nourish, to sustain")
# 'i / 'é1 (v. intr. irreg.) 1) dizer: Marã e'ipe asé, karaibebé o arõana mongetábo? - Que a gente diz, conversando com o anjo seu guardião? (Ar., Cat., 23v); Aîpó eré supikatu... - Isso dizes com razão... (Anch., Teatro, 32); 2) rezar, enunciar-se, prescrever: Aîpó tekoangaîpaba robaîara nã e'i. - Os opostos daqueles pecados assim se enunciam. (Ar., Cat., 18); 3) querer dizer, querer significar, pensar, supor, presumir, cogitar, julgar: Marã e'ipe asé o py'ape aîpó o'îabo i xupé? - Que quer dizer a gente em seu coração, dizendo isso para ela? (Ar., Cat., 31v); "Osó ipó re'a" a'é. - Presumo que ele deve ter ido. (VLB, II, 86); 4) concluir, julgar por indícios: Emonã ûĩ re'a a'é. - Concluo que talvez isso seja assim. (VLB, II, 16); Amõ îuká-potá ûĩ sekóû a'é. - Concluí que ele está querendo matar alguém. (VLB, II, 16) ● e'iba'e - o que diz: Mendara... "xe mena koîpó xe remirekó re'õ ré t'îamendar îandé îoesé" e'iba'e, se'õ nhẽ roîré nd'e'ikatuî sesé omendá. - O cônjuge que diz: "-Após a morte de meu marido ou de minha esposa havemos de nos casar", após sua morte não pode casar-se com ele (ou ela). (Ar., Cat., 1686, 279-280); 'îara (ou e'îara) - o que diz; o indicador: Îaîuká memẽ aîpó 'îara... - Matemos juntos o que diz isso. (Ar., Cat., 79); ...Îasytatá serekoarama resé... pé 'îaramo i xupé... - Por causa da estrela sua guardiã,... como indicadora do caminho para eles. (Ar., Cat., 3); ...Marã e'îara... - As que dizem coisas más. (Anch., Teatro, 36); "...-Our temõ anhanga xe rerasóbo mã" e'îara. - O que diz: -Oxalá venha o diabo para me levar... (Ar., Cat., 67); 'îaba (ou 'eaba ou 'esaba) - 1) tempo, lugar, modo, etc. de dizer; o dizer: Okaî oupa aûîeramanhẽ... o îurupe nhote aîpó o 'eagûera repyramo. - Estão queimando para sempre como pena de dizerem isso somente em suas bocas. (Ar., Cat., 1686, 248); 2) o que alguém diz, o chamado por alguém, o dito: Ybytyra Monte Calvário 'îápe... - Para o monte chamado Calvário (Ar., Cat., 89); Erimba'epe aîpó nde 'îaba ereîmopóne? - Quando cumprirás isso que tu dizes? (Ar., Cat., 111v); O'u nhẽpe a'e 'ybá, tegûama, Tupã 'îaba? - Comeu aquele fruto, causa da morte, que Deus dissera? (Ar., Cat., 40v); Aîpó i 'eagûera rerekóbo, semimbo'e-etá... miapé rari o pópe... - Tendo isso que ele disse, seus discípulos tomaram o pão em suas mãos. (Ar., Cat., 84v)
ei = Verb(
    "'i",
    definition="to say, to tell, to speak, to indicate, to mean, to conclude, to judge",
)
er = Verb("er", verb_class="(s) (adj.)", definition="to have a name")
pdb = +(pindo * abé * pedro)

santa_cruz = ProperNoun("Santa Cruz")
tupan = ProperNoun("Tupã")
aang = Verb("a'ang")
pysyro = Verb("pysyrõ")
îara = Noun("îara")
amotar = Verb("amotar")
tb = Conjunction("", tag="[CONJUNCTION:AND]")
tuba = Noun("uba", "pai")
tayra = Noun("a'yra", "filho")
espirito_santo = ProperNoun("Espírito Santo")
amen = Interjection(
    "amém", definition="so be it, truly, let it be", tag="[INTERJECTION:AMEN]"
)
jesus = ProperNoun("Jesus")
ybaka = Noun("ybaka")
moeté = Verb("moeté")
reino = Noun(
    "Reino", definition="kingdom, realm, dominion", tag="[NOUN:LOAN_WORD:PORTUGUESE]"
)
yby = Noun("yby", definition="earth, land, ground, soil, country, world")
u = Verb("'u")
iabiõ = Postposition("îabi'õ", "each, every", tag="[POSTPOSITION:EVERY]")
meeng = Verb("me'eng")
nheeng = Verb("nhe'eng")
kori = Adverb("kori")
nhyron = Verb("nhyrõ", "adj.")
angaipaba = Noun("angaîpaba")
erekomemûã = Verb("erekomemûã")
ar = Verb("'ar")
ukar = Verb("ukar")
tentação = Noun("tentação")
mbae = Noun("mba'e")
aiba = Noun("aíba")
obaîtin = Verb("obaît˜i")
ykyyra = Noun("yky'yra")
eõ = Verb("manõ")
poreaûsub = Verb(
    "poreaûsub", definition="sad, forlorn, mourn", verb_class="(2ª classe)"
)
tyb = Verb("tyb")
bebé = Verb("bebé")
okendabok = Verb("okendabok")
gûyrá = Noun("gûyrá")
pab = Verb("pab", verb_class="(v.tr)", definition="to rear, animal husbandry")
Enza = ProperNoun("Enza")
iké = Verb("iké")

tom_story = [
    ((tyb + rakae) * gûyrá),
    (emi * (xe * pab)) == ae,
    (Enza) == (bae * er),
    (ae * (okendabok * Enza)) << (+Enza * bebé),
]

avemaria = ProperNoun("Ave Maria")
santamaria = ProperNoun("Santa Maria")
graça = Noun(
    "graça", definition="grace, favor, blessing", tag="[NOUN:LOAN_WORD:PORTUGUESE]"
)
ynysema = Noun("ynysema")
mombeu = Verb("mombe'u")
kunhã = Noun("kunhã")
katu = Noun("katu")
membyra = Noun("membyra")
sy = Noun("sy")
tupãmongetá = Verb("tupãmongetá")
koyr = Adverb("ko'yr")
irã = Adverb("irã")
îekyî = Verb("îekyî")
îub = Verb("îub")
béno = Adverb("béno")
erobîar = Verb("erobîar")

salve_rainha = ProperNoun("Salva Rainha")
poraûsubara = Noun("poraûsubara")
ikobé = Verb("ikobé")
een = Noun("e'ẽ")
salve = Interjection("salve", definition="hail", tag="[INTERJECTION:HAIL]")
sapukai = Verb("sapukaî")
pea = Verb("pe'a")
eva = ProperNoun("Eva")
nheangerur = Verb("nhe'angerur")
poasema = Noun("poasema")
îaseo = Verb("îase'o")
ybytygûaîa = Noun("ybytygûaîa")
esá = Noun("esá")

enein = Interjection("ene'ĩ")
îeruré = Verb("îeruré")
erobak = Verb("erobak")
aec = Adverb("a'e")
jatf = cop() * (jesus == (pyra * (mombeu / katu))) * (nde * membyra)
syk = Verb("syk")
nheraneym = Noun("nherane'yma")
erekó = Verb("erekó")
poreaûsuberekó = Noun("poreaûsuberekó")
virgem_maria = ProperNoun("Virgem Maria")
angaturama = Noun("angaturama")
christo = ProperNoun("Christo")
enõî = Verb("enõî")
îekosub = Verb("îekosub")
eikatu = Verb("'ikatu")
tt = tupan == tuba
oîepebae = Noun("oîepeba'e", definition="unique, only one")
pitangin = Noun("pitang˜i")

ababykagûereyma = Noun("ababykagûere'yma")
morubixaba = Noun("morubixaba")
ponciopilato = ProperNoun("Poncio Pilato")
memûã = Noun("memûã")
maria = ProperNoun("Maria")
ybyrá = Noun("ybyrá")
îoasaba = Noun("îoasaba")
moîar = Verb("moîar")
tym = Verb("tym")
gûeîyb = Verb("gûeîyb")
apytera = Noun("apytera")
manõ = Verb("manõ")
ikobé = Verb("ikobé")

upir = Verb("upir")
ttomtmetkbae = (cop() * (tt)) * (
    bae * ((+tt * monhang * (opakatu + (mbae + tetiruã))) >> (+tt * eikatu))
)
ekatûaba = Noun("'ekatuaba")
ker = Verb("ker")
pytá = Verb("pytá")
inv = Verb("in")
aesuí = Adverb("a'e suí", definition="dalí, daí", tag="[ADVERB:FROM_THERE]")
îur = Verb("îur")
ekomonhang = Verb("ekomonhang")
santa_igreja = ProperNoun("Santa Igreja Catholica")
santos = ProperNoun("Santos")
îaok = Verb("îa'ok")
moîaoîaok = mo * îaok.redup()
pytybõ = Verb("pytybõ")


bettendorff_compendio_pt_1 = [
    # Santa Cruz
    ((saba * (santa_cruz * aang)) * esé)
    + (endé * (pysyro.imp()) * oré)
    + ((tupan == (oré * îara.voc())))
    + ((sara * (-(oré * amotar))) * suí),
    (((tuba + tayra + espirito_santo) * era) * pupé),
    (amen + jesus),
    # Pai nosso
    (oré * tuba).voc() @ (((pe * ybaka)) + (sara * ikó).voc())
    + (amo * (pyra * moeté))
    + (ikó * (nde * era)).perm(),
    (ur * (nde * reino)).perm(),
    (monhang * (emi * (potar * nde)) * îe).perm()
    + (pe * yby)
    + (pe * ybaka)
    + (îabé * (monhang * ae * îe)),
    (((emi * (u * oré)) @ (nduara * (ara * iabiõ))) * (meeng * +endé).imp())
    + kori
    + (oré * supé),
    ((+nde * nhyron).imp() + (oré * angaipaba * esé) + (oré * supé))
    + (îabé * ((((sara * (erekomemûã * oré))) * supé) + (oré * nhyron))),
    (endé * -(mo * (ar / ukar)).imp() * oré) + (tentação * pupé),
    ((oré * ((pysyro * endé))).imp() << te) + ((mbae / aiba) * suí),
    (amen + jesus),
    # Ave Maria
    cop() * avemaria * (bae * ((esé * graça) + v(ynysema))),
    (amo * (nde * irun)) + (ikó * (îandé * îara)),
    (amo * (pyra * (mombeu / katu))) + (ikó * +endé) + (kunhã * suí),
    cop() * ((pyra * (mombeu / katu)) + abé) * (cop() * (nde * membyra) * jesus),
    (cop() * santamaria * (tupan * sy))
    + (+endé * tupãmongetá).imp()
    + (esé * (cop() * oré * (bae * v(angaipaba))))
    + koyr
    << (irã + ((îub * oré) >> (îekyî * oré)) << béno),
    (amen + jesus),
    # salva rainha
    (cop() * (salve_rainha == (poraûsubara * sy)) + ikobé.base_nominal(True))
    + (bae * v(een))
    + (saba * (oré * erobîar * îe))
    + (salve),
    (nde * supé)
    + (+oré * sapukai.redup()).circ(False)
    + (amo * (pyra * pea))
    + (amo * (eva * membyra)),
    (nde * supé) + ((+oré * nheangerur.circ(False)) << (oré * v(poasema)))
    << ((+oré * îaseo) + (pupé * ((ikód * ybytygûaîa) == (saba * îaseo)))),
    enein + (sara * ((esé * oré) + (îeruré))).voc(),
    ((eboûing * (nde * (esá / poraûsubara))) * (+endé * erobak.imp())) + (oré * koty),
    (aec)
    + (
        (iré * (syk * (ikód * (pûera * (saba * (pea * îe))))))
        >> ((jatf * (+endé * (epîak / ukar))).imp() + (oré * supé))
    ),
    cop()
    * (nheraneym.voc())
    * ((sara * v(poreaûsuberekó)).voc())
    * ((bae * v(een)).voc())
    * virgem_maria.voc(),  # fix absoluta m
    ((cop() * santamaria * (tupan * sy)) + (v(angaturama).perm() * +oré) << ne)
    + (esé * (pûera * (emi * (christo * enõî))))
    + (
        ri * (rama * (saba * (oré * îekosub)))
    ),  # îekosupagûama here is îekosuBagûama in bettendorf, displaying already some early divergences of loss of phonetic composition which we see in nheengatu
    (amen + jesus),
    # Creio em Deus Padre
    erobîar * +ixé * ((ttomtmetkbae) * (sara * (monhang * (abé + ybaka + yby)))),
    (
        +ixé
        * erobîar
        * ((cop() * (jesus / christo / abé)) * (tayra) * (oîepebae) * (asé * îara))
    ),  # fix abé rendering on correct element
    (
        pûera
        * (
            bae
            * (
                (pe * (saba * (espirito_santo * monhang * ae)))
                >> ((amo * pitangin) >> (((monhang) * îe)))
            )
        )
    ),
    (aebae * ar) + (suí * (cop() * (maria) * (ababykagûereyma))),
    (ponciopilato * ((amo * morubixaba) >> (ikó)))
    >> ((amo * (pyra * (erekó / memûã))) + (+aebae * ikó)),
    (esé * (ybyrá / îoasaba))
    + (amo * (pyra * moîar) + (ikó * +aebae))
    + (amo * (pyra * îuká))
    + (amo * (pyra * tym) + (ikó * +aebae)),
    (+jesus * gûeîyb + (pe * (yby * apytera))),
    (pupé * (ara * mosapyr.card()))
    + ((suí * (pûera * (bae * (manõ)))) + (+jesus * (ikobé / îebyr))),
    (upir * +jesus * îe) + (pe * ybaka),
    (koty * (ttomtmetkbae * ekatûaba)) + (+jesus * inv),
    aesuí + (+jesus * îur)
    << (
        (
            (((bae * (ikobé))) + ((pûera * (bae * (manõ)))) + paben)
            * (+jesus * (ekomonhang))
        )
    )
    + ne,
    +ixé * erobîar * espirito_santo,
    +ixé * erobîar * santa_igreja,
    +ixé
    * erobîar
    * (((santos * (ikó / katu)).base_nominal(True) * (mo * îaok) * îe).redup()),
]
