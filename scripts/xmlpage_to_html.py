import sys
import math
from lxml import etree
import re
import unicodedata
from pathlib import Path

NS = {"pc": "http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15"}
ROOT_DIR = Path(__file__).resolve().parents[1]
STYLIZATION_GUIDE_PATH = ROOT_DIR / "docs" / "xmlpage-stylization-guide.md"
USAGE = "Usage: python scripts/xmlpage_to_html.py input.xml"
MANUSCRIPT_FONT_SIZE = 78
CHAR_WIDTH_FACTOR = 0.48  # only a no-JS fallback; browser JS measures exactly.
MANUSCRIPT_FONT_FAMILY = (
    '"Apple Chancery", "Bradley Hand", "Snell Roundhand", '
    '"Segoe Script", "Lucida Handwriting", cursive'
)

PREFIX_COMBINING_MARKS = {
    "^": "\u0302",
    "ˆ": "\u0302",
    "˜": "\u0303",
    "´": "\u0301",
    "`": "\u0300",
    "¨": "\u0308",
    "˙": "\u0307",
    "˚": "\u030a",
    "ˇ": "\u030c",
    "˘": "\u0306",
    "¯": "\u0304",
    "¸": "\u0327",
}

REPLACES = [
    ("$", "ſ"),
    ("-p-", "ꝑ"),
    ("A=E", "Æ"),
    ("A=e", "Æ"),
    ("a=e", "æ"),
    ("O=E", "Œ"),
    ("O=e", "Œ"),
    ("o=e", "œ"),
]


def strip_inline_markdown(input_text):
    input_text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r"\1 (\2)", input_text)
    input_text = re.sub(r"``\s?(.*?)\s?``", r"\1", input_text)
    input_text = re.sub(r"`([^`]*)`", r"\1", input_text)
    return input_text


def markdown_to_terminal(markdown_text):
    output_lines = []
    in_code_block = False

    for raw_line in markdown_text.splitlines():
        line = raw_line.rstrip()

        if line.startswith("```"):
            in_code_block = not in_code_block
            continue

        if in_code_block:
            output_lines.append(f"  {line}" if line else "")
            continue

        heading_match = re.match(r"^(#{1,6})\s+(.+)$", line)
        if heading_match:
            heading_text = strip_inline_markdown(heading_match.group(2)).upper()
            if output_lines and output_lines[-1]:
                output_lines.append("")
            output_lines.append(heading_text)
            output_lines.append("-" * len(heading_text))
            continue

        line = strip_inline_markdown(line)
        if line.startswith("- "):
            line = f"  - {line[2:]}"
        output_lines.append(line)

    return "\n".join(output_lines).strip() + "\n"


def build_help_text(guide_path=STYLIZATION_GUIDE_PATH):
    try:
        guide_text = guide_path.read_text(encoding="utf-8")
    except OSError:
        guide_text = (
            "# PAGE XML Stylization Guide\n\n"
            f"Stylization guide not found: {guide_path}\n"
        )

    return f"{USAGE}\n\n{markdown_to_terminal(guide_text)}"


def combine_prefix_diacritics(input_text):
    output = []
    index = 0

    while index < len(input_text):
        combining_mark = PREFIX_COMBINING_MARKS.get(input_text[index])
        if combining_mark and index + 1 < len(input_text):
            base_char = input_text[index + 1]
            if unicodedata.category(base_char).startswith("L"):
                output.append(unicodedata.normalize("NFC", base_char + combining_mark))
                index += 2
                continue

        output.append(input_text[index])
        index += 1

    return "".join(output)


def apply_replacements(input_text):
    input_text = combine_prefix_diacritics(input_text)
    for source, target in REPLACES:
        input_text = input_text.replace(source, target)
    return input_text


