#!/usr/bin/env python3
"""Build the Hungarian and English Markdown masters into static HTML editions."""
from __future__ import annotations

import html
import hashlib
import json
import re
import shutil
import struct
import unicodedata
from functools import lru_cache
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "sources"
DIST = ROOT / "dist"
WORKBENCH = ROOT / "workbench"
SOURCE_IMAGES = SOURCE / "images"
WEB_IMAGES = SOURCE_IMAGES / "avif"
IMAGE_MANIFEST = SOURCE_IMAGES / "avif-manifest.json"

HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
IMAGE_RE = re.compile(r"!\[([^]]*)\]\(([^)]+)\)")
LINK_RE = re.compile(r"(?<!!)\[([^]]+)\]\(([^)]+)\)")
ANCHOR_RE = re.compile(r'<a\s+id="([^"]+)"\s*></a>')
ARTICLE_SPACE_RE = re.compile(r"(?<!\w)([Aa]z?) (?=\S)")
EXAMPLE_SPACE_RE = re.compile(r"(?<!\w)([Pp]l\.) (?=\S)")


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def published_image_src(src: str) -> str:
    """Map an editable master image reference to its derived web rendition."""
    source_path = SOURCE / src
    if source_path.parent != SOURCE_IMAGES:
        raise ValueError(f"Image must be stored directly in sources/images: {src}")
    return f"images/{source_path.stem}.avif"


def validate_web_images(referenced_sources: set[str]) -> None:
    """Require current, verified AVIF renditions without encoding during build."""
    if not IMAGE_MANIFEST.is_file():
        raise ValueError(
            "Missing AVIF manifest; run: python3 build/build_images.py --adopt-existing"
        )
    manifest = json.loads(IMAGE_MANIFEST.read_text(encoding="utf-8"))
    records = manifest.get("files", {})
    errors = []
    for src in sorted(referenced_sources):
        source_path = SOURCE / src
        web_path = WEB_IMAGES / f"{source_path.stem}.avif"
        record = records.get(source_path.name)
        if not web_path.is_file():
            errors.append(f"missing {web_path.relative_to(ROOT)}")
        elif not record:
            errors.append(f"unregistered {web_path.relative_to(ROOT)}")
        elif record.get("source_sha256") != file_sha256(source_path):
            errors.append(f"stale {web_path.relative_to(ROOT)}")
        elif record.get("output_sha256") != file_sha256(web_path):
            errors.append(f"modified {web_path.relative_to(ROOT)}")
    if errors:
        raise ValueError(
            "AVIF renditions need refreshing:\n- " + "\n- ".join(errors)
            + "\nRun: python3 build/build_images.py"
        )


def heading_id(title: str) -> str:
    """Create a stable ASCII heading ID without dropping accented letters."""
    normalized = unicodedata.normalize("NFKD", title)
    ascii_title = "".join(char for char in normalized if not unicodedata.combining(char))
    return "heading-" + re.sub(r"[^a-z0-9]+", "-", ascii_title.lower()).strip("-")


@lru_cache(maxsize=None)
def image_size_attributes(src: str) -> str:
    """Reserve intrinsic image space before lazy loading, using no dependencies."""
    path = SOURCE / src
    if not path.is_file():
        return ""
    with path.open("rb") as stream:
        header = stream.read(24)
        if header.startswith(b"\x89PNG\r\n\x1a\n"):
            width, height = struct.unpack(">II", header[16:24])
        elif header.startswith(b"\xff\xd8"):
            stream.seek(2)
            while True:
                byte = stream.read(1)
                if not byte:
                    raise ValueError(f"JPEG dimensions not found: {src}")
                if byte != b"\xff":
                    continue
                marker = stream.read(1)
                while marker == b"\xff":
                    marker = stream.read(1)
                if marker in (b"\xd8", b"\xd9"):
                    continue
                size = struct.unpack(">H", stream.read(2))[0]
                if marker and marker[0] in {0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF}:
                    _, height, width = struct.unpack(">BHH", stream.read(5))
                    break
                stream.seek(size - 2, 1)
        else:
            raise ValueError(f"Unsupported image format: {src}")
    return f' width="{width}" height="{height}"'


