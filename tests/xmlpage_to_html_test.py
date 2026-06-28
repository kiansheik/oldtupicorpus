import importlib.util
import io
import tempfile
from contextlib import redirect_stdout
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = ROOT / "scripts" / "xmlpage_to_html.py"

spec = importlib.util.spec_from_file_location("xmlpage_to_html", SCRIPT_PATH)
xmlpage_to_html = importlib.util.module_from_spec(spec)
spec.loader.exec_module(xmlpage_to_html)


def sample_page_xml(text, width=100, height=200):
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<PcGts xmlns="http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15">
  <Page imageWidth="{width}" imageHeight="{height}">
    <TextRegion>
      <TextLine>
        <Baseline points="10,20 90,20"/>
        <TextEquiv><Unicode>{text}</Unicode></TextEquiv>
      </TextLine>
    </TextRegion>
  </Page>
</PcGts>
"""


def sample_mets(entries):
    file_entries = "\n".join(
        f"""        <ns3:file ID="PAGEXML_{sequence}" SEQ="{sequence}">
          <ns3:FLocat ns2:href="{href}"/>
        </ns3:file>"""
        for sequence, href in entries
    )
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<ns3:mets xmlns:ns2="http://www.w3.org/1999/xlink" xmlns:ns3="http://www.loc.gov/METS/">
  <ns3:fileSec>
    <ns3:fileGrp ID="MASTER">
      <ns3:fileGrp ID="PAGEXML">
{file_entries}
      </ns3:fileGrp>
    </ns3:fileGrp>
  </ns3:fileSec>
</ns3:mets>
"""


