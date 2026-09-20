# Lakókönyv

A BME Lakóépülettervezési Tanszék 2013-as digitális tankönyvének rekonstruált,
magyar–angol statikus webes kiadása.

## Szerkezet

- `sources/lakokonyv.md` – magyar szerkesztési mester.
- `sources/lakokonyv_en.md` – angol szerkesztési mester, az eredeti fordításból.
- `sources/xml/Bito_konyv_hu.xml` – a magyar DocBook önálló, összefűzött archívuma.
- `sources/xml/Bito_konyv_en.xml` – az angol DocBook önálló, összefűzött archívuma.
- `sources/images/` – közös, eredeti képanyag; a build nem módosítja.
- `sources/originals/figures-pdf/` – 164 nyomdai ábraforrás későbbi, jobb minőségű képexporthoz; a build nem másolja a `dist` mappába.
- `template/book.html`, `assets/book.css`, `assets/book.js` – közös megjelenés és működés.
- `assets/fonts/` – helyben tárolt Inter 4.1 változó webfontok és OFL-licenc.
- `build/locales.json` – magyar és angol felületi feliratok.
- `build/build.py` – függőségmentes Python build és hivatkozásellenőrzés.
- `audit/image_layout.json` – közös ábraméretezés és invertálhatóság.
- `audit/english_import.md`, `audit/english_import.json` – az angol átvétel és a kiadások eltérései.
- `dist/` – generált kimenet, nem verziózandó.

## Build és ellenőrzés

Python 3.10 vagy újabb szükséges. A projekt gyökeréből:

```sh
python3 build/build.py
python3 build/test_bilingual.py
```

A build a két Markdown-forrásból elkészíti a `dist/index.html` magyar és a
`dist/index_en.html` angol oldalt, a közös stílusokat, szkripteket, képmappát
és a `dist/workbench.html` munkapadot. A korábbi magyar URL-ek megmaradnak.
Minden megőrzött forrás a `sources/` mappában található. A build újragenerálja
a teljes `dist` mappát; oda ne kerüljön kézzel szerkesztett forrás.
Az XML-ekben megmaradt régi képútvonalak archivált hivatkozások. A korábbi
DocBook JPG/PNG exportok többszörös másolatai nem részei a repónak; a webes
kiadás ellenőrzött képei a `sources/images/` mappában vannak.

A Markdown szerkezeti konvenciói közvetlenül tükrözik a könyvet: az első három
címszint kerül a tartalomjegyzékbe, a `####` szint a „KÖVETELMÉNYEK ÉS
AJÁNLÁSOK” blokkok címe, a szerzői sorok pedig `— Teljes név` alakú önálló
bekezdések. A `> **Megjegyzés**`, illetve `> **Note**` kezdetű idézetblokkok
megjegyzésként jelennek meg.

A fejléc HU / EN váltója a megfelelő fejezetre vagy ábrára visz. Ha egy elem
csak az egyik kiadásban szerepel, a legközelebbi közös szülőfejezet a célpont.
A fejléc görgetés közben is elérhető. JavaScript nélkül a nyelvi oldalak
kezdőpontjai közötti váltás működik. A szín- és igazításbeállítás közös.

Helyi előnézet:

```sh
python3 -m http.server 8765 --bind 127.0.0.1 --directory dist
```

Ezután nyisd meg a `http://127.0.0.1:8765/` címet. A HTML-ek helyi fájlként is
megnyithatók, de a böngésző helyi fájlokra vonatkozó tárolási szabályai eltérhetnek.

## Ábra-munkapad

A `dist/workbench.html` az összes közös képet mutatja. A csúszkával állítható
szélesség és a sötét módbeli invertálhatóság exportálható a „Méretlista
exportálása” gombbal. Az exportált fájl kerüljön az `audit/image_layout.json`
helyére. Új build után a beállítások mindkét nyelven érvényesek; a
`sources/images/` fájljai változatlanok maradnak.

## Forráshűség és szerkesztői ügyek

Az angol kiadás a kapott fordítás szövegét őrzi, nem a magyar mester új fordítása.
Az eredeti angol forrás 201 ábrát tartalmazott; a magyar mesterből pótolt 11
ábrahellyel a kész magyar és angol kiadásban egyaránt 212 könyvábra szerepel.
A két oldal ugyanazokat a képfájlokat használja. A képekbe rajzolt magyar
feliratok megmaradnak; az angol képaláírások angolok. Részletek:
`audit/english_import.md`.

A korábbi auditok történeti pillanatfelvételek. A régi README és a magyar
Markdown metaadatainak 5.59. ábrára vonatkozó `MISSING` jelzése elavult: a kép
már megvan. A nappálya-ábrák eredeti 3.14 / 3.15 / 3.16 számozási eltérését és
az 5.31. magyar képaláírás kettős ábraszámát az `audit/xml_comparison_2026-09-16.md`
részletezi. A szakmai szöveget és az eredeti fordítást nem modernizáljuk automatikusan.

Az angol importot a `build/import_english.py` dokumentálja. A rendes build nem
futtatja; szükség esetén a `--force` kapcsolóval reprodukálható, a további
szerkesztés helye pedig a két Markdown-mester.
