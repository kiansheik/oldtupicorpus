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
from historic.navarro_lexicon import navarro_lexeme

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


# @note studio-lexical:v1 {"id":"lexical:67d2d0e6bd29b9e227c0207424930705b1e625190d2619a7f070d04b4a1db32c","name":"ekateyma","scope":"shared"}
ekateyma = Noun(
    value="ekate'yma",
    definition="(ou ekoate'yma) (t) (s.) - avareza: Tekate'yma robaîara tekate'yme'yma. - O oposto da avareza é a liberalidade. (Ar., Cat., 18); [adj.: ekate'ym (r, s)] - avaro: ...Pe rekate'ym sesé... - Vós sois avaros com ele. (Ar., Cat., 89)",
)


# @note studio-lexical:v1 {"id":"lexical:785ae19e55a33407cc5a71fc314b0145018be53b4b5d3719cf313ebfc832e0db","name":"moropotara","scope":"shared"}
moropotara = (((potar) * moro).base_nominal()).copy()
moropotara.definition = "(m) (etim. - desejar gente) (s.) - lascívia, luxúria, desejo sensual, concupiscência: Ereîtykype kunumĩ amõ... nde 'arybo moropotara suí? - Lançaste algum menino sobre ti por desejo sensual? (Anch., Doutr. Cristã, II, 95); (adj.: poropotar) - lascivo, lúbrico, desejoso de sexo, concupiscente, luxurioso: Nde resá-poropotápe amõ resé ema'ẽmo? - Tu tens olhos concupiscentes, olhando para alguém? (Ar., Cat., 104v); abá-poropotara - homem luxurioso (VLB, II, 25) ● i poropotaryba'e - o que é luxurioso: sesá-poropotaryba'e... - o que tem olhos que são luxuriosos (Ar., Cat., 71v); poropotarixûera (m) - o que tem tendência à luxúria, luxurioso (VLB, II, 25)"


# @note studio-lexical:v1 {"id":"lexical:6dd14cb447a0e71fc6aae104fcbeb2e150f070886bf3abfc90b55433899e89a9","name":"moyro","scope":"shared"}
moyro = Verb(
    value="moŷrõ",
    definition="(v.tr.) - 1) irar, irritar, agastar: Xe moaîu-marangatu, xe moŷrõetekatûabo, aîpó tekó-pysasu. - Importuna-me bem, irritando-me muitíssimo, aquela lei nova. (Anch., Teatro, 4); ...Pemoŷrõ Pa'i Îesu... - Irritastes o senhor Jesus. (Anch., Teatro, 42); 2) indispor (contra algo ou contra alguém: compl. com supé): Aîmoyrõ-yrõ (abá) supé. - Fiquei-o indispondo contra o homem. (VLB, I, 48, adapt.); 3) escandalizar (VLB, I, 122)",
    verb_class="(v.tr.)",
    vid=7597,
)


# @note studio-lexical:v1 {"id":"lexical:4614902bf71f6e759c5d2e8e8154b245eeaadb85048e0fd64318df020534d668","name":"kau","scope":"shared"}
kau = Noun(
    value="ka'u",
    definition="(s.) - bebedeira (de cauim); bebedeira em geral: Mba'e-eté ka'ugûasu... - Coisa muito boa é uma grande bebedeira. (Anch., Teatro, 6); Ixé kó ka'u resé aporomoingó îepi... - Eis que eu faço as pessoas estarem na bebedeira sempre. (Anch., Teatro, 134)",
)


# @note studio-lexical:v1 {"id":"lexical:fe3098aab88e20de2fb4f987267890b838aab27b8567abf7d70a1c488bf5365f","name":"asy","scope":"shared"}
asy = Noun(
    value="asy",
    definition="(t) (s.) - 1) dor, pena: 'Y berame'ĩ ikó îandé ratá rasy: n'osyki Anhanga ratá rasy resé. - Eis que a dor de nosso fogo parece a da água: não se equipara à dor do fogo do diabo. (Ar., Cat., 163v); Oîporará Tupã repîake'yma rasy. - Sofrem a dor de não verem a Deus. (Ar., Cat., 48); 2) mal, ruindade; problema: Na sasyî. - Não faz mal, não há problema. (Anch., Teatro, 148, 2006); [adj.: asy (r, s)] - 1) dolorido, doloroso, penoso, trabalhoso, árduo; (xe) doer, ser penoso, ser causa de pesar; pesar; ter dor, sentir dor; sofrer: T'oré pyatã, angá, mba'e-asy porarábo... - Que sejamos corajosos, sim, suportando as coisas dolorosas. (Anch., Teatro, 120); Sasy nakó ygá-pukuîa. - É penoso, de fato, remar canoa. (VLB, II, 134); Sasy nde só ixébe. - Dói-me tua ida. (Também se emprega com o gerúndio.): Sasy-eté ahẽ osóbo. - É doloroso ir-se fulano. Sasy-eté ahẽ oure'yma ixé o enõîndápe. - É muito doloroso não vir fulano ao meu chamado. (VLB, II, 75); Xe rybyt, nde nhyrõ xebo; xe rasy, xe mara'a. - Meu irmão, perdoa tu a mim; eu tenho dor, eu estou doente. (Anch., Teatro, 46); Ta sasy muru supé! - Que eles sofram junto dos malditos! (Anch., Teatro, 56); Mba'epe sasyeté a'epe tekoara supé?... - Que é mais penoso aos que estão ali? (Ar., Cat., 47v); Sasy ixébe. - Dói a mim; pesa-me (alguma coisa). (VLB, I, 105); Anhanga ratá îabépe satá rasyramo? - Como o fogo do diabo o fogo dele é penoso? (Ar., Cat., 48v); Sasy Peró supé. - Pesa a Pedro (alguma coisa); dói a Pedro (alguma coisa). (VLB, I, 105); Sasy-eté abá supé ogûe'õnama anduba. - Dói muito ao homem perceber sua morte. (Ar., Cat., 156); 2) mau, ruim: nhe'engasy - palavra ruim (VLB, I, 40); tobasy - cara ruim, mau humor (VLB, I, 140); (adv.) - demais, de doer, dolorosamente: Saîasy. - Ele está azedo demais (lit., azedo de doer). (VLB, I, 143); Osem okarype oîase'o-asykatûabo. - Saiu para o pátio chorando muito dolorosamente. (Ar., Cat., 57v) ● mba'e rasy - dor (em sentido genérico) (VLB, I, 106)",
)

