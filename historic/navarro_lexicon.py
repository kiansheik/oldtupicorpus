"""Safe access to the generated Navarro lexical registry.

The JSON registry contains data, never executable Python.  This module accepts
only the lexical constructors explicitly supported by Pydicate and passes only
validated JSON scalar keyword arguments to those constructors.  Each lookup
creates a new predicate object so a passage cannot mutate a shared registry
prototype.
"""

from __future__ import annotations

import inspect
import json
import keyword
import math
import sys
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from types import MappingProxyType
from typing import Mapping, TypeAlias


_ENGINE_ROOT = Path(__file__).resolve().parents[2] / "nhe-enga"
for _dependency in (_ENGINE_ROOT / "pydicate", _ENGINE_ROOT / "tupi"):
    if str(_dependency) not in sys.path:
        sys.path.insert(0, str(_dependency))

from pydicate.lang.tupilang.pos import (
    Adverb,
    Conjunction,
    Copula,
    Demonstrative,
    Interjection,
    Noun,
    Number,
    Particle,
    Postposition,
    Pronoun,
    ProperNoun,
    SizeSuffix,
    Verb,
)


SCHEMA_VERSION = 1
DEFAULT_REGISTRY_PATH = Path(__file__).with_name("navarro_lexicon.json")
ENTRY_STATUSES = frozenset({"shared_existing", "dictionary_only"})

_CONSTRUCTORS = MappingProxyType(
    {
        constructor.__name__: constructor
        for constructor in (
            Noun,
            ProperNoun,
            Pronoun,
            Verb,
            Adverb,
            Postposition,
            Interjection,
            Number,
            Particle,
            Conjunction,
            Demonstrative,
            Copula,
            SizeSuffix,
        )
    }
)
_REQUIRED_ENTRY_KEYS = frozenset(
    {
        "registry_id",
        "name",
        "constructor",
        "values",
        "headword",
        "definition",
        "status",
    }
)
_COVERAGE_COUNTS = (
    "total_rows",
    "tupi_source_rows",
    "supported_source_rows",
    "unresolved_source_rows",
    "registry_entries",
    "shared_existing_entries",
    "dictionary_only_entries",
)

Scalar: TypeAlias = str | int | float | bool | None


class NavarroLexiconError(ValueError):
    """The checked-in registry does not satisfy its data contract."""


@dataclass(frozen=True)
class NavarroLexiconEntry:
    registry_id: str
    name: str
    constructor: str
    values: Mapping[str, Scalar]
    headword: str
    definition: str
    status: str
    shared_name: str | None = None


@dataclass(frozen=True)
class NavarroLexiconRegistry:
    source: Mapping[str, object]
    coverage: Mapping[str, object]
    entries: tuple[NavarroLexiconEntry, ...]
    unresolved: tuple[Mapping[str, object], ...]
    _by_registry_id: Mapping[str, NavarroLexiconEntry]
    _by_name: Mapping[str, NavarroLexiconEntry]

    def lookup(self, registry_id_or_name: str) -> NavarroLexiconEntry:
        if not isinstance(registry_id_or_name, str) or not registry_id_or_name:
            raise NavarroLexiconError(
                "Navarro registry lookup requires a non-empty string"
            )
        entry = self._by_registry_id.get(registry_id_or_name)
        if entry is None:
            entry = self._by_name.get(registry_id_or_name)
        if entry is None:
            raise KeyError(f"Unknown Navarro registry entry: {registry_id_or_name}")
        return entry


def _nonnegative_int(value: object, label: str) -> int:
    if type(value) is not int or value < 0:
        raise NavarroLexiconError(f"{label} must be a non-negative integer")
    return value


def _count_map(value: object, label: str) -> dict[str, int]:
    if not isinstance(value, dict):
        raise NavarroLexiconError(f"{label} must be an object")
    result: dict[str, int] = {}
    for key, count in value.items():
        if not isinstance(key, str) or not key:
            raise NavarroLexiconError(f"{label} keys must be non-empty strings")
        result[key] = _nonnegative_int(count, f"{label}.{key}")
    return result


def _identifier(value: object, label: str) -> str:
    if (
        not isinstance(value, str)
        or not value
        or not value.isidentifier()
        or keyword.iskeyword(value)
    ):
        raise NavarroLexiconError(f"{label} must be a usable Python identifier")
    return value