def format_text(input_text):
    # Response marker: R.
    input_text = re.sub(
        r"(^|(?<=\s))R\.(?=\s|$)",
        (
            '<span class="response-mark" aria-label="R.">'
            '<span class="response-mark-letter">R</span>'
            '<span class="response-mark-dot">.</span>'
            "</span>"
        ),
        input_text,
    )

    # Bold: **bold**
    input_text = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", input_text)

    # Italic: *italic*
    input_text = re.sub(r"\*(.*?)\*", r"<em>\1</em>", input_text)

    # Underline: __underline__
    input_text = re.sub(r"__(.*?)__", r"<u>\1</u>", input_text)

    # Strikethrough: ~strikethrough~
    input_text = re.sub(r"~(.*?)~", r"<del>\1</del>", input_text)

    # Vertical strikethrough: |struck|
    input_text = re.sub(
        r"\|([^|\n]+)\|",
        r'<span class="vertical-strike">\1</span>',
        input_text,
    )

    # Superscript: ++superscript++
    input_text = re.sub(r"\+\+(.*?)\+\+", r"<sup>\1</sup>", input_text)

    # Subscript: --subscript--
    input_text = re.sub(r"--(.*?)--", r"<sub>\1</sub>", input_text)

    return input_text


def strip_formatting_markers(input_text):
    input_text = re.sub(r"\*\*(.*?)\*\*", r"\1", input_text)
    input_text = re.sub(r"\*(.*?)\*", r"\1", input_text)
    input_text = re.sub(r"__(.*?)__", r"\1", input_text)
    input_text = re.sub(r"~(.*?)~", r"\1", input_text)
    input_text = re.sub(r"\|([^|\n]+)\|", r"\1", input_text)
    input_text = re.sub(r"\+\+(.*?)\+\+", r"\1", input_text)
    input_text = re.sub(r"--(.*?)--", r"\1", input_text)
    return input_text


def unescape_literal_brackets(input_text):
    return input_text.replace(r"\[", "[").replace(r"\]", "]")


def find_closing_bracket(input_text, start_index):
    depth = 1
    index = start_index + 1

    while index < len(input_text):
        if (
            input_text[index] == "\\"
            and index + 1 < len(input_text)
            and input_text[index + 1] in "[]"
        ):
            index += 2
            continue
        if input_text[index] == "[":
            depth += 1
        elif input_text[index] == "]":
            depth -= 1
            if depth == 0:
                return index
        index += 1

    return None


def format_line_text(raw_text, footnotes):
    text = apply_replacements(raw_text)
    html_parts = []
    visible_parts = []
    index = 0

    while index < len(text):
        if text[index] == "\\" and index + 1 < len(text) and text[index + 1] in "[]":
            literal_bracket = text[index + 1]
            html_parts.append(literal_bracket)
            visible_parts.append(literal_bracket)
            index += 2
            continue

        if text[index] != "[":
            html_parts.append(text[index])
            visible_parts.append(text[index])
            index += 1
            continue

        note_end = find_closing_bracket(text, index)
        if note_end is None:
            literal_tail = unescape_literal_brackets(text[index:])
            html_parts.append(literal_tail)
            visible_parts.append(literal_tail)
            break

        note_text = unescape_literal_brackets(text[index + 1 : note_end]).strip()
        if note_text:
            footnote_number = len(footnotes) + 1
            footnotes.append(note_text)
            html_parts.append(
                f'<sup class="footnote-ref" id="fnref-{footnote_number}">'
                f'<a href="#fn-{footnote_number}" '
                f'aria-label="Footnote {footnote_number}" '
                f'data-footnote-number="{footnote_number}"></a>'
                f"</sup>"
            )
        else:
            literal_brackets = text[index : note_end + 1]
            html_parts.append(literal_brackets)
            visible_parts.append(literal_brackets)

        index = note_end + 1

    return format_text("".join(html_parts)), strip_formatting_markers(
        "".join(visible_parts)
    )


def render_footnotes(footnotes):
    if not footnotes:
        return ""

    items = "\n".join(
        f'        <li id="fn-{index}">{format_text(note)}</li>'
        for index, note in enumerate(footnotes, start=1)
    )
    return f"""      <section class="footnotes" aria-label="Footnotes">
        <ol>
{items}
        </ol>
      </section>
"""