# @note studio-lexical:v1 {"id":"lexical:e24748b0584ebd14de2fb57bb8bae67972321ff7352857fe8a5ab150d4fa0c68","name":"moasy","scope":"shared"}
moasy = ((mo) * (asy)).copy()
moasy.definition = "moasy (ou mboasy) (etim. - fazer doer) (v.tr.) -\n1) invejar:\nAbá mba'ekatu moasy.\nInvejar as coisas boas de alguém. (Anch., Doutr. Cristã, I, 151)\n\n2) ressentir-se de; levar a mal:\nAûîé sapirõmbyre'yma o moetee'yma oîmoasy...\nEnfim, o que não é pranteado ressente-se de não o honrarem. (Ar., Cat., 85v)\n\n3) sentir a dor de, ter dor por, lamentar:\nAîmoasy nde só.\nLamento tua ida. (VLB, II, 75)\nXe mba'e-moasy îá.\nEu lamento-me, de costume (isto é, reclamo de qualquer coisa). (VLB, I, 106)\n...O sy suí o 'aragûera moasŷabo...\nLamentando terem nascido de suas mães. (Ar., Cat., 163-163v)\n...O kaîa moasŷabo...\nTendo dor de suas queimaduras. (Ar., Cat., 161)\n\n4) arrepender-se de:\nO ekó moasy riré, abá sóû îemombegûabo...\nApós arrependerem-se de seus atos, os índios vão confessar-se. (Anch., Teatro, 38)\nNd'oîmoasyîpe amõ o nhe'engaibagûera?\nNão se arrependeram alguns de seus vitupérios? (Ar., Cat., 63)\n\n5) fazer sofrer:\nTupã sy îandé senõîa oîmoasy-katu-eté.\nO nosso chamado à mãe de Deus fá-lo sofrer muito. (Anch., Poemas, 186)"


# @note studio-lexical:v1 {"id":"lexical:ce0c12488b620b8e945019799466e0ec2062ae5c73af918e104d04c9d49c6be1","name":"eko","scope":"shared"}
eko = Noun(
    value="ekó",
    definition="(t) (s.) - lei, determinação, regra, costume (VLB, II, 19): Îori, t'ereîá sekó. - Vem, para que recebas a lei deles. (Anch., Teatro, 46); Ã tekó a'ereme moreroka. - Eis que era costume, então, batizar. (Ar., Cat., 3); ...Tekó-katu aby potare'yma - Não querendo transgredir a boa lei. (Ar., Cat., 125v); ...Asé 'anga rekorama oîmonhang asébe. - As leis de nossa alma fez para a gente. (Anch., Doutr. Cristã, I, 224) ● sekoba'e - o que é costume, o que está acostumado: Sekoba'e ixé. - Eu sou acostumado. (VLB, II, 140)",
)

# @note studio-lexical:v1 {"id":"lexical:4258266ba1a90cf97dfddc1d170496ae168d1425b87cbcbe3de25952b36a17d7","name":"ryryi","scope":"shared"}
ryryi = Verb(
    value="ryryî",
    verb_class="(v. intr.)",
    definition="(v. intr.) - tremer: ...Yby abé a'ereme... oryryîane. - Tremendo, então, a terra também. (Ar., Cat., 160); Aryryî, opá xe uba îesyî. - Tremo, ambas as minhas coxas adormeceram. (Anch., Teatro, 26); ...Asykyîé, aryryî! - Tenho medo, tremo! (Anch., Teatro, 62); Oryryî nde îuká ré... - Tremeram após te matarem. (Anch., Teatro, 122); Nde rera rendupa abé, anhanga ryryî okûapa. - Tão logo ouvindo o teu nome, o diabo está tremendo. (Anch., Poemas, 132)",
    vid=9467,
)


# @note studio-lexical:v1 {"id":"lexical:7f992c33db34699189006ce5970c50058f0617a4009ac1d4b83def320b3ebf52","name":"aipo","scope":"shared"}
aipo = Demonstrative(
    value="aîpó",
    definition="(dem. pron. e adj.) - esse (es, a, as), aquele (es, a, as), isso, aquilo: Mbobype aîpó i 'éû? - Quantas vezes disse isso? (Ar., Cat., 55v); Aîpó nhẽ-pipó ereîkó? - Porventura fazes isso à toa? (Anch., Teatro, 22); Aîpó nhõ-pipó nde rera? - Esse, somente, é de fato teu nome? (Anch., Teatro, 44); T'asó aîpó nhe'enga mopó... - Hei de ir cumprir essas palavras. (Anch., Teatro, 60); T'asó nde pyri, kori, aîpó tubixaba gûabo. - Hei de ir junto de ti, hoje, para comer aqueles reis. (Anch., Teatro, 66); Eteumẽ, aîpó tekó kuab'iré, tekó-poxy rerekóbo. - Guarda-te, após conhecer essa lei, de ter má vida. (Anch., Poemas, 158); Aîporama resé é peîmongaraíb abaré pyri. - É por isso que o batizais junto ao padre. (Ar., Cat., 127v); Abá nhe'engûerape aîpó? - Palavras de quem são essas? (Ar., Cat., 35); (adv.) eis que esse (es, a, as), eis que aquele (es, a, as): Aîpó turi. - Eis que esse vem (ouvindo sua voz, somente, não o vendo). (VLB, I, 109); Aîpó xe me'engarama ruri... - Eis que veio o que me entregará. (Ar., Cat., 53v) ● aîpó nhẽ! - É isso! Aí é que está!: Aîpó nhẽ! Xe putupab nhẽ nde ri. - Aí é que está! Eu estou surpreso por tua causa. (Léry, Histoire, 353); aîpó suí - daí, desse lugar (que tu dizes) (VLB, I, 89)",
)

# @note studio-lexical:v1 {"id":"lexical:25f0062399d189dac35cc7cf99597ef467b7dbc66e0d3f06c0d29ac985883b5f","name":"obaixuara","scope":"shared"}
obaixuara = Noun(value="obaîxûara", definition="(t) (s.) - mão de pilão (VLB, II, 32)")
obaixuara.definition = "(etim. - o que está em face) (s.) - oposto, contrário:\nMorerobîare'yma robaîxûara nhemoetee'yma.\nO contrário da soberba é a humildade. (Bettendorff, Compêndio, 15)"


# @note studio-lexical:v1 {"id":"lexical:ed11a994ac704e75c78ff5316b86b5ba42402afe97189917881fdcc17de4aa43","name":"tekateymeyma","scope":"shared"}
tekateymeyma = (-(ekateyma)).copy()
tekateymeyma.definition = "liberalidade"