def write_sample_export(root, pages):
    document_dir = Path(root) / "123" / "sample_doc"
    page_dir = document_dir / "page"
    page_dir.mkdir(parents=True)
    for filename, text in pages:
        (page_dir / filename).write_text(sample_page_xml(text), encoding="utf-8")
    return document_dir


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

    def test_escaped_brackets_stay_inline(self):
        footnotes = []

        html_text, visible_text = xmlpage_to_html.format_line_text(
            r"Aba \[literal\] [note]",
            footnotes,
        )

        self.assertEqual(footnotes, ["note"])
        self.assertIn("Aba [literal] ", html_text)
        self.assertNotIn(r"\[literal\]", html_text)
        self.assertEqual(visible_text, "Aba [literal] ")

    def test_escaped_brackets_work_inside_footnotes(self):
        footnotes = []

        html_text, visible_text = xmlpage_to_html.format_line_text(
            r"Aba [ver \[sic\]] oca",
            footnotes,
        )

        self.assertEqual(footnotes, ["ver [sic]"])
        self.assertEqual(html_text.count('class="footnote-ref"'), 1)
        self.assertEqual(visible_text, "Aba  oca")
        self.assertIn(
            '<li id="fn-1">ver [sic]</li>',
            xmlpage_to_html.render_footnotes(footnotes),
        )

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

    def test_ligature_shorthands_join_latin_letter_pairs(self):
        footnotes = []

        html_text, visible_text = xmlpage_to_html.format_line_text(
            "a=e o=e A=e O=e A=E O=E ae oe a-e o-e",
            footnotes,
        )

        self.assertEqual(footnotes, [])
        self.assertEqual(html_text, "æ œ Æ Œ Æ Œ ae oe a-e o-e")
        self.assertEqual(visible_text, "æ œ Æ Œ Æ Œ ae oe a-e o-e")

    def test_help_output_prints_stylization_guide(self):
        stdout = io.StringIO()

        with redirect_stdout(stdout):
            exit_code = xmlpage_to_html.main(["--help"])

        help_text = stdout.getvalue()
        self.assertEqual(exit_code, 0)
        self.assertIn(
            "Usage: python scripts/xmlpage_to_html.py [--output output.html] input.xml|export_dir",
            help_text,
        )
        self.assertIn("GUIA DE ESTILIZAÇÃO DO PAGE XML", help_text)
        self.assertIn("SINTAXE DO USUÁRIO", help_text)
        self.assertIn("Sintaxe: -p-", help_text)
        self.assertIn("Sintaxe: a=e, o=e", help_text)
        self.assertIn("Como aparece no HTML: æ œ Æ Œ", help_text)
        self.assertIn("Como aparece no HTML: aꝑaba ꝑ", help_text)
        self.assertIn("Sintaxe: **texto**", help_text)
        self.assertIn("Sintaxe: |texto|", help_text)
        self.assertIn("Sintaxe: %40 texto%", help_text)
        self.assertIn(r"Sintaxe: \[texto literal\]", help_text)
        self.assertIn("Sintaxe: &", help_text)
        self.assertIn("Transkribus", help_text)
        self.assertIn("escolha Export no menu", help_text)
        self.assertIn("Escolha PageXML 2013", help_text)
        self.assertIn("Não escolha\nPageXML 2019", help_text)
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

    def test_faded_text_marker_renders_with_opacity_and_counts_visible_text(self):
        footnotes = []

        html_text, visible_text = xmlpage_to_html.format_line_text(
            "Tertio %40 $raecepto% [leitura provável]",
            footnotes,
        )

        self.assertEqual(footnotes, ["leitura provável"])
        self.assertIn(
            '<span class="faded-text" data-visible-percent="40" '
            'style="--faded-opacity: 0.40;">ſraecepto</span>',
            html_text,
        )
        self.assertNotIn("%40", html_text)
        self.assertEqual(visible_text, "Tertio ſraecepto ")

    def test_invalid_faded_text_percent_stays_literal(self):
        footnotes = []

        html_text, visible_text = xmlpage_to_html.format_line_text(
            "Tertio %140 praecepto%",
            footnotes,
        )

        self.assertEqual(footnotes, [])
        self.assertEqual(html_text, "Tertio %140 praecepto%")
        self.assertEqual(visible_text, "Tertio %140 praecepto%")

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
        self.assertIn(".faded-text", html)
        self.assertIn("opacity: var(--faded-opacity, 0.5);", html)

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

    def test_load_transkribus_export_pages_uses_mets_sequence(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            document_dir = write_sample_export(
                tmpdir,
                [
                    ("0002.xml", "Second [second note]"),
                    ("0001.xml", "First [first note]"),
                ],
            )
            (document_dir / "mets.xml").write_text(
                sample_mets(
                    [
                        (2, "page/0002.xml"),
                        (1, "page/0001.xml"),
                    ]
                ),
                encoding="utf-8",
            )

            pages = xmlpage_to_html.load_transkribus_export_pages(tmpdir)

        self.assertEqual([page["label"] for page in pages], ["0001.xml", "0002.xml"])
        self.assertIn("First", pages[0]["lines"][0]["text"])
        self.assertIn("Second", pages[1]["lines"][0]["text"])

        html = xmlpage_to_html.render_continuous_html(pages)
        self.assertIn('class="book" data-page-count="2"', html)
        self.assertLess(html.index("Page 1: 0001.xml"), html.index("Page 2: 0002.xml"))
        self.assertIn('id="p1-fnref-1"', html)
        self.assertIn('href="#p1-fn-1"', html)
        self.assertIn('<li id="p1-fn-1">first note</li>', html)
        self.assertIn('id="p2-fnref-1"', html)
        self.assertIn('<li id="p2-fn-1">second note</li>', html)
        self.assertIn("resizeContinuousPages", html)
        self.assertIn("translateX(-50%) scale(", html)
        self.assertIn(".faded-text", html)

    def test_transkribus_export_missing_declared_page_fails_before_rendering(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            document_dir = write_sample_export(tmpdir, [])
            (document_dir / "mets.xml").write_text(
                sample_mets([(1, "page/missing.xml")]),
                encoding="utf-8",
            )

            with self.assertRaisesRegex(
                xmlpage_to_html.ExportStructureError,
                "missing PAGE XML files",
            ):
                xmlpage_to_html.load_transkribus_export_pages(tmpdir)

    def test_directory_input_writes_continuous_html_to_output_path(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            document_dir = write_sample_export(tmpdir, [("0001.xml", "Aba")])
            (document_dir / "mets.xml").write_text(
                sample_mets([(1, "page/0001.xml")]),
                encoding="utf-8",
            )
            output_path = Path(tmpdir) / "combined.html"
            stdout = io.StringIO()

            with redirect_stdout(stdout):
                exit_code = xmlpage_to_html.main(
                    ["--output", str(output_path), str(tmpdir)]
                )

            html = output_path.read_text(encoding="utf-8")

        self.assertEqual(exit_code, 0)
        self.assertIn(
            "Continuous layout with 1 PAGE XML pages written", stdout.getvalue()
        )
        self.assertIn('data-page-count="1"', html)
        self.assertIn("Page 1: 0001.xml", html)

    def test_reversed_and_polyline_baselines_are_normalized(self):
        x, y, angle, target_width = xmlpage_to_html.baseline_geometry(
            [(90, 20), (50, 20), (10, 40)]
        )

        self.assertEqual((x, y), (10, 40))
        self.assertAlmostEqual(target_width, 40 + (40**2 + 20**2) ** 0.5)
        self.assertLess(angle, 0)


if __name__ == "__main__":
    unittest.main()
