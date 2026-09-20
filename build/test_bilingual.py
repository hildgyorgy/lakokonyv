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
        if re.fullmatch(r'h[1-6]', tag) and self.article and 'id' in attrs: self.headings.append(attrs['id'])
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
        cls.hu_xml = ET.parse(ROOT / 'sources/xml/Bito_konyv_hu.xml')
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
                # The Markdown master normalizes square-metre units typographically.
                text = re.sub(r'\bm2\b', 'm²', text)
                # Correct two demonstrably stale figure numbers while retaining
                # the translated paragraph itself, plus one source typo.
                text = text.replace('(fig. 1.16)', '(fig. 1.18)') if text.startswith('A residential area (room)') else text
                text = text.replace('(fig. 3.10)', '(fig. 3.11)') if text.startswith('A free-standing building') else text
                text = text.replace('indispensible', 'indispensable')
                text = text.replace(
                    'who are identified in certain chapters by the respective initials (AN) and (AP).',
                    'whose full names are shown alongside the chapters and supplementary passages they authored.',
                )
                text = re.sub(r'\s*\((?:AN|AP)\)\.?$', '', text)
                self.assertIn(text, self.en.visible_text)
                checked += 1
        self.assertEqual(checked, 1152)
        self.assertEqual(self.en.notes, 46)
        self.assertEqual(len(self.en.article_links), 321)

    def test_shared_images_keep_workbench_settings(self):
        self.assertEqual(len(self.en.images) - 1, 212)
        for ident, image in self.en.images.items():
            for attribute in ('src', 'style', 'class', 'width', 'height'):
                self.assertEqual(image.get(attribute), self.hu.images[ident].get(attribute), (ident, attribute))
            self.assertTrue((ROOT / 'dist' / image['src']).is_file())
            self.assertGreater(int(image['width']), 0)
            self.assertGreater(int(image['height']), 0)

    def test_workbench_is_local_and_outside_publication(self):
        workbench = (ROOT / 'workbench/index.html').read_text(encoding='utf-8')
        self.assertFalse((ROOT / 'dist/workbench.html').exists())
        self.assertFalse((ROOT / 'dist/workbench.js').exists())
        self.assertFalse((ROOT / 'dist/workbench.css').exists())
        self.assertIn('../assets/workbench.css', workbench)
        self.assertIn('../assets/workbench.js', workbench)
        self.assertIn('window.LAYOUT_DATA =', workbench)
        self.assertIn('window.IMAGE_DATA =', workbench)
        self.assertIn('../sources/images/', (ROOT / 'assets/workbench.js').read_text(encoding='utf-8'))

    def test_requirement_labels_and_loose_lists(self):
        self.assertIn(
            '<h4>KÖVETELMÉNYEK ÉS AJÁNLÁSOK</h4>',
            self.hu.html,
        )
        self.assertIn(
            '<p><strong>ALAPKÖVETELMÉNY:</strong> Biztosítani kell',
            self.hu.html,
        )
        self.assertNotIn('<strong>BÚTORIGÉNY:</strong> -', self.hu.html)
        self.assertIn(
            'legalább 4 személynek</li><li>3-4 férőhelyes lakásban legalább 5 személynek',
            self.hu.html,
        )

    def test_explicit_contributor_credits(self):
        monograms = re.compile(r'\((?:N\.\s*Á\.|P\.\s*A\.|B\.\s*J\.|AN|AP|(?:Dr\.\s*)?JB)\)')
        for source in (ROOT / 'sources/lakokonyv.md', ROOT / 'sources/lakokonyv_en.md'):
            self.assertNotRegex(source.read_text(encoding='utf-8'), monograms)
        self.assertIn('<p class="contributor-credit">— Novák Ágnes</p>', self.hu.html)
        self.assertIn('<p class="contributor-credit">— Ágnes Novák</p>', self.en.html)
        self.assertIn(
            '<h3 id="E1_Vizualis_komfort">1.5.6. Vizuális komfort</h3>\n'
            '<p class="contributor-credit heading-credit">— Novák Ágnes</p>',
            self.hu.html,
        )
        self.assertNotIn('Vizuális komfort (N.', self.hu.html)

    def test_historical_sections_are_explicit_markdown_headings(self):
        self.assertIn(
            '<h3 id="E3_falusi_csaladi_hazak">3.2.1. A\u00a0falusi családi házak</h3>',
            self.hu.html,
        )
        self.assertIn(
            '<h3 id="E3_varosias_csaladi_hazak">3.2.2. Urban Homes</h3>',
            self.en.html,
        )
        for page in (self.hu, self.en):
            self.assertEqual(page.targets['E3_falusi_csaladi_hazak'], 'E3_falusi_csaladi_hazak')
            self.assertEqual(page.targets['E3_varosias_csaladi_hazak'], 'E3_varosias_csaladi_hazak')

    def test_supplemental_figures_complete_hungarian_set(self):
        expected = {
            'abra_1_18', 'abra_1_36', 'abra_1_38', 'abra_1_39', 'abra_1_44',
            'abra_3_11', 'abra_3_22_E5', 'abra_3_23_E5', 'abra_3_52',
            'abra_5_19', 'abra_6_03',
        }
        self.assertEqual({f['id'] for f in self.audit['supplemental_figures']}, expected)
        self.assertEqual(self.audit['rendered_english_figure_count'], 212)
        self.assertEqual(self.audit['hungarian_figures_absent_after_supplement'], [])

    def test_consolidated_xml_archives(self):
        hu_root = self.hu_xml.getroot()
        en_root = self.xml.getroot()
        for root, figures in ((hu_root, 212), (en_root, 201)):
            self.assertIsNotNone(root.find('bookinfo'))
            self.assertEqual(len(root.findall('preface')), 1)
            self.assertEqual(len(root.findall('chapter')), 7)
            self.assertEqual(len(root.findall('.//figure')), figures)

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

    def test_self_hosted_inter_fonts(self):
        css = (ROOT / 'dist/book.css').read_text(encoding='utf-8')
        for filename in ('InterVariable.woff2', 'InterVariable-Italic.woff2'):
            self.assertIn(f'fonts/{filename}', css)
            self.assertTrue((ROOT / 'dist/fonts' / filename).is_file())
        self.assertTrue((ROOT / 'dist/fonts/LICENSE.txt').is_file())


if __name__ == '__main__':
    unittest.main()