# @note studio-lexical:v1 {"id":"lexical:fa428c1b8cbdf245406722ed2b77ca08827521c7764ab8756a7a8fd50010269a","name":"osanga","scope":"shared"}
osanga = Noun(
    value="osanga",
    definition="(t) (s.) - paciência, sossego (VLB, II, 62; Fig., Arte, 38): Nhemoŷrõ robaîara tosanga. - O oposto da ira é a paciência. (Ar., Cat., 18); sofrimento em padecer (VLB, II, 120), resistência; [adj.: osang (r, s)] - paciente; sossegado (Fig., Arte, 38); sofrido; resistente; (xe) padecer, sofrer, ter resistência: ...Sosang poresé. - Sofre pela gente. (Anch., Poemas, 122); Mba'e o emimborará-tyba supé og osange'ymamo. - Para as coisas que costuma sofrer não tendo paciência. (Anch., Diál. da Fé, 231); Xe rosang - Eu sou paciente. (Fig., Arte, 109); Sosang, tatá porarábo... - Sofreu, suportando o fogo. (Anch., Teatro, 54); Na xe rosangi. - Eu não tenho resistência. (VLB, II, 10)",
)


# @note studio-lexical:v1 {"id":"lexical:a24b9403bf634d8e3d8f752a10ac9e3c18d67c487facb32aca020d381f414ff5","name":"kau_a24b9403","scope":"shared"}
kau_a24b9403 = Verb(
    value="ka'u",
    verb_class="(v. intr.)",
    definition="(v. intr.) - tomar cauim, tomar bebida alcoólica: E'ikatupe abá... okagûabo...? - Pode alguém beber cauim? (Ar., Cat., 76v); T'aka'une! - Vou beber cauim! (Anch., Teatro, 10); Saraûaî, îori ekagûabo. - Sarauaia, vem para beber cauim. (Anch., Teatro, 60) ● kagûara - bebedor de cauim: Onheŷnhang umã sesé kunumĩetá kagûara... - Já se juntaram por causa disso muitos moços bebedores de cauim. (Anch., Teatro, 24); kagûaba - lugar, tempo, modo, etc. de beber cauim: Nd'e'i te'e kunumĩgûasu... oîkébo memẽ kagûápe... - Por isso mesmo os moços entram sempre no lugar de beber cauim. (Anch., Teatro, 34); Kagûápe nhõ nde ratãngatu-potá? - Somente quando bebes cauim tu queres ser valente? (Anch., Teatro, 64)",
    vid=5987,
)

# @note studio-lexical:v1 {"id":"lexical:7aef32595311391ac4c7f4efa0486398cc0c9d24bba65d7fd0ab22589d044b01","name":"oia","scope":"shared"}
oia = Noun(
    value="oîá",
    definition="(s.) - o suficiente: Mba'e 'u-eté-eté robaîara oîá nhote mba'e 'u. - O oposto do comer demais é comer somente o suficiente. (Ar., Cat., 18)",
)

# @note studio-lexical:v1 {"id":"lexical:2cd77baa999d10d68e6178c7dd0248a95c2c41e9f775332cf705dea4ea5a6e92","name":"nhote","scope":"shared"}
nhote = Adverb(
    value="nhote",
    definition="(ou îõte) (adv.) - só, somente, apenas: ...Xe pópe nhote arasó. - Nas minhas mãos, somente, levei-as. (Anch., Teatro, 46); T'îasó xe irũnamo Nhoesembépe nhote. - Vamos comigo somente até Nhoesembé. (VLB, I, 46); Opûerab é ipó xe 'anga nde nhe'enga pupé nhote. - Sara mesmo minha alma apenas com tuas palavras. (Ar., Cat., 86v) V. anhõ e nhõ.",
)

# @note studio-lexical:v1 {"id":"lexical:ca96750d1b46248bd022c11ccb3260eb69fa6fef51d644e2b4c4da6ccddb86d2","name":"meme","scope":"shared"}
meme = Conjunction(
    value="memẽ",
    definition="(conj.) - quanto mais (Anch., Arte, 57; Fig., Arte, 137) (o mesmo que memetipó - v.)",
)

# @note studio-lexical:v1 {"id":"lexical:d8ae2b9a4fa65b7878afab0ff0cb1660d56d18afa7db341fc2a4abaa36e1e758","name":"mbaeuete","scope":"shared"}
mbaeuete = (((((((u) / (eté)))) * (mbae)).var(1)).base_nominal()).copy()
mbaeuete.definition = "(etim. - o comer demais as coisas) (s.) - gula (VLB, I, 152)"

# @note studio-lexical:v1 {"id":"lexical:911559febf0f61b7d1ecd8c9e393dc9c596140f28ca8e89e84a7b5b6684ca710","name":"kauete","scope":"shared"}
kauete = ((((((kau_a24b9403)) / (eté))).var(1)).base_nominal()).copy()
kauete.definition = "ka'ueté - beber demais\n\n(s.) - bebedeira (de cauim); bebedeira em geral: Mba'e-eté ka'ugûasu... - Coisa muito boa é uma grande bebedeira. (Anch., Teatro, 6); Ixé kó ka'u resé aporomoingó îepi... - Eis que eu faço as pessoas estarem na bebedeira sempre. (Anch., Teatro, 134)\n"


# @note studio-lexical:v1 {"id":"lexical:7e8f9ad17e37da68535357cece25948f1536edb346ee20fcf9932d37f3d9a8cd","name":"ioausuba","scope":"shared"}
ioausuba = ((((love) * (îo)).var(1)).base_nominal()).copy()
ioausuba.definition = "(s.) - amizade (VLB, I, 34); amor, caridade: Tupã îoaûsuba pupé îaîkóbo, tekokatu-eté îarekó... - Estando nós no amor de Deus, a verdadeira felicidade temos. (Anch., Doutr. Cristã, I, 202); ...pe ramũîa îoaûsuba... - a amizade de vossos avós (Knivet, The Adm. Adv., 1237)"


