import os
import sys

# Use local pydicate checkout for hot-reload during development.
sys.path.insert(
    0,
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..", "nhe-enga", "pydicate")
    ),
)
sys.path.insert(
    0,
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..", "nhe-enga", "tupi")
    ),
)

from pydicate.lang.tupilang import *
from pydicate.lang.tupilang.pos import *

subject_pronouns = {
    "1ps": ixé,
    "1ppi": îandé,
    "1ppe": oré,
    "2ps": endé,
    "2pp": pee,
    "3p": ae,
}
object_pronouns = {
    "1ps": xe,
    "1ppi": îandé,
    "1ppe": oré,
    "2ps": nde,
    "2pp": pee,
    "3p": ae,
    "mut": îe,
    "refl": îo,
}

# iterate through all verbs
test_cases_map = {
    "indicativo": [
        # Ixe
        # ("1ps", "1ps"),
        ("1ps", "2ps"),
        ("1ps", "2pp"),
        ("1ps", "3p"),
        ("1ps", "refl"),
        # Oré
        # ("1ppe", "1ppe"),
        ("1ppe", "2ps"),
        ("1ppe", "2pp"),
        ("1ppe", "3p"),
        ("1ppe", "refl"),
        ("1ppe", "mut"),
        # Îandé
        ("1ppi", "3p"),
        ("1ppi", "refl"),
        ("1ppi", "mut"),
        # Endé
        ("2ps", "1ps"),
        ("2ps", "1ppe"),
        # ("2ps", "2ps"),
        ("2ps", "3p"),
        ("2ps", "refl"),
        # pee
        ("2pp", "1ps"),
        ("2pp", "1ppe"),
        # ("2pp", "2pp"),
        ("2pp", "3p"),
        ("2pp", "refl"),
        ("2pp", "mut"),
        # a'e
        ("3p", "1ps"),
        ("3p", "1ppe"),
        ("3p", "1ppi"),
        ("3p", "2ps"),
        ("3p", "2pp"),
        ("3p", "3p"),
        ("3p", "refl"),
        ("3p", "mut"),
    ],
    "gerundio": [
        ("1ps", "1ps"),
        ("1ppe", "1ppe"),
        ("1ppi", "1ppi"),
        ("2ps", "2ps"),
        ("2pp", "2pp"),
        ("3p", "3p"),
        ("refl", "refl"),
        ("mut", "mut"),
    ],
    "circunstancial": [
        # ixe
        ("1ps", "refl"),
        ("1ps", "mut"),
        ("1ps", "1ppe"),
        ("1ps", "1ppi"),
        ("1ps", "2ps"),
        ("1ps", "2pp"),
        ("1ps", "3p"),
        # oré
        ("1ppe", "1ps"),
        ("1ppe", "refl"),
        ("1ppe", "mut"),
        ("1ppe", "2ps"),
        ("1ppe", "2pp"),
        ("1ppe", "3p"),
        # iande
        ("1ppi", "1ps"),
        ("1ppi", "refl"),
        ("1ppi", "mut"),
        ("1ppi", "3p"),
        # a'e
        ("3p", "1ps"),
        ("3p", "1ppe"),
        ("3p", "1ppi"),
        ("3p", "2ps"),
        ("3p", "2pp"),
        ("3p", "3p"),
        ("3p", "refl"),
        ("3p", "mut"),
    ],
    "imperativo": [
        # ende
        ("2ps", "1ps"),
        ("2ps", "1ppe"),
        ("2ps", "2ps"),
        ("2ps", "3p"),
        # pe'e
        ("2pp", "1ps"),
        ("2pp", "1ppe"),
        ("2pp", "2pp"),
        ("2pp", "3p"),
    ],
}
test_cases_map["permissivo"] = test_cases_map["indicativo"]
test_cases_map["conjuntivo"] = test_cases_map["indicativo"]

__all__ = [
    "subject_pronouns",
    "object_pronouns",
    "test_cases_map",
]
