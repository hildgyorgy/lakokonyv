#!/usr/bin/env python3
"""Build the Hungarian and English Markdown masters into static HTML editions."""
from __future__ import annotations

import html
import json
import re
import shutil
import struct
from functools import lru_cache
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "sources"
DIST = ROOT / "dist"

HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
IMAGE_RE = re.compile(r"!\[([^]]*)\]\(([^)]+)\)")
LINK_RE = re.compile(r"(?<!!)\[([^]]+)\]\(([^)]+)\)")
ANCHOR_RE = re.compile(r'<a\s+id="([^"]+)"\s*></a>')
MISSING_RE = re.compile(r"<!--\s*MISSING\s+([^:]+):")
ARTICLE_SPACE_RE = re.compile(r"(?<!\w)([Aa]z?) (?=\S)")


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
        f'<img{image_size_attributes(m.group(2))} src="{html.escape(m.group(2), quote=True)}" alt="{html.escape(m.group(1), quote=True)}" loading="lazy">'), text)
    text = LINK_RE.sub(lambda m: stash(
        f'<a href="{html.escape(m.group(2), quote=True)}">{inline(m.group(1), language)}</a>'), text)
    text = re.sub(r"<sup>([^<]+)</sup>", lambda m: stash("<sup>" + html.escape(m.group(1)) + "</sup>"), text)
    text = html.escape(text, quote=False)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<!\*)\*([^*]+?)\*(?!\*)", r"<em>\1</em>", text)
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    # Keep Hungarian articles attached to the following word in rendered HTML.
    # The source Markdown remains readable and uses ordinary spaces.
    if language == "hu":
        text = ARTICLE_SPACE_RE.sub(lambda match: match.group(1) + "\u00a0", text)
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


def render_markdown(text: str, layout: dict | None = None, language: str = "hu") -> tuple[str, str, set[str], list[str]]:
    format_inline = lambda value: inline(value, language)
    lines = text.splitlines()
    output: list[str] = []
    toc: list[tuple[int, str, str]] = []
    anchors: set[str] = set()
    missing: list[str] = []
    i = 0
    pending_anchor: str | None = None
    while i < len(lines):
        line = lines[i]
        anchor_match = ANCHOR_RE.fullmatch(line.strip())
        if anchor_match:
            pending_anchor = anchor_match.group(1)
            anchors.add(pending_anchor)
            i += 1
            continue
        if (m := MISSING_RE.search(line)):
            missing.append(m.group(1).strip())
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
            # The scan uses terminal punctuation consistently for numbered
            # subheadings, while the reconstructed master is mixed.
            title = re.sub(r"^(\d+(?:\.\d+)+)(?=\s)", r"\1.", title)
            anchor = pending_anchor or "heading-" + re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
            anchors.add(anchor)
            pending_anchor = None
            output.append(f'<h{level} id="{html.escape(anchor, quote=True)}">{format_inline(title)}</h{level}>')
            if level <= 6:
                toc.append((level, anchor, title))
            i += 1
            continue
        if line.startswith(">"):
            block: list[str] = []
            while i < len(lines) and (lines[i].startswith(">") or not lines[i].strip()):
                if lines[i].startswith(">"):
                    block.append(re.sub(r"^> ?", "", lines[i]))
                i += 1
            note = block and block[0].strip() in {"**Megjegyzés**", "**Note**"}
            body = "\n".join(block[1:] if note else block)
            if pending_anchor and "Hiányzó ábra" in body:
                output.append(f'<figure id="{html.escape(pending_anchor, quote=True)}" class="missing-figure"><figcaption>{format_inline(body)}</figcaption></figure>')
                pending_anchor = None
                continue
            # The reconstructed source contains some figures inside Markdown
            # blockquotes. They are source grouping, not editorial quotations.
            if (note and language == "en") or "![" in body or "<a id=" in body:
                nested, _nested_toc, nested_anchors, nested_missing = render_markdown(body, layout, language)
                output.append(f'<aside class="note">{nested}</aside>' if note else nested)
                anchors.update(nested_anchors)
                missing.extend(nested_missing)
                continue
            tag = "aside class=\"note\"" if note else "blockquote"
            output.append(f"<{tag}>{render_paragraphs(body, language)}</{tag.split()[0]}>")
            continue
        if re.match(r"^\s*[-*+]\s+", line) or re.match(r"^\s*\d+[.)]\s+", line):
            ordered = bool(re.match(r"^\s*\d+[.)]\s+", line))
            items: list[str] = []
            while i < len(lines):
                pat = r"^\s*\d+[.)]\s+(.*)$" if ordered else r"^\s*[-*+]\s+(.*)$"
                match = re.match(pat, lines[i])
                if not match: break
                items.append(f"<li>{format_inline(match.group(1))}</li>")
                i += 1
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
            missing_here = any(key in line or key in (lines[i] if i < len(lines) else "") for key in missing)
            classes = []
            if missing_here:
                classes.append("missing-figure")
            class_attr = f' class="{" ".join(classes)}"' if classes else ""
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
            output.append(f'<figure{figure_id}{class_attr}><img{image_class}{style_attr}{image_size_attributes(src)} src="{html.escape(src, quote=True)}" alt="{html.escape(m.group(1), quote=True)}" loading="lazy">{f"<figcaption>{caption}</figcaption>" if caption else ""}</figure>')
            pending_anchor = None
            i += 1
            continue
        paragraph: list[str] = [line]
        i += 1
        while i < len(lines) and lines[i].strip() and not HEADING_RE.match(lines[i]) and not lines[i].startswith(">") and not ANCHOR_RE.fullmatch(lines[i].strip()) and not lines[i].strip().startswith("<div"):
            paragraph.append(lines[i]); i += 1
        output.append(f"<p>{format_inline(' '.join(paragraph))}</p>")
    toc_html = build_toc([
        entry for entry in toc
        if entry[2] not in {"Lakóépületek tervezése", "Kivonat", "Housing design", "Abstract"}
    ], language)
    return "\n".join(output), toc_html, anchors, missing