# @note studio-lexical:v1 {"id":"lexical:b45f288b4f60cd0b5cc48a4c6bb141f18ba9afb45444e7548897e2aba14136b4","name":"ausubar","scope":"shared"}
ausubar = Verb(value='aûsubar', verb_class='(s) (v.tr.)', definition="(s) (v.tr.) - compadecer-se de, ter piedade de, ter misericórdia de, ter pena de: Oré raûsubá îepé... - Compadece-te de nós. (Anch., Poemas, 100); Eîori, oré raûsubá... - Vem para te compadeceres de nós. (Anch., Teatro, 120); Ta xe raûsubar... - Que ele se compadeça de mim... (Ar., Cat., 23v); Eresaûsubápe nde sy, nde ruba...? - Compadeceste-te de tua mãe e de teu pai? (Ar., Cat., 101); N'asaûsubari mba'e. - Não tenho pena das coisas (isto é, sou pródigo). (VLB, II, 87) ● saûsubaryba'e - o que tem misericórdia, o que tem pena: Tekokatu-eté rerekoara i poraûsubaryba'e... - Os que têm a bem-aventurança são os que têm pena das pessoas. (Ar., Cat., 19); saûsubarypyra - o que é objeto de compaixão, aquele de quem se tem pena, o que recebe compaixão: Mbobype saûsubarypyra? - Quantos são os que recebem compaixão? (Ar., Cat., 41v); aûsubaraba (ou aûsubasaba) (t) - tempo, lugar, modo, causa, etc. de se compadecer; compaixão: Tupã o aûsubaraûama resé onhemoapysyka. - Consolando-se com a compaixão de Deus. (Ar., Cat., 41); Xe raûsubasápe, xe 'anga moteni. - Por se compadecer de mim, minh'alma faz firme. (Anch., Poemas, 108)", vid=3608)


# @note studio-lexical:v1 {"id":"lexical:6422bad071b9bc0682001d6a3cd01baa950f96a7f4c1163a428c6c2401c1a9fd","name":"ete","scope":"shared"}
ete = Noun(value='eté', definition="(t) (s.) - 1) corpo: Pedro reté - o corpo de Pedro (Fig., Arte, 74); Sygépe o eterama Tupã tari... - Em seu ventre Deus recebeu seu próprio corpo. (Anch., Poemas, 88); Mba'epe asé reté remi'u? - Qual é a comida de nosso corpo? (Ar., Cat., 27v); Tupã aé, o karaíba pupé, i 'anga seté monhangi. - O próprio Deus, com sua santidade, as almas e os corpos deles fez. (Anch., Teatro, 28); Opá nde reté raíri itatîãîa pupé. - Riscaram todo o teu corpo com ferro pontiagudo. (Anch., Teatro, 120); 2) substância, matéria: Oîaby-eté seté tiruã oîkuabe'ymba'e. - Transgride-os muito o que não conhece sequer sua substância. (Bettendorff, Compêndio, 103) ● seteba'e - o que tem corpo, o que é corpóreo (VLB, I, 82)")


# @note studio-lexical:v1 {"id":"lexical:b59c12cf99b97b6cf72b9c94efd60b3b542aa97e9ab8783b5a1602fb0587316d","name":"amby","scope":"shared"}
amby = Noun(value='amby', definition='(s.) - ventrecha, parte inferior da barriga, parte do corpo entre o umbigo e a virilha; colo (Castilho, Nomes, 38): Xe ambyî arekó. - Trago-o no meu colo. (VLB, I, 77)')

# @note studio-lexical:v1 {"id":"lexical:3e2a82e7e450232cc519ce5c684cd998b2a5857969ff44f777bcd518b8661bfa","name":"bor","scope":"shared"}
bor = Noun(value='bor', definition="(suf. que expressa o agente habitual, hábito, constância, frequência): Anga îá, angaîpabora aîuká... - Como a esses, matarei os que costumam pecar. (Anch., Teatro, 92); mara'abora - o doente; miraibora - o bexigoso; kanhembora - o fujão, o que tem costume de fugir (Anch., Arte, 31)")

# @note studio-lexical:v1 {"id":"lexical:1ea0cca883aa370dd290d81e3b183c7e03ce946ce2fe3e3a154ccaa3f586fc19","name":"ambyasy","scope":"shared"}
ambyasy = ((amby) / (asy)).copy()
ambyasy.definition = "(etim. - dor de ventrecha) (s.) - fome: xe ambyasy posanga... - lenitivo de minha fome... (Valente, Cantigas, VII, in Ar., Cat., 1618); ...ambyasy, 'useîa porarábo... - sofrendo a fome e a sede (Ar., Cat., 169v); (adj.) - faminto; (xe) ter fome: I ambyasy bépe, i 'useî bépe asé îabé?... - Tinha também fome, tinha também sede como nós? (Ar., Cat., 44v); Xe ambyasy. - Eu estou faminto. (Léry, Histoire, 367) ● i ambyasyba'e - o que tem fome, o faminto (VLB, I, 134); ambyasybora - faminto (costumeiramente): Ambyasybora poîa. - Alimentar os famintos. (Ar., Cat., 18)"


# @note studio-lexical:v1 {"id":"lexical:490dcefa3d7537666bd3a356881223454161beb6c7d81edb0e281964e9f35a94","name":"aoba","scope":"shared"}
aoba = Noun(value='aoba', definition="(s.) - 1) roupa: Oîaobok serã ybŷa katupe nhẽ i moingóbo?... - Por acaso arrancaram sua roupa, fazendo-o estar nu? (Ar., Cat., 59v); Aîeruré aoba resé Pedro supé. - Peço a Pedro por roupa. (Anch., Arte, 44); 2) fato, vestido (VLB, I, 135); 3) pano; vela (de navio): Aroîyb aoba. - Amainei a vela. (VLB, I, 33); Osobá-syb aó-tinga pupé. - Limpou seu rosto com um pano branco. (Ar., Cat., 62); ybyraoba - pano de linho; amynyîu-aoba - pano de algodão (VLB, II, 64) ● aopesembûera - pedaço de roupa, retalho de pano (VLB, II, 104); iî aoba'e - o que está vestido (VLB, II, 144)")

# @note studio-lexical:v1 {"id":"lexical:6ef9c548f8d3b35362330e73ff43f948ae2715943e77c4026e74c25721887394","name":"i_katupe","scope":"shared"}
i_katupe = ((pe) * ((ae) * (katu))).copy()
i_katupe.definition = "(adv.) - nuamente, sem roupa, a nu, despido: ...Ikatupe nhẽ temõ mã...! - Oxalá ela estivesse sem roupa! (Ar., Cat., 104); ...ikatupe nde moĩndara... - o que te põe a nu (Ar., Cat., 187); ...Ikatupe nhẽpe sekóû te'yîpe? - Estava ele despido, sem mais, em público? (Ar., Cat., 62); Ikatupe aîkó. - Ando despido, vivo despido. (VLB, II, 51) ● ikatupendûara [ou ikatupesûara ou ikatupe (nhẽ) tekoara] - o que está ou anda despido (VLB, II, 51)"

