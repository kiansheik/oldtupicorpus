# PAGE XML Stylization Guide

This guide is the human-facing reference for the lightweight syntax, shorthand,
and sugar accepted by `scripts/xmlpage_to_html.py`.

When adding or changing PAGE XML stylization behavior, update this guide in the
same patch as the code and tests. The script's `--help` output reads this file,
so the command-line help should stay current when this document does.

## Usage

Run the converter with a PAGE XML file:

```bash
python3 scripts/xmlpage_to_html.py input.xml
```

Print this guide in terminal-friendly form:

```bash
python3 scripts/xmlpage_to_html.py --help
```

The converter writes `output.html` in the current working directory.

## Character Shorthands

- `$` becomes `ſ`, for long-s transcription.
- `-p-` becomes `ꝑ`, for the per-style p glyph.
- `&` is literal text. It is not shorthand for `R.` or for a paragraph mark.

## Prefix Diacritics

The following prefix marks combine with a following letter when possible:

- `˜q` becomes `q̃`.
- `^y` and `ˆu` become `ŷ` and `û`.
- `´a`, grave-e, `¨i`, and `¸c` become `á`, `è`, `ï`, and `ç`.
- Other supported prefix marks include `˙`, `˚`, `ˇ`, `˘`, and `¯`.
- If the next character is not a letter, the prefix mark stays literal.

## Inline Formatting

- `**text**` renders bold.
- `*text*` renders italic.
- `__text__` renders underlined.
- `~text~` renders horizontal strikethrough.
- `|text|` renders a manuscript-style vertical strike through the marked text.
- `++text++` renders superscript.
- `--text--` renders subscript.

Formatting markers are removed from the visible-text estimate used for line
width fitting, but the marked text itself remains visible.

## Footnotes

- `[note text]` becomes a numbered inline reference.
- The note text is rendered below the generated page box.
- Empty brackets such as `[]` remain literal inline text.
- Unclosed brackets remain literal inline text.
- Nested brackets stay inside one top-level note, so `[g[eral]]` becomes one
  footnote with note text `g[eral]`.

## Response Marks

- Literal standalone `R.` renders as a stylized manuscript-like response mark.
- `R.` remains text; it is not rewritten to `¶`.
- `&` does not produce a response mark.

## Maintenance Checklist

- Update this guide when adding syntax, shorthand, or visual sugar.
- Add or update `tests/xmlpage_to_html_test.py` coverage in the same patch.
- Keep searchable text and line-width estimation in mind when adding markup.
- Prefer explicit literal syntax over broad automatic replacements.
