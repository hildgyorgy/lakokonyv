# Az angol kiadás átvétele – 2026. szeptember 18.

## Szerkesztési forrás és eredet

Az angol kiadás szerkesztési mestere a `sources/lakokonyv_en.md`.
A szakmai szöveg a kapott nyolc DocBook-fejezetből származik; a kapott HTML-exporttal
is ellenőriztük. Az ellenőrzés után a fejezetfájlok és a
HTML másolatát eltávolítottuk, mert tartalmukat az összefűzött XML és a Markdown
hiánytalanul megőrzi. A magyar `sources/lakokonyv.md`, a képállomány és az
`audit/image_layout.json` változatlan.

A `sources/xml/Bito_konyv_en.xml` önálló, összefűzött archiválási példány a
`Bito_konyv_hu.xml` magyar archívum mellett. A fejezeteket helyben feloldott XInclude-okból tartalmazza,
külső DTD-letöltés nélkül olvasható. Megőrzi az eredeti angol szöveget,
azonosítókat és képhivatkozásokat. **Az eredeti angol képhivatkozások archivált
adatok: a megadott régi ábrafájlok nem részei a megtisztított forráskészletnek.** A weboldal
működő, közös képútvonalai a Markdownban vannak. Ez nem DocBook DTD-validálás.
Az aktuális archiválási forrás SHA-256 ujjlenyomata az `english_import.json`
mellékletben szerepel.

A `build/import_english.py` a kezdeti import dokumentált, történeti
segédeszköze. A rendes build nem hívja meg, és a már szerkesztett angol
Markdown-mestert nem írhatja felül. Az azóta elvégzett szerkezeti, nyelvi és
ábra-helyreállítási munkák igazságforrása maga a Markdown; az XML változatlan
ellenőrző archívum.

## Szerkezet és megfeleltetés

- Bevezetés és mind a hét főfejezet átkerült.
- Az angol XML 132 fejezet-/alfejezet-elemet tartalmazott. A kiadott angol
  Markdownban a magyarhoz igazított címsorhierarchia miatt öt technikai
  alszintet összevontunk: `3.3.1`, `4.2.1`, `4.2.2`, `5.2.1` és
  „Additional heating assistance”. A hozzájuk tartozó szöveg változatlanul,
  a közös szülőfejezet megfelelő helyén maradt.
- A magyarban számozatlan „Hatósági építési követelmények, szabályzatok” és
  „Az európai fejlődés” tartalma így közvetlenül a megfelelő magyar szerkezeti
  szinten jelenik meg az angol oldalon is. A címek nem vesznek el: ahol nincs
  külön magyar címsor, a magyar fejezetcím az irányadó.
- Az angol XML 48 `note` elemet tartalmaz. Ezek közül 45 explicit `::: note`
  blokk maradt a Markdownban. A „Rural Homes” és „Urban Homes” anyagát valódi
  3.2.1 és 3.2.2 alfejezetté emeltük; az 5.2. történeti áttekintés egykori
  megjegyzésblokkja pedig a fejezet rendes törzsszövege lett.
- A könyvcím a DocBook könyvkeret angol címe: „Housing design”. A HTML export
  címlapja még magyar címet tartalmazott; azt nem vettük át angol címként.
- A közreműködői szerepek magyar metaadatai angol feliratot kaptak. A fordító
  Oliver Sales. Az angol kivonat a magyar Kivonat fordítása; az eredeti XML
  helyőrzőként a Bevezetés elejét ismételte. A Markdownban dokumentált
  szerkesztői javítások nem írják át az archív XML-t.

## Képek

Az eredeti angol XML 201 ábrát, a rekonstrukció első magyar mestere 212-t
tartalmazott. A magyar szerkezet alapján pótolt 11 angol ábrahely mellett az
archivált egyedi ábra-PDF-ekből további hat, mindkét korai Markdown-mesterből
kimaradt ábrát állítottunk helyre: 1.37, 3.17, 3.43, 4.2, 5.38 és 5.54. Így a
kész kiadás mindkét nyelven 218 könyvábrát és a három előzéki logóval együtt
221 képelőfordulást tartalmaz. A két nyelv ugyanazt a `sources/images/`
állományt, ugyanazokat a workbench-szélességeket és ugyanazokat a sötét módbeli
invertálási beállításokat használja.

Az eredeti angol kiadásból az alábbi 11 ábra-előfordulás hiányzott:

- `abra_1_18`, `abra_1_36`, `abra_1_38`, `abra_1_39`, `abra_1_44`;
- `abra_3_11`, `abra_3_22_E5`, `abra_3_23_E5`, `abra_3_52`;
- `abra_5_19`, `abra_6_03`.

Ez 9 különböző képfájlt jelent, mert az `abra_3_22_E5` és
`abra_3_23_E5` a 3. fejezet két ábrájának szándékos, 5. fejezetbeli ismétlése.
A kilenc különböző kép közül nyolc rajz vagy diagram, és egyetlen valódi fotó
van: `abra_6_03_unagy.png`, U. Nagy Gábor falusi környezetben álló nyaralója.
A pótlás után egyetlen magyar ábra sem hiányzik az angol oldalról.

A visszahelyezett ábrák angol képaláírást és alternatív szöveget kaptak, a
szövegben pedig működő hivatkozás vezet hozzájuk. A magyar mester 1.38. ábrájának
képaláírása tévesen higiéniai felszereltséget nevezett meg, miközben a rajz
egyértelműen ruhatárolási megoldásokat mutatott; a magyar és angol feliratot is
helyesbítettük. Két nyilvánvaló régi kereszthivatkozást is a
magyar szerkezethez igazítottunk: 1.16 → 1.18 és 3.10 → 3.11.

A képaláírások és alternatív szövegek angolok; **a közös képekbe rajzolt magyar
feliratok változatlanok maradnak**, azokat ez az átvétel nem fordítja át.

A nappálya-szerkesztési ábra angol XML-azonosítója `abra_3_15`, de képfájlja
`eng_3_14_napdiaszerk.png`, a szöveges hivatkozása pedig „fig. 3.14”. A webes
mesterben ezért a magyarhoz illeszkedő `abra_3_14` azonosítót és 3.14. ábraszámot
kapta; az XML-archívum megőrzi a régi azonosítót. Az 5.59. ábránál a magyar
mester már helyes képútvonalát használjuk, nem a régi XML útvonalhibáját.

## Ellenőrzés

- 1152, ábrát vagy listakonténert nem tartalmazó XML-bekezdés szövege
  szóköz-normalizálás után hiánytalanul szerepel az angol HTML-ben és a kapott
  eredeti HTML-exportban is.
- A fordított irányú összevetés sem mutatott többlet szakmai bekezdést a kapott
  HTML-ben; a további elemek a generált „Table of Contents” feliratok.
- Mind a 201 eredeti angol ábra megmaradt, 11 magyar ábrahelyet pótoltunk, majd
  hat további ábrát az eredeti egyedi PDF-ekből állítottunk helyre. A kész oldalon
  218 könyvábra és 45 megjegyzés van; az XML két korábbi megjegyzése önálló
  alfejezetként, egy további pedig az 5.2. történeti áttekintés törzsszövegeként él tovább.
- A generált oldalakon nincsenek duplikált azonosítók, hibás belső linkek vagy
  hiányzó hivatkozott képek. A nyelvváltó összes célpontja létezik a másik oldalon.
- Az angol oldalon a címsorok száma a magyaréhoz igazodott: a korábbi 338 helyett
  333 generált azonosító maradt az első rekonstrukcióban, miközben az 1152
  ellenőrzött bekezdés és mind a 201 eredeti angol ábra változatlanul megmaradt.
  A később megtalált ábra-PDF-ek helyreállításával jelenleg 218 könyvábra jelenik meg.
- A közös ábrák útvonala, méretezése és invertálhatósága megegyezik a két oldalon.
- A magyar renderelt szöveg és ábraazonosítók összevetése megtörtént a korábbi
  builddel. Tartalmi átírás nem történt. Két jelöléskezelési hibát javítottunk:
  a HTML-szerkesztői megjegyzés rejtve marad, a `<sup>` felső indexként jelenik meg.
- Böngészőben ellenőriztük a HU → EN és EN → HU fejezetváltást, az asztali
  és mobil elrendezést, valamint a csak angol címsorról történő visszalépést
  a megfelelő közös magyar szülőfejezetre.
- A build kiírja a képek valódi szélességét és magasságát is, így a késleltetett
  betöltés nem változtatja meg a fenntartott helyet. A workbench százalékos
  méretezése továbbra is elsőbbséget élvez.

Újrafuttatható regressziós ellenőrzés, külső függőségek nélkül:

```sh
python3 build/build.py
python3 build/test_bilingual.py
```

Az ellenőrzés az átvétel hűségére vonatkozik. Az eredeti fordítás nyelvi,
szakmai vagy számszerű hibáit nem javítottuk hallgatólagosan.