# @note studio-lexical:v1 {"id":"lexical:30a543e79fe5a4671460eab76a85aaba163b883d766d2626831dd8233041fddd","name":"moaob","scope":"shared"}
moaob = ((mo) * (aoba)).copy()
moaob.definition = '(v.tr.) - vestir, pôr roupa em; fazer ter roupa: Ikatupendûara moaoba. - Vestir os nus. (Ar., Cat., 18); Aîmoaob Pedro. - Faço Pedro ter roupa. (Anch., Arte, 48v)'


# @note studio-lexical:v1 {"id":"lexical:1993a17e43a9422891d1ac540cb9985279b55942e2ec8a68b657bd5c2be4b60b","name":"sei","scope":"shared"}
sei = Verb(value='seî', verb_class='(v.tr.)', definition='(v.tr.) - querer, desejar (usado só com temas verbais incorporados): I kamu-seî kunumĩ... - Deseja o menino mamar. (Anch., Poemas, 162)', vid=9589)

# @note studio-lexical:v1 {"id":"lexical:4a80bdb3b5cf9938d4841188b19d796a5449e23397804668ece5e893f6eb2dbd","name":"y","scope":"shared"}
y = Noun(value="'y", definition="(s.) - 1) água: Oîeypyî 'y-karaíba pupé. - Asperge-se com água benta. (Ar., Cat., 24); Erur 'y ixébe. - Traze água para mim. (Léry, Histoire, 367); Asó 'y gûabo. - Vou para beber água. (VLB, I, 154); Aîeruré 'y resé. - Peço por água. (D'Evreux, Viagem, 144); 2) rio: Xe parati 'y suí aîu... - Eu vim do rio dos paratis. (Anch., Poemas, 110); 3) fonte: Kûãî 'ype. - Vai à fonte. (Léry, Histoire, 367) ● 'y-e'ẽ - água salgada (do mar) (VLB, I, 24); 'y-eté - água doce (VLB, I, 24); madre do rio, o leito dentro de suas margens, que às vezes fica descoberto (VLB, II, 27); fonte, água perene (VLB, II, 73); 'y-katu - águas tranquilas, bonança (VLB, I, 57); 'y anhẽ - água sem mistura (VLB, II, 123); 'y rapé - rego d'água (VLB, I, 65); 'y-embe'yba - margem de rio, praia, ourela de mar ou rio (VLB, II, 60); 'y-apé 'arybo - à flor d'água, na superfície da água (VLB, I, 144); 'y-apyra - cabeceiras de rio (VLB, I, 61); 'y-kûabapûana - corrente d'água (no rio ou no mar); 'y-syryka - água corrente (VLB, I, 82); maré descendente; vazante de maré (VLB, I, 91; II, 142); 'y-îebyra - remanso d'água (VLB, II, 100); 'y-pabe'ymba'e - fonte, água perene (VLB, II, 73); 'y-pytera - meio das águas, alto-mar: 'Y-pytera koty asó. - Fui em direção ao meio das águas; fui para o alto-mar. (VLB, I, 112); 'y-akã - braço de rio (VLB, I, 58); 'y-anhangoty - rio acima, a montante (VLB, II, 106); 'y-ape'ara - tona d' água, superfície d'água; 'y-ape'ara rupi - à tona d'água, na superfície da água (VLB, I, 50); 'y-apyrakoty - rio acima, a montante (VLB, II, 106); 'y-embykoty - rio abaixo, a jusante (VLB, II, 106); 'y-mombukaba - sangradouro de rio (VLB, II, 112); 'y-aíba - água ruim, água turva, água velha (D'Abbeville, Histoire, 182v)")


# @note studio-lexical:v1 {"id":"lexical:ed8a9cf2ab9371bf36fa83d64e83054815a1c8ca00feb4de6706af725d40fce5","name":"guata","scope":"shared"}
guata = Verb(value='gûatá', verb_class='(v. intr.)', definition="(v. intr.) - 1) andar, caminhar: Agûatá ko'arapukuî... - Caminhei o dia todo. (Anch., Poemas, 150); Nhũ rupi agûatá. - Ando pelo campo. (Fig., Arte, 123); Eregûatápe nhaîmbiara rupi kunhã resé? - Andaste pelos caminhos de fontes com mulheres? (Ar., Cat., 234); 2) passar: Koromõ ipó eregûatá xe rekoápe... - Logo, decerto, passarás no lugar onde moro. (Anch., Poemas, 156); 3) seguir, andar (no sentido de deslocar-se em meio de transporte): Paranã rupi agûatá. - Segui pelo mar (em navio). 'Y rupi agûatá. - Andei pelo rio (de barco). (VLB, II, 48); 4) passear: Abaregûasu ogûatá. - O bispo passeia. (Fig., Arte, 6) ● ogûataba'e - o que anda, o que caminha, o caminhante; o que passeia, o que passa: ...pé rupi ogûataba'e... - os que andam pelo caminho (Ar., Cat., 63); gûatasaba - tempo, lugar, modo, etc. de andar, de passar, de passear; caminhada, passeio, etc.: Xe anama gûatasápe, nde morerekoá sesé. - Ao passar minha família, tu cuidavas dela. (Anch., Poemas, 154); guatá-tenhẽ - andar à toa, andar de cá para lá, vaguear: Agûatá-gûatá-tenhẽ. - Fico andando à toa. (VLB, II, 140)", vid=4469)