def render_paragraphs(text: str, language: str = "hu") -> str:
    return "\n".join(f"<p>{inline(p, language)}</p>" for p in text.split("\n\n") if p.strip())


def build_toc(entries: list[tuple[int, str, str]], language: str = "hu") -> str:
    """Turn a flat heading list into nested, native HTML details controls."""
    root: list[dict] = []
    stack: list[tuple[int, list[dict]]] = [(-1, root)]
    for level, anchor, title in entries:
        while stack[-1][0] >= level:
            stack.pop()
        node = {"level": level, "anchor": anchor, "title": title, "children": []}
        stack[-1][1].append(node)
        stack.append((level, node["children"]))

    def render(nodes: list[dict]) -> str:
        items = []
        for node in nodes:
            link = f'<a href="#{html.escape(node["anchor"], quote=True)}">{inline(node["title"], language)}</a>'
            children = render(node["children"])
            if children:
                items.append(f'<li><details><summary>{link}</summary>{children}</details></li>')
            else:
                items.append(f"<li>{link}</li>")
        return "<ol>" + "".join(items) + "</ol>" if items else ""

    # The first H1 is the book title, not a structural parent. Keep its link
    # visible, but promote its children to the TOC root.
    if root and root[0]["title"] == "Lakóépületek tervezése":
        title_node = root.pop(0)
        title_link = f'<li><a href="#{html.escape(title_node["anchor"], quote=True)}">{inline(title_node["title"], language)}</a></li>'
        promoted = title_node["children"] + root
        return "<ol>" + title_link + render(promoted)[4:]
    return render(root)


class PageInventory(HTMLParser):
    """Validate actual emitted IDs and resources, not just parser bookkeeping."""
    def __init__(self, page: str):
        super().__init__()
        self.ids = []
        self.references = []
        self.resources = []
        self.locations = []
        self.feed(page)

    def handle_starttag(self, tag, attributes):
        attrs = dict(attributes)
        ident = attrs.get("id")
        if ident:
            self.ids.append(ident)
            if tag in {"h1", "h2", "h3", "h4", "h5", "h6", "figure"}:
                self.locations.append((tag, ident))
        for key in ("href", "src"):
            value = attrs.get(key, "")
            if value.startswith("#"):
                self.references.append(value[1:])
            elif value and ":" not in value and not value.startswith("//"):
                self.resources.append(value.split("#", 1)[0])

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
        content, toc, anchors, missing = render_markdown(markdown, layout, language)
        images = IMAGE_RE.findall(markdown)
        missing_images = sorted({path for _, path in images if not (SOURCE / path).is_file()})
        if missing_images:
            raise ValueError(f"{filename}: missing images: {missing_images}")
        values = dict(locales[language], language=language, title=metadata["title"])
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
        if missing:
            print("Documented missing elements: " + ", ".join(missing))

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
    for filename in ("book.css", "book.js", "workbench.css", "workbench.js", "Lako_icon.png", "site.webmanifest"):
        shutil.copy2(ROOT / "assets" / filename, DIST / filename)
    shutil.copytree(SOURCE / "images", DIST / "images")
    for language, filename in (("hu", "index.html"), ("en", "index_en.html")):
        (DIST / filename).write_text(editions[language]["page"], encoding="utf-8")
        for resource in editions[language]["inventory"].resources:
            # The second HTML page is written in this same loop.
            if resource not in {"index.html", "index_en.html"} and not (DIST / resource).is_file():
                raise ValueError(f"Missing output resource: {resource}")
    workbench = (ROOT / "template" / "workbench.html").read_text(encoding="utf-8")
    image_data = [{"file": path.name} for path in sorted((SOURCE / "images").iterdir()) if path.is_file() and not path.name.startswith(".")]
    workbench = workbench.replace("{{ layout }}", json.dumps(layout, ensure_ascii=False))
    workbench = workbench.replace("{{ images }}", json.dumps(image_data, ensure_ascii=False))
    (DIST / "workbench.html").write_text(workbench, encoding="utf-8")
    print(f"Bilingual build complete: {len(shared_ids)} shared IDs; one shared image directory and workbench.")


if __name__ == "__main__":
    main()