def _entry(raw: object, index: int) -> NavarroLexiconEntry:
    label = f"entries[{index}]"
    if not isinstance(raw, dict):
        raise NavarroLexiconError(f"{label} must be an object")
    missing = sorted(_REQUIRED_ENTRY_KEYS.difference(raw))
    if missing:
        raise NavarroLexiconError(f"{label} is missing: {', '.join(missing)}")

    registry_id = raw["registry_id"]
    if not isinstance(registry_id, str) or not registry_id:
        raise NavarroLexiconError(f"{label}.registry_id must be a non-empty string")
    name = _identifier(raw["name"], f"{label}.name")
    constructor_name = raw["constructor"]
    if constructor_name not in _CONSTRUCTORS:
        raise NavarroLexiconError(
            f"{label}.constructor is unsupported: {constructor_name!r}"
        )
    values = raw["values"]
    if not isinstance(values, dict):
        raise NavarroLexiconError(f"{label}.values must be an object")
    checked_values: dict[str, Scalar] = {}
    for key, value in values.items():
        if not isinstance(key, str) or not key:
            raise NavarroLexiconError(f"{label}.values keys must be non-empty strings")
        if type(value) not in {str, int, float, bool, type(None)}:
            raise NavarroLexiconError(
                f"{label}.values.{key} must be a JSON scalar or null"
            )
        if isinstance(value, float) and not math.isfinite(value):
            raise NavarroLexiconError(f"{label}.values.{key} must be finite")
        checked_values[key] = value
    try:
        inspect.signature(_CONSTRUCTORS[constructor_name]).bind(**checked_values)
    except TypeError as exc:
        raise NavarroLexiconError(
            f"{label}.values do not match {constructor_name}: {exc}"
        ) from exc

    headword = raw["headword"]
    definition = raw["definition"]
    status = raw["status"]
    if not isinstance(headword, str) or not headword:
        raise NavarroLexiconError(f"{label}.headword must be a non-empty string")
    if not isinstance(definition, str):
        raise NavarroLexiconError(f"{label}.definition must be a string")
    if checked_values.get("definition") != definition:
        raise NavarroLexiconError(
            f"{label}.values.definition must equal the entry definition"
        )
    headword_key = "inflection_or_verbete" if constructor_name == "Pronoun" else "value"
    if checked_values.get(headword_key) != headword:
        raise NavarroLexiconError(
            f"{label}.values.{headword_key} must equal the entry headword"
        )
    if status not in ENTRY_STATUSES:
        raise NavarroLexiconError(
            f"{label}.status must be one of {sorted(ENTRY_STATUSES)}"
        )
    shared_name = raw.get("shared_name")
    if shared_name is not None:
        shared_name = _identifier(shared_name, f"{label}.shared_name")
        if status != "shared_existing":
            raise NavarroLexiconError(
                f"{label}.shared_name requires status 'shared_existing'"
            )
    elif status == "shared_existing":
        raise NavarroLexiconError(
            f"{label}.shared_name is required for status 'shared_existing'"
        )

    return NavarroLexiconEntry(
        registry_id=registry_id,
        name=name,
        constructor=constructor_name,
        values=MappingProxyType(checked_values),
        headword=headword,
        definition=definition,
        status=status,
        shared_name=shared_name,
    )