# @note studio-lexical:v1 {"id":"lexical:5cad3ee5039d2ae68ad1bed415b0e5fd92d94b7cfe8852c1a674e26526837c69","name":"pea_5cad3ee5","scope":"shared"}
pea_5cad3ee5 = Verb(value="pe'a", verb_class='(v.tr.)', definition="(v.tr.) - 1) desterrar, degredar: Xe pe'a umẽ îepé - Não me desterres tu. (Valente, Cantigas, I, in Ar., Cat., 1618); 2) afastar, desviar, repelir, apartar (p.ex., os que lutam, os que brigam): ...anhanga pe'abo... - afastando o diabo (Anch., Poemas, 108); Aîpe'a umûã emonã xe angaîpaba. - Já afastei dessa maneira minhas maldades. (VLB, II, 129); Oîpe'ape i angaîpaba'e i angaturamba'e suíne? - Afastará os que são maus dos que são bons? (Ar., Cat., 47); Eîpe'a pabenhẽ mba'e-memûã oré suí. - Afasta todas as coisas más de nós. (Thevet, Cosm. Univ., II, 925); 3) separar, reservar, preservar: I 'anga seté pupé i mondepa bé, Tupã i pe'aû. - Assim que pôs sua alma em seu corpo, Deus a preservou. (Ar., Cat., 9); 4) deixar de: ...Tupã osaûsupe'a... - Deus deixou de amá-los. (Anch., Teatro, 28); 5) evitar (Marcgrave, Hist. Nat. Bras., 277) ● i pe'apyra - o que é (ou deve ser) desterrado, degredado, afastado, etc.; excomungado: Orosapuká-pukaî i pe'apyramo... - Ficamos bradando, como desterrados. (Ar., Cat., 14); ...I angaturamba'e suí i pe'apyra (..). - Afastados dos que são bons. (Ar., Cat., 49v); pe'asaba - tempo, lugar, modo, etc. de desterrar, de afastar, etc.; desterro: ...Ikó îope'asagûera syk'iré esepîakukar orébe. - Após acabar este desterro comum, faze a nós vê-lo. (Ar., Cat., 14v); emipe'a (t) - o que alguém desterra, repele, separa, etc.: Sasyeté niã Tupã remipe'apûera... - Eis que sofrem muito os que Deus repeliu. (Ar., Cat., 163)", vid=8510)

# @note studio-lexical:v1 {"id":"lexical:7b7fe4a2716f3558429b4e4d5b82d68d1b82fa5e4be09cbebd055c7e6dc953aa","name":"obaiara","scope":"shared"}
obaiara = Noun(value='obaîara', definition="(t) (s.) - 1) o contrário, o oposto: aîpó tekoangaîpaba robaîara... - o oposto daqueles pecados (Ar., Cat., 18); 2) inimigo, adversário: Îandé robaîareté te'õ. - Nossa verdadeira inimiga é a morte. (Ar., Cat., 155); Kaburé, îori enhana tobaîara t'îa'u! - Caburé, vem correndo para que comamos os inimigos! (Anch., Teatro, 64); Morobaîaramo aîkó. - Sou inimigo das pessoas. (VLB, I, 144). V. tb. sumarã e upîara (t).")


# @note studio-lexical:v1 {"id":"lexical:b876c84a7ddd66a02907667783498c12af5beea0da0a54ac207ca98b0c3781be","name":"sem","scope":"shared"}
sem = Verb(value='sem', verb_class='(v. intr.)', definition="(ou sẽ) (v. intr.) - 1) sair: Osem oîkobébo o tym-y roîré... - Saiu vivendo após o enterrarem. (Anch., Poemas, 124); T'osẽ anhanga i xuí... - Que saia o diabo dela. (Anch., Poemas, 146); Osem okarype... - Saiu para o pátio. (Ar., Cat., 57v); 2) mudar (a casa, indo para outra parte); mudar-se (para longe): Asem. - Mudo-me. (VLB, II, 44); 3) despontar; nascer (o sol): Otĩ kûarasy osema nde beraba robaké. - Envergonha-se o sol, nascendo, diante de teu brilho. (Valente, Cantigas, IV, in Ar., Cat., 1618) ● sembaba - tempo, lugar, modo, etc. de sair; saída: kûara sembaba - lugar de sair do sol, o nascente; kûarasy sembaba - a saída do sol, o nascer do sol (VLB, II, 46); Oîkuá-katupe a'e suí o semagûama? - Sabem bem de sua futura saída dali? (Ar., Cat., 48v)", vid=9596)

# @note studio-lexical:v1 {"id":"lexical:07c1b0cd7471fb9b7723b3b00c0e610c44bd7154c0d5d7e691a438d9728c4ee1","name":"miausuba","scope":"shared"}
miausuba = (((emi) * (love)).var(1)).copy()
miausuba.definition = "[ou (e)mbiaûsuba)] (r, s) (s.) - escravo: A'epe miaûsuba n'osapîari xûé o îara nhe'engane? - E o escravo não obedecerá às palavras de seu senhor? (Ar., Cat., 69); Miaûsuba îabépe serekóûne? - Trata-la-á como uma escrava? (Anch., Doutr. Cristã, I, 228); xe remiaûsuba - meu escravo (Léry, Histoire, 368); Nd'e'i te'e miasûbetá ikó 'ara momoranga. - Por isso mesmo os escravos festejam este dia. (Anch., Poemas, 192)"

# @note studio-lexical:v1 {"id":"lexical:26169d1f10a306b1c0dde906320971052b6d3cb90d255c0079bfb4ae9f5bed88","name":"enosem_26169d1f","scope":"shared"}
enosem_26169d1f = (((ero) * (sem)).var(1)).copy()
enosem_26169d1f.definition = "(v.tr.) - 1) retirar, arrancar, fazer sair consigo: Mamõpe Pilatos senosemi a'ereme? - Para onde Pilatos retirou-o, então? (Ar., Cat., 60v); Kó nhõ anosẽ îepé moxy suí... - Na verdade, somente estas retirei dos malditos. (Anch., Poemas, 150); 2) resgatar: I momiaûsubypyra renosema. - Resgatar os cativos. (Ar., Cat., 18v); 3) desembarcar, descarregar (p.ex., embarcação): Anosem mba'e ygara suí. - Descarreguei as coisas da canoa. (VLB, I, 97) ● enosemara (t) - o que retira, o que resgata: ...N'oîeruré-pytubari Tupã supé ogûenosemarûera resé. - Não se cansam de pedir a Deus pelos que os resgataram. (Ar., Cat., 8v); enosembaba (t) - tempo, lugar, modo, etc. de retirar; retirada: Arobîar... asé rubypy-karaibetá 'angûera a'epe turama osarõba'e renosemagûera bé. - Creio que ele retirou também as almas dos nossos primeiros e santos pais (da mansão dos mortos), que aí esperavam sua vinda. (Ar., Cat., 16); emienosema (t) - o retirado, o que alguém faz sair consigo, o que alguém retira: Marãpe a'e semienosegûama rekóû a'epe? - Que faziam aí os que ele faria sair consigo? (Ar., Cat., 44); Anosẽ-nosem (ou Anosẽ-nosemĩ). - Vivo retirando-o; Anosẽ-sem. - Vivo retirando-as [quando são muitas coisas]. (VLB, II, 129)"


