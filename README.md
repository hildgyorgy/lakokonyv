# Lakókönyv

A BME Lakóépülettervezési Tanszék 2013-as digitális tankönyvének rekonstruált,
magyar–angol statikus webes kiadása.

## Szerkezet

- `sources/lakokonyv.md` – magyar szerkesztési mester.
- `sources/lakokonyv_en.md` – angol szerkesztési mester, az eredeti fordításból.
- `sources/xml/Bito_konyv_hu.xml` – a magyar DocBook önálló, összefűzött archívuma.
- `sources/xml/Bito_konyv_en.xml` – az angol DocBook önálló, összefűzött archívuma.
- `sources/images/` – közös, eredeti PNG/JPG képanyag; a build nem módosítja.
- `sources/images/avif/` – az eredeti képekből származtatott, publikálható webes változatok.
- `sources/images/avif-manifest.json` – az eredeti és webes képek ellenőrzőösszegei.
- `sources/originals/figures-pdf/` – 164 nyomdai ábraforrás későbbi, jobb minőségű képexporthoz; a build nem másolja a `dist` mappába.
- `template/book.html`, `assets/book.css`, `assets/book.js` – közös megjelenés és működés.
- `assets/fonts/` – helyben tárolt Inter 4.1 változó webfontok és OFL-licenc.
- `build/locales.json` – magyar és angol felületi feliratok.
- `build/build.py` – függőségmentes Python build és hivatkozásellenőrzés.
- `build/build_images.py` – macOS-en futó, inkrementális AVIF-frissítő.
- `audit/image_layout.json` – közös ábraméretezés és invertálhatóság.
- `workbench/index.html` – helyben, szerver nélkül megnyitható ábra-munkapad.
- `audit/english_import.md`, `audit/english_import.json` – az angol átvétel és a kiadások eltérései.
- `dist/` – generált kimenet, nem verziózandó.

## Build és ellenőrzés

Python 3.10 vagy újabb szükséges. A projekt gyökeréből:

```sh
python3 build/build.py
python3 build/test_bilingual.py
```

A build a két Markdown-forrásból elkészíti a `dist/index.html` magyar és a
`dist/index_en.html` angol oldalt, a közös stílusokat, szkripteket és
képmappát. Emellett frissíti a publikációtól elkülönített
`workbench/index.html` munkapad beágyazott képjegyzékét és beállításait. A
korábbi magyar URL-ek megmaradnak.
Minden megőrzött forrás a `sources/` mappában található. A build újragenerálja
a teljes `dist` mappát; oda ne kerüljön kézzel szerkesztett forrás.
Az XML-ekben megmaradt régi képútvonalak archivált hivatkozások. A korábbi
DocBook JPG/PNG exportok többszörös másolatai nem részei a repónak; a webes
kiadás ellenőrzött képei a `sources/images/` mappában vannak.

A normál build nem kódol képet: a Markdown PNG/JPG hivatkozásait a megfelelő
AVIF-változatra irányítja, és csak ezeket másolja a `dist/images/` mappába. Ha
egy eredeti kép megváltozik vagy új kép kerül a könyvbe, macOS-en előbb futtasd:

```sh
python3 build/build_images.py
```

A parancs SHA-256 ellenőrzőösszeg alapján csak a hiányzó vagy megváltozott
képeket kódolja újra. A build hibával jelzi, ha egy AVIF hiányzik vagy elavult.
Az összes kép szándékos újrakódolásához használható a `--force` kapcsoló.

A Markdown szerkezeti konvenciói közvetlenül tükrözik a könyvet: egyetlen `#`
szintű könyvcímet követnek a `##` főfejezetek, a `###` alfejezetek és a `####`
alszakaszok; ezek kerülnek a tartalomjegyzékbe. A `#####` szint a
„KÖVETELMÉNYEK ÉS AJÁNLÁSOK” blokkok címe. A szerzői sorok `— Teljes név`
alakú önálló bekezdések. Minden megjegyzés félreérthetetlenül lezárt blokk:

```md
::: note
A megjegyzés szövege.
:::
```

A builder ezen kívül bekezdést, félkövér és dőlt kiemelést, hivatkozást,
egyszerű rendezett és rendezetlen listát, képet képaláírással, idézetblokkot és
vízszintes elválasztót kezel. Összetett vagy beágyazott Markdown-szerkezetet
csak a builder bővítése és új teszt után szabad a mesterekbe írni.

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

A `workbench/index.html` az összes közös kép webes AVIF-változatát mutatja, és közvetlenül,
szerver nélkül megnyitható. A csúszkával állítható szélesség és a sötét
módbeli invertálhatóság exportálható a „Méretlista exportálása” gombbal. Az
exportált fájl kerüljön az `audit/image_layout.json` helyére. Új build után a
beállítások mindkét nyelven érvényesek, a munkapad beágyazott adatai
frissülnek, a `sources/images/` fájljai pedig változatlanok maradnak. A
`dist/` nem tartalmazza a munkapadot, ezért az nem kerül a GitHub Pages oldalra.

## Forráshűség és szerkesztői ügyek

Az angol kiadás alapja a kapott fordítás; az XML ezt az eredeti állapotot
változatlanul őrzi, a Markdownban pedig a dokumentált szerkezeti, nyelvi és
szerkesztői javítások készülnek. Az angol Abstract a magyar Kivonat fordítása.
Az eredeti angol forrás 201 ábrát tartalmazott; a magyar mesterből pótolt 11
ábrahely és az egyedi eredeti PDF-ekből helyreállított további hat ábra után a
kész magyar és angol kiadásban egyaránt 218 könyvábra szerepel.
A két oldal ugyanazokat a képfájlokat használja. A képekbe rajzolt magyar
feliratok megmaradnak; az angol képaláírások angolok. Részletek:
`audit/english_import.md`.

A korábbi auditok történeti pillanatfelvételek. A régi README és a magyar
Markdown metaadatainak 5.59. ábrára vonatkozó `MISSING` jelzése elavult: a kép
már megvan. A nappálya-ábrák eredeti 3.14 / 3.15 / 3.16 számozási eltérését és
az 5.31. magyar képaláírás kettős ábraszámát az `audit/xml_comparison_2026-09-16.md`
részletezi. A szakmai szöveget és az eredeti fordítást nem modernizáljuk automatikusan.
A Claude-féle felülvizsgálat minden tételének állapota az
`audit/claude_review_triage.md` fájlban követhető.

A webes kiadás nem telepíthető PWA, ezért nem használ webmanifestet. A build a
`dist/images/` mappába csak a két Markdown-mesterben ténylegesen hivatkozott
képeket másolja; az archivált vagy szerkesztői döntésre váró képek a
`sources/images/` mappában és a helyi workbenchben továbbra is elérhetők.

A `build/import_english.py` a kezdeti angol rekonstrukció történeti,
függőségmentes segédeszköze. A rendes build nem futtatja, és a már szerkesztett
angol mestert nem írhatja felül. A publikáció kizárólagos szerkesztési forrásai
a két Markdown-mester; az XML-ek változatlan ellenőrző archívumok.
