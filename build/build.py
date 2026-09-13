#!/usr/bin/env python3
"""Build the single Lakókönyv Markdown master into a static HTML edition."""
from __future__ import annotations

import html
import json
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "source"
DIST = ROOT / "dist"

HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
IMAGE_RE = re.compile(r"!\[([^]]*)\]\(([^)]+)\)")
LINK_RE = re.compile(r"(?<!!)\[([^]]+)\]\(([^)]+)\)")
ANCHOR_RE = re.compile(r'<a\s+id="([^"]+)"\s*></a>')
MISSING_RE = re.compile(r"<!--\s*MISSING\s+([^:]+):")


def inline(text: str) -> str:
    placeholders: list[str] = []

    def stash(value: str) -> str:
        placeholders.append(value)
        return f"\x00{len(placeholders)-1}\x00"

    text = IMAGE_RE.sub(lambda m: stash(
        f'<img src="{html.escape(m.group(2), quote=True)}" alt="{html.escape(m.group(1), quote=True)}" loading="lazy">'), text)
    text = LINK_RE.sub(lambda m: stash(
        f'<a href="{html.escape(m.group(2), quote=True)}">{inline(m.group(1))}</a>'), text)
    text = html.escape(text, quote=False)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<!\*)\*([^*]+?)\*(?!\*)", r"<em>\1</em>", text)
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
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


def render_markdown(text: str, layout: dict[str, int] | None = None) -> tuple[str, str, set[str], list[str]]:
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
            output.append(f'<h{level} id="{html.escape(anchor, quote=True)}">{inline(title)}</h{level}>')
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
            note = block and block[0].strip() == "**Megjegyzés**"
            body = "\n".join(block[1:] if note else block)
            if pending_anchor and "Hiányzó ábra" in body:
                output.append(f'<figure id="{html.escape(pending_anchor, quote=True)}" class="missing-figure"><figcaption>{inline(body)}</figcaption></figure>')
                pending_anchor = None
                continue
            # The reconstructed source contains some figures inside Markdown
            # blockquotes. They are source grouping, not editorial quotations.
            if "![" in body or "<a id=" in body:
                nested, _nested_toc, nested_anchors, nested_missing = render_markdown(body, layout)
                output.append(f'<aside class="note">{nested}</aside>' if note else nested)
                anchors.update(nested_anchors)
                missing.extend(nested_missing)
                continue
            tag = "aside class=\"note\"" if note else "blockquote"
            output.append(f"<{tag}>{render_paragraphs(body)}</{tag.split()[0]}>")
            continue
        if re.match(r"^\s*[-*+]\s+", line) or re.match(r"^\s*\d+[.)]\s+", line):
            ordered = bool(re.match(r"^\s*\d+[.)]\s+", line))
            items: list[str] = []
            while i < len(lines):
                pat = r"^\s*\d+[.)]\s+(.*)$" if ordered else r"^\s*[-*+]\s+(.*)$"
                match = re.match(pat, lines[i])
                if not match: break
                items.append(f"<li>{inline(match.group(1))}</li>")
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
                caption = inline(lines[caption_index].strip()[1:-1])
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
            output.append(f'<figure{figure_id}{class_attr}><img{image_class}{style_attr} src="{html.escape(src, quote=True)}" alt="{html.escape(m.group(1), quote=True)}" loading="lazy">{f"<figcaption>{caption}</figcaption>" if caption else ""}</figure>')
            pending_anchor = None
            i += 1
            continue
        paragraph: list[str] = [line]
        i += 1
        while i < len(lines) and lines[i].strip() and not HEADING_RE.match(lines[i]) and not lines[i].startswith(">") and not ANCHOR_RE.fullmatch(lines[i].strip()) and not lines[i].strip().startswith("<div"):
            paragraph.append(lines[i]); i += 1
        output.append(f"<p>{inline(' '.join(paragraph))}</p>")
    toc_html = build_toc([
        entry for entry in toc
        if entry[2] not in {"Lakóépületek tervezése", "Kivonat"}
    ])
    return "\n".join(output), toc_html, anchors, missing


def render_paragraphs(text: str) -> str:
    return "\n".join(f"<p>{inline(p)}</p>" for p in text.split("\n\n") if p.strip())


def build_toc(entries: list[tuple[int, str, str]]) -> str:
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
            link = f'<a href="#{html.escape(node["anchor"], quote=True)}">{inline(node["title"])}</a>'
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
        title_link = f'<li><a href="#{html.escape(title_node["anchor"], quote=True)}">{inline(title_node["title"])}</a></li>'
        promoted = title_node["children"] + root
        return "<ol>" + title_link + render(promoted)[4:]
    return render(root)


def main() -> None:
    metadata, markdown = parse_frontmatter((SOURCE / "lakokonyv.md").read_text(encoding="utf-8"))
    layout_path = ROOT / "audit" / "image_layout.json"
    layout = json.loads(layout_path.read_text(encoding="utf-8")) if layout_path.exists() else {}
    content, toc, anchors, missing = render_markdown(markdown, layout)
    references = set(re.findall(r"\]\(#([^)]*)\)", markdown))
    unresolved = sorted(references - anchors)
    image_paths = IMAGE_RE.findall(markdown)
    missing_files = sorted({path for _, path in image_paths if not (SOURCE / path).is_file() and not any(key in path for key in missing)})
    if unresolved:
        raise SystemExit("Hibás belső hivatkozás(ok): " + ", ".join(unresolved))
    if missing_files:
        raise SystemExit("Hiányzó kép(ek): " + ", ".join(missing_files))
    DIST.mkdir(exist_ok=True)
    for child in DIST.iterdir():
        if child.is_dir(): shutil.rmtree(child)
        else: child.unlink()
    shutil.copy2(ROOT / "assets" / "book.css", DIST / "book.css")
    shutil.copy2(ROOT / "assets" / "book.js", DIST / "book.js")
    shutil.copy2(ROOT / "assets" / "workbench.css", DIST / "workbench.css")
    shutil.copy2(ROOT / "assets" / "workbench.js", DIST / "workbench.js")
    shutil.copytree(SOURCE / "images", DIST / "images")
    template = (ROOT / "template" / "book.html").read_text(encoding="utf-8")
    page = template.replace("{{ title }}", html.escape(metadata.get("title", "Lakókönyv")))
    page = page.replace("{{ toc }}", toc).replace("{{ content }}", content)
    (DIST / "index.html").write_text(page, encoding="utf-8")
    workbench = (ROOT / "template" / "workbench.html").read_text(encoding="utf-8")
    image_data = [{"file": path.name} for path in sorted((SOURCE / "images").iterdir()) if path.is_file()]
    workbench = workbench.replace("{{ layout }}", json.dumps(layout, ensure_ascii=False))
    workbench = workbench.replace("{{ images }}", json.dumps(image_data, ensure_ascii=False))
    (DIST / "workbench.html").write_text(workbench, encoding="utf-8")
    print(f"Build kész: {len(image_paths)} kép-hivatkozás, {len(anchors)} anchor, {len(references)} belső hivatkozás.")
    if missing:
        print("Figyelem: dokumentált MISSING elemek: " + ", ".join(missing))


if __name__ == "__main__":
    main()
