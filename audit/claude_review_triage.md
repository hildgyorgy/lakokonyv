# A Claude-hibalista tételes feldolgozása

Frissítve: 2026-09-21

Ez a lista a `lakokonyv_hibalista.md` minden tételét nyilvántartja. Az XML-ek változatlan archív ellenőrzőforrások; a szerkesztett könyv mesterei a két Markdown-fájl.

| ID | Állapot | Döntés / eredmény |
|---|---|---|
| B-01 | javítva | Minden valódi megjegyzés explicit `::: note … :::` blokk a Markdownban. Nincs több, üres sorokból következtető szétválasztás; a történeti fejezetrészek szerkesztői átminősítése után 83 magyar és 45 angol megjegyzés maradt. |
| B-02 | javítva | A `---` szemantikus `<hr>`, a záró `*` díszített `<hr class="ornamental-break">`. |
| B-03 | javítva | A `***…***` szabály helyes `<strong><em>…</em></strong>` kimenetet ad. |
| B-04 | javítva | A könyvcím explicit `book_title` azonosítót kapott; az automatikus azonosító Unicode-normalizálással őrzi meg az ékezetes betűket. |
| B-05 | javítva | A README felsorolja a támogatott Markdown-részhalmazt, és előírja, hogy összetett új szerkezet csak builderbővítéssel és teszttel kerülhet a mesterekbe. |
| B-06 | javítva | A tartalomjegyzékből kizárt előzékek explicit azonosítók alapján, mindkét nyelven azonos szabállyal maradnak ki. |
| H-01 | javítva | A két vezérlőcsoport `<fieldset>` és `<legend>` szerkezetet használ. |
| H-02 | javítva | A címsorhierarchia folytonos: egy H1 könyvcím, H2 főfejezet, H3 alfejezet, H4 alszakasz, H5 követelményblokk. |
| H-03 | javítva | Egyetlen H1 van; a címoldal külön `<header class="book-title">`, a H2–H4 hierarchia pedig egymásba ágyazott, `aria-labelledby` kapcsolattal ellátott `<section>` elemekből áll. |
| H-04 | javítva | A valódi kiegészítések `<aside class="note">` elemek maradnak. A teljes 5.2. történeti áttekintés mindkét nyelven, a teljes magyar 6.2. pedig rendes törzsszöveg lett; csak a `::: note` kereteket vettük le, a tartalom és az ábrák nem változtak. |
| H-05 | tudatosan lezárva | A követelményblokkok valódi H5 címsorok. Tartalmuk vegyesen bekezdés és lista, nem egységes címke–érték pár, ezért a `<dl>` félrevezető volna. |
| H-06 | javítva | A két valódi angol álcím és magyar párjuk H5 címsor lett a Markdownban. A követelménycímkék és a mondatértékű félkövér bevezetések szándékosan nem címsorok. |
| H-07 | javítva | A TOC `<nav>`. A lenyitás külön gomb, a fejezetcím külön link; nincs `<summary>` + belső link kettős fókusz. |
| A-01 | tudatosan elutasítva | A nyolc logószín és működésük végleges szerzői döntés; nem módosítjuk. |
| A-02 | javítva a jelenlegi körben | A képaláírással azonos alt szöveg helyett a képek dekoratív `alt=""` értéket kapnak, így a képernyőolvasó nem ismétli meg a feliratot. Az összetett ábrák hosszú szakmai leírása külön tartalomfejlesztés lehet. |
| A-03 | javítva | A csökkentett mozgást kérő beállítás kikapcsolja a sima görgetést és az átmeneteket. |
| A-04 | javítva | A nyelvváltók neve „HU – Magyar”, illetve „EN – English”. |
| A-05 | javítva | Elkészült az „Ugrás a könyv szövegéhez” / „Skip to the book text” link. |
| A-06 | tudatosan megtartva | A mobil vezérlők helye a kialakított, elfogadott felület része. |
| J-01 | javítva | A könyv és a workbench tárolókezelése `try/catch` védelmet kapott; hibás workbench-JSON sem állítja le az oldalt. |
| T-01 | javítva | A 3.17. ábra egyedi eredeti PDF-jét ellenőriztük, és az abból származó közös képet a nappálya-diagram magyarázata után helyeztük vissza mindkét Markdownba. |
| T-02 | részben javítva | Mindkét nyelven látható, Hild György által jegyzett szerkesztői figyelmeztetés került a Bevezetés elé. Az OTÉK/TÉKA szakmai felülvizsgálata külön munka; nincs mechanikus csere. |
| T-03 | szerkesztői döntéssel lezárva | Az archív XML megőrzi a támogatói logókat, de a támogatási időszak lejárta miatt a két kép kikerült mindkét Markdown címoldaláról. A tanszéki logó megmaradt. |
| T-04 | javítva | A magyar mesterben az `m3` és a HTML felső indexek Unicode `m³`, illetve `m²` alakra egységesedtek. |
| T-05 | javítva | A dátum és aláírás nélküli, csonka „Budapest,” / „Budapest” zárósort eltávolítottuk mindkét Markdown-mesterből. |
| E-01 | javítva | Az Abstract a magyar Kivonat önálló angol fordítása lett; nem ismétli a Bevezetést. |
| E-02 | javítva | „In Section 1.3” szerepel. |
| E-03 | javítva | `preject`, `it is not does cover everything` és `Könvykiadó` javítva a Markdownban. |
| E-04 | javítva | A címek sentence case formát kaptak. Az eredeti fordításban túlsúlyban lévő amerikai írásmód lett az alap; a kevert `multi-storey` és `centre` alakok egységesedtek. Több egyértelmű elütés és nyelvtani hiba is javult. |
| S-01 | javítva | A két nyelv és a rendezett fejezetszerkezet összevetése egyértelművé tette a négy célpontot: 1.51/1.53 → 1.5.1/1.5.2, 1.4.1 → 1.5.1, a régi 3.1.1 → a jelenlegi 3.2.1. Mind explicit Markdown-link lett. |
| S-02 | javítva | A létező fejezethivatkozások explicit Markdown-linkek mindkét mesterben; a build nem próbál szövegből célpontot találni. |
| S-03 | javítva / forráshűen megtartva | Az angol 5.52 ábrát a magyar szerkezettel egyezően az 5.53 elé helyeztük, a téves 5.42 hivatkozást 5.52-re javítottuk. A többi számsorrendi visszalépés az archív XML-ekben is ugyanott szerepel, ezért tartalmi elhelyezésként megmarad. |
| S-04 | részben javítva | Hat valóban hiányzó ábrát az egyedi eredeti PDF-ekből helyreállítottunk mindkét Markdownban: 1.37, 3.17, 3.43, 4.2, 5.38 és 5.54. A további, külön PDF nélküli hézagokat csak a teljes könyv-PDF alapján lehet eldönteni. |
| S-05 | tudatosan lezárva | A 7. fejezet eltérő szerkezetét megtartjuk; nem egészítjük ki kitalált előszóval. |
| S-06 | ellenőrizve / megtartva | A magyar archív XML az 5. fejezetben külön `abra_3_22_E5` és `abra_3_23_E5` ismétlést tartalmaz, az 5.19 ábrát pedig explicit a 7. fejezet rehabilitációs szövegéhez helyezi. Mindkettő forráshű, tudatos elrendezés. |
| M-01 | javítva | A meta author a nyelvi Markdown front matteréből érkezik. |
| M-02 | javítva | A statikus tankönyv nem PWA: a hiányos manifest-hivatkozás és a publikus másolás megszűnt. |
| M-03 | javítva | A GitHub Pages végleges címéhez abszolút canonical, magyar és angol hreflang, valamint x-default került. |
| R-01 | javítva | Regressziós teszt ellenőrzi a megjegyzésszámot, elválasztókat, hangsúlybeágyazást, egyetlen H1-et, nav TOC-ot és skip linket. |
| R-02 | javítva | Az angol importleírás az XML 48 note elemét és a szerkesztői átminősítések után Markdownban maradt 45 megjegyzést külön kezeli. A `qa.json` explicit jelzi, hogy történeti rekonstrukciós pillanatkép, nem az aktuális kiadás statisztikája. |
| R-03 | javítva | A build csak a két Markdownban hivatkozott képeket publikálja. A három döntésre váró állomány a forrásban és a workbenchben megmarad, a `dist`-be nem kerül. |
| R-04 | nyitott | A képtömörítés és korszerű képformátumok külön teljesítménykör. |
| R-05 | nem hiba | `.DS_Store` és `__pycache__` ignorált és nem követett; a Claude-nak adott archívum tartalma nem a repository követési állapota. |
| R-06 | tudatosan megtartva | Az XML-ek archív források, ezért a névsorrendet és ISBN-helyőrzőt nem írjuk át bennük. |

Az aktuális technikai kör után a build és mind a 13 regressziós teszt hibátlanul fut.
