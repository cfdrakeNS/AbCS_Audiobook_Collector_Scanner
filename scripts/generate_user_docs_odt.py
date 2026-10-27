r"""
Build the AbCS user guide as one OpenDocument text file for screen readers.

Source: help_docs/nn_topic_name.md, in the same order as Help → All Help Topics.
Output: abcs_userguide.odt in the project root.

The guide uses real Heading 1 to 3 styles, a linked table of contents, real
bullet and numbered lists, and tables with a marked header row. JAWS and NVDA
can move by heading, list, and table in LibreOffice Writer or Microsoft Word.
Cross-links between topics jump to the linked topic. Each table of contents
line is one link: the topic or section name, a dotted tab, and its page number.
The page numbers are page-reference fields that Writer fills in when it opens
the guide; Word shows them after Update Field (F9). The table of contents is
plain paragraphs rather than a Writer index, so Writer does not shade it grey.
Every page has its page number in the footer.

Requires odfpy (listed in requirements.txt).

Run:
    python scripts/generate_user_docs_odt.py
    python scripts/generate_user_docs_odt.py --toc-levels 1
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

DEFAULT_OUTPUT = PROJECT_ROOT / "abcs_userguide.odt"
GUIDE_TITLE = "AbCS User Guide"

BODY_FONT = "Arial"
CODE_FONT = "Courier New"

PAGE_WIDTH_CM = 21.59
PAGE_HEIGHT_CM = 27.94
PAGE_MARGIN_CM = 2.0
TEXT_WIDTH_CM = PAGE_WIDTH_CM - 2 * PAGE_MARGIN_CM
CONTENTS_INDENT_CM = 0.75

HEADING_RE = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
LIST_RE = re.compile(r"^(\s*)([-*+]|\d+[.)])\s+(.*)$")
RULE_RE = re.compile(r"^\s*([-*_])(\s*\1){2,}\s*$")
TABLE_SEP_RE = re.compile(r"^\s*\|?\s*:?-{2,}:?\s*(\|\s*:?-{2,}:?\s*)*\|?\s*$")
BOLD_LINE_RE = re.compile(r"^\*\*[^*].*\*\*$")
INLINE_RE = re.compile(
    r"(?P<code>`[^`]+`)"
    r"|(?P<link>\[(?P<label>[^\]]+)\]\((?P<target>[^)\s]+)\))"
    r"|(?P<bold>\*\*(?P<bold_text>.+?)\*\*)"
    r"|(?P<italic>(?<![\w*])\*(?P<italic_text>[^*\s](?:[^*]*[^*\s])?)\*(?![\w*]))"
    r"|(?P<escape>\\(?P<escaped>[\\`*_\[\]()#+\-.!|]))"
)

STRONG = "Strong_20_Emphasis"
EMPHASIS = "Emphasis"
CODE = "Source_20_Text"
LINK = "Internet_20_link"
VISITED_LINK = "Visited_20_Internet_20_Link"
INDEX_LINK = "Index_20_Link"


# ---------------------------------------------------------------------------
# Markdown parsing (the help_docs subset; see doc/help_docs_authoring.md)
# ---------------------------------------------------------------------------


@dataclass
class Heading:
    level: int
    text: str
    bookmark: str = ""


@dataclass
class Paragraph:
    text: str


@dataclass
class CodeBlock:
    lines: list[str]


@dataclass
class TableBlock:
    header: list[str]
    rows: list[list[str]]


@dataclass
class ListItem:
    number: int | None
    lines: list[str]
    children: list["ListBlock"] = field(default_factory=list)


@dataclass
class ListBlock:
    ordered: bool
    indent: int
    items: list[ListItem] = field(default_factory=list)


@dataclass
class Topic:
    filename: str
    title: str
    bookmark: str
    blocks: list


def split_table_row(line: str) -> list[str]:
    inner = line.strip()
    if inner.startswith("|"):
        inner = inner[1:]
    if inner.endswith("|") and not inner.endswith("\\|"):
        inner = inner[:-1]
    return [cell.strip().replace("\\|", "|") for cell in re.split(r"(?<!\\)\|", inner)]


def _join_paragraph(lines: list[str]) -> str:
    """Join source lines; a line ending in two spaces keeps its line break."""
    parts = []
    for index, line in enumerate(lines):
        hard_break = line.endswith("  ")
        parts.append(line.strip())
        if index < len(lines) - 1:
            parts.append("\n" if hard_break else " ")
    return "".join(parts)


def parse_markdown(source: str) -> list:
    lines = source.splitlines()
    blocks: list = []
    paragraph: list[str] = []
    list_stack: list[ListBlock] = []

    def flush_paragraph() -> None:
        if paragraph:
            blocks.append(Paragraph(_join_paragraph(paragraph)))
            paragraph.clear()

    def end_block() -> None:
        flush_paragraph()
        list_stack.clear()

    index = 0
    count = len(lines)
    while index < count:
        raw = lines[index].rstrip("\r\n")
        stripped = raw.strip()

        if stripped.startswith("```"):
            end_block()
            code: list[str] = []
            index += 1
            while index < count and not lines[index].strip().startswith("```"):
                code.append(lines[index].rstrip("\r\n"))
                index += 1
            blocks.append(CodeBlock(code))
            index += 1
            continue

        if not stripped:
            end_block()
            index += 1
            continue

        heading = HEADING_RE.match(raw)
        if heading:
            end_block()
            blocks.append(Heading(len(heading.group(1)), heading.group(2)))
            index += 1
            continue

        if RULE_RE.match(raw):
            end_block()
            index += 1
            continue

        if (
            stripped.startswith("|")
            and index + 1 < count
            and TABLE_SEP_RE.match(lines[index + 1])
        ):
            end_block()
            header = split_table_row(raw)
            rows: list[list[str]] = []
            index += 2
            while index < count and lines[index].strip().startswith("|"):
                row = split_table_row(lines[index])
                row = (row + [""] * len(header))[: len(header)]
                rows.append(row)
                index += 1
            blocks.append(TableBlock(header, rows))
            continue

        item = LIST_RE.match(raw)
        if item:
            flush_paragraph()
            indent = len(item.group(1).expandtabs(4))
            marker = item.group(2)
            ordered = marker[0].isdigit()
            number = int(marker[:-1]) if ordered else None
            while list_stack and indent < list_stack[-1].indent:
                list_stack.pop()
            if (
                list_stack
                and indent == list_stack[-1].indent
                and list_stack[-1].ordered != ordered
            ):
                list_stack.pop()
            if not list_stack or indent > list_stack[-1].indent:
                node = ListBlock(ordered, indent)
                if list_stack and list_stack[-1].items:
                    list_stack[-1].items[-1].children.append(node)
                else:
                    blocks.append(node)
                list_stack.append(node)
            list_stack[-1].items.append(ListItem(number, [item.group(3)]))
            index += 1
            continue

        if list_stack:
            list_stack[-1].items[-1].lines.append(stripped)
        elif BOLD_LINE_RE.match(stripped):
            flush_paragraph()
            blocks.append(Paragraph(stripped))
        else:
            paragraph.append(raw)
        index += 1

    flush_paragraph()
    return blocks


def plain_text(markdown: str) -> str:
    """Heading text without inline markup, for the table of contents."""

    def replace(match: re.Match) -> str:
        if match.group("code"):
            return match.group("code")[1:-1]
        if match.group("link"):
            return plain_text(match.group("label"))
        if match.group("bold"):
            return plain_text(match.group("bold_text"))
        if match.group("italic"):
            return plain_text(match.group("italic_text"))
        return match.group("escaped")

    return INLINE_RE.sub(replace, markdown).strip()


def load_topics() -> list[Topic]:
    """Parse every help topic in the app's All Help Topics order."""
    from src.accessibility.help_paths import discover_help_topics, resolve_help_doc_path

    topics: list[Topic] = []
    for _label, filename in discover_help_topics():
        stem = Path(filename).stem
        blocks = parse_markdown(resolve_help_doc_path(filename).read_text(encoding="utf-8"))
        title = stem
        section = 0
        for block in blocks:
            if not isinstance(block, Heading):
                continue
            if block.level == 1 and title == stem:
                title = plain_text(block.text)
                block.bookmark = f"topic_{stem}"
            else:
                section += 1
                block.bookmark = f"{stem}_s{section:03d}"
        topics.append(Topic(filename, title, f"topic_{stem}", blocks))
    if not topics:
        print("No help topics found in help_docs/", file=sys.stderr)
        raise SystemExit(1)
    return topics