# @note studio-lexical:v1 {"id":"lexical:e131e2a444021fe8e39a36e382dab395c51c92540985f0550b0ffc64d1ee3fa7","name":"ikotebe","scope":"shared"}
ikotebe = Verb(value='ikotebẽ', verb_class='(v. intr. irreg.)', definition="/ ekotebẽ (t) (v. intr. irreg.) - afligir-se, estar aflito; estar triste; estar receoso, angustiar-se: Akûeîme aîkotebẽ, xe rekopoxy purûabo. - Antigamente estava aflito, praticando meus vícios. (Anch., Poemas, 130); A'epe Îudas n'oîkotebẽî Îudeus supé o îara me'engagûera resé? - E Judas não se afligiu junto aos judeus por entregar a seu senhor? (Ar., Cat., 57v); Putunusu porarábo, oroîkotebẽngatu. - Suportando a escuridão, estamos muito aflitos. (Anch., Poemas, 142) ● oîkotebẽba'e - o que se aflige, o aflito: Oîkotebẽba'e moapysyka. - Consolar os aflitos. (Ar., Cat., 18v); ekotebẽsaba (t) - tempo, lugar, modo, etc. de afligir-se; aflição: ...A'e xe rekotebẽsaba oîme'eng ixébene... - Ele dará para mim minha aflição. (Ar., Cat., 25v)", vid=5219)

# @note studio-lexical:v1 {"id":"lexical:1b1963fa983b96e6d877bb1c823d0bfdcb6ae0cf33c411fe5d47a04b4c0fc7a3","name":"apysyka","scope":"shared"}
apysyka = Noun(value='apysyka', definition="(s.) - satisfação; consolo, sossego, agrado; (adj.: apysyk) - 1) satisfeito, farto (inclusive do que se come): Xe apysy-katu sekoápe. - Estava muito satisfeito na morada deles. (Anch., Teatro, 10); 2) (xe) consolar-se; quietar-se internamente consigo; sossegar, estar sossegado; satisfazer-se: Îasepenhan, îaîpysyk i apysyk' e'ymebé... - Ataquemo-los, prendamo-los antes que se consolem... (Anch., Teatro, 66); ...Sesé nhõ abá resá apysykamo ybakype... - Somente com Ele os olhos dos homens se satisfazem no céu. (Ar., Cat., 167); Pe apysykĩ serã peîkóbo pe rekomemûã aty-atyra pupé...? - Será que estais sossegados, sem mais, com vossos montes de maldades? (Ar., Cat., 166): Na nde apysyki, tobaîara rekorama kuabe'yma... - Tu não sossegas, não sabendo as ações dos inimigos. (Ar., Cat., 158); 3) (xe) agradar-se, regozijar-se, gostar [compl. com esé (r, s)]: Xe apysyk (mba'e) resé. - Agrado-me com as coisas. (VLB, I, 27, adapt.); I apysyk pabẽ sesé. - Todos gostaram delas. (Anch., Poesias, 259); 4) (xe) bastar a (compl. verbal no gerúndio): N'i apysyki xûépemo serobîasara o py'ape nhote serobîá? - Não bastaria ao crente acreditar nele em seu coração somente? (Bettendorff, Compêndio, 33) ● apysykaba - tempo, lugar, modo, causa, etc. de se consolar; consolo: Mba'epe asé apysykabamo a'ereme? - Qual é nosso consolo, então? (Ar., Cat., 92v)")


# @note studio-lexical:v1 {"id":"lexical:1f2d562166bf2e58985667a1e8b83eb111de9dfcc91136a62f5b25c0d808a575","name":"teombuera","scope":"shared"}
teombuera = ((pûera) * (eo)).copy()
teombuera.definition = "(t) (s.) - corpo morto; defunto; cadáver (de homem ou animal): pirá re'õmbûera - corpo morto de peixe (VLB, I, 82); A'epe asé re'õmbûera, marã? - E os cadáveres da gente, que sucede a eles? (Ar., Cat., 27); Aseîá kó se'õmbûera. - Deixei esse cadáver seu. (Anch., Teatro, 160); ...Oîoybyri se'õmbûera paranã ybyri i kûáî. - Lado a lado seus cadáveres ao longo do mar estavam. (Anch., Teatro, 52)"


# @note studio-lexical:v1 {"id":"lexical:1994069deab25c7936baa8de0e74cc81c18c17ef68bf3c74f630469f989dc14a","name":"eko_1994069d","scope":"shared"}
eko_1994069d = Noun(value='ekó', definition="(t) (s.) - fato, coisa; acontecimento: ...Tekorama mombegûabo. - Anunciando os acontecimentos futuros. (Ar., Cat., 159v); Nd'e'ikatuî abá îuru Anhanga ratápe tekó-asyeté mombegûabo. - Não pode a boca de ninguém contar as coisas muito dolorosas no inferno. (Ar., Cat., 163); Oîepé mi'u pupé esepîak tekó paraba... - Dentro de um só pão vê tu a variedade de coisas. (Valente, Cantigas, VIII, in Ar., Cat., 1618); Nd'e'ikatuîpe abaréramo oîkoe'ymba'e emonã tekó monhanga? - Não pode o que não é padre fazer as coisas assim? (Ar., Cat., 93v); I porangeté ã tekó îandébe. - São muito belas estas coisas para nós. (Léry, Histoire, 355)")

