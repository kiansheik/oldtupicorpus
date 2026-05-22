import importlib.util
import io
from contextlib import redirect_stdout
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = ROOT / "scripts" / "xmlpage_to_html.py"

spec = importlib.util.spec_from_file_location("xmlpage_to_html", SCRIPT_PATH)
xmlpage_to_html = importlib.util.module_from_spec(spec)
spec.loader.exec_module(xmlpage_to_html)


class XmlPageToHtmlFootnoteTest(unittest.TestCase):
    def test_bracketed_text_becomes_numbered_footnotes(self):
        footnotes = []

        html_text, visible_text = xmlpage_to_html.format_line_text(
            "Aba [first note] oca [**bold note**]",
            footnotes,
        )

        self.assertEqual(footnotes, ["first note", "**bold note**"])
        self.assertIn('id="fnref-1"', html_text)
        self.assertIn('href="#fn-2"', html_text)
        self.assertIn('data-footnote-number="1"', html_text)
        self.assertIn('aria-label="Footnote 2"', html_text)
        self.assertNotIn("[first note]", html_text)
        self.assertNotIn(">1</a>", html_text)
        self.assertEqual(visible_text, "Aba  oca ")

        footnote_html = xmlpage_to_html.render_footnotes(footnotes)
        self.assertIn('<li id="fn-1">first note</li>', footnote_html)
        self.assertIn('<li id="fn-2"><strong>bold note</strong></li>', footnote_html)

    def test_empty_brackets_stay_inline(self):
        footnotes = []

        html_text, visible_text = xmlpage_to_html.format_line_text(
            "Aba []",
            footnotes,
        )

        self.assertEqual(footnotes, [])
        self.assertIn("[]", html_text)
        self.assertEqual(visible_text, "Aba []")

    def test_dollar_sign_becomes_long_s(self):
        footnotes = []

        html_text, visible_text = xmlpage_to_html.format_line_text(
            "coelum, $olem",
            footnotes,
        )

        self.assertEqual(footnotes, [])
        self.assertEqual(html_text, "coelum, ſolem")
        self.assertEqual(visible_text, "coelum, ſolem")

    def test_p_shorthand_becomes_per_glyph(self):
        footnotes = []

        html_text, visible_text = xmlpage_to_html.format_line_text(
            "a-p-aba -p-",
            footnotes,
        )

        self.assertEqual(footnotes, [])
        self.assertEqual(html_text, "aꝑaba ꝑ")
        self.assertEqual(visible_text, "aꝑaba ꝑ")

    def test_help_output_prints_stylization_guide(self):
        stdout = io.StringIO()

        with redirect_stdout(stdout):
            exit_code = xmlpage_to_html.main(["--help"])

        help_text = stdout.getvalue()
        self.assertEqual(exit_code, 0)
        self.assertIn("Usage: python scripts/xmlpage_to_html.py input.xml", help_text)
        self.assertIn("GUIA DE ESTILIZAÇÃO DO PAGE XML", help_text)
        self.assertIn("SINTAXE DO USUÁRIO", help_text)
        self.assertIn("Sintaxe: -p-", help_text)
        self.assertIn("Como aparece no HTML: aꝑaba ꝑ", help_text)
        self.assertIn("Sintaxe: **texto**", help_text)
        self.assertIn("Sintaxe: |texto|", help_text)
        self.assertIn("Transkribus", help_text)
        self.assertIn("escolha Export no menu", help_text)
        self.assertLess(
            help_text.index("SINTAXE DO USUÁRIO"), help_text.index("USO DO CONVERSOR")
        )
        self.assertNotIn("```", help_text)

    def test_missing_arg_prints_help_with_error_exit(self):
        stdout = io.StringIO()

        with redirect_stdout(stdout):
            exit_code = xmlpage_to_html.main([])

        self.assertEqual(exit_code, 1)
        self.assertIn("GUIA DE ESTILIZAÇÃO DO PAGE XML", stdout.getvalue())

    def test_response_marker_stays_r_and_is_styled(self):
        footnotes = []

        html_text, visible_text = xmlpage_to_html.format_line_text(
            "R. & aba",
            footnotes,
        )

        self.assertEqual(footnotes, [])
        self.assertEqual(visible_text, "R. & aba")
        self.assertNotIn("¶", html_text)
        self.assertIn("& aba", html_text)
        self.assertEqual(html_text.count('class="response-mark"'), 1)
        self.assertIn('<span class="response-mark-letter">R</span>', html_text)
        self.assertIn('<span class="response-mark-dot">.</span>', html_text)

    def test_prefix_diacritics_combine_with_following_letter(self):
        footnotes = []

        html_text, visible_text = xmlpage_to_html.format_line_text(
            "˜q ^y ˆu ´a `e ¨i ¸c",
            footnotes,
        )

        self.assertEqual(footnotes, [])
        self.assertEqual(html_text, "q̃ ŷ û á è ï ç")
        self.assertEqual(visible_text, "q̃ ŷ û á è ï ç")

    def test_prefix_diacritic_without_letter_stays_literal(self):
        footnotes = []

        html_text, visible_text = xmlpage_to_html.format_line_text(
            "Aba ˜ [note]",
            footnotes,
        )

        self.assertEqual(footnotes, ["note"])
        self.assertIn("Aba ˜ ", html_text)
        self.assertEqual(visible_text, "Aba ˜ ")

    def test_pipe_markers_render_vertical_strike(self):
        footnotes = []

        html_text, visible_text = xmlpage_to_html.format_line_text(
            "ocäu|m|baeráma? oporomonhang|m|bae-",
            footnotes,
        )

        self.assertEqual(footnotes, [])
        self.assertIn('ocäu<span class="vertical-strike">m</span>baeráma?', html_text)
        self.assertIn(
            'oporomonhang<span class="vertical-strike">m</span>bae-',
            html_text,
        )
        self.assertEqual(visible_text, "ocäumbaeráma? oporomonhangmbae-")

    def test_nested_brackets_are_one_footnote(self):
        footnotes = []

        html_text, visible_text = xmlpage_to_html.format_line_text(
            "Aba [g[eral]] oca",
            footnotes,
        )

        self.assertEqual(footnotes, ["g[eral]"])
        self.assertEqual(html_text.count('class="footnote-ref"'), 1)
        self.assertIn('data-footnote-number="1"', html_text)
        self.assertNotIn("[g[eral]]", html_text)
        self.assertEqual(visible_text, "Aba  oca")

    def test_unclosed_brackets_stay_inline(self):
        footnotes = []

        html_text, visible_text = xmlpage_to_html.format_line_text(
            "Aba [g[eral] oca",
            footnotes,
        )

        self.assertEqual(footnotes, [])
        self.assertIn("[g[eral] oca", html_text)
        self.assertEqual(visible_text, "Aba [g[eral] oca")

    def test_render_html_places_footnotes_below_page_box(self):
        html = xmlpage_to_html.render_html(
            100,
            200,
            [
                {
                    "text": 'Aba <sup class="footnote-ref">1</sup>',
                    "x": 10,
                    "y": 20,
                    "angle": 0,
                    "target_width": 80,
                    "scale_x": 1,
                    "font_size": 24,
                }
            ],
            ["first note"],
        )

        self.assertIn('class="box"', html)
        self.assertIn('class="footnotes"', html)
        self.assertIn('<li id="fn-1">first note</li>', html)
        self.assertLess(html.index('class="box"'), html.index('class="footnotes"'))
        self.assertNotIn("transform-origin: top center", html)
        self.assertIn("const contentWidth = box.offsetWidth;", html)
        self.assertIn("function fitLines()", html)
        self.assertIn("text.offsetWidth", html)
        self.assertIn('data-target-width="80.0000"', html)
        self.assertIn('data-base-font-size="24"', html)
        self.assertIn("scaleX(", html)
        self.assertIn("MIN_HORIZONTAL_SCALE = 0.94", html)
        self.assertIn("MAX_HORIZONTAL_SCALE = 1.08", html)
        self.assertIn("spreadWithSpacing", html)
        self.assertIn("wordSpacing", html)
        self.assertIn("letterSpacing", html)
        self.assertIn("MIN_FONT_SCALE", html)
        self.assertIn("Snell Roundhand", html)
        self.assertIn('"Apple Chancery", "Bradley Hand", "Snell Roundhand"', html)
        self.assertIn("background: #eadbbd;", html)
        self.assertIn("color: #8a3419;", html)
        self.assertIn("font-family: Georgia", html)
        self.assertIn("font-size: 48px;", html)
        self.assertIn("background: transparent;", html)
        self.assertIn("content: attr(data-footnote-number);", html)
        self.assertIn("height: 0;", html)
        self.assertIn("bottom: 0;", html)
        self.assertIn(".vertical-strike::after", html)
        self.assertIn("border-left: 0.075em solid currentColor;", html)
        self.assertIn("rotate(-4deg)", html)
        self.assertIn(".response-mark", html)
        self.assertIn(".response-mark-letter", html)
        self.assertIn(".response-mark-dot", html)
        self.assertIn("rotate(-7deg)", html)

    def test_collect_text_lines_numbers_footnotes_per_page(self):
        xml = b"""<?xml version="1.0" encoding="UTF-8"?>
<PcGts xmlns="http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15">
  <Page imageWidth="100" imageHeight="200">
    <TextRegion>
      <TextLine>
        <Baseline points="10,20 90,20"/>
        <TextEquiv><Unicode>Aba [first note]</Unicode></TextEquiv>
      </TextLine>
      <TextLine>
        <Baseline points="10,40 90,40"/>
        <TextEquiv><Unicode>Oca [second note]</Unicode></TextEquiv>
      </TextLine>
    </TextRegion>
  </Page>
</PcGts>
"""
        page = xmlpage_to_html.etree.fromstring(xml).find(
            ".//pc:Page",
            xmlpage_to_html.NS,
        )

        lines, footnotes = xmlpage_to_html.collect_text_lines(page)

        self.assertEqual(footnotes, ["first note", "second note"])
        self.assertIn('id="fnref-1"', lines[0]["text"])
        self.assertIn('id="fnref-2"', lines[1]["text"])
        self.assertEqual(lines[0]["font_size"], xmlpage_to_html.MANUSCRIPT_FONT_SIZE)
        self.assertAlmostEqual(lines[0]["target_width"], 80)

    def test_reversed_and_polyline_baselines_are_normalized(self):
        x, y, angle, target_width = xmlpage_to_html.baseline_geometry(
            [(90, 20), (50, 20), (10, 40)]
        )

        self.assertEqual((x, y), (10, 40))
        self.assertAlmostEqual(target_width, 40 + (40**2 + 20**2) ** 0.5)
        self.assertLess(angle, 0)


if __name__ == "__main__":
    unittest.main()
