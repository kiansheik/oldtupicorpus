from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


HERE = Path(__file__).resolve().parent
SANS = "/System/Library/Fonts/Supplemental/Arial.ttf"
BOLD = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
SERIF = "/System/Library/Fonts/Supplemental/Georgia.ttf"
MONO = "/System/Library/Fonts/Menlo.ttc"

COLORS = {
    "paper": "#f7f1e5",
    "card": "#fffdf8",
    "ink": "#183b3a",
    "muted": "#536461",
    "line": "#69827c",
    "rust": "#b25d3b",
    "green": "#dce9e3",
    "peach": "#f4dfcf",
    "purple": "#e8e0f2",
    "purple_ink": "#513d66",
    "yellow": "#fff4d9",
    "yellow_line": "#d4a43c",
}


CARDS = [
    {
        "file": "01-iekyl-independente.png",
        "title": "1 · VERBO LEXICAL ISOLADO",
        "phrase": "oroîekyî",
        "translation": "“morremos / expiramos”",
        "root": "oração independente",
        "nodes": [
            ("SUJEITO", "oré", "1ª plural exclusiva · elíptico"),
            ("PREDICADO", "oro- + îekyî", "prefixo ativo + raiz"),
        ],
        "note_title": "CAUTELA FILOLÓGICA",
        "note": [
            "Esta é a análise ativa do Pydicate atual.",
            "A forma independente ainda precisa de mais atestações;",
            "a perífrase histórica apresenta oré îekyî.",
        ],
        "code": "îekyî * +oré",
    },
    {
        "file": "02-iub-independente.png",
        "title": "2 · VERBO POSICIONAL",
        "phrase": "oroîub",
        "translation": "“jazemos / estamos deitados”",
        "root": "oração independente",
        "nodes": [
            ("SUJEITO", "oré", "1ª plural exclusiva · elíptico"),
            ("PREDICADO", "oro- + îub", "indicativo ativo + raiz"),
        ],
        "note_title": "VALOR LEXICAL",
        "note": [
            "îub é irregular e pluriforme:",
            "“estar deitado, jazer, permanecer”.",
        ],
        "code": "îub * +oré",
    },
    {
        "file": "03-gerundio-posicional.png",
        "title": "3 · COMBINAÇÃO EM GERÚNDIO",
        "phrase": "oroîekyî oroîupa",
        "translation": "“morremos / expiramos jazendo”",
        "root": "predicação complexa",
        "nodes": [
            (
                "PREDICADO LEXICAL",
                "oro-îekyî",
                "evento: morrer / expirar\nanálise ativa atual",
            ),
            (
                "AUXILIAR POSICIONAL",
                "oro-îu-pa",
                "gerúndio: “jazendo”\noro- + alomorfe îu + -pa",
            ),
        ],
        "note_title": "EFEITO DE SENTIDO",
        "note": [
            "A postura acompanha o evento e pode fornecer",
            "um enquadramento durativo / contínuo.",
        ],
        "code": "(îekyî * +oré) << (îub * +oré)",
    },
    {
        "file": "04-temporal-simples.png",
        "title": "4 · TEMPORAL SIMPLES",
        "phrase": "xe îekyîeme",
        "translation": "“quando eu morrer / ao morrer eu”",
        "root": "oração temporal",
        "nodes": [
            ("SUJEITO", "xe", "1ª singular"),
            ("RAIZ", "îekyî", "morrer / expirar"),
            ("SUFIXO", "-eme", "conjuntivo temporal"),
        ],
        "note_title": "FORMA E EVENTO",
        "note": [
            "O evento aparece sem o enquadramento posicional durativo.",
            "Atestação: Xe îekyîme (Anch., Poemas, 102);",
            "o Pydicate atual produz xe îekyîeme.",
        ],
        "code": "eme * (îekyî * ixé)",
    },
    {
        "file": "05-temporal-complexa.png",
        "title": "5 · TEMPORAL COMPLEXA",
        "phrase": "oré îekyî oré rúme béno",
        "translation": "“também quando estivermos morrendo”\nidiomático: “e na hora de nossa morte”",
        "root": "adjunto temporal complexo",
        "nodes": [
            ("PREDICADO LEXICAL", "oré îekyî", "“nós expiramos”\nforma atestada aqui"),
            (
                "AUXILIAR CONJUNTIVO",
                "oré r-ú-me",
                "sujeito + R + îub + CONJ\npostura + duração",
            ),
            ("PARTÍCULA", "béno", "“também / ainda”\nescopo sobre o adjunto"),
        ],
        "note_title": "CONTRASTE ASPECTUAL",
        "note": [
            "Não descreve simplesmente um cadáver “jazendo”.",
            "Apresenta o morrer em curso, sob enquadramento posicional.",
        ],
        "code": "... << (irã + ((îub * oré) >> (îekyî * oré)) << béno)",
    },
    {
        "file": "06-auxiliar-derivado-ereko.png",
        "title": "6 · AUXILIAR DERIVADO",
        "phrase": "xepóy xerérecóreme",
        "translation": "“quando me estavam dando de comer”\nAnchieta, Arte, 26",
        "root": "perífrase aspectual",
        "nodes": [
            ("SUJEITO", "Ø (3ª)", "não expresso\ncompartilhado"),
            ("OBJETO + PREDICADO", "xe-póy", "xe = 1SG.OBJ\nalimentar"),
            ("AUXILIAR", "xe-r-erekó-reme", "xe = 1SG.OBJ\nconjuntivo"),
        ],
        "note_title": "ESTRUTURA CORRETA",
        "note": [
            "As duas ocorrências de xe são objetos, não sujeitos.",
            "O derivado -erekó fornece o enquadramento durativo.",
        ],
        "code": "(poî * ixé) << (erekó * ixé)  →  xepoî xererekóreme",
    },
]