def inline(text: str, language: str = "hu") -> str:
    placeholders: list[str] = []

    def stash(value: str) -> str:
        placeholders.append(value)
        return f"\x00{len(placeholders)-1}\x00"

    text = IMAGE_RE.sub(lambda m: stash(
        f'<img{image_size_attributes(m.group(2))} src="{html.escape(published_image_src(m.group(2)), quote=True)}" alt="{html.escape(m.group(1), quote=True)}" loading="lazy">'), text)
    text = LINK_RE.sub(lambda m: stash(
        f'<a href="{html.escape(m.group(2), quote=True)}">{inline(m.group(1), language)}</a>'), text)
    text = re.sub(r"<sup>([^<]+)</sup>", lambda m: stash("<sup>" + html.escape(m.group(1)) + "</sup>"), text)
    text = html.escape(text, quote=False)
    # Resolve combined emphasis before the individual bold and italic rules.
    text = re.sub(r"\*\*\*(.+?)\*\*\*", r"<strong><em>\1</em></strong>", text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<!\*)\*([^*]+?)\*(?!\*)", r"<em>\1</em>", text)
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    # Keep short Hungarian function words attached to the following word in
    # rendered HTML. The source Markdown remains readable with ordinary spaces.
    if language == "hu":
        text = ARTICLE_SPACE_RE.sub(lambda match: match.group(1) + "\u00a0", text)
        text = EXAMPLE_SPACE_RE.sub(lambda match: match.group(1) + "\u00a0", text)
    for i, value in enumerate(placeholders):
        text = text.replace(f"\x00{i}\x00", value)
    return text


def parse_frontmatter(text: str) -> tuple[dict[str, str], str]:
    if not text.startswith("---\n"):
        return {}, text
    end = text.find("\n---", 4)
    if end < 0:
        return {}, text
    metadata: dict[str, str] = {}
    for line in text[4:end].splitlines():
        if ":" in line and not line.startswith(" "):
            key, value = line.split(":", 1)
            metadata[key.strip()] = value.strip().strip('"')
    return metadata, text[end + 4:].lstrip("\n")