# @note studio-lexical:v1 {"id":"lexical:5f23bcf7b35257423f7cc365b21a0f1449db68a1853b30538d74688554162082","name":"kuab","scope":"shared"}
kuab = Verb(value='kuab', verb_class='(v.tr.)', definition="(ou kuá ou kugûab) (v.tr.) - 1) - conhecer, saber: Marãpe i kugûabine? - Como o saberão? (Anch., Doutr. Cristã, I, 229); Tupana kuapa, ko'y asaûsu xe îara Îesu. - Conhecendo a Deus, agora amo meu senhor Jesus. (Anch., Poemas, 106); N'aîkuabi a'e abá... - Não conheço esse homem. (Ar., Cat., 57); 2) reconhecer, conhecer de novo: ...O îarĩ kuapa aunhenhẽ. - Seu senhorzinho reconhecendo imediatamente. (Anch., Poemas, 118); 3) agradecer, reconhecer (algum bem): Aîkugûab. - Agradeci-o. (VLB, I, 23); Marãnamope asé santos 'ara kuabi? - Por que a gente reconhece o dia dos santos? (Ar., Cat., 24); 4) adivinhar: ...Eîkuá ra'u nde ri opûaryba'e...! - Adivinha, vamos ver, aquele que bateu em ti! (Ar., Cat., 56v); 5) interpretar (VLB, II, 13); 6) julgar (o que é duvidoso) (VLB, II, 16); 7) perceber, sentir: N'aîkugûabi xe îybá (ou xe îybá-e'õ). - Não sinto meu braço (ou meu braço morto). (VLB, II, 130) ● oîkuaba'e (ou oîkuabyba'e) - o que conhece - Oîabyeté seté tiruã oîkuabe'ymba'e. - Transgride-os muito o que não conhece sequer sua substância. (Bettendorff, Compêndio, 103); kuapara - conhecedor, o que conhece, sabedor: Abá angaîpá-nhemima i kuapare'yma supé mombegûabo. - Contando os pecados escondidos de alguém para quem não os conhece. (Ar., Cat., 73v); kuapaba: lugar, tempo, modo, instrumento, etc. de conhecer, de reconhecer, etc.; conhecimento, reconhecimento: A'e kuapápe, ko'y asaûsu... - Por conhecê-lo, agora amo-o. (Anch., Poemas, 108); Oîkuapá-me'eng umûãpe Îudas Îandé Îara îudeus supé erimba'e? - Já tinha dado Judas aos judeus o meio de reconhecer Nosso Senhor? (Ar., Cat., 54); eminguaba (t) - o que alguém sabe, o conhecido, o sabido: ...O eminguá-katue'yma oîmombe'uba'e... - O que conta o que não sabe bem... (Ar., Cat., 67); i kuabypyra - o conhecido, o sabido: ...Se'yî i kuabypyre'yma... - São numerosos os que não são conhecidos. (Ar., Cat., 37); i kugûabypypabẽ - o que é totalmente conhecido, coisa notória por fama (VLB, II, 51); i kuabypyre'yma - o que não é conhecido, coisa secreta (VLB, II, 114)", vid=6145)

# @note studio-lexical:v1 {"id":"lexical:015b56261e7508eceb6e3bda55ca0af85a7ffea5ffe00872e31708b9da05076b","name":"tekokuab","scope":"shared"}
tekokuab = ((eko_1994069d) / (kuab)).copy()
tekokuab.definition = "(ou tekokugûaba) (etim. - conhecimento dos fatos) (s.) - prudência; sabedoria, entendimento, conhecimento, compreensão, juízo, saber natural [à diferença de mba'ekuaba (v.), que é o saber adquirido], instinto natural, razão. (Neste termo, o t- é forma fixa e não um prefixo de relação. Ele nunca é substituído por r- ou s-.): Xe tekokuaba opá amokanhem. - Meu entendimento todo fiz desaparecer. (Anch., Poemas, 106); (adj.: tekokuab ou tekokugûab) - ajuizado, entendido, que tem discernimento, prudente, sábio: abá-tekokugûá-katu - homem muito entendido (VLB, I, 48); (xe) saber, ser conhecedor (das coisas): Na xe tekokuabi. - Eu não sei (sou ignorante). (VLB, II, 48); Anhẽ, n'i tekokuabi... - Na verdade, não são conhecedores das coisas. (Anch., Teatro, 38)"


# @note studio-lexical:v1 {"id":"lexical:393f120b0e1cc92b70b4f2c1d9b942a502d99132636b920510cf20ddd9af5dda","name":"tebe","scope":"shared","lexicalStatus":"hypothetical"}
tebe = Noun(value='tebẽ', definition='faz parte de ikotebẽ, não é uma palavra que se vê solta mas é óbvio que a outra parte é ikó/ekó verbo estar/ser então podemos inferir que dá para quebrar um pouco mais', tag='[NOUN][LEXICAL_STATUS:HYPOTHETICAL]')

# @note studio-lexical:v1 {"id":"lexical:a75ef014f058a15a6768dcea490e82c2333b563fc4e8b565c2c49ec6901e3e64","name":"ikotebe_a75ef014","scope":"shared","lexicalStatus":"hypothetical"}
ikotebe_a75ef014 = ((ikó) / (tebe)).copy()
ikotebe_a75ef014.definition = "/ ekotebẽ (t) (v. intr. compl. posp. irreg.) - carecer, ter falta, necessitar [de algo ou de alguém: compl. com esé (r, s)]: ...O monhemombe'ûarama resé oîkotebẽmo... - Tendo falta de um confessor seu. (Ar., Cat., 76); ...Gûemi'urama resé oîkotebẽbo nhẽ... - Necessitando de sua comida. (Ar., Cat., 78)"


# @note studio-lexical:v1 {"id":"lexical:7681b9ad85c5dceb911cd5fb00a4d5cb2f7aca4102e5b69b954752e7e35f6c33","name":"enonhen","scope":"shared"}
enonhen = Verb(value='enonhen', verb_class='(s) (v.tr.)', definition="(ou enonhẽ) (s) (v.tr.) - 1) repreender; corrigir, doutrinar em costumes (p.ex., o pai ao filho): Enonhẽ, eîakaká, t'oîepysyrõ-motá anhanga ratá suí. - Corrige-os, censura-os, para que queiram livrar-se do inferno. (Anch., Poemas, 158); Morubixaba tuîba'e onhe'eng memẽ i xupé, senonhena, i akakapa. - Os chefes velhos falam sempre a eles, repreendendo-os, censurando-os. (Anch., Teatro, 34); 2) reprimir: Mba'e-aí-potara renonhena. - Reprimir o desejo de coisas más. (Ar., Cat., 19v) ● enonhẽndara (t) - o repreensor, o que corrige, o que repreende: E'ikatu ipó senonhẽndarama supé é... - Pode certamente (contá-lo) para quem o repreenderá. (Ar., Cat., 73v)", vid=4050)

# @note studio-lexical:v1 {"id":"lexical:305f21d1e119a992c7dde2c9946a1886d760f197e9e29b90641f33800f20aa83","name":"ikomemua","scope":"shared"}
ikomemua = ((ikó) / (memûã)).copy()
ikomemua.definition = "/ ekomemûã (t) (etim. - agir mal) (v. intr. irreg.) - 1) fazer o que não deve, errar, pecar: -Marãpe ereîkó kaûĩ suí esabeypó? Ereîkomemûãpe a'ereme? - Como ages embriagando-te de cauim? Fazes o que não deves, então? (Ar., Cat., 111v); 2) desequilibrar-se, comportar-se estranhamente, entrar em colapso: ...Kûarasy, îasy, yby, paranã rekomemûã roiré... a'ereme karaibebé ruri... - Após entrarem em colapso o sol, a lua, a terra, o mar, então os anjos vêm. (Ar., Cat., 160v) ● oîkomemûãba'e - o que erra, etc.: Oîkomemûãba'e renonhena. - Corrigir os que erram. (Bettendorff, Compêndio, 23)"

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