def normalize_baseline_points(points):
    if len(points) > 1 and points[-1][0] < points[0][0]:
        return list(reversed(points))
    return points


def baseline_geometry(points):
    points = normalize_baseline_points(points)
    (x1, y1), (x2, y2) = points[0], points[-1]
    dx = x2 - x1
    dy = y2 - y1
    angle = math.atan2(dy, dx)
    target_width = sum(
        math.hypot(next_x - current_x, next_y - current_y)
        for (current_x, current_y), (next_x, next_y) in zip(points, points[1:])
    )
    if target_width == 0:
        target_width = math.hypot(dx, dy)
    return x1, y1, angle, target_width


def collect_text_lines(page):
    lines = []
    footnotes = []

    for line in page.findall(".//pc:TextLine", NS):
        text_el = line.find(".//pc:Unicode", NS)
        baseline_el = line.find(".//pc:Baseline", NS)
        if baseline_el is None or text_el is None:
            continue

        raw_text = (text_el.text or "").strip()
        if not raw_text:
            continue

        baseline_points = [
            tuple(map(int, pt.split(","))) for pt in baseline_el.get("points").split()
        ]
        x1, y1, angle, target_width = baseline_geometry(baseline_points)

        html_text, visible_text = format_line_text(raw_text, footnotes)
        estimated_text_width = (
            MANUSCRIPT_FONT_SIZE * CHAR_WIDTH_FACTOR * len(visible_text)
        )
        scale_x = (
            target_width / estimated_text_width if estimated_text_width > 0 else 1.0
        )

        lines.append(
            {
                "text": html_text,
                "x": x1,
                "y": y1,
                "angle": angle,
                "target_width": target_width,
                "scale_x": scale_x,
                "font_size": MANUSCRIPT_FONT_SIZE,
            }
        )

    return lines, footnotes