def render_markdown(
    text: str,
    layout: dict | None = None,
    language: str = "hu",
    wrap_sections: bool = True,
) -> tuple[str, str, set[str]]:
    format_inline = lambda value: inline(value, language)
    lines = text.splitlines()
    output: list[str] = []
    toc: list[tuple[int, str, str]] = []
    anchors: set[str] = set()
    i = 0
    pending_anchor: str | None = None
    pending_heading_credit = False
    title_header_open = wrap_sections and '<a id="book_title"></a>' in text
    section_levels: list[int] = []
    if title_header_open:
        output.append('<header class="book-title">')
    while i < len(lines):
        line = lines[i]
        anchor_match = ANCHOR_RE.fullmatch(line.strip())
        if anchor_match:
            pending_anchor = anchor_match.group(1)
            anchors.add(pending_anchor)
            i += 1
            continue
        if line.strip().startswith("<!--"):
            while i < len(lines) and "-->" not in lines[i]:
                i += 1
            i += 1
            continue
        if not line.strip():
            i += 1
            continue
        if line.strip().startswith("<div") or line.strip() == "</div>":
            output.append(line)
            i += 1
            continue
        if (m := HEADING_RE.match(line)):
            level, title = len(m.group(1)), m.group(2)
            anchor = pending_anchor
            if anchor is None and level <= 4:
                anchor = heading_id(title)
            if anchor:
                anchors.add(anchor)
            pending_anchor = None
            id_attr = f' id="{html.escape(anchor, quote=True)}"' if anchor else ""
            if wrap_sections and level == 2 and title_header_open:
                output.append('</header>')
                title_header_open = False
            if wrap_sections and 2 <= level <= 4 and anchor:
                while section_levels and section_levels[-1] >= level:
                    output.append('</section>')
                    section_levels.pop()
                output.append(
                    f'<section class="book-section level-{level}" '
                    f'aria-labelledby="{html.escape(anchor, quote=True)}">'
                )
                section_levels.append(level)
            output.append(f'<h{level}{id_attr}>{format_inline(title)}</h{level}>')
            if level <= 4:
                toc.append((level, anchor, title))
            pending_heading_credit = True
            i += 1
            continue
        if line.strip().startswith("— "):
            credit_class = "contributor-credit heading-credit" if pending_heading_credit else "contributor-credit"
            output.append(f'<p class="{credit_class}">{format_inline(line.strip())}</p>')
            pending_heading_credit = False
            i += 1
            continue
        pending_heading_credit = False
        if line.strip() in {"---", "*"}:
            css_class = ' class="ornamental-break"' if line.strip() == "*" else ""
            output.append(f"<hr{css_class}>")
            i += 1
            continue
        if line.strip() == "::: note":
            i += 1
            block: list[str] = []
            while i < len(lines) and lines[i].strip() != ":::":
                block.append(lines[i])
                i += 1
            if i >= len(lines):
                raise ValueError("Unclosed ::: note block")
            i += 1
            nested, _nested_toc, nested_anchors = render_markdown(
                "\n".join(block), layout, language, wrap_sections=False
            )
            output.append(f'<aside class="note">{nested}</aside>')
            anchors.update(nested_anchors)
            continue
        if line.startswith(">"):
            block: list[str] = []
            while i < len(lines) and (lines[i].startswith(">") or not lines[i].strip()):
                block.append(re.sub(r"^> ?", "", lines[i]) if lines[i].startswith(">") else "")
                i += 1
            body = "\n".join(block)
            nested, _nested_toc, nested_anchors = render_markdown(
                body, layout, language, wrap_sections=False
            )
            output.append(f"<blockquote>{nested}</blockquote>")
            anchors.update(nested_anchors)
            continue
        if re.match(r"^\s*[-*+]\s+", line) or re.match(r"^\s*\d+[.)]\s+", line):
            ordered = bool(re.match(r"^\s*\d+[.)]\s+", line))
            items: list[str] = []
            while i < len(lines):
                pat = r"^\s*\d+[.)]\s+(.*)$" if ordered else r"^\s*[-*+]\s+(.*)$"
                match = re.match(pat, lines[i])
                if match:
                    items.append(f"<li>{format_inline(match.group(1))}</li>")
                    i += 1
                    continue
                # Blank lines may separate the items of a loose Markdown list.
                next_item = i
                while next_item < len(lines) and not lines[next_item].strip():
                    next_item += 1
                if next_item > i and next_item < len(lines) and re.match(pat, lines[next_item]):
                    i = next_item
                    continue
                break
            tag = "ol" if ordered else "ul"
            output.append(f"<{tag}>" + "".join(items) + f"</{tag}>")
            continue
        if (m := IMAGE_RE.fullmatch(line.strip())):
            src = m.group(2)
            caption = ""
            caption_index = i + 1
            if caption_index < len(lines) and not lines[caption_index].strip():
                caption_index += 1
            if caption_index < len(lines) and re.match(r"^\*.*\*$", lines[caption_index].strip()):
                caption = format_inline(lines[caption_index].strip()[1:-1])
                i = caption_index
            figure_id = f' id="{html.escape(pending_anchor, quote=True)}"' if pending_anchor else ""
            setting = layout.get(Path(src).name) if layout else None
            if isinstance(setting, dict):
                width = setting.get("width")
                invert = bool(setting.get("invert"))
            else:
                width = setting
                invert = False
            style_attr = f' style="--figure-width: {int(width)}%"' if width else ""
            image_class = ' class="dark-invert"' if invert else ""
            alt = "" if caption else html.escape(m.group(1), quote=True)
            output.append(f'<figure{figure_id}><img{image_class}{style_attr}{image_size_attributes(src)} src="{html.escape(published_image_src(src), quote=True)}" alt="{alt}" loading="lazy">{f"<figcaption>{caption}</figcaption>" if caption else ""}</figure>')
            pending_anchor = None
            i += 1
            continue
        paragraph: list[str] = [line]
        i += 1
        while i < len(lines) and lines[i].strip() and not HEADING_RE.match(lines[i]) and not lines[i].startswith(">") and not ANCHOR_RE.fullmatch(lines[i].strip()) and not lines[i].strip().startswith("<div") and not re.match(r"^\s*(?:[-*+]|\d+[.)])\s+", lines[i]):
            paragraph.append(lines[i]); i += 1
        paragraph_text = " ".join(paragraph)
        output.append(f"<p>{format_inline(paragraph_text)}</p>")
    if wrap_sections:
        while section_levels:
            output.append('</section>')
            section_levels.pop()
        if title_header_open:
            output.append('</header>')
    toc_html = build_toc([
        entry for entry in toc
        if entry[1] not in {
            "book_title",
            "front_contributors", "front_abstract", "editorial_note",
        }
    ], language)
    return "\n".join(output), toc_html, anchors


