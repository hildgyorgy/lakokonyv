"""Regression checks for a built bilingual edition; run after build.py."""
import json
import re
import unittest
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def normalized(value):
    return re.sub(r'\s+', ' ', value).strip()


class BookPage(HTMLParser):
    def __init__(self, path):
        super().__init__()
        self.ids, self.links, self.images, self.headings = [], [], {}, []
        self.article_links = []
        self.figure_id = None
        self.article = False
        self.text = []
        self.notes = 0
        self.html = path.read_text(encoding='utf-8')
        self.feed(self.html)
        self.visible_text = normalized(''.join(self.text))
        self.targets = json.loads(re.search(r'<script id="language-targets" type="application/json">(.*?)</script>', self.html, re.S)[1])

    def handle_starttag(self, tag, attributes):
        attrs = dict(attributes)
        if tag == 'html': self.language = attrs['lang']
        if tag == 'article': self.article = True
        if 'id' in attrs: self.ids.append(attrs['id'])
        if tag == 'a':
            self.links.append(attrs.get('href', ''))
            if self.article: self.article_links.append(attrs.get('href', ''))
        if tag == 'figure': self.figure_id = attrs.get('id', 'logo')
        if tag == 'img': self.images[self.figure_id] = attrs
        if tag == 'aside' and attrs.get('class') == 'note': self.notes += 1
        if re.fullmatch(r'h[1-6]', tag) and self.article: self.headings.append(attrs['id'])
        if self.article and tag in {'p', 'h1', 'h2', 'h3', 'h4', 'li', 'figure', 'aside', 'figcaption'}: self.text.append('\n')

    def handle_endtag(self, tag):
        if tag == 'article': self.article = False
        if tag == 'figure': self.figure_id = None
        if self.article and tag in {'p', 'h1', 'h2', 'h3', 'h4', 'li', 'figure', 'aside', 'figcaption'}: self.text.append('\n')

    def handle_data(self, data):
        if self.article: self.text.append(data)


class BilingualBookTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.hu = BookPage(ROOT / 'dist/index.html')
        cls.en = BookPage(ROOT / 'dist/index_en.html')
        cls.xml = ET.parse(ROOT / 'sources/xml/Bito_konyv_en.xml')
        cls.audit = json.loads((ROOT / 'audit/english_import.json').read_text())

    def test_valid_pages_and_links(self):
        for language, page in [('hu', self.hu), ('en', self.en)]:
            self.assertEqual(page.language, language)
            self.assertEqual(len(page.ids), len(set(page.ids)))
            for link in page.links:
                if link.startswith('#'): self.assertIn(link[1:], page.ids)
            self.assertNotRegex(page.html, r'{{ [a-z_]+ }}')

    def test_english_source_paragraphs_preserved(self):
        checked = 0
        for chapter in self.xml.getroot():
            if chapter.tag not in {'chapter', 'preface'}: continue
            for para in chapter.iter('para'):
                if any(e.tag in {'figure', 'itemizedlist', 'variablelist'} for e in para.iter()): continue
                text = normalized(''.join(para.itertext()))
                # Correct two demonstrably stale figure numbers while retaining
                # the translated paragraph itself.
                text = text.replace('(fig. 1.16)', '(fig. 1.18)') if text.startswith('A residential area (room)') else text
                text = text.replace('(fig. 3.10)', '(fig. 3.11)') if text.startswith('A free-standing building') else text
                self.assertIn(text, self.en.visible_text)
                checked += 1
        self.assertEqual(checked, 1152)
        self.assertEqual(self.en.notes, 48)
        self.assertEqual(len(self.en.article_links), 321)

    def test_shared_images_keep_workbench_settings(self):
        self.assertEqual(len(self.en.images) - 1, 212)
        for ident, image in self.en.images.items():
            for attribute in ('src', 'style', 'class', 'width', 'height'):
                self.assertEqual(image.get(attribute), self.hu.images[ident].get(attribute), (ident, attribute))
            self.assertTrue((ROOT / 'dist' / image['src']).is_file())
            self.assertGreater(int(image['width']), 0)
            self.assertGreater(int(image['height']), 0)

    def test_supplemental_figures_complete_hungarian_set(self):
        expected = {
            'abra_1_18', 'abra_1_36', 'abra_1_38', 'abra_1_39', 'abra_1_44',
            'abra_3_11', 'abra_3_22_E5', 'abra_3_23_E5', 'abra_3_52',
            'abra_5_19', 'abra_6_03',
        }
        self.assertEqual({f['id'] for f in self.audit['supplemental_figures']}, expected)
        self.assertEqual(self.audit['rendered_english_figure_count'], 212)
        self.assertEqual(self.audit['hungarian_figures_absent_after_supplement'], [])

    def test_language_switch_targets_exist(self):
        for source, target in [(self.hu, self.en), (self.en, self.hu)]:
            for origin, destination in source.targets.items():
                self.assertIn(origin, source.ids)
                self.assertIn(destination, target.ids)
                if origin in target.ids: self.assertEqual(origin, destination)
        # English-only editorial subdivisions are folded into their shared
        # Hungarian parent and therefore have no standalone rendered target.
        for heading in ('3.3.1. Town planning codes and standards',
                        '4.2.1. European Development',
                        '4.2.2. Hungarian Development',
                        '5.2.1. Hungarian situation since the 1950s',
                        'Additional heating assistance'):
            self.assertNotIn(heading, self.en.visible_text)


if __name__ == '__main__':
    unittest.main()