def render_html(width, height, lines, footnotes):
    html = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>Responsive Text Layout</title>
  <style>
    html, body {{
      margin: 0;
      padding: 0;
      background: #d6d2ca;
      height: 100%;
      width: 100%;
      display: flex;
      justify-content: center;
      align-items: center;
    }}

    .wrapper {{
      width: 90vw;
      height: 90vh;
      display: flex;
      justify-content: center;
      align-items: center;
    }}

    #scale-container {{
      background: #eadbbd;
      box-shadow: 0 18px 48px rgba(42, 31, 15, 0.28);
      color: #3b2a19;
    }}

    .box {{
      aspect-ratio: {width} / {height};
      width: {width}px;
      height: {height}px;
      position: relative;
      background: #eadbbd;
      background-image:
        linear-gradient(90deg, rgba(111, 79, 38, 0.08), transparent 16%, rgba(255, 246, 217, 0.22) 48%, transparent 58%),
        linear-gradient(180deg, rgba(83, 55, 24, 0.08), transparent 18%, rgba(255, 247, 221, 0.18) 72%, rgba(94, 61, 25, 0.11));
      border: 1px solid #aa9169;
      transform-origin: top left;
    }}

    .line {{
      position: absolute;
      color: rgba(57, 41, 22, 0.78);
      font-family: {MANUSCRIPT_FONT_FAMILY};
      font-weight: 400;
      height: 0;
      letter-spacing: 0;
      line-height: 1;
      white-space: nowrap;
      transform-origin: left bottom;
    }}

    .text {{
      display: inline-block;
      position: absolute;
      left: 0;
      bottom: 0;
      transform-origin: left bottom;
      will-change: transform;
    }}

    .vertical-strike {{
      display: inline-block;
      position: relative;
      padding: 0 0.02em;
    }}

    .vertical-strike::after {{
      content: "";
      position: absolute;
      top: -0.08em;
      bottom: -0.08em;
      left: 50%;
      border-left: 0.075em solid currentColor;
      transform: translateX(-50%) rotate(-4deg);
      transform-origin: center;
      opacity: 0.9;
      pointer-events: none;
    }}

    .response-mark {{
      display: inline-flex;
      align-items: baseline;
      gap: 0.1em;
      margin-right: 0.08em;
      color: rgba(42, 28, 15, 0.9);
      font-family: {MANUSCRIPT_FONT_FAMILY};
      font-size: 1.08em;
      font-weight: 600;
      line-height: 0.86;
      transform: translateY(0.07em) rotate(-7deg);
      transform-origin: 42% 70%;
      text-shadow: 0.018em 0.018em 0 rgba(42, 28, 15, 0.35);
      vertical-align: -0.08em;
    }}

    .response-mark-letter {{
      display: inline-block;
      transform: skewX(-8deg);
    }}

    .response-mark-dot {{
      display: inline-block;
      font-size: 0.8em;
      font-weight: 700;
      transform: translate(0.05em, 0.04em);
    }}

    .footnote-ref {{
      color: #8a3419;
      font-family: Georgia, "Times New Roman", serif;
      font-size: 0.72em;
      font-weight: 700;
      line-height: 0;
      margin-left: 4px;
      vertical-align: super;
    }}

    .footnote-ref a {{
      border-bottom: 1px solid rgba(138, 52, 25, 0.45);
      color: #8a3419;
      display: inline-block;
      min-width: 0.45em;
      text-decoration: none;
    }}

    .footnote-ref a::before {{
      content: attr(data-footnote-number);
    }}

    .footnotes {{
      box-sizing: border-box;
      width: {width}px;
      margin: 0;
      padding: 34px 150px 48px;
      border: 1px solid #b8aa91;
      border-top: none;
      background: transparent;
      color: #2f2a22;
      font-family: Georgia, "Times New Roman", serif;
      font-size: 48px;
      line-height: 1.45;
    }}

    .footnotes ol {{
      border-top: 3px solid #7d6c54;
      margin: 0;
      padding: 24px 0 0 1.6em;
    }}

    .footnotes li {{
      margin: 0.3em 0;
      padding-left: 0.25em;
    }}

    .footnotes li::marker {{
      color: #8a3419;
      font-weight: 700;
    }}

    @media print {{
      html, body {{
        background: white !important;
        margin: 0;
        padding: 0;
      }}

      .wrapper {{
        all: unset;
      }}

      #scale-container {{
        all: unset;
      }}

      .box {{
        transform: none !important;
        border: none;
        margin: 0 auto;
        page-break-inside: avoid;
        box-shadow: none;
      }}

      .line {{
        color: black;
      }}

      body * {{
        visibility: hidden;
      }}

      .box, .box *, .footnotes, .footnotes * {{
        visibility: visible;
      }}
    }}
  </style>
</head>
<body>
  <div class="wrapper">
    <div id="scale-container">
      <div class="box">
"""

    # Inject each line
    for line in lines:
        html += f"""        <div class="line" style="
          left: {line['x']}px;
          top: {line['y']}px;
          transform: rotate({line['angle']}rad);
          font-size: {line['font_size']}px;" data-base-font-size="{line['font_size']}">
<span class="text" data-target-width="{line['target_width']:.4f}" style="transform: scaleX({line['scale_x']:.6f});">{line['text']}</span>
        </div>\n"""

    html += """      </div>