def build_toc(entries: list[tuple[int, str, str]], language: str = "hu") -> str:
    """Turn a flat heading list into a nested navigation tree."""
    root: list[dict] = []
    stack: list[tuple[int, list[dict]]] = [(-1, root)]
    for level, anchor, title in entries:
        while stack[-1][0] >= level:
            stack.pop()
        node = {"level": level, "anchor": anchor, "title": title, "children": []}
        stack[-1][1].append(node)
        stack.append((level, node["children"]))

    def render_link(node: dict) -> str:
        title = node["title"]
        number = re.match(r"^(\d+(?:\.\d+)*\.?)\s+(.+)$", title)
        if number:
            content = (
                f'<span class="toc-number">{inline(number.group(1), language)}</span>'
                f'<span class="toc-title">{inline(number.group(2), language)}</span>'
            )
            link_class = "toc-link toc-link-numbered"
        else:
            content = f'<span class="toc-title">{inline(title, language)}</span>'
            link_class = "toc-link"
        return f'<a class="{link_class}" href="#{html.escape(node["anchor"], quote=True)}">{content}</a>'

    branch_number = 0
    expand_label = "Szakasz kibontása" if language == "hu" else "Expand section"
    collapse_label = "Szakasz bezárása" if language == "hu" else "Collapse section"

    def render(nodes: list[dict]) -> str:
        nonlocal branch_number
        items = []
        for node in nodes:
            link = render_link(node)
            children = render(node["children"])
            if children:
                branch_number += 1
                child_id = f"toc-branch-{branch_number}"
                title = html.escape(node["title"], quote=True)
                button = (
                    f'<button class="toc-branch-toggle" type="button" aria-expanded="false" '
                    f'aria-controls="{child_id}" aria-label="{expand_label}: {title}" '
                    f'data-open-label="{expand_label}" data-close-label="{collapse_label}" '
                    f'data-title="{title}"><span aria-hidden="true">▶</span></button>'
                )
                children = children.replace("<ol>", f'<ol id="{child_id}" hidden>', 1)
                items.append(f'<li class="toc-item has-children"><div class="toc-row">{button}{link}</div>{children}</li>')
            else:
                items.append(f'<li class="toc-item"><div class="toc-row"><span class="toc-spacer" aria-hidden="true"></span>{link}</div></li>')
        return "<ol>" + "".join(items) + "</ol>" if items else ""

    return render(root)


class PageInventory(HTMLParser):
    """Validate actual emitted IDs and resources, not just parser bookkeeping."""
    def __init__(self, page: str):
        super().__init__()
        self.ids = []
        self.references = []
        self.resources = []
        self.locations = []
        self.in_article = False
        self.feed(page)

    def handle_starttag(self, tag, attributes):
        attrs = dict(attributes)
        if tag == "article":
            self.in_article = True
        ident = attrs.get("id")
        if ident:
            self.ids.append(ident)
            if self.in_article and tag in {"h1", "h2", "h3", "h4", "h5", "h6", "figure"}:
                self.locations.append((tag, ident))
        for key in ("href", "src"):
            value = attrs.get(key, "")
            if value.startswith("#"):
                self.references.append(value[1:])
            elif value and ":" not in value and not value.startswith("//"):
                self.resources.append(value.split("#", 1)[0])

    def handle_endtag(self, tag):
        if tag == "article":
            self.in_article = False

    def validate(self, name: str):
        duplicates = [key for key, count in Counter(self.ids).items() if count > 1]
        unresolved = sorted(set(self.references) - set(self.ids))
        if duplicates or unresolved:
            raise ValueError(f"{name}: duplicate IDs {duplicates}; unresolved links {unresolved}")


def language_targets(inventory, shared_ids):
    targets = {"top": "top"}
    parents = []
    for tag, ident in inventory.locations:
        if tag.startswith("h"):
            level = int(tag[1])
            while parents and parents[-1][0] >= level:
                parents.pop()
            parents.append((level, ident))
        parent = next((anchor for _, anchor in reversed(parents) if anchor in shared_ids), "top")
        targets[ident] = ident if ident in shared_ids else parent
    return targets


