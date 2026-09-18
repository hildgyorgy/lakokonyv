#!/usr/bin/env python3
"""Recreate the English Markdown from its consolidated archival DocBook.

Requires only Python's standard library. Refuses to overwrite the English master.
Not part of the regular build. See audit/english_import.md.
"""
from __future__ import annotations

import hashlib
import html
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCES = ROOT / 'sources'
ENGLISH_XML = SOURCES / 'xml' / 'Bito_konyv_en.xml'
STRUCTURE = {'preface': 1, 'chapter': 1, 'sect1': 2, 'sect2': 3, 'sect3': 4}
# The English DocBook splits a few passages more finely than the Hungarian
# master.  These titles are editorial subdivisions, so their text remains in
# place but their headings are suppressed when the English Markdown is made.
SUPPRESS_HEADINGS = {
    '3.3.1. Town planning codes and standards',
    '4.2.1. European Development',
    '4.2.2. Hungarian Development',
    '5.2.1. Hungarian situation since the 1950s',
    'Additional heating assistance',
}

# The supplied English DocBook omitted eleven figure placements that are present
# in the Hungarian master.  Nine are distinct illustrations; two are deliberate
# repeats in Chapter 5.  They use the same shared image assets as both editions.
SUPPLEMENTAL_FIGURES = (
    {
        'phrase': 'A residential area (room) can be assigned its given area',
        'replacements': (('([fig. 1.16](#abra_1_16))', '([fig. 1.18](#abra_1_18))'),),
        'id': 'abra_1_18', 'number': '1.18',
        'image': 'images/abra_1_18_butorcsprt2_m.png',
        'caption': 'Determining room dimensions based on furniture arrangement',
    },
    {
        'phrase': 'For alternative layouts to personal hygiene spaces',
        'replacements': (('figure 1.36', '[figure 1.36](#abra_1_36)'),),
        'id': 'abra_1_36', 'number': '1.36',
        'image': 'images/abra_1_36_higenhelys_m.png',
        'caption': 'Examples of sanitary-space layouts and dimensions',
    },
    {
        'phrase': 'Clothes can be stored in mobile cabinets',
        'replacements': (('(fig. 1.38)', '([fig. 1.38](#abra_1_38))'),),
        'id': 'abra_1_38', 'number': '1.38',
        'image': 'images/abra_1_38_ruhatarolas.png',
        'caption': 'Clothing storage arrangements',
    },
    {
        'phrase': 'Grocery storage (excluding that which is stored',
        'replacements': (('(fig. 1.39)', '([fig. 1.39](#abra_1_39))'),),
        'id': 'abra_1_39', 'number': '1.39',
        'image': 'images/abra_1_39_elelemtarolas.png',
        'caption': 'Food storage arrangements',
    },
    {
        'phrase': 'Single bedrooms are at least 8.00m²',
        'replacements': (('figure 1.44', '[figure 1.44](#abra_1_44)'),),
        'id': 'abra_1_44', 'number': '1.44',
        'image': 'images/abra_1_44_halotc.png',
        'caption': 'Example of a room arranged for different uses',
    },
    {
        'phrase': 'A free-standing building should have land on all four sides',
        'replacements': (('([fig. 3.10](#abra_3_10))', '([fig. 3.11](#abra_3_11))'),),
        'id': 'abra_3_11', 'number': '3.11',
        'image': 'images/abra_3_11_csbepmsz.png',
        'caption': 'Plot development rules for detached housing',
    },
    {
        'phrase': 'Flat roofs allow for freer contour planning',
        'replacements': (('Figure 3.52', '[Figure 3.52](#abra_3_52)'),),
        'id': 'abra_3_52', 'number': '3.52',
        'image': 'images/abra_3_52_tefoforma.png',
        'caption': 'Common pitched-roof forms used for housing',
    },
    {
        'phrase': 'Sizes for single and double garages were included',
        'replacements': (
            ('Sections 3.22.', '[Sections 3.22.](#abra_3_22_E5)'),
            ('and 3.23.', 'and [3.23.](#abra_3_23_E5)'),
        ),
        'figures': (
            ('abra_3_22_E5', '3.22', 'images/abra_3_22_autohelymod.png',
             'Motor car dimensions and turning circle'),
            ('abra_3_23_E5', '3.23', 'images/abra_3_23_cshgarazshely_m.png',
             'Spatial requirements for motor car storage'),
        ),
    },
    {
        'phrase': 'Agriculture, due to financial recession, has declined',
        'append_reference': ' ([fig. 6.3](#abra_6_03))',
        'id': 'abra_6_03', 'number': '6.3',
        'image': 'images/abra_6_03_unagy.png',
        'caption': 'Holiday home in a rural setting. Architect: Gábor U. Nagy',
    },
    {
        'phrase': 'An alternative method, called rehabilitation',
        'replacements': (('(fig. 5.19)', '([fig. 5.19](#abra_5_19))'),),
        'id': 'abra_5_19', 'number': '5.19',
        'image': 'images/abra_5_19_ferencv.png',
        'caption': ('Budapest, Ferencváros. Residential-area rehabilitation, '
                    '1987–1990. Master plan: Gábor Locsmándi; lead architect: '
                    'Zsolt Gyüre, TTI'),
    },
)