"""
    html += render_footnotes(footnotes)
    html += """    </div>
  </div>

  <script>
    const box = document.querySelector(".box");
    const wrapper = document.querySelector(".wrapper");
    const scaleContainer = document.getElementById("scale-container");
    const lineTexts = document.querySelectorAll(".text[data-target-width]");
    const MIN_HORIZONTAL_SCALE = 0.94;
    const MAX_HORIZONTAL_SCALE = 1.08;
    const MIN_FONT_SCALE = 0.82;
    const MAX_WORD_SPACING = 36;
    const MAX_LETTER_SPACING = 3.5;

    function clamp(value, min, max) {
      return Math.min(max, Math.max(min, value));
    }

    function resetLineFit(line, text, baseFontSize) {
      line.style.fontSize = `${baseFontSize}px`;
      text.style.wordSpacing = "0px";
      text.style.letterSpacing = "0px";
      text.style.transform = "scaleX(1)";
    }

    function spreadWithSpacing(text, targetWidth) {
      let actualWidth = text.offsetWidth;
      let remaining = targetWidth - actualWidth;
      const plainText = text.textContent || "";
      const wordSlots = (plainText.match(/\\s+/g) || []).length;

      if (remaining > 0 && wordSlots > 0) {
        const wordSpacing = Math.min(MAX_WORD_SPACING, remaining / wordSlots);
        text.style.wordSpacing = `${wordSpacing}px`;
        actualWidth = text.offsetWidth;
        remaining = targetWidth - actualWidth;
      }

      const letterSlots = Math.max(plainText.trim().length - 1, 1);
      if (remaining > 0 && letterSlots > 0) {
        const letterSpacing = Math.min(MAX_LETTER_SPACING, remaining / letterSlots);
        text.style.letterSpacing = `${letterSpacing}px`;
        actualWidth = text.offsetWidth;
      }

      return actualWidth;
    }

    function fitLines() {
      lineTexts.forEach((text) => {
        const line = text.closest(".line");
        const baseFontSize = Number(line.dataset.baseFontSize);
        const targetWidth = Number(text.dataset.targetWidth);
        if (!line || !baseFontSize || !targetWidth) {
          return;
        }

        resetLineFit(line, text, baseFontSize);
        let actualWidth = text.offsetWidth;
        if (actualWidth <= 0) {
          return;
        }

        let ratio = targetWidth / actualWidth;
        if (ratio < MIN_HORIZONTAL_SCALE) {
          const fontScale = clamp(ratio / MIN_HORIZONTAL_SCALE, MIN_FONT_SCALE, 1);
          line.style.fontSize = `${baseFontSize * fontScale}px`;
          actualWidth = text.offsetWidth;
          ratio = actualWidth > 0 ? targetWidth / actualWidth : 1;
        }

        if (ratio > MAX_HORIZONTAL_SCALE) {
          actualWidth = spreadWithSpacing(text, targetWidth);
          ratio = actualWidth > 0 ? targetWidth / actualWidth : 1;
        }

        text.style.transform = `scaleX(${clamp(ratio, MIN_HORIZONTAL_SCALE, MAX_HORIZONTAL_SCALE)})`;
      });
    }

    function resize() {
      const contentWidth = box.offsetWidth;
      const contentHeight = scaleContainer.scrollHeight || box.offsetHeight;
      const scaleX = wrapper.clientWidth / contentWidth;
      const scaleY = wrapper.clientHeight / contentHeight;
      const scale = Math.min(scaleX, scaleY);
      scaleContainer.style.transform = `scale(${scale})`;
    }

    function layout() {
      fitLines();
      resize();
    }

    layout();
    window.addEventListener("load", layout);
    window.addEventListener("resize", layout);
    if (document.fonts) {
      document.fonts.ready.then(layout);
    }
  </script>
</body>
</html>
"""

    return html


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv

    if argv and argv[0] in ("-h", "--help"):
        print(build_help_text())
        return 0

    if len(argv) < 1:
        print(build_help_text())
        return 1

    xml_file = argv[0]

    # Parse XML
    tree = etree.parse(xml_file)

    page = tree.find(".//pc:Page", NS)
    width = int(page.get("imageWidth"))
    height = int(page.get("imageHeight"))

    lines, footnotes = collect_text_lines(page)
    html = render_html(width, height, lines, footnotes)

    # Save output
    with open("output.html", "w", encoding="utf-8") as f:
        f.write(html)

    print(
        "✅ Responsive layout with baseline-aligned, scaled text written to output.html"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