def _validate_document(raw: object) -> NavarroLexiconRegistry:
    if not isinstance(raw, dict):
        raise NavarroLexiconError("Navarro registry root must be an object")
    if raw.get("schema_version") != SCHEMA_VERSION:
        raise NavarroLexiconError(
            f"Unsupported Navarro registry schema: {raw.get('schema_version')!r}"
        )
    source = raw.get("source")
    if not isinstance(source, dict):
        raise NavarroLexiconError("source must be an object")
    if not isinstance(source.get("dataset_fingerprint"), str) or not source.get(
        "dataset_fingerprint"
    ):
        raise NavarroLexiconError(
            "source.dataset_fingerprint must be a non-empty string"
        )
    coverage = raw.get("coverage")
    if not isinstance(coverage, dict):
        raise NavarroLexiconError("coverage must be an object")
    counts = {
        key: _nonnegative_int(coverage.get(key), f"coverage.{key}")
        for key in _COVERAGE_COUNTS
    }
    entries_by_constructor = _count_map(
        coverage.get("entries_by_constructor"), "coverage.entries_by_constructor"
    )
    unresolved_by_reason = _count_map(
        coverage.get("unresolved_by_reason"), "coverage.unresolved_by_reason"
    )
    entries_raw = raw.get("entries")
    if not isinstance(entries_raw, list):
        raise NavarroLexiconError("entries must be an array")
    entries = tuple(_entry(item, index) for index, item in enumerate(entries_raw))
    unresolved_raw = raw.get("unresolved")
    if not isinstance(unresolved_raw, list):
        raise NavarroLexiconError("unresolved must be an array")
    unresolved: list[Mapping[str, object]] = []
    unresolved_indices: set[int] = set()
    actual_unresolved_by_reason: dict[str, int] = {}
    for index, item in enumerate(unresolved_raw):
        label = f"unresolved[{index}]"
        if not isinstance(item, dict):
            raise NavarroLexiconError(f"{label} must be an object")
        entry_index = _nonnegative_int(item.get("entry_index"), f"{label}.entry_index")
        if entry_index in unresolved_indices:
            raise NavarroLexiconError(
                f"Duplicate unresolved entry_index: {entry_index}"
            )
        unresolved_indices.add(entry_index)
        reasons = item.get("reasons")
        if (
            not isinstance(reasons, list)
            or not reasons
            or any(not isinstance(reason, str) or not reason for reason in reasons)
        ):
            raise NavarroLexiconError(
                f"{label}.reasons must be a non-empty array of strings"
            )
        unresolved.append(MappingProxyType({**item, "reasons": tuple(reasons)}))
        for reason in reasons:
            actual_unresolved_by_reason[reason] = (
                actual_unresolved_by_reason.get(reason, 0) + 1
            )

    if (
        counts["supported_source_rows"] + counts["unresolved_source_rows"]
        != counts["tupi_source_rows"]
    ):
        raise NavarroLexiconError(
            "coverage supported/unresolved totals are inconsistent"
        )
    if counts["tupi_source_rows"] > counts["total_rows"]:
        raise NavarroLexiconError("coverage.tupi_source_rows exceeds total_rows")
    if (
        counts["shared_existing_entries"] + counts["dictionary_only_entries"]
        != counts["registry_entries"]
    ):
        raise NavarroLexiconError(
            "coverage shared/dictionary-only totals are inconsistent"
        )
    if counts["registry_entries"] != len(entries):
        raise NavarroLexiconError("coverage.registry_entries does not match entries")
    if sum(entries_by_constructor.values()) != len(entries):
        raise NavarroLexiconError(
            "coverage.entries_by_constructor does not match entries"
        )
    actual_by_constructor: dict[str, int] = {}
    for entry in entries:
        actual_by_constructor[entry.constructor] = (
            actual_by_constructor.get(entry.constructor, 0) + 1
        )
    if entries_by_constructor != actual_by_constructor:
        raise NavarroLexiconError(
            "coverage.entries_by_constructor does not match entry constructors"
        )
    if len(unresolved) != counts["unresolved_source_rows"]:
        raise NavarroLexiconError(
            "coverage.unresolved_source_rows does not match unresolved"
        )
    if unresolved_by_reason != actual_unresolved_by_reason:
        raise NavarroLexiconError(
            "coverage.unresolved_by_reason does not match unresolved reasons"
        )
    actual_shared = sum(entry.status == "shared_existing" for entry in entries)
    if actual_shared != counts["shared_existing_entries"]:
        raise NavarroLexiconError(
            "coverage.shared_existing_entries does not match entries"
        )
    if len(entries) - actual_shared != counts["dictionary_only_entries"]:
        raise NavarroLexiconError(
            "coverage.dictionary_only_entries does not match entries"
        )

    by_registry_id: dict[str, NavarroLexiconEntry] = {}
    by_name: dict[str, NavarroLexiconEntry] = {}
    for entry in entries:
        if entry.registry_id in by_registry_id:
            raise NavarroLexiconError(f"Duplicate registry_id: {entry.registry_id}")
        if entry.name in by_name:
            raise NavarroLexiconError(f"Duplicate registry name: {entry.name}")
        by_registry_id[entry.registry_id] = entry
        by_name[entry.name] = entry
    overlap = set(by_registry_id).intersection(by_name)
    if overlap:
        raise NavarroLexiconError(
            f"Registry identifiers collide with entry names: {sorted(overlap)[0]}"
        )

    return NavarroLexiconRegistry(
        source=MappingProxyType(dict(source)),
        coverage=MappingProxyType(dict(coverage)),
        entries=entries,
        unresolved=tuple(unresolved),
        _by_registry_id=MappingProxyType(by_registry_id),
        _by_name=MappingProxyType(by_name),
    )


@lru_cache(maxsize=8)
def _load_cached(path: str, mtime_ns: int, size: int) -> NavarroLexiconRegistry:
    del mtime_ns, size
    with Path(path).open(encoding="utf-8") as handle:
        return _validate_document(json.load(handle))


def load_navarro_registry(
    path: str | Path = DEFAULT_REGISTRY_PATH,
) -> NavarroLexiconRegistry:
    registry_path = Path(path).resolve()
    stat = registry_path.stat()
    return _load_cached(str(registry_path), stat.st_mtime_ns, stat.st_size)


def navarro_lexeme(
    registry_id_or_name: str, *, registry_path: str | Path = DEFAULT_REGISTRY_PATH
):
    """Instantiate one fresh, validated lexical predicate by ID or stable name."""

    entry = load_navarro_registry(registry_path).lookup(registry_id_or_name)
    constructor = _CONSTRUCTORS[entry.constructor]
    return constructor(**dict(entry.values))


__all__ = [
    "DEFAULT_REGISTRY_PATH",
    "NavarroLexiconEntry",
    "NavarroLexiconError",
    "NavarroLexiconRegistry",
    "load_navarro_registry",
    "navarro_lexeme",
]