def read_xml(path):
    text = path.read_text(encoding='utf-8')
    text = re.sub(r'<!DOCTYPE[^[]*?\[.*?\]\s*>|<!DOCTYPE[^>]*>', '', text, flags=re.S)
    text = text.replace('<book lang="en">', '<book lang="en" xmlns:xi="http://www.w3.org/2001/XInclude">')
    # Resolve named character entities locally, never fetch a remote DTD.
    text = re.sub(r'&([A-Za-z][A-Za-z0-9]+);', lambda m: m[0] if m[1] in {'amp', 'lt', 'gt', 'quot', 'apos'} else html.escape(html.unescape(m[0])), text)
    return ET.fromstring(text)


def norm(text):
    return re.sub(r'\s+', ' ', text).strip()


def slug(text):
    return 'heading-' + re.sub(r'[^a-z0-9]+', '-', text.lower()).strip('-')


def add_supplemental_figures(markdown):
    """Restore Hungarian-master figure placements in their matching EN paragraphs."""
    records = []
    for item in SUPPLEMENTAL_FIGURES:
        start = markdown.index(item['phrase'])
        end = markdown.find('\n\n', start)
        if end == -1:
            raise ValueError('Could not find paragraph end for ' + item['phrase'])
        paragraph = markdown[start:end]
        for old, new in item.get('replacements', ()):
            if old not in paragraph:
                raise ValueError(f'Missing expected reference {old!r} in {item["phrase"]!r}')
            paragraph = paragraph.replace(old, new, 1)
        paragraph += item.get('append_reference', '')
        figures = item.get('figures') or ((item['id'], item['number'], item['image'], item['caption']),)
        blocks = []
        for ident, number, image, caption in figures:
            blocks.append(f'<a id="{ident}"></a>\n\n![{caption}]({image})\n\n*Figure {number} – {caption}*')
            records.append({'id': ident, 'shared_image': image, 'caption': caption})
        markdown = markdown[:start] + paragraph + '\n\n' + '\n\n'.join(blocks) + markdown[end:]
    return markdown, records


