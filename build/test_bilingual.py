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
        self.list_items = []
        self.current_list_item = None
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
        if tag == 'li' and self.article: self.current_list_item = []
        if re.fullmatch(r'h[1-6]', tag) and self.article and 'id' in attrs: self.headings.append(attrs['id'])
        if self.article and tag in {'p', 'h1', 'h2', 'h3', 'h4', 'h5', 'li', 'figure', 'aside', 'figcaption'}: self.text.append('\n')

    def handle_endtag(self, tag):
        if tag == 'li' and self.current_list_item is not None:
            self.list_items.append(normalized(''.join(self.current_list_item)))
            self.current_list_item = None
        if tag == 'article': self.article = False
        if tag == 'figure': self.figure_id = None
        if self.article and tag in {'p', 'h1', 'h2', 'h3', 'h4', 'h5', 'li', 'figure', 'aside', 'figcaption'}: self.text.append('\n')

    def handle_data(self, data):
        if self.article:
            self.text.append(data)
            if self.current_list_item is not None: self.current_list_item.append(data)


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

        css = (ROOT / 'dist/book.css').read_text(encoding='utf-8')
        self.assertIn('.book-content a[href^="#"] { color: var(--accent); font-weight: 600; }', css)
        self.assertIn('-webkit-hyphenate-limit-before: 5;', css)
        self.assertIn('-webkit-hyphenate-limit-after: 5;', css)
        self.assertIn('hyphenate-limit-chars: 10 5 5;', css)

    def test_semantic_html_and_explicit_note_blocks(self):
        for source, page, expected_notes in (
            (ROOT / 'sources/lakokonyv.md', self.hu, 83),
            (ROOT / 'sources/lakokonyv_en.md', self.en, 45),
        ):
            markdown = source.read_text(encoding='utf-8')
            self.assertEqual(len(re.findall(r'^::: note$', markdown, re.M)), expected_notes)
            self.assertEqual(len(re.findall(r'^:::$', markdown, re.M)), expected_notes)
            self.assertNotRegex(markdown, re.compile(r'^> \*\*(?:Megjegyzés|Note)\*\*$', re.M))
            self.assertEqual(page.notes, expected_notes)
            self.assertNotIn('<p>---</p>', page.html)
            self.assertNotIn('<p>*</p>', page.html)
            self.assertNotIn('</strong></em>', page.html)
            self.assertIn('<nav id="book-toc"', page.html)
            self.assertNotIn('<details', page.html)
            self.assertNotIn('<summary', page.html)
            self.assertIn('class="skip-link"', page.html)
            self.assertEqual(page.html.count('<h1'), 1)
            self.assertIn('<link rel="canonical" href="https://hildgyorgy.github.io/lakokonyv/', page.html)
            self.assertIn('hreflang="x-default"', page.html)
            self.assertNotIn('rel="manifest"', page.html)
            self.assertEqual(page.html.count('<header class="book-title">'), 1)
            self.assertRegex(page.html, r'<section class="book-section level-2" aria-labelledby="E1_lakas">')
            self.assertRegex(page.html, r'<section class="book-section level-3" aria-labelledby="E1_A_fejezet_temakore">')

        self.assertIn('pl.\u00a0gyermek születésével', self.hu.html)
        self.assertNotIn('pl. gyermek születésével', self.hu.html)

    def test_english_source_paragraphs_preserved(self):
        checked = 0
        for chapter in self.xml.getroot():
            if chapter.tag not in {'chapter', 'preface'}: continue
            for para in chapter.iter('para'):
                if any(e.tag in {'figure', 'itemizedlist', 'variablelist'} for e in para.iter()): continue
                text = normalized(''.join(para.itertext()))
                if text == '*':
                    # The source ornament is rendered as a semantic separator.
                    checked += 1
                    continue
                # The Markdown master normalizes square-metre units typographically.
                text = re.sub(r'\bm2\b', 'm²', text)
                # Correct two demonstrably stale figure numbers while retaining
                # the translated paragraph itself, plus one source typo.
                text = text.replace('(fig. 1.16)', '(fig. 1.18)') if text.startswith('A residential area (room)') else text
                text = text.replace('(fig. 3.10)', '(fig. 3.11)') if text.startswith('A free-standing building') else text
                text = text.replace('indispensible', 'indispensable')
                text = text.replace('it is not does cover everything', 'it does not cover everything')
                text = text.replace('Könvykiadó', 'Könyvkiadó')
                text = text.replace('In the first and third chapters,', 'In Section 1.3,')
                text = text.replace('multi-storey', 'multi-story').replace('centre', 'center')
                text = text.replace('Two quantities are fall within the golden ratio', 'Two quantities fall within the golden ratio')
                text = text.replace('using the public bone as the center of the square', 'using the pubic bone as the center of the square')
                text = text.replace('where altered to take on an "L" shape', 'were altered to take on an "L" shape')
                text = text.replace('T own planning structure', 'Town planning structure')
                text = text.replace('The handrail should also rises', 'The handrail should also rise')
                text = text.replace('The later results in the loss', 'The latter results in the loss')
                text = text.replace('4- 5 stories', '4-5 stories')
                text = text.replace(
                    'usually parking in perpendicular rows as shown in figure 5.42.',
                    'usually parking in perpendicular rows as shown in figure 5.52.',
                )
                text = text.replace('(See Section 3.1.1.)', '(See Section 3.2.1.)')
                text = text.replace(
                    'who are identified in certain chapters by the respective initials (AN) and (AP).',
                    'whose full names are shown alongside the chapters and supplementary passages they authored.',
                )
                text = re.sub(r'\s*\((?:AN|AP)\)\.?$', '', text)
                self.assertIn(text, self.en.visible_text)
                checked += 1
        self.assertEqual(checked, 1152)
        self.assertEqual(self.hu.notes, 83)
        self.assertEqual(self.en.notes, 45)
        self.assertEqual(len(self.en.article_links), 357)

    def test_shared_images_keep_workbench_settings(self):
        self.assertEqual(len(self.en.images) - 1, 218)
        restored_figures = {
            'abra_1_37', 'abra_3_17', 'abra_3_43',
            'abra_4_02', 'abra_5_38', 'abra_5_54',
        }
        self.assertTrue(restored_figures.issubset(self.en.images))
        self.assertTrue(restored_figures.issubset(self.hu.images))
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

    def test_publication_contains_only_referenced_images(self):
        published = {path.name for path in (ROOT / 'dist/images').iterdir() if path.is_file()}
        referenced = {
            Path(image['src']).name
            for page in (self.hu, self.en)
            for image in page.images.values()
        }
        self.assertEqual(published, referenced)
        self.assertIn('Lako_tanszek.png', published)
        self.assertNotIn('Infoblokk3_ESZA_egyes.jpg', published)
        self.assertNotIn('USZT_logo_cmyk.jpg', published)

    def test_requirement_labels_and_loose_lists(self):
        self.assertIn(
            '<h5>KÖVETELMÉNYEK ÉS AJÁNLÁSOK</h5>',
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

        for xml, page in ((self.hu_xml, self.hu), (self.xml, self.en)):
            for item in xml.getroot().iter('listitem'):
                paragraphs = item.findall('para')
                if len(paragraphs) < 2:
                    continue
                for paragraph in paragraphs:
                    expected = normalized(''.join(paragraph.itertext())).removeprefix('– ')
                    self.assertIn(expected, page.list_items)

    def test_explicit_contributor_credits(self):
        monograms = re.compile(r'\((?:N\.\s*Á\.|P\.\s*A\.|B\.\s*J\.|AN|AP|(?:Dr\.\s*)?JB)\)')
        for source in (ROOT / 'sources/lakokonyv.md', ROOT / 'sources/lakokonyv_en.md'):
            self.assertNotRegex(source.read_text(encoding='utf-8'), monograms)
        self.assertIn('<p class="contributor-credit">— Novák Ágnes</p>', self.hu.html)
        self.assertIn('<p class="contributor-credit">— Ágnes Novák</p>', self.en.html)
        self.assertIn(
            '<h4 id="E1_Vizualis_komfort">1.5.6. Vizuális komfort</h4>\n'
            '<p class="contributor-credit heading-credit">— Novák Ágnes</p>',
            self.hu.html,
        )
        self.assertNotIn('Vizuális komfort (N.', self.hu.html)

    def test_historical_sections_are_explicit_markdown_headings(self):
        self.assertIn(
            '<h4 id="E3_falusi_csaladi_hazak">3.2.1. A\u00a0falusi családi házak</h4>',
            self.hu.html,
        )
        self.assertIn(
            '<h4 id="E3_varosias_csaladi_hazak">3.2.2. Urban homes</h4>',
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
