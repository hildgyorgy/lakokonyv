# Az angol kiadás átvétele – 2026. szeptember 18.

## Szerkesztési forrás és eredet

Az angol kiadás szerkesztési mestere a `sources/lakokonyv_en.md`.
A szakmai szöveg a kapott nyolc DocBook-fejezetből származik; a kapott HTML-exporttal
is ellenőriztük. Nem készült új fordítás. Az ellenőrzés után a fejezetfájlok és a
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

A `build/import_english.py` az import dokumentált, kézzel futtatható eszköze.
Alapesetben már létező angol Markdown-mestert nem ír felül; a `--force` kapcsoló
szándékos újragenerálást tesz lehetővé. A rendes build nem hívja meg. A magyar
kiadásból visszahelyezett ábrák szabályai az
importálóban is szerepelnek, ezért újraimportáláskor sem vesznek el.

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
- A 48 angol megjegyzés megmaradt, a két egymást követő megjegyzés is külön blokk.
- A könyvcím a DocBook könyvkeret angol címe: „Housing design”. A HTML export
  címlapja még magyar címet tartalmazott; azt nem vettük át angol címként.
- A közreműködői szerepek magyar metaadatai angol feliratot kaptak. A fordító
  Oliver Sales. Az angol kivonat és a jogi közlés az eredeti angol XML-ből származik.

## Képek

Az eredeti angol forrás 201 ábrát tartalmazott, a magyar 212-t. A hiányzó
ábrahelyeket a magyar mester szerkezete alapján visszahelyeztük, ezért a kész
angol oldalon is mind a 212 könyvábra szerepel. A tanszéki logóval együtt mindkét
oldalon 213 képelőfordulás van. A két nyelv ugyanazt a `sources/images/`
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
képaláírása tévesen higiéniai felszereltséget nevez meg, miközben a rajz
egyértelműen ruhatárolási megoldásokat mutat; az angol felirat ezért
„Clothing storage arrangements”. Két nyilvánvaló régi kereszthivatkozást is a
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
- Mind a 201 eredeti angol ábra megmaradt, és 11 magyar ábrahelyet pótoltunk.
  A kész oldalon 212 könyvábra, 48 megjegyzés és 321 tartalmi belső link van.
- A generált oldalakon nincsenek duplikált azonosítók, hibás belső linkek vagy
  hiányzó hivatkozott képek. A nyelvváltó összes célpontja létezik a másik oldalon.
- Az angol oldalon a címsorok száma a magyaréhoz igazodik: a korábbi 338 helyett
  333 generált azonosító marad, miközben a 1152 ellenőrzött bekezdés és mind a
  201 eredeti ábra változatlanul megmarad, a pótlásokkal együtt 212 jelenik meg.
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
