import importlib.util
import os
import sys


from authoring.source_annotations import attest, loc


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