def font(path, size):
    return ImageFont.truetype(path, size)


def centered(draw, y, text, face, fill, center=540, spacing=8):
    box = draw.multiline_textbbox(
        (0, 0), text, font=face, align="center", spacing=spacing
    )
    width = box[2] - box[0]
    draw.multiline_text(
        (center - width / 2, y),
        text,
        font=face,
        fill=fill,
        align="center",
        spacing=spacing,
    )


def render(card):
    image = Image.new("RGB", (1080, 1080), COLORS["paper"])
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle(
        (48, 48, 1032, 1032),
        radius=34,
        fill=COLORS["card"],
        outline=COLORS["ink"],
        width=3,
    )

    centered(draw, 87, card["title"], font(BOLD, 28), COLORS["rust"])
    phrase_size = 52 if len(card["phrase"]) > 24 else 62
    centered(draw, 151, card["phrase"], font(SERIF, phrase_size), COLORS["ink"])
    centered(draw, 225, card["translation"], font(SANS, 27), COLORS["muted"], spacing=6)

    root_y = 315 if "\n" not in card["translation"] else 340
    draw.rounded_rectangle(
        (325, root_y, 755, root_y + 66), radius=18, fill=COLORS["ink"]
    )
    centered(draw, root_y + 17, card["root"], font(SANS, 26), "white")

    nodes = card["nodes"]
    node_top = 480
    margin, gap = 72, 38
    node_width = (1080 - 2 * margin - gap * (len(nodes) - 1)) / len(nodes)
    centers = [
        margin + node_width / 2 + i * (node_width + gap) for i in range(len(nodes))
    ]
    branch_y = root_y + 112
    draw.line((540, root_y + 66, 540, branch_y), fill=COLORS["line"], width=4)
    draw.line(
        (centers[0], branch_y, centers[-1], branch_y), fill=COLORS["line"], width=4
    )

    node_colors = [
        (COLORS["green"], COLORS["ink"]),
        (COLORS["peach"], "#7d3e28"),
        (COLORS["purple"], COLORS["purple_ink"]),
    ]
    for index, ((title, value, detail), center) in enumerate(zip(nodes, centers)):
        left, right = center - node_width / 2, center + node_width / 2
        draw.line((center, branch_y, center, node_top), fill=COLORS["line"], width=4)
        fill, ink = node_colors[index]
        draw.rounded_rectangle(
            (left, node_top, right, 675), radius=22, fill=fill, outline=ink, width=3
        )
        centered(
            draw,
            node_top + 30,
            title,
            font(BOLD, 21 if len(nodes) == 3 else 23),
            ink,
            center=center,
        )
        centered(
            draw,
            node_top + 75,
            value,
            font(SERIF, 31 if len(value) > 14 else 36),
            ink,
            center=center,
        )
        centered(
            draw,
            node_top + 124,
            detail,
            font(SANS, 19 if len(nodes) == 3 else 20),
            ink,
            center=center,
            spacing=5,
        )

    draw.rounded_rectangle(
        (98, 727, 982, 891),
        radius=24,
        fill=COLORS["yellow"],
        outline=COLORS["yellow_line"],
        width=3,
    )
    centered(draw, 752, card["note_title"], font(BOLD, 24), "#6f5317")
    centered(draw, 798, "\n".join(card["note"]), font(SANS, 22), "#4b4639", spacing=8)
    centered(
        draw,
        953,
        card["code"],
        font(MONO, 18 if len(card["code"]) > 50 else 22),
        COLORS["muted"],
    )

    image.save(HERE / card["file"], optimize=True)


if __name__ == "__main__":
    for card in CARDS:
        render(card)