def main() -> None:
    layout_path = ROOT / "audit" / "image_layout.json"
    layout = json.loads(layout_path.read_text(encoding="utf-8")) if layout_path.exists() else {}
    locales = json.loads((ROOT / "build" / "locales.json").read_text(encoding="utf-8"))
    template = (ROOT / "template" / "book.html").read_text(encoding="utf-8")
    editions = {}
    for language, filename in (("hu", "lakokonyv.md"), ("en", "lakokonyv_en.md")):
        metadata, markdown = parse_frontmatter((SOURCE / filename).read_text(encoding="utf-8"))
        content, toc, anchors = render_markdown(markdown, layout, language)
        images = IMAGE_RE.findall(markdown)
        missing_images = sorted({path for _, path in images if not (SOURCE / path).is_file()})
        if missing_images:
            raise ValueError(f"{filename}: missing images: {missing_images}")
        values = dict(
            locales[language],
            language=language,
            title=metadata["title"],
            author=metadata.get("author") or metadata.get("authors", "Bitó János"),
            canonical_url=(
                "https://hildgyorgy.github.io/lakokonyv/"
                if language == "hu"
                else "https://hildgyorgy.github.io/lakokonyv/index_en.html"
            ),
        )
        values["hu_current"] = 'aria-current="page"' if language == "hu" else ""
        values["en_current"] = 'aria-current="page"' if language == "en" else ""
        page = template
        for key, value in values.items():
            page = page.replace("{{ " + key + " }}", value if key.endswith("_current") else html.escape(value, quote=True))
        page = page.replace("{{ toc }}", toc).replace("{{ content }}", content)
        inventory = PageInventory(page)
        inventory.validate(filename)
        editions[language] = {"page": page, "inventory": inventory, "images": images}
        print(f"{language.upper()}: {len(images)} image references, {len(inventory.ids)} IDs; internal links OK.")

    shared_ids = set(editions["hu"]["inventory"].ids) & set(editions["en"]["inventory"].ids)
    for language, edition in editions.items():
        targets = language_targets(edition["inventory"], shared_ids)
        edition["page"] = edition["page"].replace("{{ language_targets }}", json.dumps(targets, ensure_ascii=True).replace("<", "\\u003c"))
        if re.search(r"{{ [a-z_]+ }}", edition["page"]):
            raise ValueError(f"Unresolved template placeholders in {language}")

    # Both masters have passed validation before replacing the output directory.
    DIST.mkdir(exist_ok=True)
    for child in DIST.iterdir():
        if child.is_dir():
            shutil.rmtree(child)
        else:
            child.unlink()
    for filename in ("book.css", "book.js", "Lako_icon.png"):
        shutil.copy2(ROOT / "assets" / filename, DIST / filename)
    shutil.copytree(ROOT / "assets" / "fonts", DIST / "fonts")
    output_images = DIST / "images"
    output_images.mkdir()
    referenced_images = {
        path
        for edition in editions.values()
        for _, path in edition["images"]
    }
    validate_web_images(referenced_images)
    for source_name in sorted(referenced_images):
        source_path = SOURCE / source_name
        web_name = f"{source_path.stem}.avif"
        shutil.copy2(WEB_IMAGES / web_name, output_images / web_name)
    for language, filename in (("hu", "index.html"), ("en", "index_en.html")):
        (DIST / filename).write_text(editions[language]["page"], encoding="utf-8")
        for resource in editions[language]["inventory"].resources:
            # The second HTML page is written in this same loop.
            if resource not in {"index.html", "index_en.html"} and not (DIST / resource).is_file():
                raise ValueError(f"Missing output resource: {resource}")
    workbench = (ROOT / "template" / "workbench.html").read_text(encoding="utf-8")
    image_data = [
        {"file": path.name, "preview": f"avif/{path.stem}.avif"}
        for path in sorted(SOURCE_IMAGES.iterdir())
        if path.is_file() and path.suffix.lower() in {".png", ".jpg", ".jpeg"}
    ]
    workbench = workbench.replace("{{ layout }}", json.dumps(layout, ensure_ascii=False))
    workbench = workbench.replace("{{ images }}", json.dumps(image_data, ensure_ascii=False))
    WORKBENCH.mkdir(exist_ok=True)
    (WORKBENCH / "index.html").write_text(workbench, encoding="utf-8")
    print(f"Bilingual build complete: {len(shared_ids)} shared IDs; local workbench refreshed outside dist.")


if __name__ == "__main__":
    main()
