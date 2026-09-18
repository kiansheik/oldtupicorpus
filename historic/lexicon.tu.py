import importlib.util
import os
import sys


def _prepend_dev_path(*parts: str) -> None:
    path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..", "nhe-enga", *parts)
    )
    if path not in sys.path:
        sys.path.insert(0, path)


# Use local pydicate/tupi checkouts for hot-reload during development.
_prepend_dev_path("pydicate")
_prepend_dev_path("tupi")

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
aûsub = love
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
paben = Adverb(
    "pabẽ",
    definition="todo (os, a, as); totalmente, completamente",
    tag="[ADVERB:ALL]",
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
# 'i / 'é1 (v. intr. irreg.) 1) dizer: Marã e'ipe asé, karaibebé o arõana mongetábo? - Que a gente diz, conversando com o anjo seu guardião? (Ar., Cat., 23v); Aîpó eré supikatu... - Isso dizes com razão... (Anch., Teatro, 32); 2) rezar, enunciar-se, prescrever: Aîpó tekoangaîpaba robaîara nã e'i. - Os opostos daqueles pecados assim se enunciam. (Ar., Cat., 18); 3) querer dizer, querer significar, pensar, supor, presumir, cogitar, julgar: Marã e'ipe asé o py'ape aîpó o'îabo i xupé? - Que quer dizer a gente em seu coração, dizendo isso para ela? (Ar., Cat., 31v); "Osó ipó re'a" a'é. - Presumo que ele deve ter ido. (VLB, II, 86); 4) concluir, julgar por indícios: Emonã ûĩ re'a a'é. - Concluo que talvez isso seja assim. (VLB, II, 16); Amõ îuká-potá ûĩ sekóû a'é. - Concluí que ele está querendo matar alguém. (VLB, II, 16) ● e'iba'e - o que diz: Mendara... "xe mena koîpó xe remirekó re'õ ré t'îamendar îandé îoesé" e'iba'e, se'õ nhẽ roîré nd'e'ikatuî sesé omendá. - O cônjuge que diz: "-Após a morte de meu marido ou de minha esposa havemos de nos casar", após sua morte não pode casar-se com ele (ou ela) (Ar., Cat., 1686, 279-280); 'îara (ou e'îara) - o que diz; o indicador: Îaîuká memẽ aîpó 'îara... - Matemos juntos o que diz isso. (Ar., Cat., 79); ...Îasytatá serekoarama resé... pé 'îaramo i xupé... - Por causa da estrela sua guardiã,... como indicadora do caminho para eles. (Ar., Cat., 3); ...Marã e'îara... - As que dizem coisas más. (Anch., Teatro, 36); "...-Our temõ anhanga xe rerasóbo mã" e'îara. - O que diz: -Oxalá venha o diabo para me levar... (Ar., Cat., 67); 'îaba (ou 'eaba ou 'esaba) - 1) tempo, lugar, modo, etc. de dizer; o dizer: Okaî oupa aûîeramanhẽ... o îurupe nhote aîpó o 'eagûera repyramo. - Estão queimando para sempre como pena de dizerem isso somente em suas bocas. (Ar., Cat., 1686, 248); 2) o que alguém diz, o chamado por alguém, o dito: Ybytyra Monte Calvário 'îápe... - Para o monte chamado Calvário (Ar., Cat., 89); Erimba'epe aîpó nde 'îaba ereîmopóne? - Quando cumprirás isso que tu dizes? (Ar., Cat., 111v); O'u nhẽpe a'e 'ybá, tegûama, Tupã 'îaba? - Comeu aquele fruto, causa da morte, que Deus dissera? (Ar., Cat., 40v); Aîpó i 'eagûera rerekóbo, semimbo'e-etá... miapé rari o pópe... - Tendo isso que ele disse, seus discípulos tomaram o pão em suas mãos. (Ar., Cat., 84v)
ei = Verb(
    "'i",
    definition="to say, to tell, to speak, to indicate, to mean, to conclude, to judge",
)
er = Verb("er", verb_class="(s) (adj.)", definition="to have a name")
aîpo = Demonstrative("aîpo", tag="[DEMONSTRATIVE:3p:NOT_VISIBLE:AUDIBLE]")
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
jesusxto = ProperNoun("Jesus Christo")
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
kuesé = Adverb("kûesé", definition="ontem, yesterday")

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

salve_rainha = ProperNoun("Salve Rainha")
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
angaturã = Noun("angaturã")
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
opakatumonhanga = +tt * monhang * (opakatu + (mbae + tetiruã))
otmrme = bae * (opakatumonhanga >> (+tt * eikatu))
ttomtmetkbae = (cop() * (tt)) * otmrme
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
orébe = (oré * supé).var(1)
orébo = (oré * supé).var(0)
ekoangaîpaba = Noun("ekoangaîpaba")
pab = Verb("pab")
# artigos da fé
catorse = Number("catorse")
sete = Number("sete")
nã = Particle("nã", definition="assim, like this, the following")
arobiar = +ixé * erobîar
îar = Verb("îar")
carne = Noun("o'o")

opbrmym = -(rama * (bae * (pab)))
aé = Adverb("aé", definition="de fato, realmente")
pitanga = Noun("pitanga", definition="criança, child")

memen = Adverb("mem˜e")
saguera = lambda x: (pûera * (saba * x))
saguama = lambda x: (rama * (saba * x))
ybyraîoasaba = ybyrá / îoasaba

moîar = Verb("moîar")
gûeîyb = Verb("gûeîyb")
ypyOrigin = Noun("ypy")
karaiba = Noun("karaíba")
etá = Noun("etá")
soul = Noun("'anga")
aepe = Adverb("a'epe")
arõ = Verb(
    "arõ",
    verb_class="(s)",
    definition="(s) (v.tr.) - guardar, velar; olhar por (para que não se perca); proteger",
)

enosem = Verb("enosem")

noceu = pe * ybaka
risetoheaven = saguera(ae * (noceu + upir) * îe)
en = Verb("in")
rightside = Noun("'ekatûaba")
rightsidegod = (((tt * rightside) * koty) + (ae * en)).base_nominal()
inendofworld = (pe * (saba * (ara * pab))) + saguama(îur)

vivos = bae * ikobé
mortos = bae * manõ
todosvivosemortos = abé.var(2) * vivos * mortos
bondadenomundo = inendofworld + saguera(todosvivosemortos * (ikó / katu))
magreza = Noun("angaíba")
sinner = saba * v(magreza)
sinfullife = ikó / sinner

credo = lambda x: ((arobiar * ((amo * (x)) + (ae * ikó))))
pyreramo = lambda x: (amo * (pûera * (pyra * x)))
n = lambda x: (x).base_nominal(True)
payment = Verb("epyme'eng")
dez = Number("dez")
ekomonhangaba = saba * ekomonhang

eimoeté = (+nde * moeté).imp()
tenhen = Adverb("tenh˜e", definition="in vain")
anheté = Interjection("anheté", definition="it's true!")
domingo = Noun("domingo", definition="Sunday")
marã = Noun("marã", definition="trabalho")
tekó = Noun("tekó", definition="nature, law")
marãtekó = Noun("marãtekó", definition="job, occupation")
noworkday = ara @ -(saba * v(marãtekó))
domingo_e_feriado = abé.var(1) * domingo * noworkday
pais = abé * (nde * tuba) * (nde * sy)
apiti = Verb("apiti", definition="murder")

third_day = ara * mosapyr.card()
mondarõ = Verb("mondarõ")
moem = Noun("emo'em", "(t)")
momotar = Verb("momotar")
apixara = Noun("apixara", "(t)")
emirekó = Noun("emirekó", "(t)")
opkmbt = opakatu + (mbae + tetiruã)
sinco = Number("sinco", "five")
smi = Noun("Santa Madre Igreja")
esebé = Postposition(
    "esebé", definition="(t) (posp.) - com, juntamente com, assim como"
)
missa = ProperNoun("missa", definition="mass")
endub = Verb("endub")
seîxu = Noun("seîxu", "ano")

no = Adverb("no", definition="também")
Pascoa = ProperNoun("Pascoa", definition="Easter")
igreja = ProperNoun("igreja", definition="igreja")
puai = Verb(
    "pûaî",
    definition="dar ordens a, mandar, ordenar, mandar fazer [aquilo que se manda ou se ordena pode vir com esé (r, s)]:",
)
kuakub = Verb("kuakub", definition="recusar")
îekuakub = îe * kuakub

moîaoka = mo * îaok
potaba = Noun("potaba", definition="(m) porção, parte")
tupapotaba = tupan * potaba
ypy = Noun("ypy", definition="início, primeiro, começar, começo")
îasuk = Verb("îasuk", definition="batizar-se, lavar-se")
moîasuk = mbo * îasuk


# @note studio-lexical:v1 {"id": "lexical:44c788fb-9c13-5e27-b7e7-de5c88decba9", "name": "syba_2f344911", "scope": "shared", "provenance": {"source": "dictionary", "id": "navarro:9755:49b6477c313dcd70", "citation": "Navarro · verbete 9755 · nhe-enga/pydicate/pydicate/tupi_only.db"}}
syba_2f344911 = Noun(
    "sybá",
    definition="(s.) - testa (Castilho, Nomes, 37): Marãnamope asé o sybápe îoasaba moíni? - Por que a gente põe a cruz na testa? (Ar., Cat., 21)",
)


# @note studio-lexical:v1 {"id":"lexical:17060b173d476051a824b22763eee76f980055d78ac1a8feec52ae136c7b4922","name":"abareguasu","scope":"shared"}
abareguasu = Noun(
    value="abaregûasu",
    definition="(etim. - padre grande) (s.) - bispo, autoridade eclesiástica, provincial, abade, prelado: Asé sybápe abaregûasu nhandy-karaíba nonga. - Pôr o bispo em nossa testa o óleo santo. (Ar., Cat., 17v); Abaregûasu ogûatá. - O bispo passeia. (Fig., Arte, 6)",
)

# @note studio-lexical:v1 {"id":"lexical:36f1a2a79764f7a6096b2292f512f5625ee200a99563189d856a08db94d61d41","name":"nong","scope":"shared"}
nong = Verb(
    value="nong",
    verb_class="(-îo- ou -nho-) (v.tr.)",
    definition="(-îo- ou -nho-) (v.tr.) - 1) pôr, colocar: Enhonong nde itaingapema nde ku'aî. - Põe tua espada na tua cintura. (Fig., Arte, 125); Nde morerekoar xe ri, nde pó gûyrype xe nonga. - Sê tu guardião de mim, sob tuas mãos colocando-me. (Valente, Cantigas, in Ar., Cat., 1618); Aó-tinga onong asé resé. - Roupa branca põe na gente. (Ar., Cat., 81v); 2) fazer ser, fazer estar: ...Aîonong ka'umondá... - Faço-os ser ladrões de cauim. (Anch., Teatro, 134); 3) deter: T'orosóne, Anhangusu; oré reîtyk, oré nonga. - Vamos, Anhanguçu; derrotou-nos, detendo-nos. (Anch., Teatro, 172) ● nongaba - lugar, tempo, modo, causa, etc. de pôr, de colocar, ato de pôr, de colocar: ...I pysyrõû tekoangaîpabypy Adão îandé nongaba suí. - Livrou-a do pecado primeiro em que Adão nos pôs. (Ar., Cat., 9); nongara - o que põe, o que coloca, etc.: Mba'easybora o mara'ara kakareme t'osenõîukar abaré, îandykaraíba nongara... - Ao se aproximar o doente de sua agonia, que mande chamar o padre, o que põe o óleo bento. (Ar., Cat., 137v); i nongymbyra - o que é (ou deve ser) posto, colocado, etc.: ...Kaûĩ i pupé i nongymbyra... - O vinho que é colocado dentro dele. (Bettendorff, Compêndio, 85)",
    vid=7780,
)

# @note studio-lexical:v1 {"id":"lexical:8513e803f66a04e6c08f07c0b12e05e80a7152f3954fba8516b0963fc413b8bc","name":"nhandy","scope":"shared"}
nhandy = Noun(
    value="nhandy",
    definition="(s.) - azeite; óleo: pirá-nhandy - óleo de peixe (VLB, I, 49); ...Asé sybápe abaregûasu nhandy-karaíba nonga. - Pôr o bispo em nossa testa o óleo sagrado. (Ar., Cat., 17v)",
)


# @note studio-lexical:v1 {"id":"lexical:1afac1da3216239127ff0d22ee46300a4ef9a9ec63fd68cee8922cb5908c649c","name":"ianonde","scope":"shared"}
ianonde = Postposition(
    value="îanondé",
    definition="1) (posp.) - antes de (expressando tempo anterior a algo que se realizará depois, necessariamente): Xe îebyr-y îanondé. - Antes de minha volta. (Fig., Arte, 158); ...Oporaseî pysaré, oîemopaîeangaípa, tatápe o só îanondé. - Dançaram a noite toda, fazendo feitiçarias, antes de irem para o inferno. (Anch., Teatro, 14); Abá rokype erekûá, tá, nhemim-y îanondé? - Na casa de quem passaste, tomando-as [isto é, as coisas roubadas], antes de te esconderes? (Anch., Teatro, 44); Marã e'ipe asé o ké îanondé...? - Como diz a gente antes de dormir? (Ar., Cat., 24v); Xe angaturam ybakype xe só îanondé. - Eu fui bom antes de ir para o céu. (Anch., Arte, 45); 2) (adv.) antes (comparação): ...Ybakype i pyri o só îanondé Anhanga ratápe o só suí. - Antes sua ida para junto dele no céu que sua ida para o inferno. (Ar., Cat., 110)",
)

# @note studio-lexical:v1 {"id":"lexical:c6a31ecea2692f85a201ded3093f0e2b0479d2440c2967a78cf8d1c43eec0fbe","name":"eo","scope":"shared"}
eo = Noun(
    value="e'õ",
    definition="(t) (s.) - 1) morte (em geral): ...Te'õ rupîara nhẽ... - Adversária da morte (Anch., Poemas, 88); Te'õ rerobyka é, xe angaîpá-tubixagûera amosẽne... - Aproximando-me da morte, meus grandes pecados antigos farei sair. (Anch., Teatro, 38); N'ereîkuabipe ko'yr te'õ nde resé sekó? - Não sabes que agora a morte está contigo? (D'Abbeville, Histoire, 350); 2) morte natural: Te'õ suí amanõ. - Morro de morte natural. (VLB, II, 42); 3) desfalecimento, entorpecimento; [adj.: e'õ (r, s)] - moribundo; desfalecido, entorpecido; (xe) morrer; desfalecer, entorpecer-se: ...Abá 'anga re'õû nhẽ Tupana nhe'enga abŷápe. - As almas dos homens morrem ao transgredirem a palavra de Deus. (Anch., Teatro, 144); Se'õ. - Ele morre. (Anch., Arte, 40); îybá-e'õ-e'õ - braços entorpecidos, quebrantados (com algum sobressalto, grande tristeza, etc.); pó-e'õ - mãos entorpecidas (VLB, II, 93) ● e'õsara (t) - o que morre, o mortal (VLB, II, 42); e'õaba (ou e'õsaba) (t) [no futuro egûama (t)] - tempo, lugar, modo, causa, instrumento, etc. da morte, do morrer; morte (Fig., Arte, 59): ...Abá re'õagûera resé og orybamo... - Alegrando-se com a morte de alguém. (Ar., Cat., 70v); O'u nhẽpe a'e 'ybá, tegûama...? - Comeu aquele fruto, causa de morte? (Ar., Cat., 40v); Nde ma'enduá-katu... nde resé se'õagûera resé. - Lembra-te bem de que morreu por tua causa. (Ar., Cat., 249); e'õ-memûã (ou e'õ-aíba ou e'õ-korine) (t) - morte súbita ou em desastre (VLB, II, 42)",
)


# @note studio-lexical:v1 {"id":"lexical:079d07c4a115a0fbb7ed2d78bde6b200b3dcf5dcf4bb2829777855db5bad4c85","name":"abare","scope":"shared"}
abare = Noun(
    value="abaré",
    definition='(s.) - padre, ABARÉ, ABARUNA; clérigo; frade; sacerdote, religioso (VLB, II, 100): I xupé, ranhẽ, abaré, Tupã mombegûabo, i xóû. - Junto a ela, primeiramente, os padres foram, anunciando a Deus. (Anch., Poemas, 114); Oú tenhẽ xe pe\'abo "abaré" \'îaba... - Vêm em vão para me afastar os ditos "padres". (Anch., Teatro, 8)',
)

# @note studio-lexical:v1 {"id":"lexical:b6d8a095bc9a0071c7cbc600a9918a79a76d7f3d83006a641c18da019a8b6bf0","name":"nhemoabare","scope":"shared"}
nhemoabare = ((((nhe) * ((mo) * (abare))).var(1)).base_nominal()).copy()
nhemoabare.definition = "(etim. - fazer-se padre) (s.) - sacramento da ordem (Ar., Cat., 17v); definição do composto nhe + mo + abaré (Navarro 7935)."


# @note studio-lexical:v1 {"id":"lexical:83b964a833bd253195cd7bd888ef52cf58034f2ae406d7ca449c3b8d55d11349","name":"mendara","scope":"shared"}
mendara = Noun(
    value="mendara",
    definition="(s.) - 1) casado(a) - Ereîkópe mendara, mendarûera resé? - Tens relações com uma casada, com uma que foi casada? (Anch., Doutr. Cristã, II, 89); 2) casamento; matrimônio: -Marãpe amõ îandé 'anga posanga? -Mendara. -Qual é o outro remédio de nossa alma? -O matrimônio. (Ar., Cat., 94); 3) cônjuge: I mendá-mokõîa resé i byk'iré... - Após tocar em seu segundo cônjuge. (Ar., Cat., 280); (adj.: mendar) - casado: Ereîkópe kunhã-mendara resé? - Tiveste relações sexuais com uma mulher casada? (Ar., Cat., 109)",
)

__all__ = [
    name for name in globals() if not name.startswith("_") and name not in {"os", "sys"}
]

_LEXICON_CLONE_INDEX = 0


def load_lexicon() -> dict[str, object]:
    global _LEXICON_CLONE_INDEX

    package = __package__ or "historic"
    module_name = f"{package}._lexicon_clone_{_LEXICON_CLONE_INDEX}"
    _LEXICON_CLONE_INDEX += 1
    spec = importlib.util.spec_from_file_location(module_name, __file__)
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to clone historic lexicon from {__file__}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    try:
        spec.loader.exec_module(module)
        return {name: getattr(module, name) for name in module.__all__}
    finally:
        sys.modules.pop(module_name, None)
