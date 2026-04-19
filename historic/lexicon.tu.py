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
# 'i / 'é1 (v. intr. irreg.) 1) dizer: Marã e'ipe asé, karaibebé o arõana mongetábo? - Que a gente diz, conversando com o anjo seu guardião? (Ar., Cat., 23v); Aîpó eré supikatu... - Isso dizes com razão... (Anch., Teatro, 32); 2) rezar, enunciar-se, prescrever: Aîpó tekoangaîpaba robaîara nã e'i. - Os opostos daqueles pecados assim se enunciam. (Ar., Cat., 18); 3) querer dizer, querer significar, pensar, supor, presumir, cogitar, julgar: Marã e'ipe asé o py'ape aîpó o'îabo i xupé? - Que quer dizer a gente em seu coração, dizendo isso para ela? (Ar., Cat., 31v); "Osó ipó re'a" a'é. - Presumo que ele deve ter ido. (VLB, II, 86); 4) concluir, julgar por indícios: Emonã ûĩ re'a a'é. - Concluo que talvez isso seja assim. (VLB, II, 16); Amõ îuká-potá ûĩ sekóû a'é. - Concluí que ele está querendo matar alguém. (VLB, II, 16) ● e'iba'e - o que diz: Mendara... "xe mena koîpó xe remirekó re'õ ré t'îamendar îandé îoesé" e'iba'e, se'õ nhẽ roîré nd'e'ikatuî sesé omendá. - O cônjuge que diz: "-Após a morte de meu marido ou de minha esposa havemos de nos casar", após sua morte não pode casar-se com ele (ou ela) (Ar., Cat., 1686, 279-280); 'îara (ou e'îara) - o que diz; o indicador: Îaîuká memẽ aîpó 'îara... - Matemos juntos o que diz isso. (Ar., Cat., 79); ...Îasytatá serekoarama resé... pé 'îaramo i xupé... - Por causa da estrela sua guardiã,... como indicadora do caminho para eles. (Ar., Cat., 3); ...Marã e'îara... - As que dizem coisas más. (Anch., Teatro, 36); "...-Our temõ anhanga xe rerasóbo mã" e'îara. - O que diz: -Oxalá venha o diabo para me levar... (Ar., Cat., 67); 'îaba (ou 'eaba ou 'esaba) - 1) tempo, lugar, modo, etc. de dizer; o dizer: Okaî oupa aûîeramanhẽ... o îurupe nhote aîpó o 'eagûera repyramo. - Estão queimando para sempre como pena de dizerem isso somente em suas bocas. (Ar., Cat., 1686, 248); 2) o que alguém diz, o chamado por alguém, o dito: Ybytyra Monte Calvário 'îápe... - Para o monte chamado Calvário (Ar., Cat., 89); Erimba'epe aîpó nde 'îaba ereîmopóne? - Quando cumprirás isso que tu dizes? (Ar., Cat., 111v); O'u nhẽpe a'e 'ybá, tegûama, Tupã 'îaba? - Comeu aquele fruto, causa da morte, que Deus dissera? (Ar., Cat., 40v); Aîpó i 'eagûera rerekóbo, semimbo'e-etá... miapé rari o pópe... - Tendo isso que ele disse, seus discípulos tomaram o pão em suas mãos. (Ar., Cat., 84v)
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
