# Lakókönyv

A BME Lakóépülettervezési Tanszék 2013-as digitális tankönyvének rekonstruált,
magyar–angol statikus webes kiadása.

## Szerkezet

- `source/lakokonyv.md` – magyar szerkesztési mester.
- `source/lakokonyv_en.md` – angol szerkesztési mester, az eredeti fordításból.
- `source/xml/Bito_konyv.xml` – a magyar DocBook könyvkeret.
- `source/xml/Bito_konyv_en.xml` – az angol DocBook önálló, összefűzött archívuma.
- `source/images/` – közös, eredeti képanyag; a build nem módosítja.
- `template/book.html`, `assets/book.css`, `assets/book.js` – közös megjelenés és működés.
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
Az `incoming` mappa és a régi XML-ek nem szükségesek a mindennapi buildhez.
A build újragenerálja a teljes `dist` mappát; oda ne kerüljön kézzel szerkesztett forrás.

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
`source/images/` fájljai változatlanok maradnak.

## Forráshűség és szerkesztői ügyek

Az angol kiadás a kapott fordítás szövegét őrzi, nem a magyar mester új fordítása.
A két kiadás tagolása és ábrakészlete nem teljesen azonos: az angolban 201, a
magyarban 212 ábra szerepel. A közös képekbe rajzolt magyar feliratok megmaradnak;
az angol képaláírások a fordításból származnak. Részletek: `audit/english_import.md`.

A korábbi auditok történeti pillanatfelvételek. A régi README és a magyar
Markdown metaadatainak 5.59. ábrára vonatkozó `MISSING` jelzése elavult: a kép
már megvan. A nappálya-ábrák eredeti 3.14 / 3.15 / 3.16 számozási eltérését és
az 5.31. magyar képaláírás kettős ábraszámát az `audit/xml_comparison_2026-09-16.md`
részletezi. A szakmai szöveget és az eredeti fordítást nem modernizáljuk automatikusan.

Az egyszeri angol importot a `build/import_english.py` dokumentálja. Ezt nem kell
újra futtatni: a további szerkesztés helye a két Markdown-mester.