# ---------------------------------------------------------------------------
# ODF output
# ---------------------------------------------------------------------------


class GuideWriter:
    def __init__(self, topics: list[Topic], toc_levels: int):
        from odf.opendocument import OpenDocumentText

        self.topics = topics
        self.toc_levels = toc_levels
        self.doc = OpenDocumentText()
        self.link_targets = {topic.filename.casefold(): topic.bookmark for topic in topics}
        self.list_styles: dict[str, str] = {}
        self.table_counts: dict[str, int] = {}
        self._add_styles()

    # -- styles -------------------------------------------------------------

    def _add_styles(self) -> None:
        from odf.style import (
            DefaultStyle,
            ParagraphProperties,
            Style,
            TableCellProperties,
            TableProperties,
            TabStop,
            TabStops,
            TextProperties,
        )

        styles = self.doc.styles

        default = DefaultStyle(family="paragraph")
        default.addElement(
            TextProperties(
                fontfamily=BODY_FONT,
                fontsize="12pt",
                language="en",
                country="US",
            )
        )
        styles.addElement(default)

        def paragraph_style(
            name,
            display,
            parent="Standard",
            next_style=None,
            outline=None,
            text=None,
            para=None,
            cls="text",
            right_tab_cm=None,
        ):
            attrs = {"name": name, "displayname": display, "family": "paragraph"}
            if parent:
                attrs["parentstylename"] = parent
            if next_style:
                attrs["nextstylename"] = next_style
            if outline:
                attrs["defaultoutlinelevel"] = str(outline)
            attrs["attributes"] = {"class": cls}
            style = Style(**attrs)
            if para or right_tab_cm is not None:
                para_props = ParagraphProperties(**(para or {}))
                if right_tab_cm is not None:
                    tab_stops = TabStops()
                    tab_stops.addElement(
                        TabStop(
                            position=f"{right_tab_cm:.2f}cm",
                            type="right",
                            leaderstyle="dotted",
                            leadertext=".",
                        )
                    )
                    para_props.addElement(tab_stops)
                style.addElement(para_props)
            if text:
                style.addElement(TextProperties(**text))
            styles.addElement(style)

        def text_style(name, display, **props):
            style = Style(name=name, displayname=display, family="text")
            if props:
                style.addElement(TextProperties(**props))
            styles.addElement(style)

        paragraph_style("Standard", "Default Paragraph Style", parent=None)
        paragraph_style(
            "Text_20_body",
            "Text body",
            para={"marginbottom": "0.25cm", "lineheight": "125%"},
        )
        paragraph_style(
            "List",
            "List",
            parent="Text_20_body",
            para={"marginbottom": "0.1cm"},
            cls="list",
        )
        paragraph_style(
            "Heading",
            "Heading",
            next_style="Text_20_body",
            para={
                "margintop": "0.6cm",
                "marginbottom": "0.25cm",
                "keepwithnext": "always",
            },
            text={"fontweight": "bold"},
        )
        sizes = {1: "20pt", 2: "16pt", 3: "14pt", 4: "13pt", 5: "12pt", 6: "12pt"}
        for level, size in sizes.items():
            para = {"breakbefore": "page"} if level == 1 else None
            paragraph_style(
                f"Heading_20_{level}",
                f"Heading {level}",
                parent="Heading",
                next_style="Text_20_body",
                outline=level,
                text={"fontsize": size, "fontweight": "bold"},
                para=para,
            )
        paragraph_style(
            "Title",
            "Title",
            next_style="Subtitle",
            para={"textalign": "center", "margintop": "3cm", "marginbottom": "0.4cm"},
            text={"fontsize": "26pt", "fontweight": "bold"},
            cls="chapter",
        )
        paragraph_style(
            "Subtitle",
            "Subtitle",
            next_style="Text_20_body",
            para={"textalign": "center", "marginbottom": "1.5cm"},
            text={"fontsize": "14pt"},
            cls="chapter",
        )
        paragraph_style(
            "Contents_20_Heading",
            "Contents Heading",
            para={"margintop": "0.6cm", "marginbottom": "0.3cm"},
            text={"fontsize": "16pt", "fontweight": "bold"},
            cls="index",
        )
        for level in range(1, 4):
            indent = CONTENTS_INDENT_CM * (level - 1)
            paragraph_style(
                f"Contents_20_{level}",
                f"Contents {level}",
                para={"marginleft": f"{indent:.2f}cm", "marginbottom": "0.12cm"},
                cls="index",
                right_tab_cm=TEXT_WIDTH_CM - indent,
            )
        paragraph_style(
            "Footer",
            "Footer",
            para={"textalign": "center"},
            text={"fontsize": "10pt"},
            cls="extra",
        )
        paragraph_style("Table_20_Contents", "Table Contents", cls="extra")
        paragraph_style(
            "Table_20_Heading",
            "Table Heading",
            parent="Table_20_Contents",
            text={"fontweight": "bold"},
            cls="extra",
        )
        paragraph_style(
            "Preformatted_20_Text",
            "Preformatted Text",
            text={"fontfamily": CODE_FONT, "fontsize": "11pt"},
            cls="html",
        )

        text_style(STRONG, "Strong Emphasis", fontweight="bold")
        text_style(EMPHASIS, "Emphasis", fontstyle="italic")
        text_style(CODE, "Source Text", fontfamily=CODE_FONT)
        text_style(
            LINK,
            "Internet link",
            color="#0645ad",
            textunderlinestyle="solid",
            textunderlinewidth="auto",
            textunderlinecolor="font-color",
        )
        text_style(
            VISITED_LINK,
            "Visited Internet Link",
            color="#5a3696",
            textunderlinestyle="solid",
            textunderlinewidth="auto",
            textunderlinecolor="font-color",
        )
        text_style(INDEX_LINK, "Index Link")

        auto = self.doc.automaticstyles
        table_style = Style(name="GuideTable", family="table")
        table_style.addElement(
            TableProperties(align="margins", margintop="0.2cm", marginbottom="0.3cm")
        )
        auto.addElement(table_style)
        cell_style = Style(name="GuideCell", family="table-cell")
        cell_style.addElement(
            TableCellProperties(border="0.5pt solid #000000", padding="0.1cm")
        )
        auto.addElement(cell_style)
        self._add_page_layout()

    def _add_page_layout(self) -> None:
        """Letter page with 2 cm margins and the page number in the footer."""
        from odf.config import ConfigItem, ConfigItemSet
        from odf.style import (
            Footer,
            FooterStyle,
            HeaderFooterProperties,
            MasterPage,
            PageLayout,
            PageLayoutProperties,
        )
        from odf.text import P, PageNumber

        layout = PageLayout(name="GuidePage")
        margin = f"{PAGE_MARGIN_CM}cm"
        layout.addElement(
            PageLayoutProperties(
                pagewidth=f"{PAGE_WIDTH_CM}cm",
                pageheight=f"{PAGE_HEIGHT_CM}cm",
                printorientation="portrait",
                margintop=margin,
                marginbottom=margin,
                marginleft=margin,
                marginright=margin,
            )
        )
        footer_style = FooterStyle()
        footer_style.addElement(HeaderFooterProperties(minheight="0.6cm", margintop="0.3cm"))
        layout.addElement(footer_style)
        self.doc.automaticstyles.addElement(layout)

        master = MasterPage(name="Standard", pagelayoutname="GuidePage")
        footer = Footer()
        footer_line = P(stylename="Footer", text="Page ")
        footer_line.addElement(PageNumber(selectpage="current", text="1"))
        footer.addElement(footer_line)
        master.addElement(footer)
        self.doc.masterstyles.addElement(master)

        # Contents tab stops are measured from each entry's indent.
        settings = ConfigItemSet(name="ooo:configuration-settings")
        settings.addElement(
            ConfigItem(name="TabsRelativeToIndent", type="boolean", text="true")
        )
        self.doc.settings.addElement(settings)

    def _list_style(self, block: ListBlock) -> str:
        """Named list style whose levels match this list's nesting."""
        from odf.style import ListLevelProperties
        from odf.text import ListLevelStyleBullet, ListLevelStyleNumber, ListStyle

        kinds = ["n" if block.ordered else "b"]
        level_lists = [block]
        while len(kinds) < 6:
            child = next(
                (sub for node in level_lists for item in node.items for sub in item.children),
                None,
            )
            if child is None:
                break
            kinds.append("n" if child.ordered else "b")
            level_lists = [
                sub for node in level_lists for item in node.items for sub in item.children
            ]
        while len(kinds) < 6:
            kinds.append("b")
        signature = "".join(kinds)
        name = self.list_styles.get(signature)
        if name:
            return name

        name = f"GuideList_{signature}"
        list_style = ListStyle(name=name, displayname=f"Guide list {signature}")
        bullets = ["\u2022", "\u25e6", "\u25aa"]
        for level, kind in enumerate(kinds, start=1):
            if kind == "n":
                level_style = ListLevelStyleNumber(
                    level=str(level), numformat="1", numsuffix="."
                )
            else:
                level_style = ListLevelStyleBullet(
                    level=str(level), bulletchar=bullets[(level - 1) % len(bullets)]
                )
            level_style.addElement(
                ListLevelProperties(
                    spacebefore=f"{0.75 * (level - 1):.2f}cm", minlabelwidth="0.75cm"
                )
            )
            list_style.addElement(level_style)
        self.doc.styles.addElement(list_style)
        self.list_styles[signature] = name
        return name

    # -- inline text --------------------------------------------------------

    def _link_href(self, target: str) -> str | None:
        if re.match(r"^(https?:|mailto:)", target, re.IGNORECASE):
            return target
        bookmark = self.link_targets.get(Path(target.split("#", 1)[0]).name.casefold())
        return f"#{bookmark}" if bookmark else None

    def add_inline(self, parent, markdown: str) -> None:
        from odf import teletype
        from odf.text import A, Span

        def add_plain(text: str) -> None:
            if text:
                teletype.addTextToElement(parent, text)

        position = 0
        for match in INLINE_RE.finditer(markdown):
            add_plain(markdown[position : match.start()])
            if match.group("code"):
                span = Span(stylename=CODE)
                teletype.addTextToElement(span, match.group("code")[1:-1])
                parent.addElement(span)
            elif match.group("link"):
                href = self._link_href(match.group("target"))
                if href:
                    link = A(
                        type="simple",
                        href=href,
                        stylename=LINK,
                        visitedstylename=VISITED_LINK,
                    )
                    self.add_inline(link, match.group("label"))
                    parent.addElement(link)
                else:
                    self.add_inline(parent, match.group("label"))
            elif match.group("bold"):
                span = Span(stylename=STRONG)
                self.add_inline(span, match.group("bold_text"))
                parent.addElement(span)
            elif match.group("italic"):
                span = Span(stylename=EMPHASIS)
                self.add_inline(span, match.group("italic_text"))
                parent.addElement(span)
            else:
                add_plain(match.group("escaped"))
            position = match.end()
        add_plain(markdown[position:])

    # -- blocks -------------------------------------------------------------

    def _heading(self, level: int, markdown: str, bookmark: str):
        from odf.text import Bookmark, H

        level = max(1, min(level, 6))
        heading = H(outlinelevel=str(level), stylename=f"Heading_20_{level}")
        if bookmark:
            heading.addElement(Bookmark(name=bookmark))
        self.add_inline(heading, markdown)
        return heading

    def _paragraph(self, markdown: str, style: str = "Text_20_body"):
        from odf.text import P

        paragraph = P(stylename=style)
        self.add_inline(paragraph, markdown)
        return paragraph

    def _list(self, block: ListBlock, top_level: bool):
        from odf.text import List, ListItem as OdfListItem

        attrs = {"stylename": self._list_style(block)} if top_level else {}
        odf_list = List(**attrs)
        for index, item in enumerate(block.items):
            item_attrs = {}
            if index == 0 and block.ordered and item.number not in (None, 1):
                item_attrs["startvalue"] = str(item.number)
            odf_item = OdfListItem(**item_attrs)
            odf_item.addElement(self._paragraph(" ".join(item.lines), "List"))
            for child in item.children:
                odf_item.addElement(self._list(child, top_level=False))
            odf_list.addElement(odf_item)
        return odf_list

    def _table(self, block: TableBlock, topic: Topic):
        from odf.table import Table, TableCell, TableColumn, TableHeaderRows, TableRow

        count = self.table_counts.get(topic.filename, 0) + 1
        self.table_counts[topic.filename] = count
        table = Table(name=f"{topic.title} table {count}", stylename="GuideTable")
        table.addElement(TableColumn(numbercolumnsrepeated=str(len(block.header))))

        def row(cells: list[str], style: str):
            odf_row = TableRow()
            for cell in cells:
                odf_cell = TableCell(stylename="GuideCell", valuetype="string")
                odf_cell.addElement(self._paragraph(cell, style))
                odf_row.addElement(odf_cell)
            return odf_row

        header_rows = TableHeaderRows()
        header_rows.addElement(row(block.header, "Table_20_Heading"))
        table.addElement(header_rows)
        for cells in block.rows:
            table.addElement(row(cells, "Table_20_Contents"))
        return table

    def _code(self, block: CodeBlock):
        from odf import teletype
        from odf.text import P

        paragraph = P(stylename="Preformatted_20_Text")
        teletype.addTextToElement(paragraph, "\n".join(block.lines))
        return paragraph

    # -- document -----------------------------------------------------------

    def _title_page(self) -> None:
        from odf.text import P

        try:
            from src.build_config import APP_VERSION
        except ImportError:
            APP_VERSION = ""
        body = self.doc.text
        body.addElement(P(stylename="Title", text=GUIDE_TITLE))
        subtitle = "Audiobook Collector Scanner"
        if APP_VERSION:
            subtitle += f", version {APP_VERSION}"
        body.addElement(P(stylename="Subtitle", text=subtitle))
        body.addElement(
            P(
                stylename="Text_20_body",
                text=(
                    "This guide has the same topics as Help, All Help Topics, in the app. "
                    "Each topic starts with a level 1 heading. "
                    "Sections are level 2 headings, and subsections are level 3. "
                    "Use your screen reader's heading keys to move between them."
                ),
            )
        )

    def _table_of_contents(self) -> None:
        """Contents as plain linked paragraphs, each ending in a page number.

        A Writer index (text:table-of-content) is drawn with field shading,
        which is dark grey in dark colour schemes and hard to read. The page
        numbers are page-reference fields that Writer fills in when it lays
        out the document.
        """
        from odf.text import A, BookmarkRef, P, Tab

        body = self.doc.text
        body.addElement(P(stylename="Contents_20_Heading", text="Contents"))
        for topic in self.topics:
            for block in topic.blocks:
                if not isinstance(block, Heading) or block.level > self.toc_levels:
                    continue
                entry = P(stylename=f"Contents_20_{block.level}")
                link = A(type="simple", href=f"#{block.bookmark}", stylename=INDEX_LINK)
                link.addText(plain_text(block.text))
                link.addElement(Tab())
                link.addElement(
                    BookmarkRef(referenceformat="page", refname=block.bookmark, text="?")
                )
                entry.addElement(link)
                body.addElement(entry)

    def _topic(self, topic: Topic) -> None:
        body = self.doc.text
        for block in topic.blocks:
            if isinstance(block, Heading):
                body.addElement(self._heading(block.level, block.text, block.bookmark))
            elif isinstance(block, Paragraph):
                body.addElement(self._paragraph(block.text))
            elif isinstance(block, ListBlock):
                body.addElement(self._list(block, top_level=True))
            elif isinstance(block, TableBlock):
                body.addElement(self._table(block, topic))
            elif isinstance(block, CodeBlock):
                body.addElement(self._code(block))

    def _metadata(self) -> None:
        from odf.dc import Description, Language, Title

        self.doc.meta.addElement(Title(text=GUIDE_TITLE))
        self.doc.meta.addElement(Language(text="en-US"))
        self.doc.meta.addElement(
            Description(
                text=f"AbCS help topics as one document, built {date.today().isoformat()}."
            )
        )

    def write(self, output: Path) -> None:
        self._metadata()
        self._title_page()
        self._table_of_contents()
        for topic in self.topics:
            self._topic(topic)
        output.parent.mkdir(parents=True, exist_ok=True)
        self.doc.save(str(output))


def build_guide(output: Path, toc_levels: int) -> Path:
    topics = load_topics()
    GuideWriter(topics, toc_levels).write(output)
    print(f"Wrote {len(topics)} help topics to {output}")
    return output


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build abcs_userguide.odt from the help_docs topics"
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help=f"Output file (default: {DEFAULT_OUTPUT.name} in the project root)",
    )
    parser.add_argument(
        "--toc-levels",
        type=int,
        choices=(1, 2, 3),
        default=2,
        help="Heading levels listed in the table of contents (default: 2)",
    )
    args = parser.parse_args()

    try:
        import odf  # noqa: F401
    except ImportError as exc:
        print("odfpy is not installed. Run: pip install odfpy", file=sys.stderr)
        raise SystemExit(1) from exc

    build_guide(args.output, args.toc_levels)


if __name__ == "__main__":
    main()