def main():
    destination = SOURCES / 'lakokonyv_en.md'
    if destination.exists() and '--force' not in sys.argv:
        raise SystemExit('English master already exists; edit it directly instead of re-importing.')
    hu = (SOURCES / 'lakokonyv.md').read_text(encoding='utf-8')
    plain_hu = re.sub(r'^> ?', '', hu, flags=re.M)
    hu_figures = dict(re.findall(r'<a id="(abra_[^"]+)"></a>\s*!\[[^\]]*\]\(([^)]+)\)', plain_hu))
    assert len(hu_figures) == 212, len(hu_figures)
    headings = {}
    pending = None
    for line in hu.splitlines():
        anchor = re.fullmatch(r'<a id="([^"]+)"></a>', line)
        if anchor:
            pending = anchor[1]
        elif match := re.match(r'^(#{1,6}) (.+)', line):
            title = match[2]
            rendered_title = re.sub(r'^(\d+(?:\.\d+)+)(?=\s)', r'\1.', title)
            ident = pending or slug(rendered_title)
            headings[title] = ident
            if number := re.match(r'(\d+(?:\.\d+)*)\.?\s', title):
                headings[number[1]] = ident
            pending = None
        elif line.strip() and not line.startswith('>'):
            pending = None
    # Unnumbered Hungarian headings with known English numbered counterparts.
    headings['3.3.1'] = headings['Hatósági építési követelmények, szabályzatok']
    headings['4.2.1'] = headings['Az európai fejlődés']
    root = read_xml(ENGLISH_XML)
    chapters = [element for element in root if element.tag in {'preface', 'chapter'}]
    if len(chapters) != 8:
        raise ValueError(f'Expected the introduction and seven chapters, found {len(chapters)}')

    idmap = {'abra_3_15': 'abra_3_14'}
    element_ids = {}
    section_records = []
    for chapter_no, chapter in enumerate(chapters):
        for element in chapter.iter():
            if element.tag not in STRUCTURE:
                continue
            title = norm(''.join(element.find('title').itertext()))
            if element.tag == 'preface':
                ident = headings['Bevezetés']
            elif element.tag == 'chapter':
                ident = headings[str(chapter_no)]
            else:
                match = re.match(r'(\d+(?:\.\d+)*)\.?\s', title)
                ident = headings.get(match[1]) if match else None
                ident = ident or 'en-' + slug(title)
            element_ids[element] = ident
            if element.get('id'):
                idmap[element.get('id')] = ident
            section_records.append({'english_title': title, 'shared_id': ident, 'shared_with_hu': ident in headings.values()})

    figures = []
    def inline(element):
        result = element.text or ''
        for child in element:
            body = inline(child)
            if child.tag == 'emphasis':
                token = '**' if child.get('role') == 'bold' else '*'
                raw = ''.join(child.itertext())
                result += (' ' if raw[:1].isspace() else '') + token + body.strip() + token + (' ' if raw[-1:].isspace() else '')
            elif child.tag == 'link':
                target = idmap.get(child.get('linkend'), child.get('linkend'))
                result += '[' + body + '](#' + target + ')'
            elif child.tag == 'superscript':
                result += '<sup>' + body + '</sup>'
            else:
                raise ValueError('Unsupported inline element: ' + child.tag)
            result += child.tail or ''
        return norm(result)

    def children(element):
        parts = []
        previous = None
        for child in element:
            if previous == child.tag == 'note':
                parts.append('<!-- Separate source notes. -->')
            parts.append(block(child))
            previous = child.tag
        return '\n\n'.join(filter(None, parts))

    def children_without_title(element):
        container = ET.Element('container')
        for child in element:
            if child.tag != 'title': container.append(child)
        return children(container)

    def block(element):
        tag = element.tag
        if tag in STRUCTURE:
            title = inline(element.find('title'))
            plain_title = norm(''.join(element.find('title').itertext()))
            if tag == 'chapter':
                title = str(chapters.index(element)) + '. ' + title
            if plain_title in SUPPRESS_HEADINGS:
                return children_without_title(element)
            return '<a id="' + element_ids[element] + '"></a>\n' + '#' * STRUCTURE[tag] + ' ' + title + '\n\n' + children_without_title(element)
        if tag == 'para':
            if all(c.tag in {'emphasis', 'link', 'superscript'} for c in element):
                return inline(element)
            pieces, current = [], element.text or ''
            for child in element:
                if child.tag in {'emphasis', 'link', 'superscript'}:
                    wrapper = ET.Element('para'); wrapper.append(child)
                    current += inline(wrapper)
                else:
                    if norm(current): pieces.append(norm(current))
                    pieces.append(block(child)); current = child.tail or ''
            if norm(current): pieces.append(norm(current))
            return '\n\n'.join(pieces)
        if tag == 'figure':
            original_id = element.get('id')
            ident = idmap.get(original_id, original_id)
            image = hu_figures[ident]
            caption = inline(element.find('title'))
            number = '.'.join(str(int(n)) for n in ident.split('_')[1:])
            figures.append({'source_id': original_id, 'id': ident, 'shared_image': image,
                            'original_web_image': element.find('.//imageobject[@condition="web"]/imagedata').get('fileref')})
            alt = caption.replace('[', '(').replace(']', ')')
            return f'<a id="{ident}"></a>\n\n![{alt}]({image})\n\n*Figure {number} – {caption}*'
        if tag in {'note', 'blockquote'}:
            body = ('**Note**\n\n' if tag == 'note' else '') + children(element)
            return '\n'.join('> ' + line if line else '>' for line in body.splitlines())
        if tag in {'variablelist', 'varlistentry', 'listitem'}:
            return children(element)
        if tag in {'title', 'term'}:
            return '**' + inline(element) + '**'
        if tag == 'itemizedlist':
            return '\n'.join('- ' + block(child).replace('\n\n', ' ').replace('\n', ' ') for child in element)
        if tag == 'literallayout':
            return '\n\n'.join(norm(line) for line in ''.join(element.itertext()).splitlines() if norm(line))
        raise ValueError('Unsupported block element: ' + tag)

    info = root.find('bookinfo')
    abstract = children(info.find('abstract'))
    legal = children(info.find('legalnotice'))
    copyright_holder = norm(''.join(info.find('copyright/holder').itertext()))
    project = norm(''.join(info.findall('copyright/holder')[1].itertext()))
    front = f'''---
title: "Housing design"
language: "en"
author: "János Bitó"
translator: "Oliver Sales"
publisher: "Budapest University of Technology and Economics, Department of Residential Buildings"
publication_year: 2013
master_format: "single Markdown + shared original image assets"
reconstruction_basis: "English DocBook XML, checked against supplied HTML"
reconstruction_notes: "audit/english_import.md"
---

János Bitó
<a id="{headings['Lakóépületek tervezése']}"></a>
# Housing design
© 2013 {copyright_holder}

<div class="project-logos">
![Department of Residential Buildings](images/Lako_tanszek.png)
</div>

<a id="{headings['Közreműködők']}"></a>
### Contributors
András Pandula – accessibility;
Ágnes Novák – sustainability;
Oliver Sales – translation.

{project}

<a id="{headings['Kivonat']}"></a>
### Abstract

{abstract}

{legal}

'''
    markdown = front + '\n\n'.join(block(chapter) for chapter in chapters) + '\n'
    markdown, supplemental_figures = add_supplemental_figures(markdown)
    destination.write_text(markdown, encoding='utf-8')
    english_ids = {f['id'] for f in figures}
    source_files = [ENGLISH_XML]
    report = {
        'source_sha256': {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in source_files},
        'sections': section_records, 'figures': figures,
        'source_english_figures_missing_vs_hungarian': sorted(set(hu_figures) - english_ids),
        'supplemental_figures': supplemental_figures,
        'rendered_english_figure_count': len(figures) + len(supplemental_figures),
        'hungarian_figures_absent_after_supplement': sorted(
            set(hu_figures) - english_ids - {f['id'] for f in supplemental_figures}),
        'english_only_headings': [s for s in section_records if not s['shared_with_hu']],
        'xml_paragraphs': sum(len(c.findall('.//para')) for c in chapters),
        'xml_notes': sum(len(c.findall('.//note')) for c in chapters),
        'xml_links': sum(len(c.findall('.//link')) for c in chapters),
    }
    (ROOT / 'audit/english_import.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f'Imported {len(section_records)} sections, {len(figures)} figures, {report["xml_notes"]} notes.')
    print('English-only headings:', report['english_only_headings'])
    print('Figures absent after supplement:', report['hungarian_figures_absent_after_supplement'])


if __name__ == '__main__':
    main()
